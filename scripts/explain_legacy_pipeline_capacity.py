"""Build a compact interpretation from completed pipeline-capacity evidence."""
from collections import defaultdict
from pathlib import Path
import json
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT
from report_names import report_path

OUT=PROJECT_ROOT/'results/comparisons/legacy_25k_vs_50k/pipeline_capacity'


def choose(rows,score='total'):
    return max(rows,key=lambda r:(r[score],r['ongoing' if score=='total' else 'total']))


def pol(r): return (r['withdrawal'],r['cadence'],r['headroom'])


def pipe(r):
    start='batch' if r['interval']==0 else f"1 per {r['interval']}d"
    return f"{r['concurrency']} subscriptions; {start}; {r['spares']} spares; {'persistent' if r['persistent'] else 'day-only'}"


def main():
    s=json.loads((OUT/'study.json').read_text(encoding='utf-8'))
    rows=[json.loads(x) for x in (OUT/'checkpoint.jsonl').read_text(encoding='utf-8').splitlines()]
    primary=[r for r in rows if [r['initial_cash'],r['monthly_funding']]==s['spec']['budget']]
    oldroot=OUT.parent
    old=[json.loads(x) for x in (oldroot/'eval_supply/checkpoint.jsonl').read_text().splitlines()]
    instant=[json.loads(x) for x in (oldroot/'reserve_by_policy/checkpoint.jsonl').read_text().splitlines()]
    text='# What expanded evaluation capacity changed\n\n'
    text+=(f"{s['unique_simulations']:,} unique simulations, {s['controls']} reproduced historical controls. "
        'January 2020–July 2026; $5,000 initial + $200/month. Dollar figures are net of evaluation and activation fees, '
        'and exclude owner contributions. Main results retain the shared 20-seat cap.\n\n')
    if (OUT/'capacity_frontier.png').exists():
        text+='![Capacity comparison](capacity_frontier.png)\n\n'
    text+=('The earlier 57/44 funded-account counts were outcomes of the winning withdrawal policies, not production ceilings. '
        'The original five-evaluation pipeline already supplied many more accounts under aggressive withdrawals. '
        'The relevant question is whether expanded supply makes that higher turnover timely and profitable enough to win.\n\n')
    text+='## Does the old aggressive policy recover?\n\n'
    text+='| Product | Historical instant supply | Original evaluation pipeline | Best tested expanded shared-seat pipeline | Best tested evaluations-outside-cap sensitivity |\n|---|---:|---:|---:|---:|\n'
    fixed={}
    for p in s['spec']['products']:
        a=tuple(s['anchors'][p]['instant_aggressive'])
        family=[r for r in primary if r['product']==p and pol(r)==a]
        i=choose([r for r in instant if r['product']==p and [r['initial_cash'],r['monthly_funding']]==s['spec']['budget'] and not r['strict_post_payout_balance']])
        baseline=next(r for r in family if (r['persistent'],r['interval'],r['concurrency'],r['spares'],r['reserve_seats'])==(False,0,5,5,True))
        shared=choose([r for r in family if r['reserve_seats']])
        outside=choose([r for r in family if not r['reserve_seats']])
        fixed[p]=(i,baseline,shared,outside)
        cells=[f"${r['total']:,.0f} ({r['accounts']} accounts)" for r in (i,baseline,shared,outside)]
        text+=f'| {p} | '+' | '.join(cells)+' |\n'
    text+='\nThe withdrawal policy is held fixed within each product. Expanded-pipeline columns select the best tested pipeline for that policy.\n\n'
    for p,(_,_,shared,outside) in fixed.items():
        text+=f"- {p}, shared seats: {pipe(shared)}. Evaluations outside cap: {pipe(outside)}.\n"
    text+='\n## Does the earlier $6,000–$7,000 daily reserve still appear?\n\n'
    text+='| Product | Best tested daily-maximum cushion | Ongoing | Closing | Total | Funded accounts |\n|---|---:|---:|---:|---:|---:|\n'
    for p in s['spec']['products']:
        w=choose([r for r in primary if r['product']==p and r['reserve_seats']
                  and r['withdrawal']=='maximum' and r['cadence']=='daily'])
        text+=(f"| {p} | ${w['headroom']:,} | ${w['ongoing']:,.0f} | ${w['terminal']:,.0f} | "
               f"${w['total']:,.0f} | {w['accounts']} |\n")
    text+='\nThese are the best tested **daily maximum** candidates, not the winners across all withdrawal families. '
    text+='This supports the earlier reserve region under that particular withdrawal policy, not a universal reserve amount.\n\n'
    text+='\n## What retuning selected\n\n'
    text+='| Product / score | Pipeline | Withdrawal | Cushion above floor | Ongoing | Closing | Total | Funded / alive |\n|---|---|---|---:|---:|---:|---:|---:|\n'
    for r in s['winners']:
        if not r['reserve_seats']:continue
        text+=(f"| {r['product']} / {r['objective']} | {pipe(r)} | {r['withdrawal']} / {r['cadence']} | "
            f"${r['headroom']:,} | ${r['ongoing']:,.0f} | ${r['terminal']:,.0f} | ${r['total']:,.0f} | {r['accounts']} / {r['alive']} |\n")
    text+='\nCushion means profit above the frozen floor, not nominal account balance. The earlier 25K $31,900 threshold was a $6,800 cushion. '
    text+=('It is a withdrawal threshold, not a target equity balance: minimum monthly withdrawals can let balances '
           'accumulate well above it. A smaller threshold under that policy is not the same as keeping a smaller '
           'actual cushion under daily maximum withdrawals. Funded-account counts are outcomes of each policy, '
           'not quantities the optimizer directly chose.\n\n')
    ties=[]
    for w in s['winners']:
        same=('product','initial_cash','monthly_funding','persistent','interval','concurrency','spares',
              'reserve_seats','withdrawal','cadence')
        near=[r for r in primary if all(r[k]==w[k] for k in same) and abs(r[w['objective']]-w[w['objective']])<=1]
        ties.extend({**r,'objective':w['objective']} for r in near)
        if w['reserve_seats'] and len(near)>1:
            amounts=', '.join(f"${h:,}" for h in sorted({r['headroom'] for r in near}))
            text+=(f"- {w['product']} / {w['objective']}: tested cushions {amounts} are within $1 of the selected "
                   'score at this same pipeline and withdrawal family. Do not interpret cent-level rankings as a unique optimum.\n')
    text+='\n'
    import csv
    with (OUT/'reserve_near_ties.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(ties[0]))
        writer.writeheader();writer.writerows({**r,'job':json.dumps(r['job'])} for r in ties)
    text+='## Replacement service of the selected total winners\n\n'
    text+='| Product / seats | Next-check service | Deaths / unresolved | Completed wait median / p95 days | Unfilled account-days | Average live | Zero-live days | Cash-blocked days |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in s['winners']:
        if r['objective']!='total':continue
        service='n/a' if r['next_check_service'] is None else f"{r['next_check_service']:.1%}"
        text+=(f"| {r['product']} / {'shared' if r['reserve_seats'] else 'evals outside'} | {service} | "
            f"{r['deaths']} / {r['replacements_unfilled']} | {r['replacement_wait_median_days']} / {r['replacement_wait_p95_days']} | "
            f"{r['unfilled_account_days']:,.0f} | {r['average_live_accounts']} | {r['zero_live_days']} | {r['cash_blocked_days']} |\n")
    text+='\nCompleted-wait percentiles exclude unresolved replacements. Unfilled account-days includes every death’s wait until replacement or the horizon. '
    text+='Daily-state occupancy is sampled at decision boundaries; zero-live days includes startup.\n\n'
    text+='## Matched changes at frozen withdrawal settings\n\n'
    text+='These comparisons use the full screening matrix only. Each pair keeps product, withdrawal policy, seat mode, and all other pipeline settings fixed. '
    text+='Medians and win shares describe this grid, not probabilities of future improvement.\n\n'
    with (OUT/'screening.csv').open(encoding='utf-8',newline='') as f:
        ids={tuple(json.loads(r['job'])) for r in csv.DictReader(f)}
    screen=[r for r in primary if tuple(r['job']) in ids]
    text+='| Product | Seat mode | Change | Matched pairs | Median total change | Share improved |\n|---|---|---|---:|---:|---:|\n'
    for p in s['spec']['products']:
        for seats in (True,False):
            group=[r for r in screen if r['product']==p and r['reserve_seats']==seats]
            for field,a,b,label in [('persistent',False,True,'persist missed demand'),('interval',0,1,'batch → one/day'),
                                   ('interval',0,7,'batch → one/week'),('spares',0,5,'0 → 5 spares'),('spares',5,10,'5 → 10 spares'),
                                   ('concurrency',5,10,'5 → 10 subscriptions'),('concurrency',10,20,'10 → 20 subscriptions')]:
                keys=('withdrawal','cadence','headroom','persistent','interval','concurrency','spares')
                pairs=defaultdict(dict)
                for r in group:
                    if r[field] in (a,b):pairs[tuple(r[k] for k in keys if k!=field)][r[field]]=r['total']
                deltas=[v[b]-v[a] for v in pairs.values() if a in v and b in v]
                text+=(f"| {p} | {'shared' if seats else 'evals outside'} | {label} | {len(deltas)} | "
                    f"${statistics.median(deltas):,.0f} | {sum(d>0 for d in deltas)/len(deltas):.0%} |\n")
    text+='\n## Did any tested aggressive pipeline reach 95% next-check service?\n\n'
    for p,(_,_,_,_) in fixed.items():
        a=tuple(s['anchors'][p]['instant_aggressive'])
        for seats in (True,False):
            eligible=[r for r in primary if r['product']==p and r['reserve_seats']==seats and pol(r)==a
                      and r['next_check_service'] is not None and r['next_check_service']>=.95]
            label='shared seats' if seats else 'evaluations outside the cap'
            if not eligible:text+=f'- {p}, {label}: no tested candidate reached 95%.\n'
            else:
                r=choose(eligible)
                text+=f"- {p}, {label}: {len(eligible)} candidates; best total ${r['total']:,.0f}, {pipe(r)}, {r['deaths']} deaths.\n"
    text+='\nThis is realized service against each policy’s own deaths. Starvation changes which accounts exist and therefore which deaths occur; '
    text+='it is not a replay of a fixed external replacement-demand stream or a forecast of 95% reliability.\n\n'
    text+='## Smaller-budget checks\n\n'
    text+='Selected shared-seat winners were replayed without retuning at the other three budgets. '
    text+='The following are replays of the **total-score** winners, not new budget-specific optima.\n\n'
    text+='| Product | $1,000 + $0/month | $1,000 + $200/month | $5,000 + $0/month |\n|---|---:|---:|---:|\n'
    for p in s['spec']['products']:
        w=next(r for r in s['winners'] if r['product']==p and r['reserve_seats'] and r['objective']=='total')
        cells=[]
        for budget in s['spec']['budget_sensitivity']:
            r=next(r for r in s['budget_sensitivity'] if r['product']==p and [r['initial_cash'],r['monthly_funding']]==budget
                   and pol(r)==pol(w) and pipe(r)==pipe(w))
            cells.append(f"${r['total']:,.0f} ({r['accounts']} funded)")
        text+=f'| {p} | '+' | '.join(cells)+' |\n'
    text+='\nBoth selected total-winner pipelines run out of usable funding at $1,000 with no top-ups. '
    text+='This does not mean that budget cannot work under another policy: the separate 50K ongoing-winner replay remains profitable. '
    text+=f'The full budget table is in {report_path(OUT,"REPORT.generated.md").name} and budget_sensitivity.csv.\n\n'
    text+='## Limits and reproducibility\n\n'
    text+='The pipeline search screens three historical anchors before retuning a matched shortlist. It can miss a pipeline that needs an entirely different '
    text+='withdrawal policy to perform well. The same tape and starting date are used throughout. Different budgets are sensitivity replays, '
    text+='not independent samples. Increasing concurrency need not improve profit: it changes cohort timing, fees and the seats available to funded accounts. '
    text+='No constant-capacity, independent-pass or monotone-profit assumption is warranted.\n\n'
    text+=f'See [full generated report]({report_path(OUT,"REPORT.generated.md").name}), [capacity table](frontier.csv), [screening rows](screening.csv), '
    text+='[all settings](all_settings.csv), [audit](AUDIT.json), and [run contract](contract.json). Rebuild this note with '
    text+='`venv/Scripts/python.exe scripts/explain_legacy_pipeline_capacity.py`.\n'
    report_path(OUT,'FINDINGS.generated.md').write_text(text,encoding='utf-8')
    print(report_path(OUT,'FINDINGS.generated.md'))


if __name__=='__main__':main()
