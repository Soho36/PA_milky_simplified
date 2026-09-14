"""Capacity experiment: frozen-policy screening, matched reserve search, service metrics.

Run with the project venv. Saved contracts prevent mixing changed simulations.
All objectives are in-sample and include all evaluation/activation spending.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import csv
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import study_legacy_50k_operating as sim
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.report import write_outputs
from pa_milky.simulator import run_book
from pa_milky.study_reports import write_study_report

SPEC_PATH=PROJECT_ROOT/'config/studies/legacy_pipeline_capacity.json'
ROOT=PROJECT_ROOT/'results/comparisons/legacy_25k_vs_50k'
ACQ='monthly_current_slot_replacements'
SCORES=('total','ongoing')
SPEC=EVAL=None


def initialize(spec_path=SPEC_PATH):
    global SPEC,EVAL
    SPEC=json.loads(Path(spec_path).read_text(encoding='utf-8'))
    EVAL=json.loads((PROJECT_ROOT/SPEC['evaluation_spec']).read_text(encoding='utf-8'))
    sim.initialize()


def read_rows(name):
    return [json.loads(x) for x in (ROOT/name/'checkpoint.jsonl').read_text(encoding='utf-8').splitlines()]


def best(rows,score):
    return max(rows,key=lambda r:(r[score],r['ongoing' if score=='total' else 'total'], -r['accounts']))


def policy(r):
    return (r['withdrawal'],r['cadence'],r['headroom'])


def pipeline(r):
    return (r['persistent'],r['interval'],r['concurrency'],r['spares'],r['reserve_seats'])


def job(prod,budget,pol,pipe):
    return (prod,*budget,*pol,*pipe)


def evaluate(j,detail=False):
    prod,initial,monthly,rule,cadence,headroom,persistent,interval,concurrency,spares,reserve_seats=j
    base=sim.C[prod]
    pol=WithdrawalPolicy(name=f'{rule}_{cadence}_headroom_{headroom}',cadence=cadence,amount_rule=rule,
        quantize_to_amount=False,terminal_withdrawal='firm_permitted',
        min_retained_balance_usd=base.trailing_floor_balance_usd+headroom)
    acq=AcquisitionPolicy(ACQ,initial,monthly,max_live_accounts=20,spare_capacity=spares,
        evaluation=EvaluationSpec(**EVAL['evaluations'][prod]),evaluations_at_once=concurrency,
        persistent_demand=persistent,evaluation_start_interval_days=interval,
        evaluations_reserve_seats=reserve_seats)
    r=run_book(sim.T,replace(base,policy=pol),acquisition=acq)
    cash=r.acquisition.summary()
    assert Economics.measure(r).residual_usd==cash['cash_identity_residual_usd']==0
    assert cash['net_cash_created_usd']==r.pocket_usd
    assert len(r.accounts)+r.unused_spares==cash['evaluations_activated']
    assert round(cash['evaluation_fees_usd']+cash['activation_fees_usd'],2)==r.total_purchase_cost_usd
    terminal=round(sum(e.received_usd for e in r.terminal_payouts),2)
    row={'product':prod,'initial_cash':initial,'monthly_funding':monthly,'withdrawal':rule,
        'cadence':cadence,'headroom':headroom,'retained_balance':pol.min_retained_balance_usd,
        'persistent':persistent,'interval':interval,'concurrency':concurrency,'spares':spares,
        'reserve_seats':reserve_seats,'total':r.pocket_usd,'ongoing':round(r.pocket_usd-terminal,2),
        'terminal':terminal,'accounts':len(r.accounts),'alive':r.alive_at_horizon,
        'activated':cash['evaluations_activated'],'evaluations':cash['evaluations_started'],
        'evaluation_months':cash['evaluation_months_paid'],'evaluation_fees':cash['evaluation_fees_usd'],
        'activation_fees':cash['activation_fees_usd'],'spend':r.total_purchase_cost_usd,
        'ending_cash':cash['ending_owner_cash_usd'],'contributions':cash['owner_contributions_usd'],
        'spares_at_end':r.unused_spares,'in_flight_at_end':len(r.acquisition.active),
        **measure_pipeline(r),'job':list(j)}
    return (row,r) if detail else row


def csv_write(path,rows):
    if not rows: return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows({k:json.dumps(v) if isinstance(v,(list,dict,tuple)) else v for k,v in r.items()} for r in rows)


def pipeline_label(r):
    timing='batch' if not r['interval'] else f"one/{r['interval']}d"
    return f"{'persistent' if r['persistent'] else 'day-only'}, {r['concurrency']} evals, {timing}, {r['spares']} spares"


def table(rows):
    out='| Product / objective | Pipeline | Withdrawal / cushion above floor | Ongoing | Closing | Total | Funded / alive | Next-check service | Wait p95¹ | Unfilled account-days |\n'
    out+='|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in rows:
        service=f"{r['next_check_service']:.1%}" if r['next_check_service'] is not None else 'n/a'
        out+=(f"| {r['product']} / {r.get('objective','fixed')} | {pipeline_label(r)} | "
            f"{r['withdrawal']} / {r['cadence']} / ${r['headroom']:,} | ${r['ongoing']:,.0f} | "
            f"${r['terminal']:,.0f} | ${r['total']:,.0f} | {r['accounts']} / {r['alive']} | "
            f"{service} | {r['replacement_wait_p95_days']} | {r['unfilled_account_days']:,.0f} |\n")
    return out+'\n'


def render(screen,search,frontier,anchors,controls,sensitivity):
    text='# Evaluation pipeline capacity: Legacy 25K and 50K\n\n'
    text+=(f"{len(screen):,} fixed-policy screening rows; {len(search):,} reserve-search rows (overlap possible). "
        f"{controls} historical headline controls reproduced exactly. January 2020–July 2026 tape. "
        '$5,000 initial + $200/month, unless a budget sensitivity is explicitly shown.\n\n')
    text+='## What was tested\n\n'
    text+=('- Main experiment keeps live funded accounts + activated spares + evaluations in flight within 20 seats. '
        'The separate seat sensitivity allows evaluations outside that cap; live + activated spares still cannot exceed 20. '
        'This is an explicit modelling sensitivity, not a claim about firm rules.\n'
        '- Concurrent subscription caps: 2, 5, 10, 20. Starts: batch, at most one per calendar day, or one every seven calendar days. '
        'The stagger applies globally to new subscriptions; renewals keep their original monthly anniversary. '
        'Staggering also slows launch throughput and does not make the shared tape independent.\n'
        '- Spare targets: 0, 2, 5, 10; these are desired inventory, not guaranteed stock. '
        'Demand-only replenishment starts evaluations while orders or spare deficits remain. No free starting inventory.\n'
        '- Persistent demand queues missed monthly growth orders until filled. Death replacements take priority and consume '
        'the current month’s growth order. Older missed growth orders remain FIFO. Growth orders are not admitted while '
        'live accounts plus outstanding orders already cover 20 seats. Original day-only demand remains a control.\n'
        '- Three withdrawal anchors are frozen before screening: each product’s historical instant-supply total winner, '
        'evaluation-supply total winner and evaluation-supply ongoing winner. All use monthly current-slot replacements.\n'
        '- For every concurrency and seat mode, screen leaders under both objectives nominate pipelines. '
        'Both products then receive the same union of nominated pipelines plus the original pipeline, '
        'with minimum/maximum requests, daily/weekly/monthly cadence, and the configured reserve grid. '
        'Local refinements around both objectives are also paired. This is a staged search, not an exhaustive global optimum.\n\n')
    text+='## Frozen aggressive policies: can expanded supply sustain them?\n\n'
    fixed=[]
    for prod in SPEC['products']:
        for seats in (True,False):
            group=[r for r in screen if r['product']==prod and r['reserve_seats']==seats
                   and policy(r)==anchors[prod]['instant_aggressive']]
            w=best(group,'total')
            fixed.append({**w,'objective':'aggressive; '+('shared seats' if seats else 'evals outside cap')})
    text+=table(fixed)
    text+='## Retuned winners with the original shared-seat cap\n\n'
    text+=table([{**best([r for r in search if r['product']==p and r['reserve_seats']],score),'objective':score}
                 for p,score in product(SPEC['products'],SCORES)])
    text+='## Capacity frontier within shortlisted pipelines\n\n'
    for seats in (True,False):
        text+=f"### {'Shared 20 seats' if seats else 'Sensitivity: evaluations outside funded cap'}\n\n"
        text+=table([r for r in frontier if r['reserve_seats']==seats])
    text+='## Budget sensitivity: selected main-study winners replayed without retuning\n\n'
    for budget in SPEC['budget_sensitivity']:
        text+=f'### ${budget[0]:,} initial + ${budget[1]:,}/month\n\n'
        text+=table([r for r in sensitivity if [r['initial_cash'],r['monthly_funding']]==budget])
    text+='## How to interpret the service metrics\n\n'
    text+=('Next-check service is the fraction of actual account deaths replaced at the first daily decision at or after death. '
        'It is an observed service fraction, not a forward probability or a confidence estimate. '
        '¹ Wait p95 includes only completed replacements; unresolved deaths are right-censored. '
        'Unfilled account-days includes both completed waits and unresolved waits through the tape horizon. '
        'See all_settings.csv for unresolved counts, oldest unresolved wait, average live accounts, zero-live days, '
        'subscription utilization and separate unaffordable activation, renewal and start counts. '
        'Cash-blocked counts can overlap other shortages and are diagnostics, not an additive attribution of profit loss.\n\n'
        'All results are in-sample. Net cash excludes owner contributions and subtracts all evaluation and activation fees. '
        'Ongoing excludes the single permitted closing withdrawal. Funded account count is an outcome, not a decision variable. '
        'A 95% next-check service filter is reported only when reached by an observed candidate; this does not establish future reliability. '
        'The instant-supply historical result is a comparator under different timing/cost assumptions, not a mathematical upper bound.\n')
    return text


def main(spec_path=SPEC_PATH):
    initialize(spec_path)
    out=(PROJECT_ROOT/SPEC['output']).resolve()
    assert out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=True)
    protected={str(p):sha256_file(p) for p in (PROJECT_ROOT/'results').rglob('*')
               if p.is_file() and not p.is_relative_to(out) and not p.name.startswith('~$')}
    contract={'spec':SPEC,'evaluation_spec':EVAL,'configs':{k:to_payload(v) for k,v in sim.C.items()},
        'engine':engine_digest(),'inputs':input_digest(sim.C['legacy_25k']),
        'runner_sha256':sha256_file(Path(__file__)), 'initializer_sha256':sha256_file(Path(sim.__file__)),
        'prior_checkpoints':{name:sha256_file(ROOT/name/'checkpoint.jsonl') for name in ('eval_supply','reserve_by_policy')}}
    cp=out/'contract.json'
    if cp.exists(): assert json.loads(cp.read_text(encoding='utf-8'))==contract,'Changed contract: use a new output directory'
    else: cp.write_text(json.dumps(contract,indent=2),encoding='utf-8')
    prior=read_rows('eval_supply')
    instant=[r for r in read_rows('reserve_by_policy') if not r['strict_post_payout_balance']]
    anchors={}
    for p in SPEC['products']:
        a=[r for r in prior if r['product']==p and [r['initial_cash'],r['monthly_funding']]==SPEC['budget']]
        b=[r for r in instant if r['product']==p and [r['initial_cash'],r['monthly_funding']]==SPEC['budget']]
        winners={'instant_aggressive':best(b,'total'),'eval_total':best(a,'total'),'eval_ongoing':best(a,'ongoing')}
        assert all(r['acquisition']==ACQ for r in winners.values())
        anchors[p]={name:policy(r) for name,r in winners.items()}
    checkpoint=out/'checkpoint.jsonl'
    cache={}
    if checkpoint.exists():
        for line in checkpoint.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);cache[tuple(r['job'])]=r

    def run(pool,jobs,label):
        jobs=sorted(set(jobs))
        missing=[j for j in jobs if j not in cache]
        print(f'{label}: {len(missing)} new / {len(jobs)} rows',flush=True)
        with checkpoint.open('a',encoding='utf-8') as f:
            futures={pool.submit(evaluate,j):j for j in missing}
            for n,future in enumerate(as_completed(futures),1):
                r=future.result();cache[tuple(r['job'])]=r
                f.write(json.dumps(r)+'\n');f.flush()
                if n%50==0 or n==len(missing): print(f'{label}: {n}/{len(missing)}',flush=True)
        return [cache[j] for j in jobs]

    with ProcessPoolExecutor(max_workers=SPEC['workers'],initializer=initialize,initargs=(str(spec_path),)) as pool:
        # Reproduce all eight old evaluation winners, including non-hybrid acquisitions.
        # The original evaluator is used only for historical controls.
        import study_legacy_eval_supply as old
        old.initialize()
        controls=0
        for p,budget in product(SPEC['products'],EVAL['budgets']):
            w=best([r for r in prior if r['product']==p and [r['initial_cash'],r['monthly_funding']]==budget],'total')
            replay=old.evaluate(w['job'])
            assert all(replay[k]==w[k] for k in ('total','ongoing','accounts','alive'))
            w=best([r for r in instant if r['product']==p and [r['initial_cash'],r['monthly_funding']]==budget],'total')
            replay=sim.evaluate(w['job'])
            assert all(replay[k]==w[k] for k in ('total','ongoing','accounts','alive'))
            controls+=2
        print(f'Historical controls reproduced: {controls}',flush=True)
        pipes=list(product(SPEC['persistent_demand'],SPEC['start_intervals_days'],SPEC['concurrency'],SPEC['spares'],(True,)))
        # Matched second seat mode on the same full matrix, not only favourable candidates.
        pipes+=[(*p[:4],False) for p in pipes]
        screen_jobs=[job(p,SPEC['budget'],pol,pipe) for p in SPEC['products']
                     for pol in set(anchors[p].values()) for pipe in pipes]
        screen=run(pool,screen_jobs,'Fixed policies')
        selected={(False,0,5,5,True)}
        for p,seats,n,score in product(SPEC['products'],(True,False),SPEC['concurrency'],SCORES):
            w=best([r for r in screen if r['product']==p and r['reserve_seats']==seats and r['concurrency']==n],score)
            selected.add(pipeline(w))
        csv_write(out/'screening.csv',screen)
        (out/'selected_pipelines.json').write_text(json.dumps(sorted(selected),indent=2),encoding='utf-8')
        search_jobs=[job(p,SPEC['budget'],(rule,cad,h),pipe)
            for p,pipe,rule,cad,h in product(SPEC['products'],sorted(selected),SPEC['amount_rules'],SPEC['cadences'],SPEC['reserve_headrooms'])]
        coarse=run(pool,search_jobs,'Reserve search')
        refinement=set()
        for pipe,p,score in product(sorted(selected),SPEC['products'],SCORES):
            w=best([r for r in coarse if r['product']==p and pipeline(r)==pipe],score)
            for delta in range(-SPEC['refinement_radius'],SPEC['refinement_radius']+1,SPEC['refinement_step']):
                h=w['headroom']+delta
                if h>=0:
                    refinement.update(job(prod,SPEC['budget'],(w['withdrawal'],w['cadence'],h),pipe) for prod in SPEC['products'])
        refined=run(pool,refinement,'Local refinement')
        search=[cache[j] for j in sorted(set(search_jobs)|refinement)]
        frontier=[]
        for p,seats,n,score in product(SPEC['products'],(True,False),SPEC['concurrency'],SCORES):
            w=best([r for r in search if r['product']==p and r['reserve_seats']==seats and r['concurrency']==n],score)
            frontier.append({**w,'objective':score})
        winner_rows=[{**best([r for r in search if r['product']==p and r['reserve_seats']==seats],score),'objective':score}
                     for p,seats,score in product(SPEC['products'],(True,False),SCORES)]
        sensitivity_jobs={job(r['product'],budget,policy(r),pipeline(r))
                          for r in winner_rows if r['reserve_seats'] for budget in SPEC['budget_sensitivity']}
        sensitivity=run(pool,sensitivity_jobs,'Budget sensitivity')

    csv_write(out/'all_settings.csv',[cache[j] for j in sorted(cache)])
    csv_write(out/'reserve_search.csv',search)
    csv_write(out/'frontier.csv',frontier)
    csv_write(out/'budget_sensitivity.csv',sensitivity)
    # Save detailed, independently replayed winners for both objectives and seat modes.
    for w in winner_rows:
        row,r=evaluate(w['job'],True)
        assert row=={k:v for k,v in w.items() if k!='objective'}
        folder=out/f"{w['product']}__{'shared_seats' if w['reserve_seats'] else 'evals_outside_cap'}__best_{w['objective']}"
        write_outputs(r,folder)
        csv_write(folder/'pipeline_daily.csv',r.acquisition.pipeline_daily)
        csv_write(folder/'replacement_waits.csv',replacement_records(r))
        csv_write(folder/'financing_events.csv',r.acquisition.financing_events)
        fields=('eval_id','started_at','state','months_paid','resets','trades_taken','passed_at','ended_at')
        csv_write(folder/'evaluations.csv',[{k:getattr(e,k) for k in fields} for e in r.acquisition.evaluations])
        (folder/'experiment.json').write_text(json.dumps({'run_config':to_payload(r.config),
            'acquisition':asdict(r.acquisition.policy)},indent=2),encoding='utf-8')
    study={'spec':SPEC,'anchors':anchors,'controls':controls,'unique_simulations':len(cache),
        'screening_rows':len(screen),'search_rows':len(search),'selected_pipelines':sorted(selected),
        'winners':winner_rows,'frontier':frontier,'budget_sensitivity':sensitivity,
        'generated_utc':datetime.now(timezone.utc).isoformat()}
    (out/'study.json').write_text(json.dumps(study,indent=2),encoding='utf-8')
    write_study_report(out,render(screen,search,frontier,anchors,controls,sensitivity))
    assert all(Path(f).is_file() and sha256_file(Path(f))==h for f,h in protected.items())
    (out/'preservation_check.json').write_text(json.dumps({'protected_files':len(protected),'all_unchanged':True},indent=2),encoding='utf-8')
    print(f'Completed {len(cache)} unique simulations; earlier results unchanged. {out}',flush=True)


if __name__=='__main__': main(*sys.argv[1:])
