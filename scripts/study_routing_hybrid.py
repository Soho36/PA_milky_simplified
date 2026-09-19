"""Fixed-budget hybrid allocation: protect participation, use spare capacity."""
from collections import Counter
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
from pa_milky.routing import RoutingPolicy, capacity_audit
from pa_milky.routing_study import measure
from pa_milky.simulator import run_book
from study_legacy_routing import write_csv, account_rows
from audit_legacy_routing import read_csv
from report_names import report_path

PROFILE_PATH = PROJECT_ROOT/'config/studies/legacy_25k_routing_hybrid.json'
PROFILE = BASE = TAPE = OUT = None


def initialize():
    global PROFILE, BASE, TAPE, OUT
    PROFILE = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT/PROFILE['scenario'])
    TAPE = load_tape(BASE)
    OUT = PROJECT_ROOT/PROFILE['output']


def run_case(job):
    year, reserve = job
    tape = [t for t in TAPE if t.entry_at.year >= year]
    config = replace(BASE, expected_trades=len(tape), policy=WithdrawalPolicy(
        name=f'daily_minimum_retain_{reserve}', cadence='daily', amount_rule='minimum',
        min_retained_balance_usd=reserve, quantize_to_amount=False, terminal_withdrawal='firm_permitted'))
    case = f'{year}_retain_{reserve}'
    folder = OUT/case
    folder.mkdir(parents=True, exist_ok=True)
    old_folder = PROJECT_ROOT/PROFILE['control_output']/case
    controls = json.loads((old_folder/'case.json').read_text(encoding='utf-8'))
    assert to_payload(config) == controls['config']
    arms = [('unlimited_20', None), ('blocked_20', RoutingPolicy(mode='blocked')),
            ('routed_20_max_headroom', RoutingPolicy(copies=4)),
            ('routed_20_round_robin', RoutingPolicy(copies=4, allocation='round_robin'))]
    arms += [(f'hybrid_m{m}_cap{c}', RoutingPolicy(mode='hybrid', minimum_copies=m, maximum_copies=c,
                                              capacity_per_copy=PROFILE['concurrency_limit']))
             for m, c in product(PROFILE['minimum_copies'], PROFILE['maximum_copies'])]
    rows = []
    for arm, route in arms:
        reference_fills = []

        def observe(at, accounts, event, trade):
            if event == 'before_trade':
                selected = [a.account_id for a in accounts if a.alive and a.activated_at <= trade.entry_at]
                reference_fills.append({'trade_key': trade.trade_key, 'entry_at': trade.entry_at.isoformat(),
                    'exit_at': trade.exit_at.isoformat(), 'requested': len(selected), 'accounts': selected})

        result = run_book(tape, config, fixed_accounts=PROFILE['initial_accounts'], routing=route,
                          observer=observe if route is None else None)
        fills = result.routing_fills if route is not None else reference_fills
        row = measure(result, PROFILE['initial_accounts'])
        histogram = Counter(len(f['accounts']) for f in fills)
        floor = route.minimum_copies if route and route.mode == 'hybrid' else None
        row.update(case=case, arm=arm, start_year=year, retained_balance_usd=reserve,
                   initial_accounts=PROFILE['initial_accounts'], replacement_rule='none',
                   policy=asdict(route) if route else None,
                   signals_loaded=len(tape), signals_executed=len(tape)-histogram[0],
                   signal_participation=(len(tape)-histogram[0])/len(tape),
                   signals_missed=histogram[0], copies_per_signal_histogram=dict(sorted(histogram.items())),
                   mean_copies_per_signal=result.copies_filled/len(tape),
                   below_minimum_signals=sum(n < floor for n in (len(f['accounts']) for f in fills)) if floor else None,
                   minimum_copy_shortfall=sum(max(0, floor-len(f['accounts'])) for f in fills) if floor else None,
                   requested_copies=sum(f['requested'] for f in fills),
                   planned_contract_hours=round(sum((datetime.fromisoformat(f['exit_at'])-
                       datetime.fromisoformat(f['entry_at'])).total_seconds()/3600*len(f['accounts']) for f in fills), 4))
        assert len(result.accounts) == 20 and result.acquisition is None
        assert sum(len(f['accounts']) for f in fills) == row['copies']
        assert all(f.get('purchased', 0) == 0 for f in fills)
        if not arm.startswith('hybrid_'):
            old = next(r for r in controls['rows'] if r['arm'] == arm)
            for key in ('accounts', 'alive', 'deaths', 'copies', 'purchase_cost_usd', 'ongoing_net_usd',
                        'terminal_received_usd', 'total_net_usd', 'economics', 'signal_participation'):
                assert row[key] == old[key], (case, arm, key)
            old_fills = read_csv(old_folder/f'{arm}_fills.csv')
            assert [(f['trade_key'], f['accounts']) for f in old_fills] == [
                (f['trade_key'], ';'.join(map(str, f['accounts']))) for f in fills]
            row['control_reproduced'] = True
        else:
            row['control_reproduced'] = None
        write_csv(folder/f'{arm}_fills.csv', [{**f, 'accounts': ';'.join(map(str, f['accounts']))} for f in fills])
        write_csv(folder/f'{arm}_accounts.csv', account_rows(result))
        write_csv(folder/f'{arm}_payouts.csv', [asdict(e) for e in result.payouts])
        rows.append(row)
        print(f'{case} {arm}: net={row["total_net_usd"]}, coverage={row["signal_participation"]:.4%}', flush=True)
    blocked, fixed = rows[1], rows[2]
    for row in rows:
        row['delta_total_vs_blocked_usd'] = round(row['total_net_usd']-blocked['total_net_usd'], 2)
        row['delta_total_vs_fixed_usd'] = round(row['total_net_usd']-fixed['total_net_usd'], 2)
        row['delta_ongoing_vs_fixed_usd'] = round(row['ongoing_net_usd']-fixed['ongoing_net_usd'], 2)
        row['copies_vs_fixed_ratio'] = row['copies']/fixed['copies']
    metadata = {'config': to_payload(config), 'rows': rows, 'capacity_audit': capacity_audit(tape)}
    (folder/'case.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


def render(cases):
    text = ('# Hybrid allocation with 20 initial accounts\n\n'
        'All arms start with 20 paid accounts ($4,000). No growth, replacements or subsequent contributions. '
        'Daily minimum withdrawals, retained balance and terminal request rules match within each case. '
        'The main retained balance is $31,900; $30,000 and a fresh 2023 start are separate sensitivity checks. '
        'Six hybrid settings were specified before running; these are in-sample comparisons, not validated optima.\n\n'
        'For minimum copies m, cap c, free accounts F, and A distinct setups currently occupying accounts:\n\n'
        '`reserve = m * max(0, 5 - A - 1)`\n\n'
        '`target = min(c, max(m, F - reserve))`\n\n'
        'Select up to target free accounts by greatest current drawdown headroom, with account ID breaking ties. '
        'Only accepted, still-open setups count toward A. No future duration, P&L or extrema chooses the allocation. '
        'When inventory is depleted, attempt the current minimum even if future reserves cannot be maintained; '
        'report minimum shortfalls and missed signals. The five-setup assumption is historical, not a future guarantee. '
        'Same-time existing exits precede entries; instantaneous trades enter then exit.\n\n'
        'Coverage counts all exported signals, including signals after the book dies. Adaptive target coverage is '
        'not evidence that a minimum was maintained; the below-minimum column makes that visible. '
        'Copy histograms include zeros. Net cash deducts all fees; terminal receipts are shown separately. '
        'Signal weights differ, so this is a same-resource comparison, not matched exposure. '
        'The unrestricted model is an idealized settlement-time reference; one-position arms retain exported extrema '
        'at exit and omit working-order reservations.\n\n')
    for case in cases:
        r0 = case['rows'][0]
        text += f"## Start {r0['start_year']}; retain ${r0['retained_balance_usd']:,}\n\n"
        text += '| Arm | Copies | Signals traded | Below minimum | Deaths | Ongoing net | Terminal receipt | Total net |\n'
        text += '|---|---:|---:|---:|---:|---:|---:|---:|\n'
        for r in case['rows']:
            below = r['below_minimum_signals'] if r['below_minimum_signals'] is not None else '-'
            text += (f"| {r['arm']} | {r['copies']:,} | {r['signal_participation']:.2%} | {below} | {r['deaths']} | "
                     f"${r['ongoing_net_usd']:,.2f} | ${r['terminal_received_usd']:,.2f} | ${r['total_net_usd']:,.2f} |\n")
        text += '\nCopy distribution (`copies: number of signals`):\n\n'
        for r in case['rows']:
            if r['arm'].startswith('hybrid_'):
                text += f"- {r['arm']}: `{r['copies_per_signal_histogram']}`\n"
        text += '\n'
    return text


def main():
    initialize()
    control_root = PROJECT_ROOT/PROFILE['control_output']
    preserved = {str(p.relative_to(control_root)): sha256_file(p) for p in control_root.rglob('*') if p.is_file()}
    assert capacity_audit(TAPE)['peak_positions'] == PROFILE['concurrency_limit']
    OUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=PROFILE['workers'], initializer=initialize) as pool:
        cases = list(pool.map(run_case, product(PROFILE['starts'], PROFILE['retained_balances'])))
    rows = [r for c in cases for r in c['rows']]
    assert all(sha256_file(control_root/name) == checksum for name, checksum in preserved.items())
    payload = {'schema': PROFILE['schema'], 'profile': PROFILE, 'generated_utc': datetime.now(timezone.utc).isoformat(),
               'inputs': input_digest(BASE), 'engine': engine_digest(), 'runner_sha256': sha256_file(Path(__file__)),
               'shared_io_sha256': sha256_file(Path(__file__).with_name('study_legacy_routing.py')),
               'preserved_control_files': preserved, 'rows': rows}
    payload['evidence_files'] = {str(p.relative_to(OUT)).replace('\\', '/'): sha256_file(p)
                                for c in cases for p in sorted((OUT/c['rows'][0]['case']).iterdir()) if p.is_file()}
    (OUT/'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_csv(OUT/'comparison.csv', [{k:v for k,v in r.items() if not isinstance(v,dict)} for r in rows])
    report_path(OUT, 'REPORT.generated.md').write_text(render(cases), encoding='utf-8')
    print(f'Wrote {OUT}', flush=True)


if __name__ == '__main__':
    main()
