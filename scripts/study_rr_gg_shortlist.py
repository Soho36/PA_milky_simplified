"""Fixed RR/GG pair/triple shortlist, with exhaustive operating assignments."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime
from functools import partial
from itertools import permutations
import csv
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.loader import WINDOWS, load_trades
from pa_milky.provenance import engine_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from rr_curve_support import select_trades, first_markers, daily_path, curve_metrics
from rr_followup_support import Sleeves, SleeveRouter, LadderPolicy
from study_rr_curves import router_selection
from study_rr_episodes import windows, independent_marker

ROOT = PROJECT_ROOT / 'results/legacy_25k/rr_gg_shortlist'
PRIOR = PROJECT_ROOT / 'results/legacy_25k/rr_gg_episodes'
PROTOCOL = PROJECT_ROOT / 'research/legacy_25k/RR_GG_SHORTLIST.md'
PARENT_PATH = PROJECT_ROOT / 'config/studies/legacy_25k_rr_diversification.json'
COMPONENTS = ('RR:0.50', 'RR:1.00', 'RR:2.50', 'GG:1.25')
MIXES = {
    'rr_pair': ('RR:0.50', 'RR:2.50'),
    'cross_pair': ('RR:0.50', 'GG:1.25'),
    'rr_triple': ('RR:0.50', 'RR:2.50', 'RR:1.00'),
    'cross_triple': ('RR:0.50', 'GG:1.25', 'RR:1.00'),
}
ARMS = {**{a: (a,) for a in COMPONENTS}, **MIXES}
START = datetime(2020, 1, 1)
END = datetime(2026, 7, 1)
BASE = PARENT = EVAL = TAPES = None


def read(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def boot():
    global BASE, PARENT, EVAL, TAPES
    PARENT = json.loads(PARENT_PATH.read_text())
    BASE = load_config(PROJECT_ROOT / PARENT['scenario'])
    EVAL = EvaluationSpec(**json.loads((PROJECT_ROOT / PARENT['evaluation_spec']).read_text())['evaluations']['legacy_25k'])
    TAPES = {name: load_trades(BASE.sweeps_root, strategy=name.split(':')[0], risk_reward=name.split(':')[1])
             for name in COMPONENTS}


def isolate():
    old_markers = {(r['rr'], r['case']): r for r in read(PRIOR / 'windows.csv')
                   if r['months'] == '3' and r['budget'] == '1500'}
    old_curves = {(r['left'], r['right'], r['case']): r for r in read(PRIOR / 'quarter_curves.csv')}
    dates = [r['date'] for r in read(PRIOR / 'episode_calendar.csv')]
    daily, rows, components = [], [], []
    checks = Counter()
    for start, end in windows(3):
        case = f'3m_{start.date()}'
        days = [d for d in dates if str(start.date()) <= d < str(end.date())]
        paths, failed, cm = {}, {}, {}
        for arm, tape in TAPES.items():
            selected = select_trades(tape, start, end)
            assert [t.trade_key for t in selected] == router_selection(tape, start, end)
            marker = first_markers(selected, 1500, end, BASE.commission_per_copy_usd)['excursion_floor']
            actual = (marker['trade_key'], marker['interval_start'], marker['exit']) if marker else None
            assert actual == independent_marker(selected, 1500, end, BASE.commission_per_copy_usd)
            old = old_markers[arm, case]
            expected = (old['trade_key'], old['interval_start'], old['exit']) if old['breached'] == 'True' else None
            assert actual == expected
            paths[arm] = daily_path(selected, days, end, BASE.commission_per_copy_usd)
            failed[arm] = bool(marker)
            cm[arm] = curve_metrics(paths[arm], days, start.isoformat())[0]
            components.append(dict(case=case, arm=arm, breached=bool(marker),
                                   trade_key=marker['trade_key'] if marker else '',
                                   interval_start=marker['interval_start'] if marker else '',
                                   exit=marker['exit'] if marker else '', accepted=len(selected),
                                   open_at_end=sum(t.exit_at >= end for t in selected)))
            checks['component_router_decimal_and_prior_markers'] += 1
        mixed = {}
        for name, members in ARMS.items():
            path = [statistics.mean(paths[a][i] for a in members) for i in range(len(days))]
            mixed[name] = path
            m = curve_metrics(path, days, start.isoformat())[0]
            assert abs(m['net_pnl'] - statistics.mean(cm[a]['net_pnl'] for a in members)) < 1e-7
            assert m['max_drawdown'] <= statistics.mean(cm[a]['max_drawdown'] for a in members) + 1e-7
            lost = sum(failed[a] for a in members)
            rows.append(dict(case=case, portfolio=name, members=';'.join(members), groups=len(members),
                             failed_groups=lost, failed_fraction=lost / len(members),
                             full_loss=lost == len(members), **m))
            checks['weighted_curve_accounting'] += 1
            if len(members) < 3:
                key = (members[0], members[-1], case)
                old = old_curves[key]
                for field in ('net_pnl', 'max_drawdown'):
                    assert abs(m[field] - float(old[field])) < 1e-7, (key, field)
                checks['prior_curve_matches'] += 1
        daily.extend(dict(case=case, date=d, **{a: mixed[a][i] for a in ARMS}) for i, d in enumerate(days))
    paths = {a: daily_path(select_trades(t, START, END), dates, END, BASE.commission_per_copy_usd)
             for a, t in TAPES.items()}
    continuous = {name: [statistics.mean(paths[a][i] for a in members) for i in range(len(dates))]
                  for name, members in ARMS.items()}
    summaries = []
    for name, members in ARMS.items():
        r = [r for r in rows if r['portfolio'] == name]
        m = curve_metrics(continuous[name], dates, START.isoformat())[0]
        summaries.append(dict(portfolio=name, members=';'.join(members), quarters=len(r),
                              full_loss_quarters=sum(v['full_loss'] for v in r),
                              partial_loss_quarters=sum(0 < v['failed_fraction'] < 1 for v in r),
                              no_loss_quarters=sum(v['failed_fraction'] == 0 for v in r),
                              mean_failed_fraction=statistics.mean(v['failed_fraction'] for v in r),
                              worst_failed_fraction=max(v['failed_fraction'] for v in r),
                              mean_quarter_pnl=statistics.mean(v['net_pnl'] for v in r),
                              mean_quarter_mdd=statistics.mean(v['max_drawdown'] for v in r),
                              worst_quarter_mdd=max(v['max_drawdown'] for v in r),
                              continuous_pnl=m['net_pnl'], continuous_mdd=m['max_drawdown'],
                              full_loss_cases=';'.join(v['case'] for v in r if v['full_loss'])))
    write(ROOT / 'isolation_components.csv', components)
    write(ROOT / 'isolation_quarters.csv', rows)
    write(ROOT / 'isolation_summary.csv', summaries)
    write(ROOT / 'isolation_daily.csv', daily)
    write(ROOT / 'continuous_daily.csv', [dict(date=d, **{a: continuous[a][i] for a in ARMS}) for i, d in enumerate(dates)])
    return summaries, checks


def continuity(accounts, end):
    events = Counter()
    for a in accounts:
        events[a.activated_at] += 1
        if not a.alive:
            events[a.died_at] -= 1
    live = 0
    previous = None
    first = None
    empty = 0.0
    wipes = 0
    episodes = []
    for at, delta in sorted(events.items()):
        if first is not None and live == 0:
            empty += (at - previous).total_seconds() / 86400
            episodes.append(dict(start=previous.isoformat(), end=at.isoformat()))
        after = live + delta
        assert 0 <= after <= 20
        wipes += int(live > 0 and after == 0)
        if first is None and after > 0:
            first = at
        live, previous = after, at
    if first is not None and live == 0:
        empty += (end - previous).total_seconds() / 86400
        episodes.append(dict(start=previous.isoformat(), end=end.isoformat()))
    return dict(book_wipeouts=wipes, days_empty_after_first_activation=round(empty, 4),
                continuous_after_activation=first is not None and wipes == 0,
                first_activation=first.isoformat() if first else '', empty_episodes=episodes)


def operating(job):
    name, year, order = job
    members = ARMS[name]
    perm = list(permutations(members))[order]
    case = f'{name.replace(":", "_")}__{year}__p{order + 1:02d}'
    sleeves = Sleeves([dict(rr=a, reserve=6800) for a in perm])
    policy = LadderPolicy(sleeves=sleeves, floor_balance=BASE.trailing_floor_balance_usd,
                         name='shortlist_minimum', cadence='daily', amount_rule='minimum', terminal_withdrawal='none')
    config = replace(BASE, policy=policy, path_order='mae_first', expected_trades=None, expected_windows=None)
    acquisition = AcquisitionPolicy('monthly_current_slot_replacements', evaluation=EVAL, **PARENT['operating'])
    tapes = {a: [t for t in tape if t.entry_at.year >= year] for a, tape in TAPES.items()}
    trades = sorted([t for tape in tapes.values() for t in tape],
                    key=lambda t: (t.exit_at, t.entry_at, t.window_order, t.source_row, t.ticket, t.trade_key))
    trade_arm = {t.trade_key: a for a, tape in tapes.items() for t in tape}
    assert len(trade_arm) == len(trades)
    lookup = {t.trade_key: t for t in trades}
    daily = []
    def observe(at, accounts, event, trade):
        if event != 'decision':
            return
        sleeves.assign(accounts)
        live = [a for a in accounts if a.alive]
        counts = Counter(sleeves.definition(a.account_id)['rr'] for a in live)
        daily.append(dict(at=at.isoformat(), alive=len(live),
                          **{a: counts[a] for a in members},
                          retained_positive_equity=round(sum(max(a.equity_profit_usd, 0) for a in live), 2)))
    result = run_book(trades, config, acquisition=acquisition, observer=observe,
                      routing=RoutingPolicy(mode='blocked'),
                      router_factory=partial(SleeveRouter, sleeves=sleeves,
                                             weights=dict(Counter(perm)), trade_rr=trade_arm),
                      evaluation_tape=tapes['RR:1.00'])
    assert Economics.measure(result).residual_usd == 0
    ledger = result.acquisition.summary()
    assert ledger['cash_identity_residual_usd'] == 0
    assert min(e['cash_after_usd'] for e in result.acquisition.cash_events) >= 0
    assert len(result.accounts) + result.unused_spares == ledger['evaluations_activated']
    assert all(d['alive'] + d['spares'] + d['in_flight'] <= 20 and d['subscriptions'] <= 5
               for d in result.acquisition.pipeline_daily)
    byid = {a.account_id: a for a in result.accounts}
    copies, until = Counter(), {}
    for fill in result.routing_fills:
        t = lookup[fill['trade_key']]
        for aid in fill['accounts']:
            a = byid[aid]
            assert sleeves.definition(aid)['rr'] == fill['rr'] == trade_arm[t.trade_key]
            assert a.activated_at <= t.entry_at and (a.alive or a.died_at >= t.exit_at)
            assert until.get(aid, t.entry_at) <= t.entry_at
            until[aid] = t.exit_at
            copies[aid] += 1
    assert sum(copies.values()) == result.copies_filled
    assert all(copies[a.account_id] == a.trades_taken for a in result.accounts)
    assert all(p.balance_after_usd + .005 >= BASE.trailing_floor_balance_usd + 6800 for p in result.payouts)
    accounts = [dict(account_id=a.account_id, arm=sleeves.definition(a.account_id)['rr'],
                     activated_at=a.activated_at.isoformat(), alive=a.alive,
                     died_at=a.died_at.isoformat() if not a.alive else None,
                     death_trade_key=a.death_trade_key, trades=a.trades_taken,
                     ending_balance=a.balance_usd, ending_headroom=a.headroom_usd,
                     received_payouts=a.received_usd) for a in result.accounts]
    stats = continuity(result.accounts, result.tape_last_exit)
    empty_episodes = stats.pop('empty_episodes')
    regression = False
    if len(members) == 1 and members[0].startswith('RR:'):
        rr = members[0].split(':')[1]
        file = PROJECT_ROOT / f'results/legacy_25k/rr_followup/cases/primary__operating__{year}__mae_first__rr_{rr}.json'
        old = json.loads(file.read_text())
        assert len(accounts) == len(old['accounts'])
        for a, b in zip(accounts, old['accounts'], strict=True):
            for key in a.keys() - {'arm'}:
                assert a[key] == b[key], (case, key, a[key], b[key])
        assert result.pocket_usd == old['row']['net_operating_cash']
        assert result.copies_filled == old['row']['copies']
        assert stats['book_wipeouts'] == old['row']['book_wipeouts']
        regression = True
    row = dict(case=case, portfolio=name, start_year=year, permutation=order + 1,
               assignment_order=';'.join(perm), accounts=len(accounts), deaths=len(result.dead),
               alive=result.alive_at_horizon, net_operating_cash=result.pocket_usd,
               receipts=result.total_received_usd, acquisition_costs=result.total_purchase_cost_usd,
               retained_equity=result.equity_at_horizon_usd, copies=result.copies_filled,
               mean_daily_alive=statistics.mean(d['alive'] for d in daily),
               **stats, prior_ledger_reproduced=regression,
               tape_first_entry=result.tape_first_entry.isoformat(), tape_last_exit=result.tape_last_exit.isoformat())
    evidence = dict(row=row, accounts=accounts, daily_occupancy=daily,
                    empty_episodes=empty_episodes, acquisition=ledger,
                    audit=dict(cash_and_economics_reconciled=True, copies_checked=result.copies_filled,
                               lifetime_membership_and_nonoverlap=True, capacity_checked=True,
                               payouts_reserve_checked=len(result.payouts)))
    (ROOT / 'operating_cases' / f'{case}.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    return row


def summarize_operating(rows):
    bystart, pooled = [], []
    for name in ARMS:
        for year in range(2020, 2026):
            cases = [r for r in rows if r['portfolio'] == name and r['start_year'] == year]
            record = dict(portfolio=name, start_year=year, permutations=len(cases),
                          continuous_orders=sum(r['continuous_after_activation'] for r in cases))
            for key in ('book_wipeouts', 'days_empty_after_first_activation', 'deaths', 'net_operating_cash', 'retained_equity'):
                values = [r[key] for r in cases]
                record.update({f'{key}_min': min(values), f'{key}_mean': statistics.mean(values), f'{key}_max': max(values)})
            bystart.append(record)
        cases = [r for r in rows if r['portfolio'] == name]
        starts = [r for r in bystart if r['portfolio'] == name]
        record = dict(portfolio=name, starts=6, cases=len(cases),
                      continuous_cases=sum(r['continuous_after_activation'] for r in cases),
                      starts_continuous_all_orders=sum(r['continuous_orders'] == r['permutations'] for r in starts),
                      starts_continuous_any_order=sum(r['continuous_orders'] > 0 for r in starts))
        for key in ('book_wipeouts', 'days_empty_after_first_activation', 'deaths', 'net_operating_cash', 'retained_equity'):
            record[f'{key}_mean'] = statistics.mean(r[f'{key}_mean'] for r in starts)
            record[f'{key}_worst_order_mean'] = statistics.mean(r[f'{key}_max' if key not in ('net_operating_cash','retained_equity') else f'{key}_min'] for r in starts)
        pooled.append(record)
    write(ROOT / 'operating_by_start.csv', bystart)
    write(ROOT / 'operating_summary.csv', pooled)
    return pooled


def report(isolation, operating_rows):
    lines = ['# Fixed RR/GG shortlist', '', '## Isolation: all 26 quarters, equal allocations', '',
             '| Portfolio | Full loss / 26 | Mean accounts failed | Mean quarter P&L | Mean quarter DD | Worst quarter DD |',
             '|---|---:|---:|---:|---:|---:|']
    for r in isolation:
        lines.append(f'| {r["portfolio"]} | {r["full_loss_quarters"]} | {r["mean_failed_fraction"]:.2%} | '
                     f'${r["mean_quarter_pnl"]:,.0f} | ${r["mean_quarter_mdd"]:,.0f} | ${r["worst_quarter_mdd"]:,.0f} |')
    lines += ['', 'All settings use one MNQ, $1,500 fixed initial headroom and $1.05 commission. '
              'Fractions and curves are normalized to equal total allocation. Analytical P&L continues '
              'after failure and is not cash earned by surviving accounts. DD is realized daily maximum '
              'drawdown, not exact intratrade portfolio equity. Every arm has a worst-quarter failed fraction of 100%.', '',
              '## Operating: all assignment orders', '',
              '| Portfolio | Continuous cases / cases | Starts continuous in every order / 6 | Mean wipeouts | Mean empty days | Mean deaths | Mean net cash |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for r in operating_rows:
        lines.append(f'| {r["portfolio"]} | {r["continuous_cases"]}/{r["cases"]} | {r["starts_continuous_all_orders"]} | '
                     f'{r["book_wipeouts_mean"]:.3f} | {r["days_empty_after_first_activation_mean"]:.2f} | '
                     f'{r["deaths_mean"]:.1f} | ${r["net_operating_cash_mean"]:,.0f} |')
    lines += ['', 'Starts are equally weighted; each start averages all of that portfolio\'s assignment orders. '
              'Cases/start horizons overlap and are not independent trials. Continuity requires activation and '
              'no subsequent empty-book event. Cash is receipts less acquisition costs, excluding retained equity; '
              'funding contributions are not trading profits.', '',
              'Operating uses the inherited daily-minimum/$6,800-reserve policy, shared cap 20, RR1 evaluation '
              'supply and replacement rules, over 2020–2025 starts through July 13, 2026. PAs begin with '
              'their original trailing floor; the reserve is not starting headroom. Integer group sizes and '
              'actual occupancy vary during deployment. This differs deliberately from the fixed-floor isolation.', '',
              '[Design](../../../research/legacy_25k/RR_GG_SHORTLIST.md) · [Isolation quarters](isolation_quarters.csv) · '
              '[Isolation summary](isolation_summary.csv) · [Operating cases](operating_comparison.csv) · '
              '[Per-start order ranges](operating_by_start.csv) · [Operating summary](operating_summary.csv) · '
              '[Audit](audit.json)', '']
    (ROOT / 'REPORT.generated.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    boot()
    (ROOT / 'operating_cases').mkdir(parents=True, exist_ok=True)
    old = json.loads((PRIOR / 'manifest.json').read_text())
    assert old['engine'] == engine_digest()
    for name in ('windows.csv', 'quarter_curves.csv', 'episode_calendar.csv'):
        assert sha256_file(PRIOR / name) == old['files'][name]
    source_paths = [BASE.sweeps_root / directory / w / f'{w}_{rr}{suffix}.csv'
                    for arm in COMPONENTS for strategy, rr in [arm.split(':')] for w in WINDOWS
                    for directory, suffix in ((strategy, ''), (strategy + '_stats', '_stats'))]
    inputs = {p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in source_paths}
    for p, h in inputs.items():
        assert old['inputs'].get(p, old['inputs'].get(str(Path(p)))) == h, p
    paths = [Path(__file__), PROTOCOL, PARENT_PATH, PROJECT_ROOT / PARENT['scenario'],
             PROJECT_ROOT / PARENT['evaluation_spec'], PROJECT_ROOT / 'config/tape_coverage.json']
    paths += [PROJECT_ROOT / 'scripts' / f for f in ('rr_curve_support.py', 'rr_followup_support.py',
                                                    'study_rr_curves.py', 'study_rr_episodes.py')]
    contract = dict(arms=ARMS, config=to_payload(BASE), operating=PARENT['operating'], engine=engine_digest(),
                    inputs=inputs, code={p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in paths},
                    prior_manifest_sha256=sha256_file(PRIOR / 'manifest.json'))
    contract = json.loads(json.dumps(contract))
    cp = ROOT / 'contract.json'
    if cp.exists():
        assert json.loads(cp.read_text()) == contract, 'Frozen contract changed'
    else:
        cp.write_text(json.dumps(contract, indent=2) + '\n', encoding='utf-8')
    isolation, checks = isolate()
    print('Isolation summary:', json.dumps(isolation, indent=2), flush=True)
    jobs = [(name, year, i) for name, members in ARMS.items() for year in range(2020, 2026)
            for i, _ in enumerate(permutations(members))]
    assert len(jobs) == 120
    rows = []
    with ProcessPoolExecutor(max_workers=4, initializer=boot) as pool:
        for future in as_completed([pool.submit(operating, job) for job in jobs]):
            r = future.result()
            rows.append(r)
            if len(rows) % 10 == 0:
                print(f'Operating {len(rows)}/120: {r["case"]}, wipeouts={r["book_wipeouts"]}, cash={r["net_operating_cash"]}', flush=True)
    rows.sort(key=lambda r: (list(ARMS).index(r['portfolio']), r['start_year'], r['permutation']))
    write(ROOT / 'operating_comparison.csv', rows)
    summary = summarize_operating(rows)
    report(isolation, summary)
    assert sum(r['prior_ledger_reproduced'] for r in rows) == 18
    assert all(sha256_file(PROJECT_ROOT / p) == h for p, h in inputs.items())
    assert all(sha256_file(PROJECT_ROOT / p) == h for p, h in contract['code'].items())
    audit = dict(status='passed', isolation_checks=dict(checks), operating_cases=120,
                 prior_operating_ledgers_reproduced=18, operating_copies_checked=sum(r['copies'] for r in rows),
                 contract_sha256=sha256_file(cp),
                 files={p.relative_to(ROOT).as_posix(): sha256_file(p) for p in ROOT.rglob('*')
                        if p.is_file() and p.name not in ('audit.json', 'contract.json', 'FINDINGS.md')})
    (ROOT / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print('Complete:', json.dumps({k: v for k, v in audit.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    main()
