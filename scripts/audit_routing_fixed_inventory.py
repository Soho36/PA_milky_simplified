"""Independent evidence audit: inventory, cash, coverage and single-position use."""
from datetime import datetime
import json

from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from audit_legacy_routing import read_csv


def cents(value):
    return round(float(value) * 100)


def audit(root):
    data = json.loads((root/'study.json').read_text(encoding='utf-8'))
    for name, checksum in data['evidence_files'].items():
        assert sha256_file(root/name) == checksum, name
    cases = sorted({r['case'] for r in data['rows']})
    assert len(cases) == len(data['profile']['starts'])*len(data['profile']['retained_balances'])
    total_copies = offers = exact_pairs = 0
    for case in cases:
        folder = root/case
        meta = json.loads((folder/'case.json').read_text(encoding='utf-8'))
        assert meta['rows'] == [r for r in data['rows'] if r['case'] == case]
        fee = cents(meta['config']['product']['purchase_fee_usd'])
        demand = read_csv(folder/'demand.csv')
        ref = {f['trade_key']: int(f['reference_copies']) for f in demand}
        full = {f['trade_key']: int(f['full_target_copies']) for f in demand}
        common_tape = None
        for row in meta['rows']:
            arm = row['arm']
            accounts = read_csv(folder/f'{arm}_accounts.csv')
            payouts = read_csv(folder/f'{arm}_payouts.csv')
            fills = read_csv(folder/f'{arm}_fills.csv')
            amap = {int(a['account_id']): a for a in accounts}
            assert len(accounts) == len(amap) == row['initial_accounts'] == row['accounts']
            assert set(amap) == set(range(1, len(accounts)+1))
            activation = {datetime.fromisoformat(a['activated_at']) for a in accounts}
            assert len(activation) == 1
            assert next(iter(activation)) <= min(datetime.fromisoformat(f['entry_at']) for f in fills)
            assert len(accounts)*fee == cents(row['purchase_cost_usd'])
            assert sum(cents(p['received_usd']) for p in payouts) == cents(row['total_received_usd'])
            assert cents(row['total_received_usd'])-len(accounts)*fee == cents(row['total_net_usd'])
            assert cents(row['ongoing_net_usd'])+cents(row['terminal_received_usd']) == cents(row['total_net_usd'])
            assert sum(a['alive'] == 'True' for a in accounts) == row['alive']
            assert sum(bool(a['died_at']) for a in accounts) == row['deaths']
            assert row['alive']+row['deaths'] == len(accounts)
            if row['group'] == 'same_resources':
                assert len(accounts) == 20
            tape = {f['trade_key']: (f['entry_at'], f['exit_at']) for f in fills}
            assert len(tape) == len(fills) == row['signals_loaded'] == len(ref)
            if common_tape is None:
                common_tape = tape
            assert tape == common_tape
            until, seen, counts, per_account = {}, set(), {}, {}
            wanted = signals = zero = 0
            for f in fills:
                key = f['trade_key']
                entry, exit_at = map(datetime.fromisoformat, (f['entry_at'], f['exit_at']))
                ids = [int(i) for i in f['accounts'].split(';') if i]
                assert len(ids) == len(set(ids))
                target = int(f['requested'])
                wanted += target
                signals += bool(ids)
                zero += target == 0
                counts[key] = len(ids)
                if arm != 'unlimited_20':
                    live = set()
                    for i, a in amap.items():
                        if a['died_at']:
                            death = datetime.fromisoformat(a['died_at'])
                            if death < entry:
                                continue
                            if death == entry:
                                dt = tape[a['death_trade_key']]
                                if datetime.fromisoformat(dt[0]) != death or a['death_trade_key'] in seen:
                                    continue
                        live.add(i)
                    free = {i for i in live if until.get(i, entry) <= entry}
                    assert int(f['alive']) == len(live)
                    assert int(f['free']) == len(free)
                    assert int(f['purchased']) == 0
                    expected = (len(live) if arm == 'blocked_20' else ref[key] if row['group'] == 'matched_reference'
                                else full[key] if row['group'] == 'full_target' else 4)
                    assert target == expected
                    assert len(ids) == min(len(free), target)
                    assert set(ids) <= free
                    offers += 1
                else:
                    assert target == ref[key] == len(ids)
                for i in ids:
                    assert i in amap
                    if arm != 'unlimited_20':
                        assert until.get(i, entry) <= entry
                        until[i] = exit_at
                    per_account[i] = per_account.get(i, 0)+1
                seen.add(key)
            assert all(int(a['trades_taken']) == per_account.get(int(a['account_id']), 0) for a in accounts)
            assert sum(counts.values()) == row['copies']
            assert wanted == row['requested_copies']
            assert wanted-row['copies'] == row['missed_requested_copies']
            assert signals == row['signals_executed']
            assert zero == row['signals_without_target']
            assert (counts == ref) == row['exact_reference_exposure']
            assert sum(counts[t] != ref[t] for t in ref) == row['signals_different_from_reference']
            if row['group'] == 'matched_reference' and row['missed_requested_copies'] == 0:
                assert counts == ref
                exact_pairs += 1
            if row['group'] == 'full_target' and row['missed_requested_copies'] == 0:
                assert counts == full
            total_copies += row['copies']
        trials = read_csv(folder/'capacity_trials.csv')
        for label, target in (('exact_reference_capacity', 'matched_reference'), ('full_target_capacity', 'full_target')):
            check = meta[label]
            tested = [t for t in trials if t['target'] == target]
            step = check['step']
            first = max(step, ((check['mechanical_lower_bound']+step-1)//step)*step)
            assert [int(t['initial_accounts']) for t in tested] == list(range(first, int(tested[-1]['initial_accounts'])+1, step))
            successes = [int(t['initial_accounts']) for t in tested if int(t['missed']) == 0]
            assert check['first_successful_tested_inventory'] == (successes[0] if successes else None)
            assert check['minimum_proven'] == (check['first_successful_tested_inventory'] == check['mechanical_lower_bound'])
    return {'cases': len(cases), 'arms': len(data['rows']), 'audited_copies': total_copies,
            'audited_entry_offers': offers, 'exact_reference_pairs': exact_pairs,
            'all_purchases_initial': True, 'no_replacements_or_rescue_purchases': True,
            'cash_reconciled': True, 'single_position_arms_no_overlap': True,
            'per_signal_targets_and_exposure_verified': True}


if __name__ == '__main__':
    root = PROJECT_ROOT/'results/legacy_25k/routing_fixed_inventory'
    result = audit(root)
    (root/'AUDIT.generated.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
