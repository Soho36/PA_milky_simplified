"""Independent exported-ledger audit for the blocked evaluation-supply study."""
from collections import Counter
from datetime import datetime
from itertools import product
import json

from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.provenance import sha256_file, engine_digest, input_digest
from audit_legacy_routing import read_csv
from report_names import engine_accepted, verified


def cents(value):
    return round(float(value)*100)


def audit(root):
    data=json.loads((root/'study.json').read_text())
    contract=json.loads((root/'contract.json').read_text())
    assert sha256_file(root/'contract.json')==data['contract_sha256']
    assert verified(PROJECT_ROOT/'scripts/study_blocked_pipeline.py',contract['runner_sha256'])
    for path,digest in contract['protected'].items():
        assert verified(PROJECT_ROOT/path,digest),path
    for name,digest in contract['helpers'].items():
        assert verified(PROJECT_ROOT/'scripts'/name,digest),name
    spec=data['spec']; assert spec==contract['spec']
    config=load_config(PROJECT_ROOT/spec['scenario'])
    assert to_payload(config)==contract['config']
    assert engine_accepted(contract['engine'],engine_digest()),'unrecorded engine change; see results/ENGINE_CHANGES.json'
    assert input_digest(config)==contract['inputs']
    checkpoint={tuple(r['job']):r for r in map(json.loads,(root/'checkpoint.jsonl').read_text().splitlines())}
    assert len(checkpoint)==data['unique_simulations']
    pipes=list(product(spec['persistent_demand'],spec['start_intervals_days'],spec['concurrency'],spec['spares'],(True,False)))
    expected={('blocked',2020,*spec['budget'],*pol,*pipe) for pol,pipe in product(spec['anchors'].values(),pipes)}
    assert {tuple(r['job']) for r in data['screen']}==expected
    assert {tuple(r['job']) for r in data['unrestricted_screen']}=={('unrestricted',*j[1:]) for j in expected}
    def select(rows, score):
        return min(rows,key=lambda r:(-r[score],-r['total' if score=='ongoing' else 'ongoing'],
                                      r['spend'],r['headroom'],tuple(r['job'])))
    def pipe(r):
        return (r['persistent'],r['interval'],r['concurrency'],r['spares'],r['reserve_seats'])
    nominated={(False,0,5,5,True)}
    for seats,n,score in product((True,False),spec['concurrency'],('ongoing','total')):
        nominated.add(pipe(select([r for r in data['screen'] if r['reserve_seats']==seats and r['concurrency']==n],score)))
    assert set(map(tuple,data['selected_pipelines']))==nominated
    coarse={('blocked',2020,*spec['budget'],rule,cad,h,amount,*pipe)
            for pipe,(rule,amount),cad,h in product(data['selected_pipelines'],spec['amounts'],spec['cadences'],spec['headrooms'])}
    assert set(map(tuple,data['coarse_jobs']))==coarse
    refined=set()
    for p,(rule,amount),cad,score in product(nominated,spec['amounts'],spec['cadences'],('ongoing','total')):
        w=select([checkpoint[j] for j in coarse if j[4]==rule and j[5]==cad and j[7]==amount and j[8:]==p],score)
        for delta in range(-spec['refinement_radius'],spec['refinement_radius']+1,spec['refinement_step']):
            h=w['headroom']+delta
            if 0<=h<=max(spec['headrooms']):
                refined.add(('blocked',2020,*spec['budget'],rule,cad,h,amount,*p))
    assert set(map(tuple,data['refined_jobs']))==refined
    assert {tuple(r['job']) for r in data['search']}==expected|coarse|set(map(tuple,data['refined_jobs']))
    for name in ('screen','unrestricted_screen','search','winners','paired','transfers'):
        for row in data[name]:
            assert checkpoint[tuple(row['job'])]=={k:v for k,v in row.items() if k!='label'}
    for r in checkpoint.values():
        assert r['accounts']==r['deaths']+r['alive']
        assert r['activated']==r['accounts']+r['spares_at_end']
        assert cents(r['spend'])==cents(r['evaluation_fees'])+cents(r['activation_fees'])
        assert cents(r['total'])==cents(r['receipts'])-cents(r['spend'])
        assert cents(r['total'])==cents(r['ending_cash'])-cents(r['contributions'])
        assert cents(r['total'])==cents(r['ongoing'])+cents(r['terminal'])
        assert r['economics']['residual_usd']==0
        assert r['deaths']==r['replacements_filled']+r['replacements_unfilled']
    for winner in data['winners']:
        score=winner['label'].split(' / ')[1]
        assert winner[score]==max(r[score] for r in data['search'] if r['reserve_seats']==winner['reserve_seats'])
    selected={tuple(w['job']) for w in data['winners'] if w['reserve_seats']}
    transfers={(j[0],year,*j[2:]) for j in selected for year in spec['transfer_starts']}
    transfers|={(j[0],j[1],initial,monthly,*j[4:]) for j in selected for initial,monthly in spec['transfer_budgets']}
    assert {tuple(r['job']) for r in data['transfers']}==transfers
    spec_eval=contract['evaluation_spec']['evaluations']['legacy_25k']
    copies=0
    for label in data['details']:
        folder=root/label
        detail=json.loads((folder/'summary.json').read_text())
        r=detail['row']; assert r==checkpoint[tuple(r['job'])]
        accounts=read_csv(folder/'accounts.csv')
        fills=read_csv(folder/'blocked_fills.csv')
        payouts=read_csv(folder/'payouts.csv')
        cash=read_csv(folder/'cash.csv')
        pipeline=read_csv(folder/'pipeline_daily.csv')
        evaluations=read_csv(folder/'evaluations.csv')
        waits=read_csv(folder/'replacement_waits.csv')
        amap={int(a['account_id']):a for a in accounts}
        assert len(amap)==r['accounts']
        balance=contributed=received=evalfees=activationfees=0
        activations=Counter()
        contributions=[]
        for e in cash:
            amount=cents(e['amount_usd']); balance+=amount
            assert balance==cents(e['cash_after_usd'])>=0
            if e['kind']=='owner_contribution': contributed+=amount; contributions.append(e)
            elif e['kind']=='payout_received': received+=amount
            elif e['kind']=='evaluation_fee':
                assert -amount==cents(spec_eval['monthly_fee_usd']); evalfees-=amount
            elif e['kind']=='activation_fee':
                assert -amount==cents(spec_eval['activation_fee_usd']); activationfees-=amount
                activations[datetime.fromisoformat(e['at'])]+=1
            else: raise AssertionError(e['kind'])
        assert balance-contributed==cents(r['total'])
        assert contributed==cents(r['contributions'])
        assert cents(contributions[0]['amount_usd'])==cents(r['initial_cash'])
        assert all(cents(e['amount_usd'])==cents(r['monthly_funding']) for e in contributions[1:])
        assert received==sum(cents(e['received_usd']) for e in payouts)==cents(r['receipts'])
        assert evalfees==cents(r['evaluation_fees'])==sum(int(e['months_paid']) for e in evaluations)*cents(spec_eval['monthly_fee_usd'])
        assert activationfees==cents(r['activation_fees'])==r['activated']*cents(spec_eval['activation_fee_usd'])
        assert len(evaluations)==r['evaluations']
        funded=[e for e in evaluations if e['state']=='funded']
        assert len(funded)==r['activated']
        assert Counter(datetime.fromisoformat(e['ended_at']) for e in funded)==activations
        assert all(datetime.fromisoformat(e['started_at'])<=datetime.fromisoformat(e['passed_at'])<=datetime.fromisoformat(e['ended_at']) for e in funded)
        # Every deployed PA has a previously paid activation; no seeded or borrowed inventory.
        deployed=Counter(datetime.fromisoformat(a['activated_at']) for a in accounts)
        available=0
        for at in sorted(set(activations)|set(deployed)):
            available+=activations[at]-deployed[at]
            assert available>=0
        assert available==r['spares_at_end']
        assert all(int(d['alive'])+int(d['spares'])+(int(d['in_flight']) if r['reserve_seats'] else 0)<=20
                   and int(d['subscriptions'])<=r['concurrency'] for d in pipeline)
        starts=sorted(datetime.fromisoformat(e['started_at']) for e in evaluations)
        if r['interval']:
            assert all((b-a).days>=r['interval'] for a,b in zip(starts,starts[1:]))
        tape={f['trade_key']:(f['entry_at'],f['exit_at']) for f in fills}
        assert len(tape)==len(fills)==r['signals_loaded']
        until={}; seen=set(); per_account=Counter()
        signals=zero=allocated=0
        for f in fills:
            at,end=map(datetime.fromisoformat,(f['entry_at'],f['exit_at']))
            ids={int(i) for i in f['accounts'].split(';') if i}
            live=set()
            for i,a in amap.items():
                if datetime.fromisoformat(a['activated_at'])>at: continue
                if a['died_at']:
                    death=datetime.fromisoformat(a['died_at'])
                    if death<at: continue
                    if death==at:
                        dt=tape[a['death_trade_key']]
                        if datetime.fromisoformat(dt[0])!=death or a['death_trade_key'] in seen: continue
                live.add(i)
            free={i for i in live if until.get(i,at)<=at}
            assert ids==free, 'All and only free live accounts must copy'
            assert int(f['alive'])==int(f['requested'])==len(live)
            assert int(f['free'])==len(free) and int(f['purchased'])==0
            for i in ids: until[i]=end; per_account[i]+=1
            seen.add(f['trade_key']); signals+=bool(ids); zero+=not live; allocated+=len(ids)
        assert signals==r['signals_executed'] and zero==r['zero_live_signals']
        assert allocated==r['copies']
        assert all(int(a['trades_taken'])==per_account[int(a['account_id'])] for a in accounts)
        assert len(waits)==r['deaths']
        assert round(sum(float(w['wait_days']) for w in waits),2)==r['unfilled_account_days']
        copies+=allocated
    return dict(unique_simulations=len(checkpoint), blocked_screen=len(expected), paired_unrestricted_screen=len(expected),
        coarse_settings=len(coarse), selected_pipelines=len(data['selected_pipelines']),
        detailed_ledgers=len(data['details']), audited_trade_copies=copies,
        no_seeded_inventory=True, fees_cash_and_capacity_reconciled=True,
        all_free_accounts_copy_without_overlap=True, prior_results_preserved=True,
        winners_maximize_tested_objectives=True)


if __name__=='__main__':
    root=PROJECT_ROOT/'results/legacy_25k/blocked_pipeline'
    result=audit(root)
    (root/'AUDIT.generated.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
