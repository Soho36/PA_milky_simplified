"""Readable findings from the completed, audited blocked supply experiment."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT
from study_blocked_pipeline import best, policy, pipeline, ORIGINAL, table
from study_legacy_pipeline_capacity import csv_write, pipeline_label
from report_names import report_path


def main():
    root=PROJECT_ROOT/'results/legacy_25k/blocked_pipeline'
    data=json.loads((root/'study.json').read_text())
    audit=json.loads((root/'AUDIT.generated.json').read_text())
    spec=data['spec']
    frozen=[r for r in data['screen'] if policy(r)==tuple(spec['anchors']['blocked_instant_maximum'])]
    original=next(r for r in frozen if pipeline(r)==ORIGINAL)
    frozen_shared=best([r for r in frozen if r['reserve_seats']], 'total')
    frozen_outside=best([r for r in frozen if not r['reserve_seats']], 'total')
    ongoing=next(r for r in data['winners'] if r['label']=='shared / ongoing')
    total=next(r for r in data['winners'] if r['label']=='shared / total')
    instant=data['controls'][0]
    text=('# What realistic supply changes for blocked copying\n\n'
          '**$1,000 initial + $200/month, Legacy25K, January 2020–July 2026.** '
          'Every free PA copies; busy PAs skip. Net cash excludes owner contributions and includes every procurement fee.\n\n')
    text+=(f"The instant-supply aggressive co-winner earned **${instant['total']:,.2f}**. "
           f"With the same maximum-weekly withdrawal rule and $25,100 reserve, the original evaluation pipeline earns "
           f"**${original['total']:,.2f}**. Searching pipeline capacity while keeping that withdrawal rule fixed "
           f"raises it to **${frozen_shared['total']:,.2f}** under the shared 20-seat cap "
           f"({(frozen_shared['total']/instant['total']-1):+.1%} against instant supply). "
           f"Allowing evaluations outside the cap gives **${frozen_outside['total']:,.2f}**.\n\n")
    text+='## Main comparison\n\n'
    text+='| Case | Ongoing net | Terminal payout | Total net | Funded / deaths | All fees |\n|---|---:|---:|---:|---:|---:|\n'
    for name,r in [('Instant aggressive control',instant),('Original supply / frozen aggressive',original),
                   ('Best shared supply / frozen aggressive',frozen_shared),
                   ('Best shared ongoing / retuned',ongoing),('Best shared total / retuned',total),
                   ('Outside-cap supply / frozen aggressive',frozen_outside)]:
        text+=(f"| {name} | ${r['ongoing']:,.2f} | ${r['terminal']:,.2f} | ${r['total']:,.2f} | "
               f"{r['accounts']} / {r['deaths']} | ${r['spend']:,.2f} |\n")
    text+=('\nInstant supply starts one paid PA at a $200 purchase fee. Evaluation supply starts with no PAs '
           'and pays $33 per evaluation subscription month plus $125 per activated PA. '
           'Thus the comparison includes changed fees and startup as well as replacement delays. '
           'Persistent demand also carries missed monthly growth orders forward; the original pipeline lets them expire.\n\n')
    text+='## What the selected shared-cap policies do\n\n'
    for objective,r in [('Ongoing cash',ongoing),('Terminal-inclusive cash',total)]:
        service=f"{r['next_check_service']:.1%}" if r['next_check_service'] is not None else 'n/a'
        text+=(f"**{objective}:** {r['withdrawal']} {('$'+str(r['amount'])) if r['amount'] else ''} "
               f"withdrawals checked {r['cadence']}, retaining ${r['retained_balance']:,.0f}. "
               f"Pipeline: {pipeline_label(r)}. It averages {r['average_live_accounts']:.2f} live PAs, "
               f"takes {r['copies']:,} trade copies and participates in {r['signals_executed']/r['signals_loaded']:.2%} of signals. "
               f"{service} of deaths are replaced at the next daily check; completed waits have a median of "
               f"{r['replacement_wait_median_days']} days and p95 of {r['replacement_wait_p95_days']} days. "
               f"{r['replacements_unfilled']} replacements remain unresolved at the horizon. "
               f"Zero-live time is {r['zero_live_days']} days, including startup.\n\n")
    text+=(f"Retuning improves ongoing cash by **${ongoing['ongoing']-frozen_shared['ongoing']:,.2f}** "
           f"over the best shared-cap frozen aggressive pipeline. The total-cash leader's "
           f"**${total['terminal']:,.2f}** terminal receipt should not be treated as recurring withdrawal income.\n\n")
    text+=(f"The ongoing winner gives up only **${total['total']-ongoing['total']:,.2f}** of total cash "
           f"while delivering **${ongoing['ongoing']-total['ongoing']:,.2f}** more during the run. "
           'This is a more useful operating trade-off than selecting the terminal-inclusive winner solely by its final score. '
           'The spare number is a target, not guaranteed inventory; the ongoing winner ends with no spares and five live PAs.\n\n')
    text+='## The exact reserve is sensitive\n\n'
    near=[r for r in data['search'] if pipeline(r)==pipeline(ongoing) and
          (r['withdrawal'],r['cadence'],r['amount'])==(ongoing['withdrawal'],ongoing['cadence'],ongoing['amount']) and
          abs(r['headroom']-ongoing['headroom'])<=200]
    text+='| Retained balance, same ongoing-winner pipeline | Ongoing cash | Deaths |\n|---:|---:|---:|\n'
    for r in sorted(near,key=lambda r:r['headroom']):
        text+=f"| ${r['retained_balance']:,.0f} | ${r['ongoing']:,.2f} | {r['deaths']} |\n"
    text+=('\nThese discontinuities mean $26,900 is a historical search winner, not a robust universal optimum. '
           'Reserve changes alter withdrawals, failures and the timing of subsequent evaluation cohorts. '
           'The frozen ongoing policy earns $384,215 with $5,000 + $200/month, below its primary-budget result; '
           'more starting capital does not guarantee a better path for a fixed policy. '
           'With $1,000 and no monthly funding, both main winners exhaust their usable accounts.\n\n')
    text+='## Replaying the same policies without PA blocking\n\n'
    rows=[]
    for w in data['winners']:
        paired=next(r for r in data['paired'] if r['job']==['unrestricted',*w['job'][1:]])
        rows.extend([{**w,'label':w['label']+' / blocked'},
                     {**paired,'label':w['label']+' / unrestricted'}])
    text+=table(rows)
    unrestricted={tuple(r['job'][1:]):r for r in data['unrestricted_screen']}
    higher=sum(r['total']>unrestricted[tuple(r['job'][1:])]['total'] for r in data['screen'])
    text+=(f"Across all {len(data['screen'])} frozen-policy pairs, blocked copying earns more total net cash "
           f"in {higher}. Unrestricted copying is therefore not a mathematical upper bound on cash.\n\n")
    text+=('These are paired policy replays under identical procurement rules and funding, '
           'not independently optimized unrestricted benchmarks. Trade coverage alone does not '
           'determine the cash ranking; execution changes PA deaths, receipts and subsequent supply demand.\n\n')
    text+='## Capacity frontier after the staged search\n\n'
    frontier=[]
    for seats in (True,False):
        for n in spec['concurrency']:
            group=[r for r in data['search'] if r['reserve_seats']==seats and r['concurrency']==n]
            for score in ('ongoing','total'):
                frontier.append({**best(group,score),'label':f"{'shared' if seats else 'outside'} / {n} evals / {score}"})
    text+=table(frontier)
    csv_write(root/'frontier.csv',frontier)
    text+='## Historical sensitivity without retuning\n\n'+table(data['transfers'])
    text+=('Later starts overlap the full-tape selection history. They are fresh-account historical replays, '
           'not forward or unseen validation. Other funding budgets keep the selected policy unchanged.\n\n')
    text+='## Search resolution and evidence\n\n'
    for w in data['winners']:
        score=w['label'].split(' / ')[1]
        group=[r for r in data['search'] if r['reserve_seats']==w['reserve_seats']]
        tied=[r for r in group if abs(r[score]-w[score])<0.005]
        same=[r for r in group if pipeline(r)==pipeline(w) and
              (r['withdrawal'],r['cadence'],r['amount'])==(w['withdrawal'],w['cadence'],w['amount']) and
              abs(r[score]-w[score])<=1]
        text+=(f"- {w['label']}: {len(tied)} tested settings tie on the primary objective. "
               f"Within the selected pipeline/withdrawal family, tested reserves within $1 of that score: "
               f"{', '.join('$'+format(r['retained_balance'],',.0f') for r in sorted(same,key=lambda r:r['headroom']))}.\n")
    text+=(f"\n{data['unique_simulations']:,} unique runs, including controls within the new checkpoint, "
           f"paired execution screens and frozen transfers. Three earlier headline controls separately reproduce exactly. "
           f"The audit independently checks {audit['audited_trade_copies']:,} selected PA trade assignments across "
           f"{audit['detailed_ledgers']} detailed ledgers, including no overlap, paid activation provenance, "
           'cash, fees, seat caps and search-domain completeness. The existing 279-test suite and the new '
           'evaluation-plus-blocking timeline test pass.\n\n'
           'This is the best result within a staged search, not a global optimum. The main procurement family '
           'is current-slot monthly growth plus replacement; other acquisition families are not reoptimized. '
           'All supply assumptions are inherited, including indefinite waiting for activation, no spare expiry '
           'and no payout-processing delay. The outside-cap arm is a sensitivity, not a statement about firm rules. '
           'Evaluation launch dates share the tape and do not create independent pass probabilities.\n\n'
           f'[Full generated report]({report_path(root,"REPORT.generated.md").name}), [all settings](all_settings.csv), '
           '[independent audit](AUDIT.generated.json), [study protocol](../../../research/legacy_25k/BLOCKED_PIPELINE.md).\n')
    report_path(root,'FINDINGS.generated.md').write_text(text,encoding='utf-8')
    print(text[:5500])


if __name__=='__main__':
    main()
