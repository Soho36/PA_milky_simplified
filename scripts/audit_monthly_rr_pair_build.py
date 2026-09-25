"""Independently reconstruct copies, purchase eligibility and empty intervals."""
from collections import Counter,defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

import study_monthly_rr_pair_build as study
from pa_milky.provenance import engine_digest,input_digest,sha256_file
from dataclasses import replace
from rr_curve_support import select_trades


def read(name):
    with (study.OUT/name).open(newline='',encoding='utf-8') as f:
        return list(study.csv.DictReader(f))


def main():
    study.boot();saved=json.loads((study.OUT/'study.json').read_text(encoding='utf-8'))
    assert saved['engine']==engine_digest()
    for name,digest in saved['scripts'].items():assert sha256_file(study.ROOT/'scripts'/name)==digest
    for rr,source in saved['inputs'].items():assert input_digest(replace(study.BASE,risk_reward=rr))==source['digest']
    grouped={}
    for name in ('accounts','payouts','purchases','empty_episodes'):
        g=defaultdict(list)
        for r in read(name+'.csv'):g[r['case']].append(r)
        grouped[name]=g
    cases=read('cases.csv');checks=Counter()
    selection_cache={}
    for r in cases:
        case=r['case'];accounts=grouped['accounts'][case];start=datetime.fromisoformat(r['start'])
        for a in accounts:
            aid=int(a['account_id']);rr=a['rr'];born=datetime.fromisoformat(a['activated_at'])
            assert rr==study.RR[(aid-1)%2]
            key=(rr,born)
            if key not in selection_cache:
                selection_cache[key]=[t.trade_key for t in select_trades(study.TAPES[rr],born,study.END)]
            keys=selection_cache[key]
            if a['died_at']:
                keys=keys[:keys.index(a['death_trade_key'])+1]
            assert len(keys)==int(a['trades'])
            assert hashlib.sha256(json.dumps(keys).encode()).hexdigest()==a['trade_keys_sha256']
            checks['independent_account_entry_paths']+=1
            checks['accepted_copies']+=len(keys)
        by_birth=Counter(a['activated_at'] for a in accounts)
        for d in grouped['purchases'][case]:
            at=d['at']
            before=sum(a['activated_at']<at and (not a['died_at'] or a['died_at']>at) for a in accounts)
            assert int(d['alive_before'])==before
            assert int(d['bought'])==by_birth[at]==int(before<20)
            checks['purchase_boundaries']+=1
        # Independent interval test: evaluate active intervals at every change point.
        points=sorted({start,study.END}|{datetime.fromisoformat(a[k]) for a in accounts for k in ('activated_at','died_at') if a[k]})
        empty=[];span=None
        for at,nxt in zip(points,points[1:]):
            live=sum(datetime.fromisoformat(a['activated_at'])<=at and
                     (not a['died_at'] or datetime.fromisoformat(a['died_at'])>at) for a in accounts)
            assert 0<=live<=20
            if live==0 and span is None:span=at
            if live>0 and span is not None:empty.append((span,at));span=None
        if span is not None:empty.append((span,study.END))
        saved_gaps=grouped['empty_episodes'][case]
        assert [(a.isoformat(),b.isoformat()) for a,b in empty]==[(e['start'],e['end']) for e in saved_gaps]
        assert len(empty)==int(r['empty_episodes'])
        assert abs(sum((b-a).total_seconds()/86400 for a,b in empty)-float(r['empty_days']))<1e-5
        assert int(r['deaths'])==sum(bool(a['died_at']) for a in accounts)
        payouts=grouped['payouts'][case]
        assert study.money(sum(float(p['received']) for p in payouts))==float(r['received'])
        assert study.money(float(r['received'])-len(accounts)*200)==float(r['net_cash'])
        assert all(float(p['balance_after'])>=31900 for p in payouts)
        if r['policy']=='minimum':assert all(float(p['gross'])==500 for p in payouts)
        checks['independent_case_ledgers_and_empty_timelines']+=1
    for c in read('checkpoints.csv'):
        accounts=grouped['accounts'][c['case']];end=study.add_months(datetime.fromisoformat(c['start']),int(c['months'])).isoformat()
        born=[a for a in accounts if a['activated_at']<end]
        assert len(born)==int(c['purchased'])
        assert sum(bool(a['died_at']) and a['died_at']<end for a in born)==int(c['deaths'])
        receipt=study.money(sum(float(p['received']) for p in grouped['payouts'][c['case']] if p['at']<end))
        assert receipt==float(c['received'])
        assert study.money(receipt-len(born)*200)==float(c['net_cash'])
        checks['checkpoint_ledgers']+=1
    for start,rule in ((datetime(2020,1,1),'minimum'),(datetime(2021,1,1),'maximum'),(datetime(2025,12,1),'maximum')):
        actual=study.evaluate((start,rule))['summary']
        expected=next(r for r in saved['cases'] if r['case']==actual['case'])
        assert actual==expected
        checks['reproduced_cases']+=1
    output=dict(status='passed',checks=dict(checks),auditor_sha256=sha256_file(Path(__file__)),
                study_sha256=sha256_file(study.OUT/'study.json'))
    (study.OUT/'audit.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
