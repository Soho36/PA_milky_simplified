"""Audit hybrid reservations using recorded intervals, inventory and cash."""
from collections import Counter
from datetime import datetime
import json

from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from audit_legacy_routing import read_csv


def cents(value):
    return round(float(value)*100)


def audit(root):
    data = json.loads((root/'study.json').read_text(encoding='utf-8'))
    profile = data['profile']
    for name, checksum in data['evidence_files'].items():
        assert sha256_file(root/name) == checksum, name
    for name, checksum in data['preserved_control_files'].items():
        assert sha256_file(PROJECT_ROOT/profile['control_output']/name) == checksum, name
    cases = sorted({r['case'] for r in data['rows']})
    assert len(cases) == len(profile['starts'])*len(profile['retained_balances'])
    assert len(data['rows']) == len(cases)*(4+len(profile['minimum_copies'])*len(profile['maximum_copies']))
    copies = offers = hybrid_offers = controls = 0
    for case in cases:
        folder = root/case
        meta = json.loads((folder/'case.json').read_text(encoding='utf-8'))
        assert meta['rows'] == [r for r in data['rows'] if r['case'] == case]
        fee = cents(meta['config']['product']['purchase_fee_usd'])
        common_tape = None
        for row in meta['rows']:
            arm = row['arm']
            accounts = read_csv(folder/f'{arm}_accounts.csv')
            fills = read_csv(folder/f'{arm}_fills.csv')
            payouts = read_csv(folder/f'{arm}_payouts.csv')
            amap = {int(a['account_id']): a for a in accounts}
            assert len(accounts) == len(amap) == row['accounts'] == profile['initial_accounts']
            assert set(amap) == set(range(1, 21))
            assert len({a['activated_at'] for a in accounts}) == 1
            assert datetime.fromisoformat(accounts[0]['activated_at']) <= min(datetime.fromisoformat(f['entry_at']) for f in fills)
            assert cents(row['purchase_cost_usd']) == len(accounts)*fee
            assert sum(cents(p['received_usd']) for p in payouts)-len(accounts)*fee == cents(row['total_net_usd'])
            assert cents(row['ongoing_net_usd'])+cents(row['terminal_received_usd']) == cents(row['total_net_usd'])
            assert sum(bool(a['died_at']) for a in accounts) == row['deaths']
            assert row['alive']+row['deaths'] == len(accounts)
            tape = {f['trade_key']: (f['entry_at'], f['exit_at']) for f in fills}
            assert len(tape) == len(fills) == row['signals_loaded']
            if common_tape is None:
                common_tape = tape
            assert tape == common_tape
            until, seen, active, trades_taken, histogram = {}, set(), {}, Counter(), Counter()
            wanted = below = shortfalls = protection_offers = 0
            hybrid = arm.startswith('hybrid_')
            policy = row['policy']
            for f in fills:
                key = f['trade_key']
                entry, exit_at = map(datetime.fromisoformat, tape[key])
                ids = [int(i) for i in f['accounts'].split(';') if i]
                assert len(set(ids)) == len(ids)
                target = int(f['requested'])
                wanted += target
                histogram[len(ids)] += 1
                if arm != 'unlimited_20':
                    active = {k:v for k,v in active.items() if v > entry}
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
                    if hybrid:
                        m, cap = policy['minimum_copies'], policy['maximum_copies']
                        reserve = m*max(0, profile['concurrency_limit']-len(active)-1)
                        expected = min(cap, max(m, len(free)-reserve))
                        assert int(f['active_setups_before']) == len(active)
                        assert int(f['reserved_accounts']) == reserve
                        shortage = max(0, m-len(ids))
                        protection = max(0, m+reserve-len(free))
                        assert int(f['minimum_copy_shortfall']) == shortage
                        assert int(f['protection_shortfall']) == protection
                        shortfalls += shortage
                        below += shortage > 0
                        protection_offers += protection > 0
                        if len(free) >= m+reserve:
                            assert len(free)-len(ids) >= reserve
                        hybrid_offers += 1
                    else:
                        expected = len(live) if arm == 'blocked_20' else 4
                    assert target == expected
                    assert len(ids) == min(target, len(free))
                    assert set(ids) <= free
                    if ids:
                        active[key] = exit_at
                    offers += 1
                for i in ids:
                    assert i in amap
                    if arm != 'unlimited_20':
                        assert until.get(i, entry) <= entry
                        until[i] = exit_at
                    trades_taken[i] += 1
                seen.add(key)
            assert sum(trades_taken.values()) == row['copies']
            assert all(int(a['trades_taken']) == trades_taken[int(a['account_id'])] for a in accounts)
            assert {str(k):v for k,v in histogram.items()} == row['copies_per_signal_histogram']
            assert histogram[0] == row['signals_missed']
            assert len(tape)-histogram[0] == row['signals_executed']
            assert wanted == row['requested_copies']
            if hybrid:
                assert below == row['below_minimum_signals']
                assert shortfalls == row['minimum_copy_shortfall'] == row['routing']['minimum_copy_shortfall']
                assert protection_offers == row['routing']['reservation_shortfall_offers']
            else:
                old_folder = PROJECT_ROOT/profile['control_output']/case
                old_meta = json.loads((old_folder/'case.json').read_text(encoding='utf-8'))
                old = next(r for r in old_meta['rows'] if r['arm'] == arm)
                for field in ('copies', 'deaths', 'alive', 'economics', 'ongoing_net_usd', 'terminal_received_usd', 'total_net_usd'):
                    assert row[field] == old[field]
                old_fills = read_csv(old_folder/f'{arm}_fills.csv')
                assert [(f['trade_key'], f['accounts']) for f in fills] == [(f['trade_key'], f['accounts']) for f in old_fills]
                controls += 1
            copies += row['copies']
    return {'cases': len(cases), 'arms': len(data['rows']), 'controls_reproduced': controls,
            'audited_copies': copies, 'audited_entry_offers': offers, 'audited_hybrid_offers': hybrid_offers,
            'reservation_and_minimum_rules_verified': True, 'no_overlapping_account_trades': True,
            'all_purchases_initial': True, 'cash_reconciled': True, 'prior_artifacts_preserved': True}


if __name__ == '__main__':
    root = PROJECT_ROOT/'results/legacy_25k/routing_hybrid'
    result = audit(root)
    (root/'AUDIT.generated.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
