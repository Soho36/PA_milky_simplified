"""Paired daily-minimum/maximum reserve curves with fixed evaluation supply."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import study_legacy_reserve_frontier as reference
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.dispersion_metrics import DispersionObserver
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.simulator import run_book

SPEC_PATH = PROJECT_ROOT/'config/studies/legacy_minimum_reserve_frontier.json'
SPEC = None


def initialize():
    global SPEC
    reference.initialize()
    SPEC = json.loads(SPEC_PATH.read_text())
    assert PROJECT_ROOT/SPEC['reference_spec'] == reference.SPEC_PATH


def grid():
    return sorted(set(SPEC['extra_reserves']) | {n for lo, hi, step in SPEC['reserve_ranges']
                                                for n in range(lo, hi+1, step)})


def jobs():
    return [(p, w['name'], rule, h) for p in reference.SPEC['pipelines']
            for w in reference.SPEC['windows'] for rule in SPEC['amount_rules'] for h in grid()]


def evaluate(job, detail=False):
    product, window, rule, headroom = job
    pipe = reference.SPEC['pipelines'][product]
    base = reference.prior.sim.C[product]
    policy = WithdrawalPolicy(name=f'{rule}_daily_headroom_{headroom}', cadence='daily',
        amount_rule=rule, quantize_to_amount=False, terminal_withdrawal='firm_permitted',
        min_retained_balance_usd=base.trailing_floor_balance_usd+headroom)
    acquisition = AcquisitionPolicy(reference.prior.ACQ, *reference.SPEC['budget'],
        max_live_accounts=20, spare_capacity=pipe['spares'],
        evaluation=EvaluationSpec(**reference.prior.EVAL['evaluations'][product]),
        evaluations_at_once=pipe['concurrency'], persistent_demand=True,
        evaluation_start_interval_days=pipe['interval'], evaluations_reserve_seats=True,
        activate_on_first_check=True)
    tape = reference.TAPES[window]
    first, last = min(t.entry_at for t in tape), max(t.exit_at for t in tape)
    observer = DispersionObserver(first, last, trace=detail)
    result = run_book(tape, replace(base, policy=policy), acquisition=acquisition, observer=observer)
    ledger = result.acquisition
    cash = ledger.summary()
    terminal = round(sum(p.received_usd for p in result.terminal_payouts), 2)
    assert Economics.measure(result).residual_usd == cash['cash_identity_residual_usd'] == 0
    assert cash['net_cash_created_usd'] == result.pocket_usd
    assert len(result.accounts)+result.unused_spares == cash['evaluations_activated']
    assert all(d['alive']+d['spares']+d['in_flight'] <= 20 for d in ledger.pipeline_daily)
    assert all(d['awaiting_activation'] == 0 for d in ledger.pipeline_daily)
    activation_hours = [(e.ended_at-e.passed_at).total_seconds()/3600
                        for e in ledger.evaluations if e.state == 'funded']
    assert all(0 <= h <= 24 for h in activation_hours)
    forfeits = Counter(e['kind'] for e in ledger.financing_events)
    deaths = result.dead
    row = {'product': product, 'window': window, 'withdrawal': rule, 'headroom': headroom,
        'retained_balance_target': policy.min_retained_balance_usd,
        'first_entry': first.isoformat(), 'last_exit': last.isoformat(), 'trades': len(tape),
        'ongoing': round(result.pocket_usd-terminal, 2), 'terminal': terminal, 'total': result.pocket_usd,
        'ongoing_received_after_split': round(result.total_received_usd-terminal, 2),
        'terminal_profit_equity_before_withdrawal': result.equity_at_horizon_usd,
        'accounts': len(result.accounts), 'alive': result.alive_at_horizon,
        'evaluations': len(ledger.evaluations), 'evaluation_months': cash['evaluation_months_paid'],
        'evaluation_resets': sum(e.resets for e in ledger.evaluations),
        'evaluation_fees': ledger.evaluation_fees_usd, 'activation_fees': ledger.activation_fees_usd,
        'spend': result.total_purchase_cost_usd, 'contributions': ledger.contributed_usd,
        'ending_owner_cash': ledger.cash_usd, 'spares_at_end': ledger.spares,
        'passes_forfeited_cash': forfeits['pass_forfeited_cash'],
        'passes_forfeited_capacity': forfeits['pass_forfeited_capacity'],
        'max_pass_to_activation_hours': round(max(activation_hours, default=0), 4),
        'passes_awaiting_first_check_at_horizon': sum(e.state == 'passed' for e in ledger.active),
        'deaths_after_startup_year': sum(a.died_at >= first+timedelta(days=365) for a in deaths),
        'deaths_of_pas_at_least_one_year_old': sum((a.died_at-a.activated_at).days >= 365 for a in deaths),
        'mature_pa_days': round(sum(max(0, (min(last, a.died_at or last)-
            max(first, a.activated_at+timedelta(days=365))).total_seconds()/86400)
            for a in result.accounts), 2),
        'deaths_after_two_years': sum(a.died_at >= first+timedelta(days=730) for a in deaths)
            if last > first+timedelta(days=730) else None,
        'deaths_2026_03_30': sum(a.died_at.date().isoformat() == '2026-03-30' for a in deaths),
        'last_death': max((a.died_at.isoformat() for a in deaths), default=None),
        'largest_simultaneous_deaths': max(Counter(a.died_at for a in deaths).values(), default=0),
        **measure_pipeline(result), **observer.summary(), 'job': list(job)}
    return (row, result, observer) if detail else row


def outputs(out, rows):
    write = reference.prior.csv_write
    write(out/'frontier.csv', rows)
    lookup = {tuple(r['job']): r for r in rows}
    paired = []
    for a in rows:
        if a['withdrawal'] != 'minimum':
            continue
        b = lookup[(a['product'], a['window'], 'maximum', a['headroom'])]
        r = {k: a[k] for k in ('product', 'window', 'headroom')}
        for key in ('ongoing', 'total', 'terminal', 'deaths', 'alive', 'unfilled_account_days',
                    'average_retained_profit_per_live_pa', 'average_retained_profit_book',
                    'frozen_mean_balance_std_usd', 'largest_simultaneous_deaths'):
            r['minimum_'+key], r['maximum_'+key] = a[key], b[key]
            r['minimum_minus_maximum_'+key] = round(a[key]-b[key], 4) if a[key] is not None and b[key] is not None else None
        paired.append(r)
    write(out/'matched_reserves.csv', paired)
    families = {}
    for r in rows:
        families.setdefault((r['product'], r['window'], r['withdrawal']), []).append(r)
    summaries, capital = [], []
    for (product, window, rule), family in families.items():
        family.sort(key=lambda r: r['headroom'])
        best_cash = max(family, key=lambda r: (r['ongoing'], r['total'], -r['headroom']))
        best_total = max(family, key=lambda r: (r['total'], r['ongoing'], -r['headroom']))
        boundary = next((r for i, r in enumerate(family) if r['mature_pa_days'] > 0 and
            all(x['deaths_of_pas_at_least_one_year_old'] == 0 and x['mature_pa_days'] > 0 for x in family[i:])), None)
        summaries.append({'product': product, 'window': window, 'withdrawal': rule,
            'best_ongoing_headroom': best_cash['headroom'], 'best_ongoing': best_cash['ongoing'],
            'best_ongoing_alive': best_cash['alive'], 'best_ongoing_deaths': best_cash['deaths'],
            'best_total_headroom': best_total['headroom'], 'best_total': best_total['total'],
            'aged_pa_survival_boundary': boundary['headroom'] if boundary else None,
            'mature_pa_days_at_boundary': boundary['mature_pa_days'] if boundary else None,
            'all_deaths_at_boundary': boundary['deaths'] if boundary else None,
            'reserves_within_one_pct_best_ongoing': [r['headroom'] for r in family
                if best_cash['ongoing'] > 0 and r['ongoing'] >= .99*best_cash['ongoing']]})
        if rule != 'minimum':
            continue
        candidates = families[(product, window, 'maximum')]
        for a in family:
            keys = ('average_retained_profit_per_live_pa', 'average_retained_profit_book')
            if any(a[k] is None or a[k] <= 0 for k in keys):
                continue
            usable = [b for b in candidates if all(b[k] is not None and b[k] > 0 for k in keys)]
            if not usable:
                continue
            b = min(usable, key=lambda b: (sum(abs(b[k]-a[k])/a[k] for k in keys), b['headroom']))
            gaps = [abs(b[k]-a[k])/a[k] for k in keys]
            capital.append({'product': product, 'window': window, 'minimum_reserve': a['headroom'],
                'maximum_reserve': b['headroom'], 'per_pa_capital_gap_pct': round(gaps[0]*100, 3),
                'book_capital_gap_pct': round(gaps[1]*100, 3),
                'within_tolerance': max(gaps) <= SPEC['capital_match_tolerance_fraction'],
                'minimum_ongoing': a['ongoing'], 'maximum_ongoing': b['ongoing'],
                'minimum_total': a['total'], 'maximum_total': b['total'],
                'minimum_alive': a['alive'], 'maximum_alive': b['alive'],
                'minimum_deaths': a['deaths'], 'maximum_deaths': b['deaths'],
                'minimum_frozen_std': a['frozen_mean_balance_std_usd'],
                'maximum_frozen_std': b['frozen_mean_balance_std_usd'],
                'minimum_per_pa_capital': a[keys[0]], 'maximum_per_pa_capital': b[keys[0]],
                'minimum_book_capital': a[keys[1]], 'maximum_book_capital': b[keys[1]]})
    write(out/'window_summaries.csv', summaries)
    write(out/'similar_capital.csv', capital)
    reference.write_json(out/'study.json', {'spec': SPEC, 'reference_spec': reference.SPEC,
        'rows': rows, 'window_summaries': summaries, 'similar_capital': capital})
    selected = {tuple(max(family, key=lambda r: (r[score], r['ongoing']))['job'])
                for (p, w, rule), family in families.items() if w == 'full' for score in ('ongoing', 'total')}
    selected |= {(p, 'full', rule, h) for p in reference.SPEC['pipelines']
                 for rule in SPEC['amount_rules'] for h in (6700, 6800, 7100, 7500)}
    for job in sorted(selected):
        row, result, observer = evaluate(job, True)
        assert row == lookup[job]
        folder = out/f'{job[0]}__{job[2]}__reserve_{job[3]}'
        folder.mkdir(exist_ok=True)
        reference.write_json(folder/'summary.json', row)
        reference.write_json(folder/'march30_balances.json', observer.snapshots)
        write(folder/'march_trade_trace.csv', observer.trade_trace)
        write(folder/'replacement_waits.csv', replacement_records(result))
        write(folder/'pipeline_daily.csv', result.acquisition.pipeline_daily)
        write(folder/'deaths.csv', [{'account_id': a.account_id, 'activated_at': a.activated_at,
            'died_at': a.died_at, 'trade': a.death_trade_key, 'death_equity': a.death_equity_usd,
            'reason': a.death_reason} for a in result.dead])
    return len(selected)


def main():
    initialize()
    out = PROJECT_ROOT/SPEC['output']
    out.mkdir(parents=True, exist_ok=True)
    files = [Path(__file__), SPEC_PATH, reference.SPEC_PATH, Path(reference.__file__),
             Path(reference.prior.__file__), Path(reference.prior.sim.__file__)]
    contract = {'schema': 'pa_milky.minimum_frontier.v1', 'spec': SPEC,
        'reference_spec': reference.SPEC, 'engine': engine_digest(),
        'inputs': input_digest(reference.prior.sim.C['legacy_25k']),
        'configs': {k: to_payload(v) for k, v in reference.prior.sim.C.items()},
        'evaluation_spec': reference.prior.EVAL,
        'runner_hashes': {str(p.relative_to(PROJECT_ROOT)): sha256_file(p) for p in files},
        'protected_results': {str(p.relative_to(PROJECT_ROOT)): sha256_file(p)
            for p in (PROJECT_ROOT/'results').rglob('*') if p.is_file() and out not in p.parents
            and p.name != 'START_HERE.txt'}}
    path = out/'contract.json'
    if path.exists():
        if json.loads(path.read_text()) != contract:
            raise ValueError('Resume refused: experiment contract changed')
    else:
        reference.write_json(path, contract)
    prior_rows = reference.prior.read_rows('reserve_frontier')
    historical = {tuple(r['job']): r for r in prior_rows}
    march_rows = json.loads((reference.prior.ROOT/'march_failure_review/baselines.json').read_text())
    checkpoint = out/'checkpoint.jsonl'
    completed = {tuple(r['job']): r for r in
        (json.loads(line) for line in checkpoint.read_text().splitlines())} if checkpoint.exists() else {}
    all_jobs = jobs()
    missing = [j for j in all_jobs if j not in completed]
    print(f'Paired frontier: {len(all_jobs)} settings; {len(missing)} remaining', flush=True)
    with ProcessPoolExecutor(max_workers=SPEC['workers'], initializer=initialize) as pool:
        pending = {pool.submit(evaluate, j): j for j in missing}
        with checkpoint.open('a', encoding='utf-8') as log:
            for i, future in enumerate(as_completed(pending), 1):
                row = future.result()
                completed[tuple(row['job'])] = row
                log.write(json.dumps(row)+'\n')
                log.flush()
                if i % 40 == 0 or i == len(missing):
                    print(f'Completed {i}/{len(missing)} new runs', flush=True)
    rows = [completed[j] for j in all_jobs]
    comparisons = []
    for r in rows:
        prior_key = (r['product'], r['window'], r['headroom'])
        if r['withdrawal'] == 'maximum' and prior_key in historical:
            old = historical[prior_key]
            keys = (set(r) & set(old))-{'job'}
            assert all(r[k] == old[k] for k in keys), (r['job'], {k: (r[k], old[k]) for k in keys if r[k] != old[k]})
            comparisons.append({'job': r['job'], 'matching_fields': len(keys)})
        if r['window'] == 'full':
            for old in march_rows:
                if old['first_check'] and 'winner' not in old['label'] and (
                    old['product'], old['rule'], old['reserve']) == (r['product'], r['withdrawal'], r['headroom']):
                    assert (r['ongoing'], r['total'], r['accounts'], r['alive']) == (
                        old['ongoing'], old['total'], old['accounts'], old['alive_at_end'])
    details = outputs(out, rows)
    assert all(sha256_file(PROJECT_ROOT/p) == digest for p, digest in contract['protected_results'].items())
    reference.write_json(out/'AUDIT.json', {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'runs': len(rows), 'maximum_controls': comparisons, 'detail_replays_matched': details,
        'prior_result_files_unchanged': len(contract['protected_results']),
        'all_cash_and_capacity_checks_passed': True, 'contract_sha256': sha256_file(path)})
    print(f'Complete: {out}', flush=True)


if __name__ == '__main__':
    main()
