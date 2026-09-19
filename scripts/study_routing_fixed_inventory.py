"""Separate fixed-resource allocation from exact modeled-exposure replay."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import heapq
from itertools import product
import json
from pathlib import Path

from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import input_digest, engine_digest, sha256_file
from pa_milky.routing import RoutingPolicy, capacity_audit, entry_key
from pa_milky.routing_study import measure, demand_digest
from pa_milky.simulator import run_book
from study_legacy_routing import write_csv, account_rows
from report_names import report_path

PROFILE_PATH = PROJECT_ROOT / 'config/studies/legacy_25k_routing_fixed_inventory.json'
PROFILE = BASE = TAPE = OUT = None


def initialize():
    global PROFILE, BASE, TAPE, OUT
    PROFILE = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT / PROFILE['scenario'])
    TAPE = load_tape(BASE)
    OUT = PROJECT_ROOT / PROFILE['output']


def weighted_peak(tape, demand):
    """Necessary seats before allowing for deaths; instantaneous offers need seats."""
    heap, occupied, peak = [], 0, 0
    for i, trade in sorted(enumerate(tape), key=lambda p: entry_key(p[1])):
        while heap and heap[0][0] <= trade.entry_at:
            _, n = heapq.heappop(heap)
            occupied -= n
        occupied += demand[i]
        heapq.heappush(heap, (trade.exit_at, demand[i]))
        peak = max(peak, occupied)
    return peak


def run_case(job):
    year, reserve = job
    tape = [t for t in TAPE if t.entry_at.year >= year]
    config = replace(BASE, expected_trades=len(tape), policy=WithdrawalPolicy(
        name=f'daily_minimum_retain_{reserve}', cadence='daily', amount_rule='minimum',
        min_retained_balance_usd=reserve, quantize_to_amount=False, terminal_withdrawal='firm_permitted'))
    case = f'{year}_retain_{reserve}'
    folder = OUT / case
    folder.mkdir(parents=True, exist_ok=True)
    rows, reference_fills, demand, capacity_trials = [], [], [], []
    k = PROFILE['initial_accounts']

    def observe(at, accounts, event, trade):
        if event == 'before_trade':
            selected = [a.account_id for a in accounts if a.alive and a.activated_at <= trade.entry_at]
            demand.append(len(selected))
            reference_fills.append({'trade_key': trade.trade_key, 'entry_at': trade.entry_at.isoformat(),
                'exit_at': trade.exit_at.isoformat(), 'requested': len(selected), 'accounts': selected})

    reference = run_book(tape, config, fixed_accounts=k, observer=observe)
    assert sum(demand) == reference.copies_filled
    reference_map = {t.trade_key: n for t, n in zip(tape, demand)}
    full_target = [k] * len(tape)

    def save(arm, result, group, target_r=None):
        fills = result.routing_fills if result.routing is not None else reference_fills
        counts = {f['trade_key']: len(f['accounts']) for f in fills}
        counts_in_tape_order = [counts[t.trade_key] for t in tape]
        wanted = sum(f['requested'] for f in fills)
        row = measure(result, len(result.accounts))
        row.update(case=case, arm=arm, group=group, start_year=year, retained_balance_usd=reserve,
            initial_accounts=len(result.accounts), target_R=target_r, replacement_rule='none',
            signals_loaded=len(tape), signals_executed=sum(bool(f['accounts']) for f in fills),
            signal_participation=sum(bool(f['accounts']) for f in fills) / len(tape),
            requested_copies=wanted, missed_requested_copies=wanted-result.copies_filled,
            signals_without_target=sum(f['requested'] == 0 for f in fills),
            signals_different_from_reference=sum(counts[t.trade_key] != reference_map[t.trade_key] for t in tape),
            exact_reference_exposure=counts_in_tape_order == demand,
            filled_demand_sha256=demand_digest(tape, counts_in_tape_order),
            planned_contract_hours=round(sum((t.exit_at-t.entry_at).total_seconds()/3600 * counts[t.trade_key]
                                              for t in tape), 4),
            ongoing_received_usd=round(result.total_received_usd-sum(e.received_usd for e in result.terminal_payouts), 2),
            total_received_usd=result.total_received_usd,
            last_executed_entry=max((f['entry_at'] for f in fills if f['accounts']), default=None),
            last_death_at=max((a.died_at.isoformat() for a in result.dead), default=None),
            delta_total_vs_reference_usd=round(result.pocket_usd-reference.pocket_usd, 2))
        assert sum(counts.values()) == result.copies_filled
        assert result.acquisition is None and len(result.accounts) == row['initial_accounts']
        assert len({a.activated_at for a in result.accounts}) == 1
        assert all(f.get('purchased', 0) == 0 for f in fills)
        write_csv(folder / f'{arm}_fills.csv', [{**f, 'accounts': ';'.join(map(str, f['accounts']))} for f in fills])
        write_csv(folder / f'{arm}_accounts.csv', account_rows(result))
        write_csv(folder / f'{arm}_payouts.csv', [asdict(e) for e in result.payouts])
        rows.append(row)

    save('unlimited_20', reference, 'same_resources')
    save('blocked_20', run_book(tape, config, fixed_accounts=k, routing=RoutingPolicy(mode='blocked')), 'same_resources')
    for allocation in ('max_headroom', 'round_robin'):
        save(f'routed_20_{allocation}', run_book(tape, config, fixed_accounts=k,
             routing=RoutingPolicy(copies=k//PROFILE['capacity_per_copy'], allocation=allocation)),
             'same_resources', k//PROFILE['capacity_per_copy'])

    def search(target, name, lower_bound):
        # Test an explicit grid; no monotonicity assumption about account health.
        step = PROFILE['capacity_search_step']
        start = max(step, ((lower_bound+step-1)//step)*step)
        successful = None
        for seats in range(start, PROFILE['capacity_search_limit']+1, step):
            result = run_book(tape, config, fixed_accounts=seats,
                              routing=RoutingPolicy(copies=k), routing_demand=target)
            missed = result.routing['copies_requested']-result.copies_filled
            capacity_trials.append({'target': name, 'initial_accounts': seats, 'lower_bound': lower_bound,
                                    'copies': result.copies_filled, 'missed': missed,
                                    'deaths': len(result.dead), 'total_net_usd': result.pocket_usd})
            print(f'{case} {name}: K={seats}, missed={missed}', flush=True)
            if seats == start or missed == 0:
                save(f'{name}_{seats}', result, name, k if name == 'full_target' else None)
            if missed == 0:
                successful = seats
                break
        return {'mechanical_lower_bound': lower_bound, 'first_successful_tested_inventory': successful,
                'step': step, 'search_limit': PROFILE['capacity_search_limit'],
                'minimum_proven': successful == lower_bound}

    exact = search(demand, 'matched_reference', weighted_peak(tape, demand))
    intended = search(full_target, 'full_target', weighted_peak(tape, full_target))
    write_csv(folder / 'capacity_trials.csv', capacity_trials)
    write_csv(folder / 'demand.csv', [{'trade_key': t.trade_key, 'reference_copies': n, 'full_target_copies': k}
                                     for t, n in zip(tape, demand)])
    metadata = {'config': to_payload(config), 'rows': rows, 'capacity_audit': capacity_audit(tape),
                'reference_demand_sha256': demand_digest(tape, demand),
                'exact_reference_capacity': exact, 'full_target_capacity': intended}
    (folder / 'case.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


def render(cases):
    text = ('# Fixed initial inventory: resources and exposure\n\n'
        'All accounts are purchased before the first signal, at the first calendar boundary. '
        '**No later purchases or death replacements.** Initial K is fixed; live inventory may decline. '
        'Daily minimum withdrawal checks, retained balance, terminal withdrawal, contract size and all modeled rules '
        'are identical within each case. Retain $31,900 is the main policy; $30,000 and a fresh 2023 start are sensitivities.\n\n'
        'Same resources compares 20 unrestricted accounts, 20 blocked copying accounts, and 20 routed accounts '
        'targeting R=4 throughout (max-headroom and round-robin). R is not reduced after deaths. '
        'Unrestricted accounts use the existing settlement-time model and ignore overlapping positions.\n\n'
        'Same exposure freezes that reference model\'s realized copy count on every trade, then routes exactly those '
        'copies from a larger initial inventory. This is an ex-post counterfactual, not a live routing signal. '
        'It stops requesting trades when the reference model stops. Matching is verified per signal, not just in aggregate.\n\n'
        'A separate **full_target** diagnostic requests 20 copies of every exported signal, including after the reference '
        'dies. Five overlapping setups imply 100 seats before deaths. We test this initial inventory and, if necessary, '
        'larger sizes in steps of 20. The first successful tested size is sufficient historically; it is not a global '
        'minimum unless it equals the weighted concurrency lower bound. It is also not matched realized reference exposure. '
        'Searches above 20 deliberately suspend the configured operating cap.\n\n'
        'Initial fees are counted in ongoing and total net cash. Ongoing net excludes terminal receipts; total net includes them. '
        'No leftover nominal account balance is counted as cash. Account deaths follow per-trade extrema applied at exit; '
        'concurrent floating P&L is not aggregated in the unrestricted benchmark. Exported entry/exit intervals do not '
        'include pending-order reservation times. Same modeled copy exposure need not give the same booked P&L because '
        'failure truncation and commissions depend on account allocation.\n\n')
    for case in cases:
        r0 = case['rows'][0]
        text += f"## Start {r0['start_year']}; retained balance ${r0['retained_balance_usd']:,}\n\n"
        for group in ('same_resources', 'matched_reference', 'full_target'):
            text += f'### {group}\n\n| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |\n'
            text += '|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
            for r in case['rows']:
                if r['group'] == group:
                    text += (f"| {r['arm']} | {r['accounts']} | {r['deaths']} | {r['copies']:,} | "
                        f"{r['signal_participation']:.2%} | {r['missed_requested_copies']:,} | "
                        f"${r['ongoing_net_usd']:,.2f} | ${r['terminal_received_usd']:,.2f} | ${r['total_net_usd']:,.2f} |\n")
            text += '\n'
        for label in ('exact_reference_capacity', 'full_target_capacity'):
            c = case[label]
            text += (f"- {label}: mechanical lower bound {c['mechanical_lower_bound']}; first successful tested K "
                     f"{c['first_successful_tested_inventory']}; minimum proven: {c['minimum_proven']}.\n")
        text += '\n'
    return text


def main():
    initialize()
    assert capacity_audit(TAPE)['peak_positions'] == PROFILE['capacity_per_copy']
    OUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=PROFILE['workers'], initializer=initialize) as pool:
        cases = list(pool.map(run_case, product(PROFILE['starts'], PROFILE['retained_balances'])))
    rows = [r for case in cases for r in case['rows']]
    payload = {'schema': PROFILE['schema'], 'profile': PROFILE, 'generated_utc': datetime.now(timezone.utc).isoformat(),
               'inputs': input_digest(BASE), 'engine': engine_digest(), 'runner_sha256': sha256_file(Path(__file__)),
               'shared_io_sha256': sha256_file(Path(__file__).with_name('study_legacy_routing.py')), 'rows': rows}
    payload['evidence_files'] = {str(p.relative_to(OUT)).replace('\\', '/'): sha256_file(p)
                                for c in cases for p in sorted((OUT/c['rows'][0]['case']).iterdir()) if p.is_file()}
    (OUT/'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_csv(OUT/'comparison.csv', [{k:v for k,v in r.items() if not isinstance(v,dict)} for r in rows])
    report_path(OUT, 'REPORT.generated.md').write_text(render(cases), encoding='utf-8')
    print(f'Wrote {OUT}', flush=True)


if __name__ == '__main__':
    main()
