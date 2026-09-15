"""Fixed daily-maximum reserve frontier and historical cold-start sensitivity."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import study_legacy_pipeline_capacity as prior
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.reserve_metrics import ReserveObserver
from pa_milky.simulator import run_book

SPEC_PATH = PROJECT_ROOT/'config/studies/legacy_reserve_frontier.json'
SPEC = TAPES = None


def initialize():
    global SPEC, TAPES
    prior.initialize()
    SPEC = json.loads(SPEC_PATH.read_text())
    TAPES = {}
    for window in SPEC['windows']:
        first, last = map(datetime.fromisoformat, (window['start'], window['end_exclusive']))
        # Never import a position entered before the new system existed, or
        # settle a position using an exit beyond the historical window.
        TAPES[window['name']] = [t for t in prior.sim.T if t.entry_at >= first and t.exit_at < last]


def grid():
    return sorted({h for low, high, step in SPEC['reserve_grid'].values()
                   for h in range(low, high+1, step)})


def jobs():
    return [(product, window['name'], headroom)
            for product in SPEC['pipelines'] for window in SPEC['windows']
            for headroom in sorted(set(grid()+(
                SPEC['full_tape_extra_reserves'] if window['name'] == 'full' else [])))]


def evaluate(job, detail=False):
    product, window, headroom = job
    pipe = SPEC['pipelines'][product]
    base = prior.sim.C[product]
    policy = WithdrawalPolicy(name=f'maximum_daily_headroom_{headroom}', cadence='daily',
        amount_rule='maximum', quantize_to_amount=False, terminal_withdrawal='firm_permitted',
        min_retained_balance_usd=base.trailing_floor_balance_usd+headroom)
    acquisition = AcquisitionPolicy('monthly_current_slot_replacements', *SPEC['budget'],
        max_live_accounts=20, spare_capacity=pipe['spares'],
        evaluation=EvaluationSpec(**prior.EVAL['evaluations'][product]),
        evaluations_at_once=pipe['concurrency'], persistent_demand=True,
        evaluation_start_interval_days=pipe['interval'], evaluations_reserve_seats=True,
        activate_on_first_check=True)
    tape = TAPES[window]
    first, last = min(t.entry_at for t in tape), max(t.exit_at for t in tape)
    observer = ReserveObserver(first, last, trace=detail)
    result = run_book(tape, replace(base, policy=policy), acquisition=acquisition, observer=observer)
    ledger = result.acquisition
    cash = ledger.summary()
    terminal = round(sum(e.received_usd for e in result.terminal_payouts), 2)
    cutoff = first+timedelta(days=SPEC['post_startup_days'])
    deaths = [a for a in result.accounts if a.died_at]
    activation_hours = [(e.ended_at-e.passed_at).total_seconds()/3600
                        for e in ledger.evaluations if e.state == 'funded']
    forfeits = Counter(e['kind'] for e in ledger.financing_events)
    assert Economics.measure(result).residual_usd == cash['cash_identity_residual_usd'] == 0
    assert cash['net_cash_created_usd'] == result.pocket_usd
    assert len(result.accounts)+result.unused_spares == cash['evaluations_activated']
    assert all(d['alive']+d['spares']+d['in_flight'] <= 20 for d in ledger.pipeline_daily)
    assert all(d['awaiting_activation'] == 0 for d in ledger.pipeline_daily)
    assert all(0 <= h <= 24 for h in activation_hours)
    row = {'product': product, 'window': window, 'headroom': headroom,
        'retained_balance_target': policy.min_retained_balance_usd,
        'first_entry': first.isoformat(), 'last_exit': last.isoformat(), 'trades': len(tape),
        'ongoing': round(result.pocket_usd-terminal, 2), 'terminal': terminal,
        'total': result.pocket_usd,
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
        'deaths_after_startup_year': sum(a.died_at >= cutoff for a in deaths),
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


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str)+'\n', encoding='utf-8')


def main():
    initialize()
    out = PROJECT_ROOT/SPEC['output']
    out.mkdir(parents=True, exist_ok=True)
    contract = {'schema': 'pa_milky.reserve_frontier.v1', 'spec': SPEC,
        'engine': engine_digest(), 'inputs': input_digest(prior.sim.C['legacy_25k']),
        'configs': {k: to_payload(v) for k, v in prior.sim.C.items()},
        'evaluation_spec': prior.EVAL,
        'runner_hashes': {str(p.relative_to(PROJECT_ROOT)): sha256_file(p) for p in
            [Path(__file__), Path(prior.__file__), Path(prior.sim.__file__), SPEC_PATH]},
        'protected_results': {str(p.relative_to(PROJECT_ROOT)): sha256_file(p)
            for p in (PROJECT_ROOT/'results').rglob('*') if p.is_file() and out not in p.parents}}
    contract_path = out/'contract.json'
    if contract_path.exists():
        if json.loads(contract_path.read_text()) != contract:
            raise ValueError('Resume refused: code, inputs, settings or protected results changed')
    else:
        write_json(contract_path, contract)

    # Re-run the inherited policy with the new option OFF to protect numerical
    # history. Compare any saved matching rows rather than assuming their presence.
    old = prior.read_rows('pipeline_capacity')
    controls = []
    for product, pipe in SPEC['pipelines'].items():
        for h in (6000, 6800, 8000):
            j = (product, *SPEC['budget'], 'maximum', 'daily', h, True,
                 pipe['interval'], pipe['concurrency'], pipe['spares'], True)
            saved = next((r for r in old if tuple(r['job']) == j), None)
            if saved is None:
                continue
            now = prior.evaluate(j)
            for key, value in saved.items():
                if key in now:
                    assert now[key] == value, (j, key, now[key], value)
            controls.append({'job': j, 'matching_fields': len(set(saved) & set(now))})
    print(f'Historical controls reproduced: {len(controls)}', flush=True)
    checkpoint = out/'checkpoint.jsonl'
    completed = {tuple(r['job']): r for r in
                 [json.loads(line) for line in checkpoint.read_text().splitlines()] } if checkpoint.exists() else {}
    requested = jobs()
    missing = [j for j in requested if j not in completed]
    with ProcessPoolExecutor(max_workers=SPEC['workers'], initializer=initialize) as pool:
        futures = {pool.submit(evaluate, j): j for j in missing}
        with checkpoint.open('a', encoding='utf-8') as log:
            for i, future in enumerate(as_completed(futures), 1):
                row = future.result()
                completed[tuple(row['job'])] = row
                log.write(json.dumps(row)+'\n')
                log.flush()
                if i % 20 == 0 or i == len(missing):
                    print(f'Frontier: {i}/{len(missing)} newly completed', flush=True)
    rows = [completed[j] for j in requested]
    prior.csv_write(out/'frontier.csv', rows)
    boundaries = []
    for product in SPEC['pipelines']:
        for window in SPEC['windows']:
            family = sorted((r for r in rows if r['product'] == product and r['window'] == window['name']),
                            key=lambda r: r['headroom'])
            row = {'product': product, 'window': window['name']}
            for key in ('deaths_after_startup_year', 'deaths_of_pas_at_least_one_year_old', 'deaths_2026_03_30'):
                row[key+'_stable_zero_from'] = next((r['headroom'] for i, r in enumerate(family)
                    if all(x[key] == 0 for x in family[i:])), None)
            best = max(family, key=lambda r: r['ongoing'])
            row.update(best_ongoing_headroom=best['headroom'], best_ongoing=best['ongoing'])
            boundaries.append(row)
    prior.csv_write(out/'boundaries.csv', boundaries)
    for product in SPEC['pipelines']:
        for h in (6700, 6780.10, 6780.11, 6800):
            row, result, observer = evaluate((product, 'full', h), detail=True)
            assert row == completed[(product, 'full', h)]
            folder = out/f'{product}__shared_seats__reserve_{h}'
            folder.mkdir(exist_ok=True)
            write_json(folder/'summary.json', row)
            prior.csv_write(folder/'march_trade_trace.csv', observer.trade_trace)
            prior.csv_write(folder/'replacement_waits.csv', replacement_records(result))
            prior.csv_write(folder/'deaths.csv', [{k: v for k, v in asdict(a).items() if k != 'day_pnl_usd'} for a in result.dead])
            prior.csv_write(folder/'evaluations.csv', [asdict(e) for e in result.acquisition.evaluations])
            prior.csv_write(folder/'pipeline_daily.csv', result.acquisition.pipeline_daily)
    assert all(sha256_file(PROJECT_ROOT/p) == digest for p, digest in contract['protected_results'].items())
    write_json(out/'study.json', {'spec': SPEC, 'rows': rows, 'boundaries': boundaries})
    write_json(out/'AUDIT.json', {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'runs': len(rows), 'historical_controls': controls,
        'protected_files_unchanged': len(contract['protected_results']),
        'all_economic_and_cap_checks_passed': True,
        'detail_replays_matched': 8, 'contract_sha256': sha256_file(contract_path)})
    print(f'Complete: {out}', flush=True)


if __name__ == '__main__':
    main()
