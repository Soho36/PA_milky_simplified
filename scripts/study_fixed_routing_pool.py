"""Fixed strategy-copy demand with shared, incrementally replenished capacity."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path

from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import input_digest, engine_digest, sha256_file
from pa_milky.routing import capacity_audit
from pa_milky.routing_study import fixed_pool_run, funding_requirements, measure, demand_digest
from study_legacy_routing import write_csv, account_rows

PROFILE = BASE = TAPE = OUT = None


def initialize(path):
    global PROFILE, BASE, TAPE, OUT
    PROFILE = json.loads(Path(path).read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT / PROFILE['scenario'])
    TAPE = load_tape(BASE)
    OUT = PROJECT_ROOT / PROFILE['output']


def run_case(job):
    year, copies, withdrawal = job
    tape = [t for t in TAPE if t.entry_at.year >= year]
    seats = copies * PROFILE['capacity_per_copy']
    config = replace(BASE, expected_trades=len(tape), policy=WithdrawalPolicy(
        name=f"{withdrawal['amount_rule']}_{withdrawal['cadence']}_{withdrawal['retained_balance_usd']}",
        amount_rule=withdrawal['amount_rule'], cadence=withdrawal['cadence'],
        min_retained_balance_usd=withdrawal['retained_balance_usd'],
        quantize_to_amount=False, terminal_withdrawal='firm_permitted'))
    case = f'{year}_R{copies}_{config.policy.name}'
    folder = OUT / case
    folder.mkdir(parents=True, exist_ok=True)
    demand = [copies] * len(tape)
    write_csv(folder / 'demand.csv', [{'trade_key': t.trade_key, 'entry_at': t.entry_at,
                                     'exit_at': t.exit_at, 'copies': copies} for t in tape])
    rows = []
    for allocation in PROFILE['allocations']:
        result, plan = fixed_pool_run(tape, config, copies=copies, allocation=allocation,
                                      initial_seats=seats, max_live_accounts=PROFILE['max_live_accounts'])
        start = datetime.fromisoformat(plan.purchase_events[0]['at'])
        seed = seats * config.purchase_fee_usd
        financing = funding_requirements(result, plan, [(start, seed)])
        row = measure(result, plan.peak_live)
        row.update(case=case, start_year=year, R=copies, initial_seats=seats,
                   max_live_accounts=PROFILE['max_live_accounts'], arm=allocation,
                   procurement='fixed_pool', withdrawal=config.policy.name,
                   initial_seat_funding_usd=seed,
                   additional_external_funding_usd=financing['additional_external_funding_usd'],
                   financing=financing,
                   total_owner_funding_usd=seed + financing['additional_external_funding_usd'],
                   shortfall_seats=sum(p['count'] for p in plan.purchase_events if p['emergency']),
                   demand_sha256=demand_digest(tape, demand), requested_copies=sum(demand))
        # On this tape 5R <= 20; replacement supply must keep full coverage.
        assert result.copies_filled == sum(demand)
        assert result.routing['copy_coverage'] == 1
        assert plan.peak_live <= PROFILE['max_live_accounts']
        write_csv(folder / f'{allocation}_fills.csv',
                  [{**f, 'accounts': ';'.join(map(str, f['accounts']))} for f in result.routing_fills])
        write_csv(folder / f'{allocation}_accounts.csv', account_rows(result))
        write_csv(folder / f'{allocation}_payouts.csv', [asdict(e) for e in result.payouts])
        write_csv(folder / f'{allocation}_purchases.csv', plan.purchase_events)
        rows.append(row)
    (folder / 'case.json').write_text(json.dumps({'config': to_payload(config), 'rows': rows}, indent=2), encoding='utf-8')
    return rows


def report(rows):
    text = ('# Fixed-R shared routing pools\n\n'
            'Every exported trade receives R copies. Start once with K=5R accounts; '
            'reuse free seats and buy only a current shortfall. No monthly or weekly purchases. '
            'Account deaths can require replacements, so lifetime purchases can exceed initial K while live inventory stays within 20.\n\n'
            'All cases use the inherited withdrawal settings, one MNQ per copy and the same rulebook. '
            'Each start/R group has identical signal-copy demand across withdrawals and allocations. '
            'The daily and monthly settings also have different retained balances: differences cannot be attributed to cadence alone.\n\n'
            'This remains a capacity/economics experiment: funded seats are available immediately when needed, '
            'and external funding is supplied as required. The table measures that funding; it does not impose an affordability gate '
            'or Evaluation/activation delays. Five is the observed tape overlap, not a future guarantee. '
            'Trade extrema are applied at exit and working-order reservations are absent. '
            '2023 is a start-date sensitivity, not independent out-of-sample policy selection.\n\n'
            'Net cash subtracts all account costs and excludes contributions. Total includes one firm-permitted terminal request.\n\n')
    for year in PROFILE['starts']:
        text += f'## Fresh start in {year}\n\n'
        text += '| R / initial K | Withdrawal | Allocation | Bought / peak live | Deaths | Coverage | Ongoing net | Terminal receipt | Total net | Total owner funding needed |\n'
        text += '|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
        for r in rows:
            if r['start_year'] != year:
                continue
            text += (f"| {r['R']} / {r['initial_seats']} | {r['withdrawal']} | {r['arm']} | {r['accounts']} / {r['peak_live']} | "
                     f"{r['deaths']} | {r['routing']['copy_coverage']:.0%} | ${r['ongoing_net_usd']:,.2f} | "
                     f"${r['terminal_received_usd']:,.2f} | ${r['total_net_usd']:,.2f} | ${r['total_owner_funding_usd']:,.2f} |\n")
        text += '\n'
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, default=PROJECT_ROOT / 'config/studies/legacy_25k_fixed_pool.json')
    args = parser.parse_args()
    initialize(args.profile)
    capacity = capacity_audit(TAPE)
    assert capacity['peak_positions'] == PROFILE['capacity_per_copy']
    jobs = list(product(PROFILE['starts'], PROFILE['copies'], PROFILE['withdrawals']))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=PROFILE['workers'], initializer=initialize, initargs=(args.profile,)) as pool:
        for index, case in enumerate(pool.map(run_case, jobs), 1):
            rows.extend(case)
            print(f'Fixed-R cases {index}/{len(jobs)}', flush=True)
    payload = {'schema': 'pa_milky.fixed_pool_study.v1', 'profile': PROFILE,
               'generated_utc': datetime.now(timezone.utc).isoformat(), 'capacity': capacity,
               'base_config': to_payload(BASE), 'inputs': input_digest(BASE), 'engine': engine_digest(),
               'runner_sha256': sha256_file(Path(__file__)),
               'shared_io_sha256': sha256_file(Path(__file__).with_name('study_legacy_routing.py')), 'rows': rows}
    payload['evidence_files'] = {str(p.relative_to(OUT)).replace('\\', '/'): sha256_file(p)
                                 for case in sorted({r['case'] for r in rows})
                                 for p in sorted((OUT / case).iterdir()) if p.is_file()}
    (OUT / 'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_csv(OUT / 'comparison.csv', [{k: v for k, v in r.items() if not isinstance(v, dict)} for r in rows])
    (OUT / 'REPORT.generated.md').write_text(report(rows), encoding='utf-8')
    print(f'Wrote {OUT}', flush=True)


if __name__ == '__main__':
    main()
