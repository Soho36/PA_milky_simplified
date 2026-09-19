"""Blocked PA copying with inherited evaluation supply; checkpointed staged search."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.loader import load_tape
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from report_names import write_study_report
from study_legacy_pipeline_capacity import csv_write, pipeline_label
from study_legacy_routing import write_csv, account_rows

SPEC_PATH = PROJECT_ROOT/'config/studies/legacy_25k_blocked_pipeline.json'
SPEC = BASE = EVAL = TAPES = None
SCORES = ('ongoing', 'total')
ORIGINAL = (False, 0, 5, 5, True)


def initialize():
    global SPEC, BASE, EVAL, TAPES
    SPEC = json.loads(SPEC_PATH.read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT/SPEC['scenario'])
    EVAL = json.loads((PROJECT_ROOT/SPEC['evaluation_spec']).read_text(encoding='utf-8'))
    tape = load_tape(BASE)
    TAPES = {year:[t for t in tape if t.entry_at.year >= year]
             for year in [2020]+SPEC['transfer_starts']}


def job(pol, pipe, mode='blocked', year=2020, budget=None):
    return (mode, year, *(budget or SPEC['budget']), *pol, *pipe)


def policy(r):
    return (r['withdrawal'], r['cadence'], r['headroom'], r['amount'])


def pipeline(r):
    return (r['persistent'], r['interval'], r['concurrency'], r['spares'], r['reserve_seats'])


def best(rows, score):
    return min(rows, key=lambda r:(-r[score], -r['total' if score=='ongoing' else 'ongoing'],
                                  r['spend'], r['headroom'], tuple(r['job'])))


def evaluate(j, detail=False):
    mode, year, initial, monthly, rule, cadence, h, amount, persistent, interval, n, spares, seats = j
    pol = WithdrawalPolicy(name=f'{rule}_{amount}_{cadence}_h{h}', cadence=cadence,
        amount_rule=rule, amount_usd=amount, shortfall='accrue_backlog' if rule=='fixed' else 'skip',
        quantize_to_amount=False, terminal_withdrawal='firm_permitted',
        min_retained_balance_usd=BASE.trailing_floor_balance_usd+h)
    acq = AcquisitionPolicy('monthly_current_slot_replacements', initial, monthly,
        max_live_accounts=20, spare_capacity=spares,
        evaluation=EvaluationSpec(**EVAL['evaluations']['legacy_25k']), evaluations_at_once=n,
        persistent_demand=persistent, evaluation_start_interval_days=interval,
        evaluations_reserve_seats=seats)
    tape = TAPES[year]
    r = run_book(tape, replace(BASE, policy=pol, expected_trades=len(tape)), acquisition=acq,
                 routing=RoutingPolicy(mode='blocked') if mode=='blocked' else None)
    cash = r.acquisition.summary()
    econ = Economics.measure(r)
    assert econ.residual_usd == cash['cash_identity_residual_usd'] == 0
    assert cash['net_cash_created_usd'] == r.pocket_usd
    assert len(r.accounts)+r.unused_spares == cash['evaluations_activated']
    assert round(cash['evaluation_fees_usd']+cash['activation_fees_usd'], 2) == r.total_purchase_cost_usd
    assert min(e['cash_after_usd'] for e in r.acquisition.cash_events) >= 0
    assert all(d['alive']+d['spares']+(d['in_flight'] if seats else 0)<=20
               and d['subscriptions']<=n for d in r.acquisition.pipeline_daily)
    terminal = round(sum(e.received_usd for e in r.terminal_payouts), 2)
    row = dict(job=list(j), mode=mode, start_year=year, initial_cash=initial, monthly_funding=monthly,
        withdrawal=rule, cadence=cadence, headroom=h, amount=amount, retained_balance=pol.min_retained_balance_usd,
        persistent=persistent, interval=interval, concurrency=n, spares=spares, reserve_seats=seats,
        ongoing=round(r.pocket_usd-terminal,2), terminal=terminal, total=r.pocket_usd,
        accounts=len(r.accounts), alive=r.alive_at_horizon, receipts=r.total_received_usd,
        activated=cash['evaluations_activated'], evaluations=cash['evaluations_started'],
        evaluation_months=cash['evaluation_months_paid'], evaluation_fees=cash['evaluation_fees_usd'],
        activation_fees=cash['activation_fees_usd'], spend=r.total_purchase_cost_usd,
        ending_cash=cash['ending_owner_cash_usd'], contributions=cash['owner_contributions_usd'],
        spares_at_end=r.unused_spares, in_flight_at_end=len(r.acquisition.active),
        copies=sum(a.trades_taken for a in r.accounts), signals_loaded=len(tape),
        economics=econ.to_payload(), **measure_pipeline(r))
    if mode=='blocked':
        row.update(signals_executed=sum(bool(f['accounts']) for f in r.routing_fills),
            zero_live_signals=sum(f['alive']==0 for f in r.routing_fills),
            allocation_sha256=r.routing['allocation_sha256'])
        assert row['copies'] == r.copies_filled
    return (row,r) if detail else row


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def export(out, label, row):
    actual, r = evaluate(tuple(row['job']), True)
    assert actual == row
    folder = out/label; folder.mkdir(exist_ok=True)
    json_write(folder/'summary.json', {'row':row, 'config':to_payload(r.config),
                                     'acquisition':asdict(r.acquisition.policy)})
    write_csv(folder/'accounts.csv', account_rows(r))
    write_csv(folder/'payouts.csv', [asdict(e) for e in r.payouts])
    write_csv(folder/'cash.csv', r.acquisition.cash_events)
    write_csv(folder/'pipeline_daily.csv', r.acquisition.pipeline_daily)
    write_csv(folder/'replacement_waits.csv', replacement_records(r))
    write_csv(folder/'financing_events.csv', r.acquisition.financing_events)
    write_csv(folder/'blocked_fills.csv', [{**f, 'accounts':';'.join(map(str,f['accounts']))} for f in r.routing_fills])
    fields = ('eval_id','started_at','state','months_paid','resets','trades_taken','passed_at','ended_at')
    write_csv(folder/'evaluations.csv', [{k:getattr(e,k) for k in fields} for e in r.acquisition.evaluations])


def table(rows):
    text = '| Case | Pipeline | Withdrawal / reserve | Ongoing | Closing | Total | Funded / deaths | Copies | Coverage |\n'
    text += '|---|---|---|---:|---:|---:|---:|---:|---:|\n'
    for r in rows:
        coverage = f"{r['signals_executed']/r['signals_loaded']:.2%}" if 'signals_executed' in r else 'n/a'
        text += (f"| {r.get('label',r['mode'])} | {pipeline_label(r)} | {r['withdrawal']} "
                 f"{r['amount'] or ''} / {r['cadence']} / ${r['retained_balance']:,.0f} | "
                 f"${r['ongoing']:,.2f} | ${r['terminal']:,.2f} | ${r['total']:,.2f} | "
                 f"{r['accounts']} / {r['deaths']} | {r['copies']:,} | {coverage} |\n")
    return text+'\n'


def render(data):
    screen, search = data['screen'], data['search']
    text = ('# Blocked copying with evaluation supply\n\n'
        '**Legacy25K; $1,000 initial + $200/month; January 2020–July 2026.** '
        'One MNQ per free funded account; occupied accounts skip new setups. '
        'No free starting PAs: every funded account must pass an evaluation and pay activation. '
        'Same evaluation model as the earlier pipeline-capacity study: 3 MNQ, $1,500 target/drawdown, '
        '$33 per subscription month and $125 activation. These are inherited study assumptions, not newly verified firm terms.\n\n'
        'Main capacity: live PAs + activated spares + in-flight evaluations <=20. '
        'The separate outside-cap sensitivity excludes evaluations only. Concurrency is 2/5/10/20; '
        'launches batch/one per day/one per seven days; spare targets 0/2/5/10. '
        'Current-slot monthly growth/replacement demand is held fixed; missed growth demand either expires '
        'or persists as a FIFO queue. Death replacements have priority. Renewals, failed evaluations, '
        'cash shortages, pass delays and dormant activated spares all cost time or money.\n\n'
        '## Frozen aggressive policy: supply impact\n\n'
        'The instant-supply current-slot + maximum-weekly co-winner retained $25,100, started with one '
        'paid PA, and produced **$665,420.55**, 531 purchases and 511 deaths. '
        'The evaluation rows below retain its withdrawal and current-slot purchase rules. '
        'They change procurement fees, lead time and initial inventory; persistent rows additionally change '
        'how missed monthly orders are carried forward. This is a combined supply-scenario comparison, '
        'not an attribution to delay alone.\n\n')
    frozen = [r for r in screen if policy(r)==tuple(SPEC['anchors']['blocked_instant_maximum'])]
    rows = [{**next(r for r in frozen if pipeline(r)==ORIGINAL), 'label':'original supply'}]
    rows += [{**best([r for r in frozen if r['reserve_seats']==s], 'total'),
              'label':'best frozen / '+('shared' if s else 'outside cap')} for s in (True,False)]
    text += table(rows)
    text += '## Retuned winners\n\n'+table(data['winners'])
    text += '## Same supply and withdrawals, changing only PA blocking\n\n'+table(data['paired'])
    text += ('Rows are frozen-policy replays, not separately optimized unrestricted winners. '
        'Evaluation outcomes use the same one-position engine in both arms; resulting procurement and '
        'funding decisions remain endogenous to PA receipts and deaths.\n\n'
        '## Replacement service at the selected winners\n\n'
        '| Case | Next-check replacement | Resolved wait median / p95 days | Unresolved deaths | Unfilled account-days | Mean live | Zero-live days | Eval / activation fees |\n'
        '|---|---:|---:|---:|---:|---:|---:|---:|\n')
    for r in data['winners']:
        service = f"{r['next_check_service']:.1%}" if r['next_check_service'] is not None else 'n/a'
        text += (f"| {r['label']} | {service} | {r['replacement_wait_median_days']} / {r['replacement_wait_p95_days']} | "
                 f"{r['replacements_unfilled']} | {r['unfilled_account_days']:,.1f} | {r['average_live_accounts']} | "
                 f"{r['zero_live_days']} | ${r['evaluation_fees']:,.0f} / ${r['activation_fees']:,.0f} |\n")
    text += '\nZero-live days includes startup. Wait percentiles cover completed replacements; unresolved deaths remain censored through the horizon.\n\n'
    text += '## Frozen main-winner budget and starting-date transfers\n\n'+table(data['transfers'])
    text += (f"## Search and validation\n\n{len(screen):,} blocked screening rows across four frozen policies and 192 pipelines; "
        f"{len(data['selected_pipelines'])} nominated pipelines; {len(search):,} coarse/refined search settings. "
        'For each seat mode and concurrency, both cash leaders nominate a pipeline; the original pipeline is always retained. '
        'Each selected pipeline gets minimum/maximum/fixed-$1,500 monthly-accrual backlog withdrawals at three check cadences '
        'and the configured reserve grid. Local reserve refinement holds pipeline and withdrawal family fixed. '
        'An entire paired unrestricted screen supplies the same-policy execution control. '
        'This is a staged best-tested search, not an exhaustive optimum over all pipelines and policies. '
        'Other acquisition families, contract sizing, launch phases and signal filters are not optimized.\n\n'
        'Net cash subtracts every evaluation and activation fee and excludes owner contributions. Ongoing excludes the '
        'single permitted terminal payout; total includes it. Terminal cash is not recurring income. '
        'All runs reconcile cash, P&L, fees and seat caps; selected winners have full ledgers and entry allocations. '
        'Historical controls replay both previous engines. Transfers overlap the selection history and are not unseen validation. '
        'Evaluations share one historical tape, not independent pass-rate draws. Exported trade extrema are booked at exits; '
        'pending-order reservations and payment-processing delays are not modeled.\n')
    return text


def main():
    initialize()
    out = PROJECT_ROOT/SPEC['output']; out.mkdir(parents=True, exist_ok=True)
    prior_roots = [PROJECT_ROOT/'results/legacy_25k/blocked_optimization',
                   PROJECT_ROOT/'results/comparisons/legacy_25k_vs_50k/pipeline_capacity']
    protected = {str(p.relative_to(PROJECT_ROOT)):sha256_file(p)
                 for root in prior_roots for p in root.rglob('*') if p.is_file()}
    contract = dict(spec=SPEC, evaluation_spec=EVAL, config=to_payload(BASE), engine=engine_digest(),
        inputs=input_digest(BASE), runner_sha256=sha256_file(Path(__file__)), protected=protected,
        helpers={name:sha256_file(PROJECT_ROOT/'scripts'/name) for name in
                 ('study_legacy_pipeline_capacity.py','study_legacy_routing.py')})
    cp = out/'contract.json'
    if cp.exists():
        assert json.loads(cp.read_text(encoding='utf-8'))==contract, 'Contract changed; use a new output directory'
    else:
        json_write(cp,contract)
    checkpoint = out/'checkpoint.jsonl'
    cache = {tuple(r['job']):r for r in map(json.loads,checkpoint.read_text().splitlines())} if checkpoint.exists() else {}

    def run(pool, jobs, label):
        jobs = sorted(set(jobs)); missing = [j for j in jobs if j not in cache]
        print(f'{label}: {len(missing)} new / {len(jobs)}', flush=True)
        with checkpoint.open('a',encoding='utf-8') as f:
            futures = [pool.submit(evaluate,j) for j in missing]
            for i,future in enumerate(as_completed(futures),1):
                row = future.result(); cache[tuple(row['job'])]=row
                f.write(json.dumps(row)+'\n'); f.flush()
                if i%50==0 or i==len(missing): print(f'{label}: {i}/{len(missing)}',flush=True)
        return [cache[j] for j in jobs]

    # Reproduce one instant co-winner and both former shared-capacity objectives.
    import optimize_blocked_copying as old
    old.initialize()
    instant = old.evaluate(old.job('monthly_current_slot_replacements',1,'maximum','weekly',0))
    stored = [json.loads(s) for s in (prior_roots[0]/'checkpoint.jsonl').read_text().splitlines()]
    assert instant == next(r for r in stored if r['job']==instant['job'])
    import study_legacy_pipeline_capacity as previous
    previous.initialize()
    historical = json.loads((prior_roots[1]/'study.json').read_text())
    controls = [instant]
    for w in historical['winners']:
        if w['product']=='legacy_25k' and w['reserve_seats']:
            row = previous.evaluate(w['job'])
            assert row == {k:v for k,v in w.items() if k!='objective'}
            new = evaluate(job((*previous.policy(w),0), previous.pipeline(w), mode='unrestricted',
                               budget=[w['initial_cash'],w['monthly_funding']]))
            assert all(new[k]==row[k] for k in ('total','ongoing','accounts','alive','spend','deaths'))
            controls.append(row)
    print('Three historical controls reproduced; new supply evaluator matches both prior winners.',flush=True)
    pipes = list(product(SPEC['persistent_demand'],SPEC['start_intervals_days'],SPEC['concurrency'],SPEC['spares'],(True,False)))
    screen_jobs = [job(tuple(pol),pipe) for pol,pipe in product(SPEC['anchors'].values(),pipes)]
    with ProcessPoolExecutor(max_workers=SPEC['workers'],initializer=initialize) as pool:
        screen = run(pool,screen_jobs,'Frozen blocked policies')
        unrestricted_screen = run(pool,[('unrestricted',*j[1:]) for j in screen_jobs],'Matched unrestricted screen')
        selected = {ORIGINAL}
        for seats,n,score in product((True,False),SPEC['concurrency'],SCORES):
            selected.add(pipeline(best([r for r in screen if r['reserve_seats']==seats and r['concurrency']==n],score)))
        coarse_jobs = [job((rule,cad,h,amount),pipe) for pipe,(rule,amount),cad,h in
                       product(sorted(selected),SPEC['amounts'],SPEC['cadences'],SPEC['headrooms'])]
        coarse = run(pool,coarse_jobs,'Withdrawal search')
        refined_jobs = set()
        for pipe,(rule,amount),cad,score in product(sorted(selected),SPEC['amounts'],SPEC['cadences'],SCORES):
            w = best([r for r in coarse if pipeline(r)==pipe and (r['withdrawal'],r['amount'],r['cadence'])==(rule,amount,cad)],score)
            for delta in range(-SPEC['refinement_radius'],SPEC['refinement_radius']+1,SPEC['refinement_step']):
                h = w['headroom']+delta
                if 0<=h<=max(SPEC['headrooms']): refined_jobs.add(job((rule,cad,h,amount),pipe))
        run(pool,refined_jobs,'Local refinement')
        search = [cache[j] for j in sorted(set(coarse_jobs)|refined_jobs|set(screen_jobs))]
        winners = [{**best([r for r in search if r['reserve_seats']==s],score),
                    'label':f"{'shared' if s else 'outside cap'} / {score}"} for s,score in product((True,False),SCORES)]
        paired_raw = run(pool,[('unrestricted',*w['job'][1:]) for w in winners],'Winner execution controls')
        paired = [{**r,'label':'unrestricted / '+('shared' if r['reserve_seats'] else 'outside cap')} for r in paired_raw]
        transfer_jobs = set()
        for w in winners:
            if not w['reserve_seats']: continue
            transfer_jobs.update(job(policy(w),pipeline(w),year=y) for y in SPEC['transfer_starts'])
            transfer_jobs.update(job(policy(w),pipeline(w),budget=b) for b in SPEC['transfer_budgets'])
        transfers = [{**r,'label':f"{r['start_year']} / ${r['initial_cash']}+${r['monthly_funding']}/mo"}
                     for r in run(pool,transfer_jobs,'Frozen transfers')]
    details = []
    for i,w in enumerate(winners,1):
        label=f'winner_{i}'; export(out,label,{k:v for k,v in w.items() if k!='label'}); details.append(label)
    for i,s in enumerate((True,False),1):
        w=best([r for r in screen if r['reserve_seats']==s and policy(r)==tuple(SPEC['anchors']['blocked_instant_maximum'])],'total')
        label=f'frozen_aggressive_{i}'; export(out,label,w); details.append(label)
    data = dict(spec=SPEC, controls=controls, screen=screen, unrestricted_screen=unrestricted_screen,
        search=search, coarse_jobs=coarse_jobs, refined_jobs=sorted(refined_jobs), selected_pipelines=sorted(selected),
        winners=winners, paired=paired, transfers=transfers, details=details, unique_simulations=len(cache),
        contract_sha256=sha256_file(cp), generated_utc=datetime.now(timezone.utc).isoformat())
    for name,rows in [('all_settings',list(cache.values())),('screening',screen),('unrestricted_screen',unrestricted_screen),
                      ('winners',winners),('transfers',transfers)]: csv_write(out/f'{name}.csv',rows)
    json_write(out/'study.json',data)
    write_study_report(out,render(data))
    assert all(sha256_file(PROJECT_ROOT/p)==h for p,h in protected.items())
    json_write(out/'preservation_check.json',{'files':len(protected),'all_unchanged':True})
    print(f'Completed {len(cache)} unique simulations: {out}',flush=True)


if __name__=='__main__':
    main()
