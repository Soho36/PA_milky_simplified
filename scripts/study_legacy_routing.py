"""Run the frozen-policy, matched-exposure routing experiment."""
import argparse
import csv
import gzip
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import input_digest, engine_digest, sha256_file
from pa_milky.routing import capacity_audit
from pa_milky.routing_study import reference_run, replay_run, measure, demand_digest, required_topups
from report_names import report_path

PROFILE = BASE = TAPE = OUT = None


def initialize(profile_path):
    global PROFILE, BASE, TAPE, OUT
    PROFILE = json.loads(Path(profile_path).read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT / PROFILE['scenario'])
    TAPE = load_tape(BASE)
    OUT = PROJECT_ROOT / PROFILE['output']


def write_csv(path, rows):
    compressed = path.name == 'demand.csv' or path.name.endswith('_fills.csv')
    if compressed:
        path = path.with_suffix(path.suffix + '.gz')
    opener = gzip.open if compressed else open
    if not rows:
        with opener(path, 'wt', encoding='utf-8') as handle:
            handle.write('')
        return
    with opener(path, 'wt', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
        writer.writeheader()
        writer.writerows(rows)


def compress_existing_evidence(root):
    # Convert only this runner's generated demand/allocation CSVs, losslessly.
    for pattern in ('*/demand.csv', '*/*_fills.csv'):
        for path in root.glob(pattern):
            assert path.resolve().is_relative_to(root.resolve())
            raw = path.read_bytes()
            compressed = gzip.compress(raw, mtime=0)
            assert gzip.decompress(compressed) == raw
            path.with_suffix('.csv.gz').write_bytes(compressed)
            path.unlink()


def case_id(job):
    year, (initial, monthly), purchase, withdrawal = job
    return f"{year}_{initial}_{monthly}_{purchase}_{withdrawal['amount_rule']}_{withdrawal['cadence']}_{withdrawal['retained_balance_usd']}"


def account_rows(result):
    return [{k: getattr(a, k) for k in (
        'account_id', 'activated_at', 'alive', 'died_at', 'death_trade_key',
        'trades_taken', 'gross_pnl_usd', 'commission_usd', 'equity_profit_usd',
        'gross_paid_usd', 'received_usd', 'payout_count')} for a in result.accounts]


def run_case(job):
    year, budget, purchase, withdrawal = job
    initial, monthly = budget
    tape = [t for t in TAPE if t.entry_at.year >= year]
    config = replace(BASE, expected_trades=len(tape), policy=WithdrawalPolicy(
        name=f"{withdrawal['amount_rule']}_{withdrawal['cadence']}_{withdrawal['retained_balance_usd']}",
        amount_rule=withdrawal['amount_rule'], cadence=withdrawal['cadence'],
        min_retained_balance_usd=withdrawal['retained_balance_usd'],
        quantize_to_amount=False, terminal_withdrawal='firm_permitted'))
    acquisition = AcquisitionPolicy(purchase, initial, monthly,
                                    max_live_accounts=PROFILE['reference_live_cap'])
    reference, demand, peak_live = reference_run(tape, config, acquisition)
    case = case_id(job)
    folder = OUT / case
    folder.mkdir(parents=True, exist_ok=True)
    controls = measure(reference, peak_live)
    common = {'case': case, 'start_year': year, 'initial_cash_usd': initial,
              'monthly_contribution_usd': monthly, 'purchase_policy': purchase,
              'withdrawal': config.policy.name, 'reference_copies': sum(demand),
              'demand_sha256': demand_digest(tape, demand)}
    controls.update(common, arm='reference', emergency_seats=0,
                    extra_purchase_cost_usd=0, additional_external_funding_usd=0,
                    delta_ongoing_usd=0, delta_total_usd=0)
    rows = [controls]
    write_csv(folder / 'demand.csv', [{'trade_key': t.trade_key, 'entry_at': t.entry_at,
                                     'exit_at': t.exit_at, 'copies': n} for t, n in zip(tape, demand)])
    write_csv(folder / 'reference_accounts.csv', account_rows(reference))
    write_csv(folder / 'reference_payouts.csv', [asdict(e) for e in reference.payouts])
    write_csv(folder / 'reference_cash.csv', reference.acquisition.cash_events)
    for allocation in PROFILE['allocations']:
        arm, plan = replay_run(tape, reference, demand, allocation=allocation,
                               capacity=PROFILE['expected_capacity'],
                               procurement=PROFILE.get('procurement', 'five_per_purchase'))
        row = measure(arm, plan.peak_live)
        row.update(common, arm=allocation,
                   emergency_seats=sum(e['count'] for e in plan.purchase_events if e['emergency']),
                   extra_purchase_cost_usd=round(arm.total_purchase_cost_usd-reference.total_purchase_cost_usd, 2),
                   delta_ongoing_usd=round(row['ongoing_net_usd']-controls['ongoing_net_usd'], 2),
                   delta_total_usd=round(row['total_net_usd']-controls['total_net_usd'], 2),
                   financing=required_topups(arm, plan, reference),
                   economic_bridge=Economics.measure(arm).bridge_against(Economics.measure(reference)))
        row['additional_external_funding_usd'] = row['financing']['additional_external_funding_usd']
        row['procurement'] = plan.procurement
        row['shortfall_seats'] = row['emergency_seats']
        assert row['economic_bridge']['residual_usd'] == 0
        assert arm.routing['copies_missed_busy'] == arm.routing['copies_missed_inventory'] == 0
        # Independently check every recorded offer against frozen demand.
        lookup = {t.trade_key: n for t, n in zip(tape, demand)}
        assert len(arm.routing_fills) == len(lookup)
        assert all(len(f['accounts']) == lookup[f['trade_key']] for f in arm.routing_fills)
        write_csv(folder / f'{allocation}_fills.csv',
                  [{**f, 'accounts': ';'.join(map(str, f['accounts']))} for f in arm.routing_fills])
        write_csv(folder / f'{allocation}_accounts.csv', account_rows(arm))
        write_csv(folder / f'{allocation}_payouts.csv', [asdict(e) for e in arm.payouts])
        write_csv(folder / f'{allocation}_purchases.csv', plan.purchase_events)
        rows.append(row)
    (folder / 'case.json').write_text(json.dumps({'config': to_payload(config),
        'acquisition': asdict(acquisition), 'rows': rows}, indent=2), encoding='utf-8')
    return rows


def verify_saved_controls(rows):
    path = PROJECT_ROOT / 'results/study__full_rulebook__RR__account_purchases__cash_budgets/study.json'
    old = json.loads(path.read_text(encoding='utf-8'))['rows']
    checked = 0
    for row in rows:
        if row['arm'] != 'reference' or row['start_year'] != 2020:
            continue
        candidates = [r for r in old if r['purchase_policy'] == row['purchase_policy']
                      and r['initial_cash_usd'] == row['initial_cash_usd']
                      and r['monthly_contribution_usd'] == row['monthly_contribution_usd']]
        case = json.loads((OUT / row['case'] / 'case.json').read_text(encoding='utf-8'))
        # Compare the resolved withdrawal semantics, ignoring its display name.
        policy = case['config']['policy']
        candidates = [r for r in candidates if all(r['withdrawal_config'][k] == policy[k]
                      for k in ('amount_rule', 'cadence', 'min_retained_balance_usd'))]
        if not candidates:
            raise ValueError(f"Missing saved policy control: {row['case']}")
        expected = candidates[0]
        assert (row['ongoing_net_usd'], row['total_net_usd'], row['accounts'], row['alive']) == (
            expected['ongoing_net_cash_usd'], expected['combined_net_cash_usd'],
            expected['accounts_bought'], expected['alive_before_terminal']), row['case']
        checked += 1
    return checked


def render_report(rows, capacity, verified):
    text = '# Matched-exposure account routing\n\n'
    text += (f"The full tape contains {capacity['trades']:,} trades and peaks at **{capacity['peak_positions']} simultaneous positions**. "
             f"The historical mechanical ratio remains **K = {capacity['peak_positions']}R**. {verified} saved full-period controls reproduced exactly.\n\n")
    text += ('Each pair has identical reference trade-copy demand, contract size, commission and withdrawal settings. '
             'Original purchase dates are frozen; each reference purchase provisions five routed seats. '
             'Instant paid seats would fill any shortage after deaths. All routed cases must fill 100% of requested copies. '
             'This is an ex-post counterfactual: the reference survival path determines the replay demand, so it is not a prospective live strategy.\n\n'
             '**Resources are not matched.** Routed seats are externally financeable and the reference 20-live-account cap is relaxed. '
             'Costs below include every extra seat. The underlying purchase schedule is inherited, but physical account purchases differ. '
             'Additional funding is the minimum extra cash required on top of the original contribution schedule when routed receipts can be reinvested. '
             'It is separate from purchase costs. Net cash excludes owner contributions.\n\n'
             'Same withdrawal rules apply per physical account, so dispersing profits changes eligibility, payout timing and retained balances. '
             'Terminal means a firm-permitted final request, not liquidation. Account failures may truncate realized trade P&L even with identical entry-copy demand. '
             'MAE/MFE remain per-trade extrema applied at exit; payouts during open trades and intratrade death timing retain that approximation. '
             'Working-order reservations are absent from the export. Five is a historical interval result, not a future/live-order capacity guarantee.\n\n'
             '2023 starts are fresh-account sensitivity runs through the same final date, not independent validation: these policies were already selected using the wider dataset. '
             'No policy has been re-optimized.\n\n')
    if PROFILE.get('procurement') == 'reuse':
        text = text.replace('Original purchase dates are frozen; each reference purchase provisions five routed seats.',
                            'The pool starts empty. Each entry reuses all available seats and buys only max(0, requested copies minus free seats). Original purchase dates do not trigger routed purchases.')
        text = text.replace('Instant paid seats would fill any shortage after deaths.',
                            'Instant paid seats fill only the observed shortfall, including replacements after deaths.')
        text = text.replace('The underlying purchase schedule is inherited, but physical account purchases differ.',
                            'Reference demand is inherited; routed procurement is based solely on available capacity.')
        text = text.replace('# Matched-exposure account routing', '# Corrected routing: reuse capacity at matched exposure')
    for year in PROFILE['starts']:
        text += f'## Fresh start in {year}\n\n'
        for initial, monthly in PROFILE['budgets']:
            text += f'### Reference funding ${initial:,} initially + ${monthly:,}/month\n\n'
            text += '| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |\n'
            text += '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
            for r in rows:
                if (r['start_year'], r['initial_cash_usd'], r['monthly_contribution_usd']) != (year, initial, monthly):
                    continue
                text += (f"| {r['purchase_policy']} / {r['withdrawal']} | {r['arm']} | {r['copies']:,} | {r['accounts']} / {r['peak_live']} | {r['deaths']} | "
                         f"${r['ongoing_net_usd']:,.0f} | ${r['terminal_received_usd']:,.0f} | ${r['total_net_usd']:,.0f} | "
                         f"${r['extra_purchase_cost_usd']:,.0f} | ${r['additional_external_funding_usd']:,.0f} |\n")
            text += '\n'
    text += ('## Evidence\n\n`study.json` records resolved inputs and engine hashes; `comparison.csv` contains the paired metrics. '
             'Each case folder contains demand, per-account ledgers, payouts, purchases and every routed allocation. '
             'See the research note for interpretation.\n')
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, default=PROJECT_ROOT / 'config/studies/legacy_25k_routing_reuse.json')
    parser.add_argument('--smoke', action='store_true', help='Run one case into a separate smoke directory')
    parser.add_argument('--report-only', action='store_true', help='Verify and repackage existing cases without rerunning simulations')
    args = parser.parse_args()
    initialize(args.profile)
    capacity = capacity_audit(TAPE)
    assert capacity['peak_positions'] == PROFILE['expected_capacity'], capacity
    jobs = list(product(PROFILE['starts'], PROFILE['budgets'], PROFILE['acquisitions'], PROFILE['withdrawals']))
    if args.smoke:
        # Keep smoke outputs away from the final evidence path.
        global OUT
        OUT = PROJECT_ROOT / 'outputs/legacy_25k_routing_smoke'
        rows = run_case(jobs[0])
        print(json.dumps(rows, indent=2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    if args.report_only:
        previous = json.loads((OUT / 'study.json').read_text(encoding='utf-8'))
        assert previous['inputs'] == input_digest(BASE), 'Inputs changed; rerun simulations'
        assert previous['engine'] == engine_digest(), 'Engine changed; rerun simulations'
        assert previous['profile'] == PROFILE, 'Profile changed; rerun simulations'
        for job in jobs:
            case = json.loads((OUT / case_id(job) / 'case.json').read_text(encoding='utf-8'))
            rows.extend(case['rows'])
    else:
        with ProcessPoolExecutor(max_workers=PROFILE['workers'], initializer=initialize,
                                 initargs=(args.profile,)) as pool:
            for index, case_rows in enumerate(pool.map(run_case, jobs), 1):
                rows.extend(case_rows)
                print(f'Matched cases {index}/{len(jobs)}', flush=True)
    compress_existing_evidence(OUT)
    verified = verify_saved_controls(rows)
    payload = {'schema': 'pa_milky.routing_study.v1', 'generated_utc': datetime.now(timezone.utc).isoformat(),
               'profile': PROFILE, 'base_config': to_payload(BASE), 'capacity': capacity,
               'inputs': input_digest(BASE), 'engine': engine_digest(),
               'runner_sha256': sha256_file(Path(__file__)), 'verified_controls': verified, 'rows': rows}
    if PROFILE.get('previous_study'):
        previous_path = PROJECT_ROOT / PROFILE['previous_study']
        previous = json.loads(previous_path.read_text(encoding='utf-8'))
        prior = {(r['case'], r['arm']): r for r in previous['rows']}
        for row in rows:
            old = prior[row['case'], row['arm']]
            assert row['demand_sha256'] == old['demand_sha256']
            assert row['copies'] == old['copies']
            if row['arm'] == 'reference':
                assert all(row[k] == old[k] for k in ('total_net_usd', 'ongoing_net_usd', 'accounts', 'alive'))
            row['previous_accounts'] = old['accounts']
            row['previous_total_net_usd'] = old['total_net_usd']
            row['delta_vs_previous_routed_usd'] = round(row['total_net_usd'] - old['total_net_usd'], 2)
        # Keep case manifests and aggregate rows identical after the comparison.
        for job in jobs:
            path = OUT / case_id(job) / 'case.json'
            case = json.loads(path.read_text(encoding='utf-8'))
            case['rows'] = [r for r in rows if r['case'] == case_id(job)]
            path.write_text(json.dumps(case, indent=2), encoding='utf-8')
        payload['previous_study_sha256'] = sha256_file(previous_path)
        payload['verified_prior_cases'] = len(jobs)
    payload['evidence_files'] = {str(path.relative_to(OUT)).replace('\\', '/'): sha256_file(path)
                                 for job in jobs for path in sorted((OUT / case_id(job)).iterdir()) if path.is_file()}
    (OUT / 'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    scalar_rows = [{k: v for k, v in r.items() if not isinstance(v, dict) and k != 'routing'} for r in rows]
    write_csv(OUT / 'comparison.csv', scalar_rows)
    report_path(OUT, 'REPORT.generated.md').write_text(render_report(rows, capacity, verified), encoding='utf-8')
    print(f'Wrote {OUT}', flush=True)


if __name__ == '__main__':
    main()
