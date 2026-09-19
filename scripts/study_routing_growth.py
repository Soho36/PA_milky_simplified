"""Compare funded monthly growth under identical operating rules, not exposure."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import input_digest, engine_digest, sha256_file
from pa_milky.routing import RoutingPolicy, capacity_audit
from pa_milky.routing_study import measure
from pa_milky.simulator import run_book
from study_legacy_routing import write_csv, account_rows
from report_names import report_path

PROFILE_PATH = PROJECT_ROOT / 'config/studies/legacy_25k_routing_growth.json'
PROFILE = BASE = TAPE = OUT = None


def initialize():
    global PROFILE, BASE, TAPE, OUT
    PROFILE = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT / PROFILE['scenario'])
    TAPE = load_tape(BASE)
    OUT = PROJECT_ROOT / PROFILE['output']


def run_case(job):
    year, (initial, monthly), reserve = job
    tape = [t for t in TAPE if t.entry_at.year >= year]
    config = replace(BASE, expected_trades=len(tape), policy=WithdrawalPolicy(
        name=f'daily_minimum_retain_{reserve}', cadence='daily', amount_rule='minimum',
        min_retained_balance_usd=reserve, quantize_to_amount=False, terminal_withdrawal='firm_permitted'))
    acquisition = AcquisitionPolicy(PROFILE['acquisition'], initial, monthly,
                                    max_live_accounts=PROFILE['max_live_accounts'])
    case = f'{year}_{initial}_{monthly}_retain_{reserve}'
    folder = OUT / case
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for arm in PROFILE['arms']:
        route = (None if arm == 'unlimited_reference' else
                 RoutingPolicy(mode='blocked') if arm == 'blocked_copy' else
                 RoutingPolicy(mode='adaptive', allocation=arm.removeprefix('adaptive_'),
                               capacity_per_copy=PROFILE['capacity_per_copy']))
        snapshots, reference_fills = [], []
        first_capacity = {}
        peak_live = 0

        def observe(at, accounts, event, trade):
            nonlocal peak_live
            live = sum(a.alive for a in accounts)
            peak_live = max(peak_live, live)
            for k in (5, 10, 15, 20):
                if live >= k and k not in first_capacity:
                    first_capacity[k] = at.isoformat()
            if event == 'decision':
                snapshots.append({'at': at.isoformat(), 'live': live,
                                  'lifetime_purchases': len(accounts),
                                  'capacity_R': live // PROFILE['capacity_per_copy']})
            if route is None and event == 'before_trade':
                selected = [a.account_id for a in accounts if a.alive and a.activated_at <= trade.entry_at]
                reference_fills.append({'trade_key': trade.trade_key, 'entry_at': trade.entry_at.isoformat(),
                    'exit_at': trade.exit_at.isoformat(), 'requested': len(selected), 'accounts': selected})

        result = run_book(tape, config, acquisition=acquisition, initial_accounts=PROFILE['initial_accounts'],
                          routing=route, observer=observe)
        fills = result.routing_fills if route is not None else reference_fills
        row = measure(result, peak_live)
        ledger = result.acquisition.summary()
        assert ledger['cash_identity_residual_usd'] == 0
        assert ledger['net_cash_created_usd'] == result.pocket_usd
        assert min(e['cash_after_usd'] for e in result.acquisition.cash_events) >= 0
        assert peak_live <= PROFILE['max_live_accounts']
        assert sum(len(f['accounts']) for f in fills) == result.copies_filled
        wanted = sum(f['requested'] for f in fills)
        executed_signals = sum(bool(f['accounts']) for f in fills)
        zero_target = sum(f['requested'] == 0 for f in fills)
        planned_hours = sum((t.exit_at - t.entry_at).total_seconds() / 3600 * len(f['accounts'])
                            for t, f in zip(tape, fills)) if route is None else sum(
                            (datetime.fromisoformat(f['exit_at']) - datetime.fromisoformat(f['entry_at'])).total_seconds()
                            / 3600 * len(f['accounts']) for f in fills)
        row.update(case=case, arm=arm, start_year=year, initial_cash_usd=initial,
                   monthly_contribution_usd=monthly, retained_balance_usd=reserve,
                   initial_accounts=PROFILE['initial_accounts'], acquisition=PROFILE['acquisition'],
                   max_live_accounts=PROFILE['max_live_accounts'], first_capacity_dates=first_capacity,
                   capacity_R_at_horizon=result.alive_at_horizon // PROFILE['capacity_per_copy'],
                   signals_loaded=len(tape), signals_executed=executed_signals,
                   signal_participation=executed_signals / len(tape), signals_without_target=zero_target,
                   requested_copies=wanted, missed_requested_copies=wanted-result.copies_filled,
                   requested_copy_coverage=result.copies_filled / wanted if wanted else None,
                   mean_copies_per_exported_signal=result.copies_filled / len(tape),
                   planned_contract_hours=round(planned_hours, 4),
                   owner_contributions_usd=ledger['owner_contributions_usd'],
                   ending_owner_cash_usd=ledger['ending_owner_cash_usd'],
                   cash_limited_decisions=ledger['cash_limited_decisions'],
                   capacity_limited_decisions=ledger['capacity_limited_decisions'],
                   pending_replacements=result.acquisition.pending_replacements,
                   growth_purchases=sum(e['scheduled_bought'] for e in result.acquisition.replacement_events),
                   replacement_purchases=sum(e['replacements'] for e in result.acquisition.replacement_events))
        assert len(result.accounts) == row['initial_accounts'] + row['growth_purchases'] + row['replacement_purchases']
        write_csv(folder / f'{arm}_fills.csv',
                  [{**f, 'accounts': ';'.join(map(str, f['accounts']))} for f in fills])
        write_csv(folder / f'{arm}_accounts.csv', account_rows(result))
        write_csv(folder / f'{arm}_payouts.csv', [asdict(e) for e in result.payouts])
        write_csv(folder / f'{arm}_cash.csv', result.acquisition.cash_events)
        write_csv(folder / f'{arm}_decisions.csv', result.acquisition.decisions)
        write_csv(folder / f'{arm}_replacement_events.csv', result.acquisition.replacement_events)
        write_csv(folder / f'{arm}_daily_pool.csv', snapshots)
        rows.append(row)
    reference = rows[0]
    blocked = rows[1]
    for row in rows:
        row['delta_total_vs_unlimited_usd'] = round(row['total_net_usd'] - reference['total_net_usd'], 2)
        row['delta_total_vs_blocked_usd'] = round(row['total_net_usd'] - blocked['total_net_usd'], 2)
        row['copies_vs_unlimited_ratio'] = row['copies'] / reference['copies'] if reference['copies'] else None
    (folder / 'case.json').write_text(json.dumps({'config': to_payload(config),
        'acquisition': asdict(acquisition), 'initial_accounts': PROFILE['initial_accounts'], 'rows': rows}, indent=2), encoding='utf-8')
    return rows


def render(rows):
    text = ('# Routing versus copying under funded monthly growth\n\n'
            'Each case starts with five paid accounts, identical initial cash/monthly contributions, a 20-live-account cap, '
            'one additional account at the start of each subsequent month, and daily checks for funded death replacements. '
            'Replacements do not consume monthly growth slots. Both obey available owner cash; receipts can fund purchases. '
            'No extra external funding or entry-time rescue purchases are allowed. Unaffordable scheduled growth is skipped; '
            'unfilled replacements remain pending. The initial five replace the first ordinary monthly purchase.\n\n'
            'Daily minimum withdrawal checks, retained balance, rulebook, contract size and commission are identical within a case. '
            'Purchases and account balances can diverge because trading outcomes and receipt timing differ. '
            'The two retained-balance settings are separate fixed-policy comparisons, not an optimization.\n\n'
            '| Arm | Execution |\n|---|---|\n'
            '| unlimited_reference | Existing model: every eligible account takes every trade, including overlap. An idealized benchmark. |\n'
            '| blocked_copy | Every live account tries each signal but accepts only when flat. No spreading copies to recover missed signals. |\n'
            '| adaptive_max_headroom | One shared pool; R=floor(live accounts/5); choose free accounts with most headroom. |\n'
            '| adaptive_round_robin | Same dynamic R and budget; rotate through free accounts. |\n\n'
            'R is recomputed before each entry from live inventory, including busy accounts. R rises at 10, 15 and 20 seats '
            'and falls after deaths. Below five it is zero; those zero-target signals are reported separately. '
            'R affects new entries only. This study matches resources and operating rules, **not trade exposure**: '
            'at 20 accounts the unlimited model targets 20 copies, while full-coverage routing targets four.\n\n'
            'Coverage of requested copies excludes R=0 offers. Signal participation counts exported signals receiving at least one copy '
            'and therefore exposes pauses. Copy counts and planned contract-hours describe exposure; they do not normalize away '
            'payout thresholds or account failure. Extrema remain applied at exit, and unlimited concurrent floating P&L is not aggregated. '
            'Funded seats remain instantly available at daily purchase checks; evaluation lead times and working-order reservations are absent. '
            'The 2023 starts are sensitivity checks, not independent policy selection.\n\n'
            'All net figures subtract all account fees and exclude owner contributions. Total includes a firm-permitted terminal request.\n\n')
    for year in PROFILE['starts']:
        text += f'## Fresh start in {year}\n\n'
        for initial, monthly in PROFILE['budgets']:
            text += f'### ${initial:,} initially + ${monthly:,}/month\n\n'
            text += '| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |\n'
            text += '|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
            for r in rows:
                if (r['start_year'], r['initial_cash_usd'], r['monthly_contribution_usd']) != (year, initial, monthly):
                    continue
                text += (f"| ${r['retained_balance_usd']:,} | {r['arm']} | {r['accounts']} / {r['alive']} | {r['copies']:,} | "
                         f"{r['signal_participation']:.1%} | {r['signals_without_target']:,} | ${r['ongoing_net_usd']:,.2f} | "
                         f"${r['terminal_received_usd']:,.2f} | ${r['total_net_usd']:,.2f} | ${r['ending_owner_cash_usd']:,.2f} |\n")
            text += '\n'
    return text


def main():
    initialize()
    assert capacity_audit(TAPE)['peak_positions'] == PROFILE['capacity_per_copy']
    jobs = list(product(PROFILE['starts'], PROFILE['budgets'], PROFILE['retained_balances']))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=PROFILE['workers'], initializer=initialize) as pool:
        for i, case in enumerate(pool.map(run_case, jobs), 1):
            rows.extend(case)
            print(f'Funded growth cases {i}/{len(jobs)}', flush=True)
    payload = {'schema': PROFILE['schema'], 'profile': PROFILE,
               'generated_utc': datetime.now(timezone.utc).isoformat(),
               'inputs': input_digest(BASE), 'engine': engine_digest(),
               'runner_sha256': sha256_file(Path(__file__)),
               'shared_io_sha256': sha256_file(Path(__file__).with_name('study_legacy_routing.py')), 'rows': rows}
    payload['evidence_files'] = {str(p.relative_to(OUT)).replace('\\', '/'): sha256_file(p)
                                 for case in sorted({r['case'] for r in rows})
                                 for p in sorted((OUT / case).iterdir()) if p.is_file()}
    (OUT / 'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_csv(OUT / 'comparison.csv', [{k: v for k, v in r.items() if not isinstance(v, dict)} for r in rows])
    report_path(OUT, 'REPORT.generated.md').write_text(render(rows), encoding='utf-8')
    print(f'Wrote {OUT}', flush=True)


if __name__ == '__main__':
    main()
