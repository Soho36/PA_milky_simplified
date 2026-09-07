"""Budget-matched, capped cadence comparisons and purchase-study controls."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import csv, json, sys
import study_account_purchases as purchases
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.policy_study import policies
from pa_milky.provenance import input_digest, engine_digest, sha256_file
from pa_milky.config import to_payload
from pa_milky.study_reports import write_study_report

OUT=Path('results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets')
SOURCE=Path('results/study__full_rulebook__RR__account_purchases__cash_budgets/study.json')
BUDGETS=[(1000,0),(1000,200),(5000,0),(5000,200)]


def key(row):
    p=dict(row['withdrawal_config']);p.pop('name',None)
    return (row['initial_cash_usd'],row['monthly_contribution_usd'],tuple(sorted(p.items())))


def table(rows):
    lines=['| Policy | Checks | Retain | Accounts | Alive | Ongoing net cash | Terminal receipt | Total net cash |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        p=r['withdrawal_config']
        lines.append(f"| {r['withdrawal_policy']} | {p['cadence']} | ${p['min_retained_balance_usd']:,.0f} | {r['accounts_bought']} | {r['alive_before_terminal']} | ${r['ongoing_net_cash_usd']:,.2f} | ${r['terminal_received_usd']:,.2f} | ${r['combined_net_cash_usd']:,.2f} |")
    return '\n'.join(lines)+'\n\n'


def main():
    purchases.initialize()
    source=json.loads(SOURCE.read_text())
    assert source['config']==to_payload(purchases.C)
    assert source['inputs']==input_digest(purchases.C)
    chosen=[p for p in policies() if p.name in ('fixed_750_backlog','fixed_1000_backlog','fixed_1500_backlog','minimum_monthly','maximum_excess_monthly')]
    jobs=[]
    for initial,monthly in BUDGETS:
        a=AcquisitionPolicy('monthly_one',initial,monthly,max_live_accounts=20)
        for p in chosen:
            for c in ('calendar_month','weekly','daily'):
                levels=list(range(31600,32101,100))+([30000] if p.amount_rule=='minimum' else [])
                for level in levels:
                    jobs.append(('monthly_one',a,replace(p,cadence=c,min_retained_balance_usd=level,terminal_withdrawal='firm_permitted')))
    rows=[]
    cached=None
    if '--refresh-purchase-tables' in sys.argv:
        # This is a presentation refresh, not a new simulation. Keep original provenance.
        cached=json.loads((OUT/'study.json').read_text())
        assert cached['config']==to_payload(purchases.C)
        assert cached['inputs']==input_digest(purchases.C)
        rows=cached['rows']
        assert len(rows)==len(jobs)
    else:
        with ProcessPoolExecutor(max_workers=4,initializer=purchases.initialize) as pool:
            for i,r in enumerate(pool.map(purchases.evaluate,jobs),1):
                rows.append(r)
                if i%20==0: print(f'Completed {i}/{len(jobs)}',flush=True)
    lookup={key(r):r for r in rows}
    checks=[]
    for old in source['rows']:
        if old['purchase_policy']!='monthly_one':continue
        new=lookup[key(old)]
        compared=[k for k in old if k not in ('withdrawal_policy','withdrawal_config')]
        differences=[k for k in compared if old[k]!=new[k]]
        checks.append({'budget':[old['initial_cash_usd'],old['monthly_contribution_usd']], 'withdrawal_policy':old['withdrawal_policy'],'fields_compared':compared,'differences':differences})
        assert not differences, (key(old),differences)
    assert len(checks)==12
    for r in rows:
        p=r['withdrawal_config']; q=dict(p);q['cadence']='calendar_month';q.pop('name')
        control=lookup[(r['initial_cash_usd'],r['monthly_contribution_usd'],tuple(sorted(q.items())))]
        for score in ('ongoing_net_cash_usd','combined_net_cash_usd','accounts_bought'):
            r['delta_'+score+'_vs_monthly']=round(r[score]-control[score],2)
    OUT.mkdir(parents=True,exist_ok=True)
    payload={'schema':'pa_milky.budget_cadence_study.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'config':to_payload(purchases.C),'inputs':input_digest(purchases.C),'engine':engine_digest(),'runner_sha256':sha256_file(Path(__file__)),'evaluator_sha256':sha256_file(Path(purchases.__file__)),'design':{'budgets':BUDGETS,'max_live_accounts':20,'purchase_policy':'monthly_one','funding_starts':'second calendar month','selection':'same historical 93 settings per budget; no fresh cushion optimization','terminal':'one permitted request; no reinvestment of terminal receipts'},'purchase_source_sha256':sha256_file(SOURCE),'shared_controls':checks,'rows':rows}
    if cached is not None:
        payload=cached
        payload['report_refresh']={'generated_utc':datetime.now(timezone.utc).isoformat(),
            'runner_sha256':sha256_file(Path(__file__)), 'purchase_source_sha256':sha256_file(SOURCE),
            'shared_controls':checks, 'note':'Original cadence simulations and provenance retained; purchase tables refreshed.'}
    (OUT/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','acquisition_config','withdrawal_config')]
    with (OUT/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report='# Withdrawal cadence: monthly purchases, 20 live accounts, matched cash budgets\n\n'
    report+='372 candidates: the historical 93 cadence/cushion settings under each of four approved budgets. Accounts means total purchased across the dataset; Alive means survivors before terminal withdrawal.\n\n'
    report+='All 12 shared monthly-purchase controls exactly reproduce the purchase study across cash, account counts, funding diagnostics and economic ledgers. Only policy display names differ.\n\n'
    report+='Net cash subtracts account fees and excludes owner contributions. Purchases use available owner cash, including received payouts; monthly contributions begin in the second month. Monthly purchase attempts expire if blocked. All runs use the same tape, execution, rules, daily purchase checks and terminal treatment as the purchase study.\n\n'
    for initial,monthly in BUDGETS:
        family=[r for r in rows if r['initial_cash_usd']==initial and r['monthly_contribution_usd']==monthly]
        report+=f'## ${initial:,} initial; ${monthly:,}/month\n\n'
        for score,title in [('ongoing_net_cash_usd','Ongoing cash'),('combined_net_cash_usd','Terminal-inclusive cash')]:
            leaders=[max([r for r in family if r['withdrawal_policy']==p.name and r['withdrawal_config']['cadence']==c],key=lambda r:(r[score],r['ongoing_net_cash_usd'])) for p in chosen for c in ('calendar_month','weekly','daily')]
            best=max(family,key=lambda r:(r[score],r['ongoing_net_cash_usd']))
            report+=f"### {title}: best tested cushion per policy and cadence\n\nOverall leader: {best['withdrawal_policy']}, {best['withdrawal_config']['cadence']}, retain ${best['withdrawal_config']['min_retained_balance_usd']:,.0f}: **${best[score]:,.2f}**.\n\n"+table(leaders)
        report+='### Fixed-policy purchase comparisons\n\nEach table holds the withdrawal setting and funding fixed. These are purchase-strategy comparisons, not a ranking of separately optimized bundles.\n\n'
        for p in purchases.withdrawal_choices():
            arms=[r for r in source['rows'] if r['initial_cash_usd']==initial and r['monthly_contribution_usd']==monthly and r['withdrawal_policy']==p.name]
            report+=f'#### {p.name}\n\n'+purchases.table(sorted(arms,key=lambda r:r['combined_net_cash_usd'],reverse=True))+'\n\n'
    report+='## Interpretation limits\n\nCadence comparisons at the same policy and cushion are available as monthly-control deltas in candidates.csv. Best-cushion tables adapt cushion as well as cadence. For minimum requests, cadence changes the opportunity to request $500; fixed targets still accrue entitlement monthly.\n\nFunding and capacity are held constant as rules, but realized purchases can change with payout timing and survival. These are operating-policy effects including those purchase responses, not cash-timing effects on an identical book. No trading-neutral or hold-ceiling claim is made.\n\nThe three withdrawal settings in the purchase study are shared controls, not necessarily the winners of this wider capped cadence grid. Re-optimizing all purchase strategies over this wider grid is a separate experiment. All results are historical and in-sample.\n\nReproduce: `venv/Scripts/python.exe scripts/study_budgeted_withdrawal_cadence.py`. Historical reports and reader breakdowns are retained unchanged.\n'
    write_study_report(OUT,report)
    print('All 12 shared controls matched. Report: '+str(OUT/'REPORT.md'),flush=True)


if __name__=='__main__':main()
