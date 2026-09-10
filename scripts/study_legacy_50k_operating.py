"""Focused 50K operating search, matched 25K controls and interpretation sensitivity."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace,asdict
from datetime import datetime,timezone
from pathlib import Path
import sys,json,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import load_config,PROJECT_ROOT,to_payload
from pa_milky.study_config import load_study_profile,study_path,profile_provenance
from pa_milky.loader import load_tape
from pa_milky.simulator import run_book
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.policy import WithdrawalPolicy
from pa_milky.firm import Rulebook
from pa_milky.economics import Economics
from pa_milky.provenance import input_digest,engine_digest,sha256_file
from pa_milky.report import write_outputs
from pa_milky.study_reports import write_study_report
P=None;C=None;T=None


def initialize():
    global P,C,T
    P={k:load_study_profile(f'config/studies/{k}.json') for k in ('legacy_25k','legacy_50k')}
    C={k:load_config(study_path(p,'scenario')) for k,p in P.items()}
    T=load_tape(C['legacy_50k'])


def job(product,initial,monthly,acquisition,rule,cadence,headroom,strict=False):
    return (product,initial,monthly,acquisition,rule,cadence,headroom,strict)


def evaluate(j,detail=False):
    product,initial,monthly,acq,rule,cadence,headroom,strict=j
    base=C[product]
    pol=WithdrawalPolicy(name=f'{rule}_{cadence}_headroom_{headroom}',cadence=cadence,amount_rule=rule,
        quantize_to_amount=False,min_retained_balance_usd=base.trailing_floor_balance_usd+headroom,terminal_withdrawal='firm_permitted')
    cfg=replace(base,policy=pol)
    if strict:
        rules=dict(cfg.rulebook.rules);r=rules['minimum_balance']
        rules['minimum_balance']=replace(r,params={**r.params,'retain_after_payout_from':6})
        cfg=replace(cfg,rulebook=Rulebook(rules))
    acquisition=AcquisitionPolicy(acq,initial,monthly,max_live_accounts=P[product]['max_live_accounts'])
    result=run_book(T,cfg,acquisition=acquisition)
    e=Economics.measure(result);cash=result.acquisition.summary()
    assert e.residual_usd==cash['cash_identity_residual_usd']==0
    assert cash['net_cash_created_usd']==result.pocket_usd
    terminal=round(sum(x.received_usd for x in result.terminal_payouts),2)
    row={'product':product,'initial_cash':initial,'monthly_funding':monthly,'acquisition':acq,
         'withdrawal':rule,'cadence':cadence,'headroom':headroom,'reserve':pol.min_retained_balance_usd,
         'strict_post_payout_balance':strict,'fee':base.purchase_fee_usd,'accounts':len(result.accounts),
         'alive':result.alive_at_horizon,'ongoing':round(result.pocket_usd-terminal,2),
         'terminal':terminal,'total':result.pocket_usd,'contributions':cash['owner_contributions_usd'],
         'ending_owner_cash':cash['ending_owner_cash_usd'],'economics':e.to_payload(),'job':j}
    return (row,result) if detail else row


def batch(pool,jobs,label):
    rows=[]
    for i,r in enumerate(pool.map(evaluate,jobs),1):
        rows.append(r)
        if i%20==0 or i==len(jobs):print(f'{label}: {i}/{len(jobs)}',flush=True)
    return rows


def table(rows):
    t='| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |\n|---|---|---|---:|---:|---:|---:|---:|---:|\n'
    for r in rows:t+=f"| {r['product']} | {r['acquisition']} | {r['withdrawal']} / {r['cadence']} | ${r['reserve']:,.0f} | {r['accounts']} | {r['alive']} | ${r['ongoing']:,.2f} | ${r['terminal']:,.2f} | ${r['total']:,.2f} |\n"
    return t+'\n'


def main():
    initialize();p=P['legacy_50k'];out=study_path(p,'operating_policies');out.mkdir(parents=True,exist_ok=True)
    assert input_digest(C['legacy_25k'])==input_digest(C['legacy_50k'])
    # A read-only manifest makes preservation of all existing 25K result files verifiable.
    protected={str(f):sha256_file(f) for f in (PROJECT_ROOT/'results').rglob('*') if f.is_file() and 'legacy_50k' not in f.parts}
    spec=p['operating_search'];budgets=p['budgets']
    anchors=[('minimum','daily',6800),('maximum','weekly',6500),('minimum','calendar_month',4900)]
    controls=[job(prod,i,m,a,r,c,h) for prod in C for i,m in budgets for a in spec['acquisitions'] for r,c,h in anchors]
    coarse=[job('legacy_50k',i,m,'monthly_one',r,c,h) for i,m in budgets for r in spec['amount_rules'] for c in spec['cadences'] for h in spec['headrooms']]
    with ProcessPoolExecutor(max_workers=p['workers'],initializer=initialize) as pool:
        matched=batch(pool,controls,'Matched account-size controls')
        search=batch(pool,coarse,'50K reserve/cadence coarse search')
        seen={tuple(r['job']) for r in search};refine=[]
        for i,m in budgets:
            family=[r for r in search if (r['initial_cash'],r['monthly_funding'])==(i,m)]
            for score in ('ongoing','total'):
                best=max(family,key=lambda r:(r[score],r['ongoing']))
                for delta in range(-spec['refinement_radius'],spec['refinement_radius']+1,spec['refinement_step']):
                    h=best['headroom']+delta
                    if h<0:continue
                    j=job('legacy_50k',i,m,'monthly_one',best['withdrawal'],best['cadence'],h)
                    if j not in seen:refine.append(j);seen.add(j)
        search+=batch(pool,refine,'50K local refinement')
        operating_jobs=set()
        for i,m in budgets:
            family=[r for r in search if (r['initial_cash'],r['monthly_funding'])==(i,m)]
            selected=set(anchors)
            for score in ('ongoing','total'):
                best=max(family,key=lambda r:(r[score],r['ongoing']));selected.add((best['withdrawal'],best['cadence'],best['headroom']))
            for a in spec['acquisitions']:
                for r,c,h in selected:operating_jobs.add(job('legacy_50k',i,m,a,r,c,h))
        operating=batch(pool,sorted(operating_jobs),'50K purchase policies')
        sensitivity_jobs={tuple(r['job'][:-1])+ (True,) for r in matched+operating}
        sensitivity=batch(pool,sorted(sensitivity_jobs),'Later-payout minimum-balance sensitivity')
    # Verify legacy model controls against saved 25K evidence, allowing different display names.
    old=[]
    for label in ('purchases','replacements'):
        old+=json.loads((study_path(P['legacy_25k'],label)/'study.json').read_text())['rows']
    verified=0
    for r in matched:
        if r['product']!='legacy_25k':continue
        candidates=[x for x in old if x['initial_cash_usd']==r['initial_cash'] and x['monthly_contribution_usd']==r['monthly_funding'] and x['purchase_policy']==r['acquisition'] and x['withdrawal_config']['amount_rule']==r['withdrawal'] and x['withdrawal_config']['cadence']==r['cadence'] and x['withdrawal_config']['min_retained_balance_usd']==r['reserve']]
        assert candidates,(r,'missing control');x=candidates[0]
        assert (r['ongoing'],r['total'],r['accounts'],r['alive'])==(x['ongoing_net_cash_usd'],x['combined_net_cash_usd'],x['accounts_bought'],x['alive_before_terminal'])
        verified+=1
    payload={'schema':'pa_milky.account_product_comparison.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
      'profiles':{k:profile_provenance(v) for k,v in P.items()},'configs':{k:to_payload(v) for k,v in C.items()},
      'inputs':input_digest(C['legacy_50k']),'engine':engine_digest(),'runner_sha256':sha256_file(Path(__file__)),
      'verified_25k_controls':verified,'matched_controls':matched,'reserve_search':search,'operating_policies':operating,'strict_sensitivity':sensitivity}
    (out/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    for name,rows in [('matched_controls',matched),('reserve_search',search),('operating_policies',operating),('strict_sensitivity',sensitivity)]:
        with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
            fields=[k for k in rows[0] if k not in ('economics','job')];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report='# Legacy 50K operating policies and matched 25K comparison\n\n'
    report+='Same RR tape, contract exposure, owner budgets and 20-live-account cap. User-specified seat fees: 25K $200; 50K $250. This measures account specification, size-dependent payout parameters AND cost together. Legacy availability throughout the dataset is counterfactual. No evaluation phase is modelled.\n\n'
    report+=f'{verified} saved 25K controls reproduced exactly. Coarse plus local reserve search: {len(search)} settings; purchase shortlist: {len(operating)} settings. Local refinement is only around the coarse ongoing/total winners per budget, not an exhaustive joint search.\n\n'
    report+='Main tables retain the inherited 25K payout interpretation for comparability. They are model outputs, not a claim of complete Apex compliance. The separate sensitivity enforces the published minimum-balance wording after payout six for BOTH products. See [sources and model limits](../../../research/legacy_50k/SOURCES.md).\n\n'
    strict_lookup={tuple(r['job'][:-1]):r for r in sensitivity}
    for i,m in budgets:
        report+=f'## ${i:,} initial; ${m:,}/month\n\n'
        report+='### Matched daily minimum, equal $6,800 floor headroom\n\n'
        report+=table([r for r in matched if (r['initial_cash'],r['monthly_funding'],r['withdrawal'],r['cadence'],r['headroom'])==(i,m,'minimum','daily',6800)])
        report+='### Best tested 50K bundles by acquisition\n\n'
        winners=[]
        for a in spec['acquisitions']:
            f=[r for r in operating if (r['initial_cash'],r['monthly_funding'],r['acquisition'])==(i,m,a)]
            winners.append(max(f,key=lambda r:(r['total'],r['ongoing'])))
        report+=table(winners)
        report+='### Same selected bundles with later-payout retained minimum\n\n'+table([strict_lookup[tuple(r['job'][:-1])] for r in winners])
        for score in ('ongoing','total'):
            best=max([r for r in operating if (r['initial_cash'],r['monthly_funding'])==(i,m)],key=lambda r:(r[score],r['ongoing']))
            row,result=evaluate(tuple(best['job']),True);assert row==best
            folder=out/f'budget_{i}_{m}__best_{score}';write_outputs(result,folder)
            (folder/'experiment.json').write_text(json.dumps({'run_config':to_payload(result.config),'acquisition':asdict(result.acquisition.policy)},indent=2),encoding='utf-8')
            report+=f"{score.capitalize()} leader: {best['acquisition']} / {best['withdrawal']} {best['cadence']} / reserve ${best['reserve']:,.0f}: ${best[score]:,.2f}. [Detailed ledger]({folder.name}/report.txt).\n\n"
    report+='## Interpretation\n\nMatched tables hold dollar headroom above the frozen floor fixed, not headroom as a multiple of drawdown. With the same tape/exposure, a larger account does not double per-trade earnings: it changes survival, extraction gates and acquisition affordability. Fresh search winners compare adapted bundles, not the isolated effect of the account size. Purchase shortlist reserves were selected with monthly-one; other acquisitions were not independently exhaustively optimized.\n\n'
    report+='Both scored objectives use the same path, with one endpoint request releasing the voluntary reserve. Results can depend strongly on that receipt. The strict sensitivity can alter subsequent cohorts as well as terminal cash; it is not merely an arithmetic haircut. All profiles retain the cumulative first-$25,000 split interpretation and the inherited concurrency approximation. Historical 25K reports are unchanged.\n'
    write_study_report(out,report)
    assert all(Path(f).is_file() and sha256_file(Path(f))==h for f,h in protected.items()),'25K result changed'
    (out/'preservation_check.json').write_text(json.dumps({'protected_files':len(protected),'all_unchanged':True},indent=2),encoding='utf-8')
    print(f'Completed. {verified} controls verified; {len(protected)} prior result files unchanged. {out}',flush=True)


if __name__=='__main__':main()
