"""Targeted full-grid search for survivors of three shared failed quarters."""
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from datetime import datetime
from decimal import Decimal
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import WINDOWS, load_trades
from pa_milky.provenance import engine_digest, sha256_file
from rr_curve_support import select_trades, first_markers
from study_rr_curves import router_selection
from study_rr_episodes import independent_marker, windows

ROOT = PROJECT_ROOT / 'results/legacy_25k/common_quarter_survivors'
PRIOR = PROJECT_ROOT / 'results/legacy_25k/rr_gg_episodes'
TARGETS = ('2022-04-01', '2024-07-01', '2025-04-01')
LABELS = ('Q2 2022', 'Q3 2024', 'Q2 2025')
CONTROLS = ('RR:0.50', 'RR:2.50', 'GG:1.25')
CONFIG = PROJECT_ROOT / 'config/scenarios/full_rulebook_monthly_500.json'
PROTOCOL = PROJECT_ROOT / 'research/legacy_25k/COMMON_QUARTER_SURVIVORS.md'


def read(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def measure(tape, strategy, rr, start, end, commission):
    selected = select_trades(tape, start, end)
    ids = [t.trade_key for t in selected]
    assert ids == router_selection(tape, start, end)
    assert all(a.exit_at <= b.entry_at for a, b in zip(selected, selected[1:]))
    marker = first_markers(selected, 1500, end, commission)['excursion_floor']
    actual = (marker['trade_key'], marker['interval_start'], marker['exit']) if marker else None
    assert actual == independent_marker(selected, 1500, end, commission)
    settled = Decimal(0)
    minimum = Decimal(0)
    for t in selected:
        if t.exit_at >= end:
            continue
        adverse = settled + min(Decimal(str(t.mae_usd)), Decimal(0))
        settled += (Decimal(str(t.gross_pnl_usd)) - Decimal(str(commission))).quantize(Decimal('.01'))
        minimum = min(minimum, adverse, settled)
    assert bool(marker) == (minimum <= -1500)
    return dict(arm=f'{strategy}:{rr}', strategy=strategy, risk_reward=rr,
                case=f'3m_{start.date()}', start=start.isoformat(), end=end.isoformat(),
                survived=not bool(marker), breached=bool(marker),
                trade_key=marker['trade_key'] if marker else '',
                interval_start=marker['interval_start'] if marker else '',
                exit=marker['exit'] if marker else '',
                accepted=len(selected), closed=sum(t.exit_at < end for t in selected),
                open_at_end=sum(t.exit_at >= end for t in selected),
                minimum_headroom_usd=str(Decimal(1500) + minimum),
                quarter_net_pnl_usd=str(settled),
                selection_sha256=hashlib.sha256(json.dumps(ids, separators=(',', ':')).encode()).hexdigest())


def worker(job):
    strategy, rr = job
    cfg = load_config(CONFIG)
    paths = [cfg.sweeps_root / directory / window / f'{window}_{rr}{suffix}.csv'
             for window in WINDOWS
             for directory, suffix in ((strategy, ''), (strategy + '_stats', '_stats'))]
    inputs = {p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in paths}
    tape = load_trades(cfg.sweeps_root, strategy=strategy, risk_reward=rr)
    quarters = list(windows(3))
    target = [measure(tape, strategy, rr, start, end, cfg.commission_per_copy_usd)
              for start, end in quarters if str(start.date()) in TARGETS]
    all_quarters = []
    if any(r['survived'] for r in target) or f'{strategy}:{rr}' in CONTROLS:
        bycase = {r['case']: r for r in target}
        for start, end in quarters:
            case = f'3m_{start.date()}'
            all_quarters.append(bycase[case] if case in bycase else
                                measure(tape, strategy, rr, start, end, cfg.commission_per_copy_usd))
    assert all(sha256_file(p) == inputs[p.relative_to(PROJECT_ROOT).as_posix()] for p in paths), 'Inputs changed during run'
    return target, all_quarters, inputs


def bands(values):
    values = sorted(int(Decimal(v) * 100) for v in values)
    runs = []
    for value in values:
        if runs and value == runs[-1][-1] + 1:
            runs[-1].append(value)
        else:
            runs.append([value])
    return ', '.join(f'{r[0]/100:.2f}' if len(r) == 1 else f'{r[0]/100:.2f}–{r[-1]/100:.2f}' for r in runs) or 'None'


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    prior_manifest = json.loads((PRIOR / 'manifest.json').read_text())
    assert engine_digest() == prior_manifest['engine']
    assert sha256_file(PRIOR / 'windows.csv') == prior_manifest['files']['windows.csv']
    prior = {(r['rr'], r['case']): r for r in read(PRIOR / 'windows.csv')
             if r['months'] == '3' and r['budget'] == '1500'}
    code_paths = [Path(__file__), PROTOCOL, CONFIG, PROJECT_ROOT / 'config/tape_coverage.json',
                  PROJECT_ROOT / 'scripts/rr_curve_support.py', PROJECT_ROOT / 'scripts/study_rr_curves.py',
                  PROJECT_ROOT / 'scripts/study_rr_episodes.py']
    code = {p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in code_paths}
    jobs = [(s, f'{i/100:.2f}') for s in ('RR', 'GG') for i in range(50, 351)]
    targets, contextual, inputs = [], [], {}
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, (target, full, hashes) in enumerate(pool.map(worker, jobs), 1):
            targets.extend(target)
            contextual.extend(full)
            inputs.update(hashes)
            if i % 25 == 0 or i == len(jobs):
                print(f'{i}/{len(jobs)} settings validated; {sum(r["survived"] for r in targets)} surviving setting-quarter cases', flush=True)
    checks = Counter()
    for r in targets:
        old = prior.get((r['arm'], r['case']))
        if old:
            for field in ('breached', 'trade_key', 'interval_start', 'exit', 'accepted', 'closed'):
                assert str(r[field]) == old[field], (r['arm'], r['case'], field)
            checks['prior_target_results_reproduced'] += 1
    for name, h in prior_manifest['inputs'].items():
        assert inputs[Path(name).as_posix()] == h, name
        checks['prior_source_hashes_matched'] += 1
    assert len(targets) == 1806 and checks['prior_target_results_reproduced'] == 78
    assert len({(r['arm'], r['case']) for r in targets}) == 1806
    checks['router_and_decimal_cases'] = len(targets) + sum(str(r['start'][:10]) not in TARGETS for r in contextual)
    failures = {arm: {r['case'] for r in contextual if r['arm'] == arm and r['breached']}
                for arm in {r['arm'] for r in contextual}}
    common = set.intersection(*(failures[a] for a in CONTROLS))
    assert common == {f'3m_{s}' for s in TARGETS}
    summaries = []
    for strategy, rr in jobs:
        arm = f'{strategy}:{rr}'
        rows = [r for r in targets if r['arm'] == arm]
        survived = [r['case'] for r in rows if r['survived']]
        summaries.append(dict(arm=arm, strategy=strategy, risk_reward=rr,
                              survived_targets=len(survived), survived_cases=';'.join(survived),
                              worst_target_headroom_usd=min(Decimal(r['minimum_headroom_usd']) for r in rows),
                              failed_quarters_of_26=len(failures[arm]) if arm in failures else '',
                              common_failures_remaining=len(common & failures[arm]) if arm in failures else '',
                              failed_cases=';'.join(sorted(failures[arm])) if arm in failures else ''))
    write(ROOT / 'target_quarters.csv', targets)
    write(ROOT / 'setting_summary.csv', summaries)
    write(ROOT / 'context_quarters.csv', contextual)
    lines = ['# Survivors of the three shared failure quarters', '',
             'Full ordinary grid: 602 settings, RR and GG r/r 0.50–3.50 in 0.01 steps. '
             'Each test starts fresh at quarter start with $1,500 fixed headroom, one MNQ '
             'and $1.05 commission. No withdrawals or replacements.', '',
             '| Quarter | RR surviving r/r bands | Count / 301 | GG surviving r/r bands | Count / 301 |',
             '|---|---|---:|---|---:|']
    for start, label in zip(TARGETS, LABELS):
        cells = []
        for strategy in ('RR', 'GG'):
            values = [r['risk_reward'] for r in targets if r['strategy'] == strategy and r['start'][:10] == start and r['survived']]
            cells.extend([bands(values), str(len(values))])
        lines.append(f'| {label} | ' + ' | '.join(cells) + ' |')
    all_survivors = [r['arm'] for r in summaries if r['survived_targets'] == 3]
    lines += ['', '**Settings surviving all three: ' + (', '.join(all_survivors) or 'none') + '.**', '',
              '## Context for every setting surviving at least one target', '',
              'All 26 fresh-start quarters are recalculated for survivors and three reference settings. '
              '“Common failures remaining” is the intersection with RR 0.50, RR 2.50 and GG 1.25; '
              'it is not a simulated allocation or replacement policy.', '',
              '| Arm | Target quarters survived / 3 | Minimum headroom in survived target(s) | Failed quarters / 26 | Common failures remaining |',
              '|---|---:|---:|---:|---:|']
    for r in summaries:
        if r['survived_targets'] or r['arm'] in CONTROLS:
            margin = min((Decimal(t['minimum_headroom_usd']) for t in targets if t['arm'] == r['arm'] and t['survived']), default=None)
            money = f'${margin:,.2f}' if margin is not None else '—'
            lines.append(f'| {r["arm"]} | {r["survived_targets"]} | {money} | {r["failed_quarters_of_26"]} | {r["common_failures_remaining"]} |')
    lines += ['', '## Interpretation and checks', '',
              'These quarters were selected because the earlier candidates failed in them. '
              'A finely selected survivor is therefore a historical finding, not independent evidence '
              'that it will protect a future portfolio. Inspect neighboring settings and other failed quarters.', '',
              'Survival means no MAE/net-close breach during the quarter; positive ending P&L does '
              'not erase an earlier failure. Minimum headroom is relative to the fixed starting floor, '
              'not peak-to-trough drawdown. Analytical P&L continues after a failure solely for diagnostics.', '',
              f'Target cases with a position unclosed at the horizon: {sum(r["open_at_end"] > 0 for r in targets)}. '
              'Those positions and their full MAE are censored as in the prior studies. '
              'Breach times based on MAE remain intervals.', '',
              f'All {checks["prior_target_results_reproduced"]} coarse target results reproduce exactly. '
              f'{checks["router_and_decimal_cases"]} cases passed independent router and Decimal marker checks. '
              'Every tape passed loader reconciliation and coverage; source hashes were unchanged during loading.', '',
              'RR1000 is excluded from this grid because it is a separate all-hours tape with '
              'different entry availability. Existing studies and their manifests are unchanged.', '',
              '[Design](../../../research/legacy_25k/COMMON_QUARTER_SURVIVORS.md) · '
              '[All target paths](target_quarters.csv) · [All setting summaries](setting_summary.csv) · '
              '[Context quarters](context_quarters.csv) · [Manifest](manifest.json)', '']
    (ROOT / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    assert all(sha256_file(PROJECT_ROOT / p) == h for p, h in code.items()), 'Code changed during run'
    manifest = dict(engine=engine_digest(), design=dict(target_starts=TARGETS, strategies=['RR', 'GG'],
                    rr_min='0.50', rr_max='3.50', rr_step='0.01', budget=1500, contracts=1,
                    commission=load_config(CONFIG).commission_per_copy_usd), checks=dict(checks),
                    code=code, inputs=inputs, prior_manifest_sha256=sha256_file(PRIOR / 'manifest.json'),
                    files={name:sha256_file(ROOT / name) for name in
                           ('target_quarters.csv', 'setting_summary.csv', 'context_quarters.csv', 'REPORT.md')})
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(checks), indent=2), flush=True)
    print('All-three survivors:', all_survivors, flush=True)


if __name__ == '__main__':
    main()
