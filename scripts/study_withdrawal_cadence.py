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
from pa_milky.study_config import load_study_profile, study_path, study_policies, profile_provenance
STUDY = load_study_profile()
from pa_milky.simulator import run_book
C=None
T=None


def initialize():
    global C,T
    C=load_config(study_path(STUDY, 'scenario'))
    T=load_tape(C)


def work(job):
    p,cadence,cushion=job
    return {**measure(T,C,replace(p,cadence=cadence),cushion),'cadence':cadence}


def table(rows):
    lines=['| Policy | Checks | Retain | Ongoing cash | Final receipt | Total cash | Accounts | Alive | Same trading path |',
           '|---|---|---:|---:|---:|---:|---:|---:|:---:|']
    for r in rows:
        display={'minimum_monthly':'minimum_500_per_check','maximum_excess_monthly':'maximum_excess_per_check'}.get(r['policy'],r['policy'])
        lines.append(f"| {display} | {r['cadence']} | ${r['retained_balance_usd']:,.0f} | "
                     f"${r['ongoing_pocket_usd']:,.2f} | ${r['terminal_received_usd']:,.2f} | "
                     f"${r['combined_pocket_usd']:,.2f} | {int(r['economics']['purchase_fees_usd'] / C.purchase_fee_usd)} | {r['alive_before_terminal']} | {r['trading_neutral']} |")
    return '\n'.join(lines)


def main():
    initialize()
    out=study_path(STUDY, 'cadence')
    out.mkdir(parents=True,exist_ok=True)
    chosen=[p for p in study_policies(STUDY) if p.name in STUDY['cadence']['policy_names']]
    cadences=STUDY['cadence']['cadences']
    levels=STUDY['cadence']['retained_balances']
    jobs=[(p,c,l) for p in chosen for c in cadences for l in levels]
    minimum=next(p for p in chosen if p.amount_rule=='minimum')
    jobs.extend((minimum,c,STUDY['cadence']['minimum_extra_retained_balance']) for c in cadences)
    benchmark=measure(T,C,WithdrawalPolicy(name='hold'),None)
    rows=[]
    with ProcessPoolExecutor(max_workers=STUDY["workers"],initializer=initialize) as pool:
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
             'study_profile':profile_provenance(STUDY),'config':to_payload(C),'inputs':input_digest(C),'engine':engine_digest(),
             'runner_sha256':sha256_file(Path(__file__)),'git_revision':git_revision(),
             'design':{'retained_balances':levels,'minimum_policy_extra_control':STUDY['cadence']['minimum_extra_retained_balance'],
                       'cadences':cadences,'purchase_cadence':'monthly','fixed_entitlement_accrual':'monthly',
                       'weekly_anchor':'Monday 00:00 tape clock','daily_anchor':'00:00 tape clock',
                       'eligibility_starts':'second calendar month','terminal':'one permitted request'},
             'benchmark':benchmark,'rows':rows}
    (out/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','policy_config')]
    with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report='# Withdrawal cadence with monthly account purchases\n\n'
    report+=f'{len(rows)} settings from the selected study profile, including the minimum-policy extra control.\n\n'
    for metric,title in [('ongoing_pocket_usd','Ongoing cash'),('combined_pocket_usd','Cash including final request')]:
        leaders=[max([r for r in rows if r['policy']==p.name and r['cadence']==c],key=lambda r:(r[metric],r['ongoing_pocket_usd']))
                 for p in chosen for c in cadences]
        report+=f'## {title}: best tested cushion per policy and cadence\n\n'+table(leaders)+'\n\n'
    level=STUDY['cadence']['comparison_retained_balance']
    report+=f'## Controlled comparison: maximum excess at ${level:,.0f}\n\n'
    report+=table([r for r in rows if r['policy']=='maximum_excess_monthly' and r['retained_balance_usd']==level])+'\n\n'
    report+='## Interpretation\n\n'
    for metric in ('ongoing_pocket_usd','combined_pocket_usd'):
        best=max(rows,key=lambda r:(r[metric],r['ongoing_pocket_usd']))
        report+=f"{metric}: {best['policy']}, {best['cadence']}, retain ${best['retained_balance_usd']:,.0f}, cash ${best[metric]:,.2f}, {best['alive_before_terminal']} survivors.\n\n"
    report+='Best-cushion comparisons adapt both cadence and cushion. Fixed-setting monthly-control deltas are recorded in CSV/JSON. These are in-sample results.\n\n'
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
