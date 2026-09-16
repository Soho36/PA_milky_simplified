"""Independently verify saved routing demand, capacity and cash evidence."""
import csv
import argparse
import gzip
from datetime import datetime
import json
from pathlib import Path

from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file


def read_csv(path):
    if path.exists():
        handle = path.open(encoding='utf-8', newline='')
    else:
        handle = gzip.open(path.with_suffix('.csv.gz'), 'rt', encoding='utf-8', newline='')
    with handle:
        return list(csv.DictReader(handle))


def audit(root):
    payload = json.loads((root / 'study.json').read_text(encoding='utf-8'))
    profile = payload['profile']
    fixed = payload['schema'] == 'pa_milky.fixed_pool_study.v1'
    for name, expected in payload.get('evidence_files', {}).items():
        assert sha256_file(root / name) == expected, name
    expected_cases = (len(profile['starts']) * len(profile['copies']) * len(profile['withdrawals']) if fixed else
                      len(profile['starts']) * len(profile['budgets']) * len(profile['acquisitions']) * len(profile['withdrawals']))
    assert len(payload['rows']) == expected_cases * (int(not fixed) + len(profile['allocations']))
    cases = sorted({r['case'] for r in payload['rows']})
    assert len(cases) == expected_cases
    arms = copies = 0
    for case in cases:
        folder = root / case
        case_payload = json.loads((folder / 'case.json').read_text(encoding='utf-8'))
        assert case_payload['rows'] == [r for r in payload['rows'] if r['case'] == case]
        demand_rows = read_csv(folder / 'demand.csv')
        demand = {r['trade_key']: r for r in demand_rows}
        assert len(demand) == len(demand_rows)
        reference = case_payload['rows'][0]
        owner_contributions = (reference['initial_seat_funding_usd'] if fixed else
                               sum(float(e['amount_usd']) for e in read_csv(folder / 'reference_cash.csv')
                                   if e['kind'] == 'owner_contribution'))
        assert sum(int(r['copies']) for r in demand_rows) == reference['copies']
        fee = case_payload['config']['product']['purchase_fee_usd']
        for row in case_payload['rows']:
            allocation = row['arm']
            accounts = read_csv(folder / f'{allocation}_accounts.csv')
            payouts = read_csv(folder / f'{allocation}_payouts.csv')
            assert len(accounts) == row['accounts']
            assert round(sum(float(r['received_usd']) for r in payouts) - len(accounts) * fee, 2) == row['total_net_usd']
            if allocation == 'reference':
                continue
            assert round(owner_contributions + row['additional_external_funding_usd']
                         + row['total_net_usd'], 2) == row['financing']['ending_owner_cash_usd']
            arms += 1
            account_map = {int(a['account_id']): a for a in accounts}
            fills = read_csv(folder / f'{allocation}_fills.csv')
            assert len(fills) == len(demand)
            seen = set()
            occupied_until = {}
            trade_counts = {}
            filled = 0
            for fill in fills:
                key = fill['trade_key']
                assert key not in seen
                seen.add(key)
                entry = datetime.fromisoformat(fill['entry_at'])
                exit_at = datetime.fromisoformat(fill['exit_at'])
                assert entry == datetime.fromisoformat(demand[key]['entry_at'])
                assert exit_at == datetime.fromisoformat(demand[key]['exit_at'])
                ids = [int(x) for x in fill['accounts'].split(';') if x]
                assert len(ids) == len(set(ids)) == int(demand[key]['copies']) == int(fill['requested'])
                for account_id in ids:
                    a = account_map[account_id]
                    assert datetime.fromisoformat(a['activated_at']) <= entry
                    assert occupied_until.get(account_id, entry) <= entry, (case, allocation, key, account_id)
                    if a['died_at']:
                        death = datetime.fromisoformat(a['died_at'])
                        assert entry <= death
                        if entry == death:
                            assert a['death_trade_key'] == key
                    occupied_until[account_id] = exit_at
                    trade_counts[account_id] = trade_counts.get(account_id, 0) + 1
                filled += len(ids)
            assert seen == set(demand)
            assert filled == reference['copies'] == row['copies']
            assert all(int(a['trades_taken']) == trade_counts.get(int(a['account_id']), 0) for a in accounts)
            purchases = read_csv(folder / f'{allocation}_purchases.csv')
            assert sum(int(p['count']) for p in purchases) == len(accounts)
            assert len(accounts) * fee == row['purchase_cost_usd']
            if fixed or profile.get('procurement') == 'reuse':
                audit_incremental_purchases(fills, accounts, purchases, demand,
                                            profile['max_live_accounts'] if fixed else None)
            if fixed:
                assert row['peak_live'] <= profile['max_live_accounts']
            copies += filled
    return {'cases': len(cases), 'routed_arms': arms, 'audited_copy_assignments': copies,
            'no_overlap': True, 'exact_requested_demand': True, 'cash_reconciled': True,
            'incremental_purchases_verified': fixed or profile.get('procurement') == 'reuse'}


def audit_incremental_purchases(fills, accounts, purchases, demand, cap):
    """Reconstruct pre-purchase free seats, independent of recorded free counts."""
    initial = [p for p in purchases if p['emergency'] == 'False']
    assert len(initial) <= 1
    seed_count = int(initial[0]['count']) if initial else 0
    known = set(range(1, seed_count + 1))
    account_map = {int(a['account_id']): a for a in accounts}
    until, seen, inferred = {}, set(), []

    def alive(account_id, at):
        a = account_map[account_id]
        if datetime.fromisoformat(a['activated_at']) > at:
            return False
        if not a['died_at']:
            return True
        death = datetime.fromisoformat(a['died_at'])
        if death != at:
            return death > at
        # Existing exits precede new entries. A zero-duration death occurs only
        # after its own offer has been processed at the shared timestamp.
        d = demand.get(a['death_trade_key'])
        return bool(d and datetime.fromisoformat(d['entry_at']) == death
                    and a['death_trade_key'] not in seen)

    for f in fills:
        at = datetime.fromisoformat(f['entry_at'])
        live = {i for i in known if alive(i, at)}
        free = {i for i in live if until.get(i, at) <= at}
        wanted = int(f['requested'])
        needed = max(0, wanted - len(free))
        if cap is not None:
            needed = min(needed, cap - len(live))
        assert int(f['free_before_purchase']) == len(free)
        assert int(f['purchased']) == needed, (f['trade_key'], needed, f['purchased'])
        if needed:
            first_new = max(known, default=0) + 1
            new = set(range(first_new, first_new + needed))
            assert all(datetime.fromisoformat(account_map[i]['activated_at']) == at for i in new)
            known.update(new)
            live.update(new)
            free.update(new)
            inferred.append((f['entry_at'], needed))
        assert len(live) == int(f['alive'])
        if cap is not None:
            assert len(live) <= cap
        ids = {int(i) for i in f['accounts'].split(';') if i}
        assert ids <= free
        for i in ids:
            until[i] = datetime.fromisoformat(f['exit_at'])
        seen.add(f['trade_key'])
    assert known == set(account_map)
    assert inferred == [(p['at'], int(p['count'])) for p in purchases if p['emergency'] == 'True']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=PROJECT_ROOT / 'results/legacy_25k/routing_capacity_reuse')
    root = parser.parse_args().root
    result = audit(root)
    (root / 'AUDIT.generated.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
