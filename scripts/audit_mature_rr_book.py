"""Reconstruct mature-book capacity/recovery from account lifetimes."""
from collections import Counter
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'results/legacy_25k/mature_rr_book'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    primary=json.loads((ROOT/'audit.json').read_text())
    contract=json.loads((ROOT/'contract.json').read_text())
    assert sha(ROOT/'contract.json')==primary['contract_sha256']
    for p,h in primary['files'].items():assert sha(ROOT/p)==h,p
    for p,h in contract['code'].items():assert sha(BASE/p)==h,p
    cases=0
    for p in sorted((ROOT/'cases').glob('*.json')):
        data=json.loads(p.read_text());r=data['row'];accounts=data['accounts']
        start=datetime.fromisoformat(r['start']);end=datetime.fromisoformat(r['end'])
        initial=data['initial_accounts'];weights=contract['arms'][r['portfolio']]
        assert len(initial)==20 and Counter(a['rr'] for a in initial)==Counter(weights)
        assert all(a['headroom']==r['headroom'] and a['floor']==100 and a['balance']==25100+r['headroom']
                   and a['payout_count']==a['prior_days']==0 for a in initial)
        intervals=[(datetime.fromisoformat(a['activated_at']),
                    datetime.fromisoformat(a['died_at']) if not a['alive'] else end,a) for a in accounts]
        boundaries=sorted({start,end,*[x for s,e,a in intervals for x in (s,e)]})
        spans=[]
        for a,b in zip(boundaries,boundaries[1:]):
            if start<=a<b<=end:
                n=sum(s<=a<e for s,e,_ in intervals)
                spans.append((a,b,n))
        assert all(0<=n<=20 for a,b,n in spans)
        assert min(n for a,b,n in spans)==r['min_live']
        for threshold,key in [(1,'empty_days'),(5,'days_below_5'),(10,'days_below_10'),(20,'days_below_20')]:
            days=sum((b-a).total_seconds()/86400 for a,b,n in spans if n<threshold)
            assert abs(days-r[key])<1e-7,(r['case'],key)
        # Merge consecutive deficient intervals; no runner/event-counter import.
        deficient=[]
        for a,b,n in spans:
            if n<20:
                if deficient and deficient[-1][1]==a:deficient[-1][1]=b
                else:deficient.append([a,b])
        assert bool(deficient)==r['had_loss']
        if deficient:
            a,b=deficient[0]
            recovered=b<end
            assert recovered==r['first_restored']
            key='first_recovery_days' if recovered else 'first_unrecovered_followup_days'
            assert abs((b-a).total_seconds()/86400-r[key])<1e-7
        original_survivors=sum(a['original'] and (a['alive'] or a['died_at']>=r['stress_end']) for a in accounts)
        assert original_survivors==r['original_survivors_quarter']
        for i,a in enumerate(accounts):
            live=Counter(b['rr'] for b in accounts[:i] if b['alive'] or b['died_at']>a['activated_at'])
            expected=min(weights,key=lambda rr:live[rr]/weights[rr])
            assert a['rr']==expected,(r['case'],a['account_id'])
        ledger=data['acquisition']
        if ledger:
            assert abs(ledger['ending_owner_cash_usd']-ledger['owner_contributions_usd']-
                       ledger['payouts_received_usd']+ledger['purchase_spend_usd'])<.001
            assert len(accounts)-20+ledger['spares_unused_at_end']==ledger['evaluations_activated']
        else:
            assert len(accounts)==20 and r['receipts']==r['replacement_costs']==0
        assert abs(r['receipts']-r['replacement_costs']-r['forward_net_cash'])<.001
        cases+=1
    assert cases==624
    out=dict(status='passed',lifetime_capacity_and_recovery_cases=cases,weighted_assignments_replayed=True,
             matched_endowments_and_cash_checked=True,primary_audit_sha256=sha(ROOT/'audit.json'),
             auditor_sha256=sha(Path(__file__)))
    (ROOT/'verification').mkdir(exist_ok=True)
    (ROOT/'verification/audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
