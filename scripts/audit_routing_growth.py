"""Audit funded growth budgets, one-position execution and dynamic copy targets."""
from datetime import datetime
import json

from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from audit_legacy_routing import read_csv


def cents(value):
    return round(float(value) * 100)


def audit(root):
    data = json.loads((root / 'study.json').read_text(encoding='utf-8'))
    profile = data['profile']
    for name, checksum in data['evidence_files'].items():
        assert sha256_file(root / name) == checksum, name
    cases = sorted({r['case'] for r in data['rows']})
    expected = len(profile['starts']) * len(profile['budgets']) * len(profile['retained_balances'])
    assert len(cases) == expected
    assert len(data['rows']) == expected * len(profile['arms'])
    audited_copies = 0
    routed_offers = 0
    for case in cases:
        folder = root / case
        case_data = json.loads((folder / 'case.json').read_text(encoding='utf-8'))
        rows = case_data['rows']
        assert rows == [r for r in data['rows'] if r['case'] == case]
        assert [r['arm'] for r in rows] == profile['arms']
        fee = cents(case_data['config']['product']['purchase_fee_usd'])
        common_contributions = None
        common_tape = None
        for row in rows:
            arm = row['arm']
            accounts = read_csv(folder / f'{arm}_accounts.csv')
            cash = read_csv(folder / f'{arm}_cash.csv')
            payouts = read_csv(folder / f'{arm}_payouts.csv')
            decisions = read_csv(folder / f'{arm}_decisions.csv')
            replacements = read_csv(folder / f'{arm}_replacement_events.csv')
            pools = read_csv(folder / f'{arm}_daily_pool.csv')
            assert len(accounts) == row['accounts']
            balance = 0
            contributions = []
            purchase_events = []
            for e in cash:
                balance += cents(e['amount_usd'])
                assert balance >= 0
                assert balance == cents(e['cash_after_usd'])
                assert e['kind'] in {'owner_contribution', 'account_purchase', 'payout_received'}
                if e['kind'] == 'owner_contribution':
                    contributions.append((e['at'], cents(e['amount_usd'])))
                if e['kind'] == 'account_purchase':
                    purchase_events.append((e['at'], -cents(e['amount_usd']) // fee))
                    assert cents(e['amount_usd']) % fee == 0
            assert contributions[0][1] == cents(row['initial_cash_usd'])
            assert all(v == cents(row['monthly_contribution_usd']) for _, v in contributions[1:])
            if common_contributions is None:
                common_contributions = contributions
            assert contributions == common_contributions
            assert balance == cents(row['ending_owner_cash_usd'])
            assert balance - sum(v for _, v in contributions) == cents(row['total_net_usd'])
            assert sum(cents(e['received_usd']) for e in payouts) - len(accounts) * fee == cents(row['total_net_usd'])
            assert sum(n for _, n in purchase_events) == len(accounts)
            assert purchase_events[0][1] == profile['initial_accounts']
            for at, n in purchase_events:
                moment = datetime.fromisoformat(at)
                assert moment.hour == moment.minute == moment.second == 0
                assert sum(a['activated_at'] == moment.isoformat(sep=' ') for a in accounts) == n
            assert int(decisions[0]['bought']) == profile['initial_accounts']
            assert int(pools[0]['live']) == profile['initial_accounts']
            assert max(int(p['live']) for p in pools) == row['peak_live'] <= profile['max_live_accounts']
            pending = observed = 0
            for e in replacements:
                at = datetime.fromisoformat(e['at'])
                deaths = sum(bool(a['died_at']) and datetime.fromisoformat(a['died_at']) <= at for a in accounts)
                pending += deaths - observed
                observed = deaths
                bought = int(e['replacements'])
                assert 0 <= bought <= pending
                pending -= bought
                assert pending == int(e['pending_replacements'])
                assert int(e['scheduled_bought']) in (0, 1)
                if int(e['scheduled_bought']):
                    assert at.day == 1
                assert e['consumed_current_month_slot'] == 'False'
            fills = read_csv(folder / f'{arm}_fills.csv')
            tape = {f['trade_key']: (f['entry_at'], f['exit_at']) for f in fills}
            assert len(tape) == len(fills) == row['signals_loaded']
            if common_tape is None:
                common_tape = tape
            assert tape == common_tape
            account_map = {int(a['account_id']): a for a in accounts}
            until, seen = {}, set()
            n_filled = n_wanted = n_signals = n_zero = 0
            trade_counts = {}
            # The reference records settlement-time acceptance. One-position
            # arms record entry-time allocation and can be audited causally.
            for f in fills:
                entry = datetime.fromisoformat(f['entry_at'])
                exit_at = datetime.fromisoformat(f['exit_at'])
                ids = [int(i) for i in f['accounts'].split(';') if i]
                assert len(ids) == len(set(ids))
                requested = int(f['requested'])
                n_filled += len(ids)
                n_wanted += requested
                n_signals += bool(ids)
                n_zero += requested == 0
                if arm != 'unlimited_reference':
                    live = set()
                    for i, a in account_map.items():
                        if datetime.fromisoformat(a['activated_at']) > entry:
                            continue
                        if a['died_at']:
                            death = datetime.fromisoformat(a['died_at'])
                            if death < entry:
                                continue
                            if death == entry:
                                d = tape.get(a['death_trade_key'])
                                if not d or datetime.fromisoformat(d[0]) != death or a['death_trade_key'] in seen:
                                    continue
                        live.add(i)
                    free = {i for i in live if until.get(i, entry) <= entry}
                    assert int(f['alive']) == len(live)
                    assert int(f['free']) == len(free)
                    assert int(f['purchased']) == 0, 'No entry-time rescue buys in a funded growth run'
                    target = len(live) if arm == 'blocked_copy' else len(live) // profile['capacity_per_copy']
                    assert requested == target
                    assert len(ids) == min(len(free), target)
                    assert set(ids) <= free
                    routed_offers += 1
                for i in ids:
                    assert datetime.fromisoformat(account_map[i]['activated_at']) <= entry
                    if arm != 'unlimited_reference':
                        assert until.get(i, entry) <= entry
                        until[i] = exit_at
                    trade_counts[i] = trade_counts.get(i, 0) + 1
                seen.add(f['trade_key'])
            assert n_filled == row['copies']
            assert n_wanted == row['requested_copies']
            assert n_signals == row['signals_executed']
            assert n_zero == row['signals_without_target']
            assert n_wanted - n_filled == row['missed_requested_copies']
            assert all(int(a['trades_taken']) == trade_counts.get(int(a['account_id']), 0) for a in accounts)
            audited_copies += n_filled
    return {'cases': len(cases), 'arms': len(data['rows']), 'audited_copies': audited_copies,
            'audited_entry_offers': routed_offers, 'matched_owner_contributions': True,
            'cash_never_negative': True, 'live_cap_enforced': True,
            'no_entry_time_purchases': True, 'dynamic_targets_verified': True,
            'single_position_arms_no_overlap': True}


if __name__ == '__main__':
    root = PROJECT_ROOT / 'results/legacy_25k/routing_funded_growth'
    result = audit(root)
    (root / 'AUDIT.generated.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
