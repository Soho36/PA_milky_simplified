"""Audit search completeness, winner selection and selected blocked-copy ledgers."""
from collections import Counter, defaultdict
from datetime import datetime
from itertools import product
import json

from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from audit_legacy_routing import read_csv


def cents(value):
    return round(float(value)*100)


def audit(root):
    data = json.loads((root/'study.json').read_text(encoding='utf-8'))
    contract_path = root/'contract.json'
    assert sha256_file(contract_path) == data['contract_sha256']
    contract = json.loads(contract_path.read_text(encoding='utf-8'))
    assert sha256_file(PROJECT_ROOT/'scripts/optimize_blocked_copying.py') == contract['runner_sha256']
    spec = data['spec']
    assert spec == contract['spec']
    for name,digest in contract['protected_controls'].items():
        assert sha256_file(PROJECT_ROOT/spec['control_output']/name) == digest
    for name,digest in data['evidence_files'].items():
        assert sha256_file(root/name) == digest
    initial, monthly = spec['budget']
    expected = {(2020,initial,monthly,a['id'],seed,rule,cadence,h,0)
                for a,seed,rule,cadence,h in product(spec['acquisitions'],spec['initial_accounts'],
                    spec['amount_rules'],spec['cadences'],spec['coarse_headrooms'])}
    assert set(map(tuple,data['coarse_jobs'])) == expected
    rows = {tuple(r['job']):r for r in data['rows']}
    assert len(rows) == len(data['rows'])
    assert set(rows) == expected|set(map(tuple,data['refined_jobs']))|set(map(tuple,data['fixed_jobs']))
    assert all(j[:3] == (2020,initial,monthly) for j in rows)
    checkpoint = {tuple(r['job']):r for r in map(json.loads,(root/'checkpoint.jsonl').read_text().splitlines())}
    for r in data['rows']+data['controls']+data['transfers']:
        assert checkpoint[tuple(r['job'])] == r
        assert r['peak_live'] <= spec['max_live_accounts']
        assert r['minimum_owner_cash'] >= 0
        assert r['deaths']+r['alive'] == r['accounts']
        assert cents(r['total']) == cents(r['receipts'])-cents(r['spend'])
        assert cents(r['total']) == cents(r['ending_owner_cash'])-cents(r['contributions'])
        assert cents(r['ongoing'])+cents(r['terminal']) == cents(r['total'])
        assert r['economics']['residual_usd'] == 0
    for score,w in zip(data['winner_objectives'],data['winners']):
        assert w == rows[tuple(w['job'])]
        assert w[score] == max(r[score] for r in rows.values())
    selected = {tuple(r['job']) for r in data['winners']}
    transfers = {(year,*j[1:]) for j in selected for year in spec['transfer_starts']}
    transfers |= {(j[0],i,m,*j[3:]) for j in selected for i,m in spec['transfer_budgets']}
    assert {tuple(r['job']) for r in data['transfers']} == transfers
    old = json.loads((PROJECT_ROOT/spec['control_output']/'study.json').read_text(encoding='utf-8'))
    old_rows = [r for r in old['rows'] if r['arm'] == 'blocked_copy']
    assert len(old_rows) == len(data['controls']) == 16
    for old_r in old_rows:
        j = (old_r['start_year'],old_r['initial_cash_usd'],old_r['monthly_contribution_usd'],
             'monthly_plus_replacements',5,'minimum','daily',old_r['retained_balance_usd']-25100,0)
        new = checkpoint[j]
        assert new['allocation_sha256'] == old_r['routing']['allocation_sha256']
        assert new['total'] == old_r['total_net_usd'] and new['ongoing'] == old_r['ongoing_net_usd']
    audited_copies = 0
    for label in data['details']:
        folder = root/label
        detail = json.loads((folder/'summary.json').read_text(encoding='utf-8'))
        r = detail['row']
        assert tuple(r['job']) in selected
        assert r == rows[tuple(r['job'])]
        accounts = read_csv(folder/'accounts.csv')
        fills = read_csv(folder/'blocked_fills.csv')
        payouts = read_csv(folder/'payouts.csv')
        cash = read_csv(folder/'cash.csv')
        decisions = read_csv(folder/'decisions.csv')
        amap = {int(a['account_id']):a for a in accounts}
        assert len(accounts) == r['accounts'] == len(amap)
        fee = cents(detail['config']['product']['purchase_fee_usd'])
        balance = contributed = spent = received = 0
        purchases = Counter()
        contributions = []
        for e in cash:
            balance += cents(e['amount_usd'])
            assert balance == cents(e['cash_after_usd']) >= 0
            if e['kind'] == 'owner_contribution':
                contributed += cents(e['amount_usd']); contributions.append(e)
            elif e['kind'] == 'account_purchase':
                spent -= cents(e['amount_usd'])
                n = -cents(e['amount_usd'])//fee
                assert -cents(e['amount_usd']) == n*fee
                purchases[datetime.fromisoformat(e['at'])] += n
            elif e['kind'] == 'payout_received':
                received += cents(e['amount_usd'])
            else:
                raise AssertionError(e['kind'])
        assert cents(contributions[0]['amount_usd']) == cents(initial)
        assert all(cents(e['amount_usd']) == cents(monthly) for e in contributions[1:])
        first = min(datetime.fromisoformat(f['entry_at']) for f in fills)
        last = max(datetime.fromisoformat(f['exit_at']) for f in fills)
        expected_dates = []
        year, month = first.year, first.month
        while (year, month) <= (last.year, last.month):
            expected_dates.append(datetime(year, month, 1))
            year, month = (year+1, 1) if month == 12 else (year, month+1)
        assert [datetime.fromisoformat(e['at']) for e in contributions] == expected_dates
        assert spent == len(accounts)*fee == cents(r['spend'])
        assert received == sum(cents(e['received_usd']) for e in payouts) == cents(r['receipts'])
        assert contributed == cents(r['contributions'])
        assert balance-contributed == cents(r['total'])
        assert purchases == Counter(datetime.fromisoformat(a['activated_at']) for a in accounts)
        assert int(decisions[0]['bought']) == r['initial_accounts']
        for at in purchases:
            assert at.hour == at.minute == at.second == 0
            live = sum(datetime.fromisoformat(a['activated_at']) <= at and
                       (not a['died_at'] or datetime.fromisoformat(a['died_at']) > at) for a in accounts)
            assert live <= spec['max_live_accounts']
        tape = {f['trade_key']:(f['entry_at'],f['exit_at']) for f in fills}
        assert len(tape) == len(fills) == r['signals_loaded']
        until, seen, per_account = {}, set(), Counter()
        n_signals = n_zero = n_copies = 0
        for f in fills:
            at, end = map(datetime.fromisoformat,(f['entry_at'],f['exit_at']))
            ids = {int(i) for i in f['accounts'].split(';') if i}
            live = set()
            for i,a in amap.items():
                if datetime.fromisoformat(a['activated_at']) > at:
                    continue
                if a['died_at']:
                    death = datetime.fromisoformat(a['died_at'])
                    if death < at:
                        continue
                    if death == at:
                        dt = tape[a['death_trade_key']]
                        if datetime.fromisoformat(dt[0]) != death or a['death_trade_key'] in seen:
                            continue
                live.add(i)
            free = {i for i in live if until.get(i,at) <= at}
            assert ids == free, 'Every free live account must copy; occupied accounts must skip'
            assert int(f['alive']) == int(f['requested']) == len(live)
            assert int(f['free']) == len(free) and int(f['purchased']) == 0
            for i in ids:
                until[i] = end; per_account[i] += 1
            seen.add(f['trade_key'])
            n_signals += bool(ids); n_zero += not live; n_copies += len(ids)
        assert n_signals == r['signals_executed'] and n_zero == r['zero_live_signals']
        assert n_copies == r['copies']
        assert all(int(a['trades_taken']) == per_account[int(a['account_id'])] for a in accounts)
        audited_copies += n_copies
    return {'coarse_combinations':len(expected),'search_settings':len(rows),
            'controls_reproduced':16,'frozen_transfers':len(transfers),
            'detailed_winners':len(data['details']),'audited_winner_copies':audited_copies,
            'coarse_grid_complete':True,'both_winners_maximize_tested_score':True,
            'cash_and_cap_reconciled':True,'all_free_accounts_copy_no_overlap':True,
            'prior_results_preserved':True,
            'global_optimum_claim':'Only exhaustive over declared coarse grid; broader continuous/dynamic optimum not proven'}


if __name__ == '__main__':
    root = PROJECT_ROOT/'results/legacy_25k/blocked_optimization'
    result = audit(root)
    (root/'AUDIT.generated.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
