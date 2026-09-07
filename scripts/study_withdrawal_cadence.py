"""Cadence study: same monthly purchases, entitlement, rules, and cushion grid."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from pa_milky.config import CONFIG_ROOT,load_config,to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.policy_study import policies,measure,annotate_against_benchmark
from pa_milky.provenance import input_digest,engine_digest,git_revision,sha256_file
from pa_milky.report import write_outputs
from pa_milky.study_reports import write_study_report
from pa_milky.simulator import run_book
C=None
T=None


def initialize():
    global C,T
    C=load_config(CONFIG_ROOT/'scenarios/full_rulebook_monthly_500.json')
    T=load_tape(C)


def work(job):
    p,cadence,cushion=job
    return {**measure(T,C,replace(p,cadence=cadence),cushion),'cadence':cadence}


def table(rows):
    lines=['| Policy | Checks | Retain | Ongoing cash | Final receipt | Total cash | Alive | Same trading path |',
           '|---|---|---:|---:|---:|---:|---:|:---:|']
    for r in rows:
        display={'minimum_monthly':'minimum_500_per_check','maximum_excess_monthly':'maximum_excess_per_check'}.get(r['policy'],r['policy'])
        lines.append(f"| {display} | {r['cadence']} | ${r['retained_balance_usd']:,.0f} | "
                     f"${r['ongoing_pocket_usd']:,.2f} | ${r['terminal_received_usd']:,.2f} | "
                     f"${r['combined_pocket_usd']:,.2f} | {r['alive_before_terminal']} | {r['trading_neutral']} |")
    return '\n'.join(lines)


def main():
    initialize()
    out=Path('results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases')
    out.mkdir(parents=True,exist_ok=True)
    chosen=[p for p in policies() if p.name in ('fixed_750_backlog','fixed_1000_backlog',
            'fixed_1500_backlog','minimum_monthly','maximum_excess_monthly')]
    cadences=('calendar_month','weekly','daily')
    levels=list(range(31600,32101,100))
    jobs=[(p,c,l) for p in chosen for c in cadences for l in levels]
    minimum=next(p for p in chosen if p.amount_rule=='minimum')
    jobs.extend((minimum,c,30000) for c in cadences)
    benchmark=measure(T,C,WithdrawalPolicy(name='hold'),None)
    rows=[]
    with ProcessPoolExecutor(max_workers=4,initializer=initialize) as pool:
        for i,row in enumerate(pool.map(work,jobs),1):
            rows.append(row)
            if i%10==0:print(f'Completed {i}/{len(jobs)}',flush=True)
    annotate_against_benchmark(rows,benchmark)
    controls={(r['policy'],r['retained_balance_usd']):r for r in rows if r['cadence']=='calendar_month'}
    for r in rows:
        control=controls[r['policy'],r['retained_balance_usd']]
        r['delta_ongoing_vs_monthly_usd']=round(r['ongoing_pocket_usd']-control['ongoing_pocket_usd'],2)
        r['delta_combined_vs_monthly_usd']=round(r['combined_pocket_usd']-control['combined_pocket_usd'],2)
    payload={'schema':'pa_milky.cadence_study.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
             'config':to_payload(C),'inputs':input_digest(C),'engine':engine_digest(),
             'runner_sha256':sha256_file(Path(__file__)),'git_revision':git_revision(),
             'design':{'retained_balances':levels,'minimum_policy_extra_control':30000,
                       'cadences':cadences,'purchase_cadence':'monthly','fixed_entitlement_accrual':'monthly',
                       'weekly_anchor':'Monday 00:00 tape clock','daily_anchor':'00:00 tape clock',
                       'eligibility_starts':'second calendar month','terminal':'one permitted request'},
             'benchmark':benchmark,'rows':rows}
    (out/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','policy_config')]
    with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report='# Withdrawal cadence with monthly account purchases\n\n'
    report+='93 settings: five policies, six cushions in the $31,600-$32,100 band, three request cadences, plus the minimum-policy $30,000 control.\n\n'
    for metric,title in [('ongoing_pocket_usd','Ongoing cash'),('combined_pocket_usd','Cash including final request')]:
        leaders=[max([r for r in rows if r['policy']==p.name and r['cadence']==c],key=lambda r:(r[metric],r['ongoing_pocket_usd']))
                 for p in chosen for c in cadences]
        report+=f'## {title}: best tested cushion per policy and cadence\n\n'+table(leaders)+'\n\n'
    report+='## Controlled comparison: maximum excess at $31,600\n\n'
    report+=table([r for r in rows if r['policy']=='maximum_excess_monthly' and r['retained_balance_usd']==31600])+'\n\n'
    report+='## Interpretation\n\n'
    report+='At $31,600, weekly maximum-excess checks bring $15,189.65 more cash forward than monthly checks and add $784.57 to terminal-inclusive cash, with the same trading path. Daily maximum-excess checks at this cushion instead lose accounts and substantially reduce total cash.\n\n'
    report+='Daily minimum-$500 checks at $31,900 receive $357,800 during trading and $460,511.75 including the terminal request. That is $91,600 more ongoing cash than monthly minimum checks at $30,000, with equal total cash. This comparison adapts BOTH cadence and cushion. Weekly minimum checks at $31,600 receive $349,600 with the same total.\n\n'
    report+='The highest ongoing-only cash is $373,200 from daily minimum checks at $30,000, but only two accounts survive and nothing more is received at exit. It is not the strongest candidate for preserving earning capacity. The next candidate comparison should retain the daily-minimum/high-cushion and weekly-excess policies rather than assume more frequent withdrawal is always better. These numbers are historical, not forecasts.\n\n'
    report+='## Conventions and limits\n\n'
    report+='Daily means one midnight check after completed exits; weekly means Monday midnight; monthly means the first midnight of the month. '
    report+='Checks start in the second calendar month for every cadence. Fixed-target entitlement accrues once per calendar month, never per check. '
    report+='Minimum means $500 per eligible check, not a $500 monthly budget; changing its cadence therefore changes desired extraction frequency. '
    report+='Maximum requests spare cash above the cushion. Firm gates still apply, including days since payout. '
    report+='A failed eligibility check is recorded as a denial by the existing ledger; this is not proof of an externally submitted application. '
    report+='Trades at an exact decision timestamp settle first. No post-midnight future trades are used. '
    report+='All policies permit one final request releasing the voluntary cushion, with zero processing delay.\n\n'
    report+='The study holds the tape, account purchases, contract size and rulebook fixed. Candidate deltas in CSV/JSON are against the same policy and cushion with monthly checks. '
    report+='Trading-neutral means the per-account path fingerprint matches hold on this shared tape and activation schedule. '
    report+='The hold reference is not a guaranteed earnings maximum. These are in-sample comparisons over the chosen band; cadence-specific global cushion optima remain unsearched.\n\n'
    for metric,label in [('ongoing_pocket_usd','best_ongoing'),('combined_pocket_usd','best_terminal')]:
        best=max(rows,key=lambda r:(r[metric],r['ongoing_pocket_usd']));p=WithdrawalPolicy.from_payload(best['policy_config'])
        cfg=replace(C,policy=p,scenario=f'cadence_study_{label}',brick_name=f'cadence_study_{label}')
        result=run_book(T,cfg)
        assert result.pocket_usd==best['combined_pocket_usd']
        write_outputs(result,out/label)
        (out/label/'config.json').write_text(json.dumps(to_payload(cfg),indent=2),encoding='utf-8')
        report+=f'[{label} detailed report]({label}/report.txt) and its embedded config.json reproduce the leading run.\n\n'
    report+='Reproduce: `venv/Scripts/python.exe scripts/study_withdrawal_cadence.py`.\n'
    write_study_report(out, report)
    print(report,flush=True)


if __name__=='__main__': main()
