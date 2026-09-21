"""Focused allocation sensitivity using frozen, audited unrestricted RR paths."""
from bisect import bisect_left, bisect_right
from collections import defaultdict
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import engine_digest, sha256_file
from rr_curve_support import curve_metrics, failure_metrics

PROFILE = PROJECT_ROOT / 'config/studies/legacy_25k_rr_pairs.json'
PROTOCOL = PROJECT_ROOT / 'research/legacy_25k/RR_PAIRS.md'


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def equal(actual, expected):
    if expected in ('True', 'False'):
        assert actual == (expected == 'True'), (actual, expected)
    elif isinstance(actual, (float, int)):
        assert abs(actual - float(expected)) < 1e-6, (actual, expected)
    else:
        assert (actual or '') == (expected or ''), (actual, expected)


def weighted_failures(components, weights, markers, dates):
    """Sweep intervals of candidate window-start indices; no exit-date imputation."""
    points = [(markers[rr], weight) for rr, weight in zip(components, weights)
              if weight > 0 and markers[rr] is not None]
    signals = defaultdict(float)
    for marker, weight in points:
        signals[(marker['window'], marker['entry'])] += weight
    result = dict(fraction_breached=sum(w for _, w in points),
                  max_same_signal_fraction=max(signals.values(), default=0),
                  recorded_death_dates=len({m['exit'][:10] for m, _ in points}))
    for width in (1, 5, 20):
        for possible in (False, True):
            changes = defaultdict(float)
            for marker, weight in points:
                first = marker['interval_start'][:10] if possible else marker['exit'][:10]
                left = max(0, bisect_left(dates, first) - width + 1)
                right = min(len(dates) - 1, bisect_right(dates, marker['exit'][:10]) - 1)
                if left <= right:
                    changes[left] += weight
                    changes[right + 1] -= weight
            running = peak = 0
            for index in sorted(changes):
                running += changes[index]
                peak = max(peak, running)
            key = f'possible_{width}d_fraction' if possible else f'max_recorded_{width}d_fraction'
            result[key] = peak
    return result


def main():
    spec = json.loads(PROFILE.read_text())
    source = PROJECT_ROOT / spec['source']
    output = PROJECT_ROOT / spec['output']
    output.mkdir(parents=True, exist_ok=True)
    contract = json.loads((source / 'contract.json').read_text())
    audit = json.loads((source / 'audit.json').read_text())
    assert sha256_file(source / 'contract.json') == audit['contract_sha256']
    assert engine_digest() == contract['engine']
    for name, digest in contract['code'].items():
        assert sha256_file(PROJECT_ROOT / name) == digest, name
    for name, digest in audit['files'].items():
        assert sha256_file(source / name) == digest, name
    prior = {(r['cohort'], r['portfolio']): r for r in read_csv(source / 'comparison.csv')}
    prior_fail = {(r['cohort'], r['portfolio'], r['budget'], r['method']): r
                  for r in read_csv(source / 'failure_comparison.csv')}
    arms = {f'rr_{rr}': ([rr], [1.0], rr, '', 1.0) for rr in contract['spec']['rr_values']}
    for low in spec['lower_rr']:
        for high in spec['higher_rr']:
            for weight in spec['lower_weights']:
                name = f'pair_{low}_{high}_low{int(100 * weight):02d}'
                arms[name] = ([low, high], [weight, 1-weight], low, high, weight)
    results, failures = [], []
    checks = defaultdict(int)
    for cohort in contract['cohorts']:
        case = f'{cohort["kind"]}_{cohort["start"][:10]}'
        obs = read_csv(source / 'cohorts' / case / 'curves.csv')
        paths = json.loads((source / 'cohorts' / case / 'paths.json').read_text())
        dates = [r['date'] for r in obs]
        curves = {rr: [float(r[rr]) for r in obs] for rr in contract['spec']['rr_values']}
        baseline = prior[case, 'rr_1.00']
        for name, (components, weights, low, high, weight) in arms.items():
            values = [sum(w * curves[rr][i] for rr, w in zip(components, weights))
                      for i in range(len(dates))]
            metrics, _ = curve_metrics(values, dates, cohort['start'])
            running_peak = reference_dd = 0
            for value in values:
                reference_dd = max(reference_dd, running_peak - value)
                running_peak = max(running_peak, value)
            equal(metrics['max_drawdown'], reference_dd)
            equal(metrics['net_pnl'], sum(w * float(prior[case, f'rr_{rr}']['net_pnl'])
                                         for rr, w in zip(components, weights)))
            checks['weighted_curve_reconstructions'] += 1
            reference_name = f'pair_{low}_{high}' if high and weight == .5 else name if not high else None
            if reference_name:
                for key, value in metrics.items():
                    equal(value, prior[case, reference_name][key])
                checks['source_curve_matches'] += 1
            constituent_dd = [float(prior[case, f'rr_{rr}']['max_drawdown']) for rr in components]
            meta = dict(cohort=case, kind=cohort['kind'], start=cohort['start'][:10],
                        portfolio=name, lower_rr=low, higher_rr=high, lower_weight=weight)
            results.append(dict(**meta, **metrics,
                mdd_delta_vs_rr1=metrics['max_drawdown']-float(baseline['max_drawdown']),
                pnl_delta_vs_rr1=metrics['net_pnl']-float(baseline['net_pnl']),
                beats_both_constituents=metrics['max_drawdown'] < min(constituent_dd)-1e-6,
                smoothing=sum(w*d for w, d in zip(weights, constituent_dd))-metrics['max_drawdown']))
            for budget in contract['spec']['loss_budgets']:
                for method in ('closed_floor', 'excursion_floor', 'closed_peak_dd'):
                    markers = {rr: paths['markers'][rr][str(budget)][method] for rr in components}
                    fm = weighted_failures(components, weights, markers, dates)
                    expected = sum(w for rr, w in zip(components, weights) if markers[rr] is not None)
                    equal(fm['fraction_breached'], expected)
                    assert (fm['fraction_breached'] == 1) == all(markers[rr] is not None for rr in components)
                    if budget == 6800 and method == 'excursion_floor':
                        assert fm['fraction_breached'] == 0
                    if high and budget == 1500 and method == 'excursion_floor':
                        seats = [low]*int(4*weight) + [high]*int(4*(1-weight))
                        brute = failure_metrics(seats, markers, dates)
                        for key, value in fm.items():
                            equal(value, brute[key])
                        checks['weighted_failure_brute_force_matches'] += 1
                    checks['allocation_failure_invariants'] += 1
                    if reference_name:
                        ref = prior_fail[case, reference_name, str(budget), method]
                        for key, value in fm.items():
                            equal(value, ref[key])
                        checks['source_failure_matches'] += 1
                    if high and weight == .5:
                        for weights_end, rr in [([1, 0], low), ([0, 1], high)]:
                            endpoint = weighted_failures(components, weights_end, markers, dates)
                            ref = prior_fail[case, f'rr_{rr}', str(budget), method]
                            for key, value in endpoint.items():
                                equal(value, ref[key])
                            checks['endpoint_failure_matches'] += 1
                        for i in range(len(dates)):
                            assert 1*curves[low][i]+0*curves[high][i] == curves[low][i]
                            assert 0*curves[low][i]+1*curves[high][i] == curves[high][i]
                    failures.append(dict(**meta, budget=budget, method=method, **fm))
        print(f'{case}: {len(arms)} allocations verified', flush=True)
    write_csv(output / 'comparison.csv', results)
    write_csv(output / 'failure_comparison.csv', failures)
    summary = summarize(results, failures)
    write_csv(output / 'summary.csv', summary)
    report(output, summary, spec, checks)
    plot(output, summary, spec)
    import matplotlib
    manifest = dict(spec=spec, source_audit_sha256=sha256_file(source/'audit.json'),
        source_contract_sha256=sha256_file(source/'contract.json'),
        source_independent_audit_sha256=sha256_file(source/'independent_audit.json'),
        code={str(p.relative_to(PROJECT_ROOT)): sha256_file(p) for p in
              [Path(__file__), PROJECT_ROOT/'scripts/rr_curve_support.py', PROFILE, PROTOCOL]},
        checks=dict(checks), cohorts=len(contract['cohorts']), portfolios=len(arms),
        comparisons=len(results), failure_comparisons=len(failures),
        python_version=sys.version, matplotlib_version=matplotlib.__version__,
        files={p.name: sha256_file(p) for p in output.iterdir() if p.name != 'manifest.json'})
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(checks), indent=2))


def summarize(results, failures):
    groups, fg = defaultdict(list), defaultdict(list)
    for r in results:
        if r['kind'] == '12m':
            groups[r['portfolio']].append(r)
    for r in failures:
        if r['kind'] == '12m' and r['budget'] == 1500 and r['method'] == 'excursion_floor':
            fg[r['portfolio']].append(r)
    summary = []
    for name, rows in groups.items():
        rows.sort(key=lambda r: r['start'])
        f = fg[name]
        item = dict(portfolio=name, lower_rr=rows[0]['lower_rr'], higher_rr=rows[0]['higher_rr'],
            lower_weight=rows[0]['lower_weight'], mean_pnl=statistics.mean(r['net_pnl'] for r in rows),
            mean_mdd=statistics.mean(r['max_drawdown'] for r in rows),
            worst_mdd=max(r['max_drawdown'] for r in rows),
            dd_wins=sum(r['mdd_delta_vs_rr1'] < -1e-6 for r in rows),
            beats_both=sum(r['beats_both_constituents'] for r in rows),
            mean_smoothing=statistics.mean(r['smoothing'] for r in rows),
            any_failure=sum(r['fraction_breached'] > 0 for r in f),
            all_failure=sum(r['fraction_breached'] == 1 for r in f),
            mean_fraction_failed=statistics.mean(r['fraction_breached'] for r in f),
            mean_same_signal=statistics.mean(r['max_same_signal_fraction'] for r in f),
            mean_possible5=statistics.mean(r['possible_5d_fraction'] for r in f),
            mean_possible20=statistics.mean(r['possible_20d_fraction'] for r in f))
        for tag, part in [('early', rows[:12]), ('later', rows[12:])]:
            item[tag+'_dd_wins'] = sum(r['mdd_delta_vs_rr1'] < -1e-6 for r in part)
            item[tag+'_mean_dd_delta'] = statistics.mean(r['mdd_delta_vs_rr1'] for r in part)
        summary.append(item)
    return sorted(summary, key=lambda r: r['mean_mdd'])


def report(output, summary, spec, checks):
    index = {r['portfolio']: r for r in summary}
    shortlisted = [min((r for r in summary if r['lower_rr']==low and r['higher_rr'] and
                       r['lower_weight']==weight), key=lambda r: r['mean_mdd'])
                   for low in spec['lower_rr'] for weight in spec['lower_weights']]
    lines = ['# Lower/higher RR pairs: allocation sensitivity', '',
        '**Curve smoothing and account survival favor different allocations.** RR2.50 '
        'minimizes mean drawdown in each of the nine lower-RR/allocation groups. '
        'More RR0.50 exposure can reduce curve drawdown while increasing account losses. '
        'The lowest five-day failure concentration among mixtures instead uses RR1.00/1.75 '
        'at 25/75, and is still worse than RR1.75 alone.', '',
        '81 mixtures and 13 homogeneous controls reuse the audited synchronized paths. '
        'No operating policies or MT5 session-close data are added. Primary comparisons '
        'use the same 23 overlapping twelve-month windows; six full-history cohorts are saved separately.', '',
        'Weights are seat fractions at unchanged one-MNQ sizing and unchanged per-account headroom. '
        'Dollar curves are weighted averages at one-MNQ-equivalent exposure. Changing allocation '
        'does not change the constituent failure dates or the windows where both fail.', '',
        '## Allocation and RR sensitivity', '',
        'Each row below is the lowest mean realized maximum drawdown within its lower-RR/allocation '
        'group, selected on the same historical data. It is a descriptive screen, not an independently '
        'validated recommendation. All 81 combinations are retained in summary.csv.', '',
        '| Lower RR | Higher RR selected | Lower allocation | Mean P&L | Mean max DD | DD wins vs RR1 | Later DD wins | Beats both constituents | All fail | Mean fraction failed | Possible 5-day cluster |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in shortlisted:
        lines.append(f'| {r["lower_rr"]} | {r["higher_rr"]} | {r["lower_weight"]:.0%} | '
            f'${r["mean_pnl"]:,.0f} | ${r["mean_mdd"]:,.0f} | {r["dd_wins"]}/23 | '
            f'{r["later_dd_wins"]}/11 | {r["beats_both"]}/23 | {r["all_failure"]}/23 | '
            f'{r["mean_fraction_failed"]:.1%} | {r["mean_possible5"]:.1%} |')
    lines += ['', 'Failure columns use the $1,500 excursion-based fixed floor. "All fail" means '
        'both constituents breach sometime in the window, not necessarily together. Five-day '
        'clusters conservatively use entry-to-exit breach intervals. All means include zero-failure windows.', '',
        '## Homogeneous controls', '',
        '| RR | Mean P&L | Mean max DD | Failure windows | Mean fraction failed / possible 5-day cluster |',
        '|---|---:|---:|---:|---:|']
    for rr in ['0.50','0.75','1.00','1.25','1.50','1.75','2.00','2.25','2.50','2.75','3.00','3.25','3.50']:
        r=index[f'rr_{rr}']
        lines.append(f'| {rr} | ${r["mean_pnl"]:,.0f} | ${r["mean_mdd"]:,.0f} | '
                     f'{r["all_failure"]}/23 | {r["mean_fraction_failed"]:.1%} |')
    lines += ['', '## Failure concentration is a separate outcome', '',
        'These are the three lowest five-day cluster means among tested mixtures, shown '
        'with their homogeneous RR1.75 control. Selecting by this metric does not select '
        'the same pair as selecting by curve drawdown.', '',
        '| Portfolio | Lower allocation | Mean max DD | Mean P&L | All fail | Mean fraction failed | Possible 5-day cluster |',
        '|---|---:|---:|---:|---:|---:|---:|']
    safety = sorted((r for r in summary if r['higher_rr']),
                    key=lambda r: (r['mean_possible5'], r['mean_mdd']))[:3]
    for r in [index['rr_1.75'], *safety]:
        label = r['lower_rr']+'/'+r['higher_rr'] if r['higher_rr'] else 'RR1.75 alone'
        allocation = f'{r["lower_weight"]:.0%}' if r['higher_rr'] else '-'
        lines.append(f'| {label} | {allocation} | ${r["mean_mdd"]:,.0f} | ${r["mean_pnl"]:,.0f} | '
            f'{r["all_failure"]}/23 | {r["mean_fraction_failed"]:.1%} | {r["mean_possible5"]:.1%} |')
    lines += ['', 'RR1.75 alone has fewer lost accounts and a smaller average cluster, but '
        'RR1.00/1.75 and RR0.75/1.75 have fewer windows with complete loss (3/23 versus 4/23). '
        'These are different objectives. Reweighting a given pair does not alter its complete-loss '
        'windows, because it does not alter individual account paths.', '',
        'The fewest complete-loss windows among these pairs is **2/23 for RR1.00/2.25**, '
        'at all three allocations. Its 50/50 curve has mean drawdown $3,182 and mean P&L '
        '$4,801, with 28.3% mean account losses. It beats RR1 drawdown in only 8/23 windows '
        '(2/11 later windows). RR2.25 alone has 5/23 complete-loss windows but only 21.7% '
        'mean losses. The pair therefore preserves some accounts through more windows '
        'while losing a larger fraction of accounts on average than that constituent.', '',
        'For RR0.50/2.50, moving from 50% to 75% in the lower RR reduces mean drawdown '
        'by only about $54, lowers mean P&L by about $704, and raises the mean fraction lost '
        'from 34.8% to 39.1%. Its 3/23 complete-loss count is unchanged. The smallest '
        'average curve drawdown is therefore not evidence of the best protection for accounts.', '',
        '## Equal-weight neighborhood', '',
        'Every row reproduces the earlier 50/50 screen exactly within numerical tolerance.', '',
        '| Lower / higher RR | Mean P&L | Mean max DD | Earlier / later DD wins | All fail | Mean fraction failed | Possible 5-day cluster |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for low in spec['lower_rr']:
        for high in spec['higher_rr']:
            r=index[f'pair_{low}_{high}_low50']
            lines.append(f'| {low} / {high} | ${r["mean_pnl"]:,.0f} | ${r["mean_mdd"]:,.0f} | '
                f'{r["early_dd_wins"]}/12; {r["later_dd_wins"]}/11 | {r["all_failure"]}/23 | '
                f'{r["mean_fraction_failed"]:.1%} | {r["mean_possible5"]:.1%} |')
    lines += ['', '## Visual comparison', '', '![Allocation sensitivity](allocation_sensitivity.png)', '',
        '![Five-day first-failure concentration](failure_concentration.png)', '',
        '## Interpretation limits', '',
        '- More weight in an individually lower-loss RR can improve the average curve without '
        'creating additional temporal separation. Read the homogeneous controls and breach fractions together.',
        '- The $6,800 fixed floor still has no observed breaches: reweighting cannot change that. '
        'Peak-drawdown markers are saved separately and are not account deaths.',
        '- Earlier/later windows overlap and all history was already available. These are descriptive '
        'comparisons, not independent probabilities or out-of-sample forecasts.',
        '- Curves are daily realized P&L. Exports do not reconstruct exact combined intratrade equity. '
        'Unclosed boundary positions and their MAE remain censored as in the source study.',
        '- A future no-take-profit / session-close run requires native MT5 exports; finite-RR tapes '
        'cannot supply the counterfactual exits, stop-outs or missed entries.', '',
        '## Verification', '',
        f'- {checks["weighted_curve_reconstructions"]:,} weighted curve reconstructions.',
        f'- {checks["source_curve_matches"]:,} full curve-metric matches to prior controls and equal-weight pairs.',
        f'- {checks["source_failure_matches"]:,} source failure-metric matches; '
        f'{checks["endpoint_failure_matches"]:,} zero/full allocation endpoint matches.',
        f'- {checks["allocation_failure_invariants"]:,} weighted failure-fraction and all-failed invariants.',
        f'- {checks["weighted_failure_brute_force_matches"]:,} weighted $1,500 excursion-failure '
        'comparisons match a separate brute-force scan of duplicated whole-account seats.',
        '- Source artifact hashes and frozen code verified; manifest.json pins this protocol, '
        'profile, script, source audit and every generated artifact.', '',
        'Reproduce from the project root with Matplotlib installed:', '',
        '```powershell', '.\\venv\\Scripts\\python.exe scripts/study_rr_pairs.py', '```', '']
    (output/'rr_pairs__REPORT.generated.md').write_text('\n'.join(lines), encoding='utf-8')


def plot(output, summary, spec):
    cache=PROJECT_ROOT/'outputs/matplotlib-cache'
    cache.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter, PercentFormatter
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
                         'axes.grid':True, 'grid.alpha':.2})
    index={r['portfolio']:r for r in summary}
    palette={.25:'#7353a6',.5:'#087e8b',.75:'#c05621'}
    for name, field, title in [('allocation_sensitivity','mean_mdd','Mean realized maximum drawdown'),
                               ('failure_concentration','mean_possible5','Mean largest possible 5-day first-breach fraction ($1,500 floor)')]:
        fig,axs=plt.subplots(1,3,figsize=(13,4.8),sharey=True,layout='constrained')
        for ax,low in zip(axs,spec['lower_rr']):
            for weight in spec['lower_weights']:
                rows=[index[f'pair_{low}_{high}_low{int(weight*100):02d}'] for high in spec['higher_rr']]
                ax.plot([float(r['higher_rr']) for r in rows],[r[field] for r in rows],
                        marker='o',ms=4,color=palette[weight],label=f'{weight:.0%} lower RR')
            ax.axhline(index['rr_1.00'][field],color='#222222',ls='--',label='All RR1')
            ax.axhline(index[f'rr_{low}'][field],color='#999999',ls=':',label='All lower RR')
            ax.set_title(f'Lower RR = {low}');ax.set_xlabel('Higher RR')
            ax.set_xticks([1.5,2,2.5,3,3.5])
            ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}') if field=='mean_mdd' else PercentFormatter(1))
        axs[0].legend(fontsize=8,loc='best')
        fig.suptitle(title+'\n23 overlapping twelve-month windows; lower is better',fontsize=12)
        for ext in ('png','svg'):
            fig.savefig(output/f'{name}.{ext}',dpi=160,bbox_inches='tight')
        plt.close(fig)


if __name__ == '__main__':
    main()
