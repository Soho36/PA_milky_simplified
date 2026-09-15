"""Readable paired-policy interpretation from the completed frontier."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/comparisons/legacy_25k_vs_50k/reserve_frontier_minimum'


def cash(v):
    return f'${v:,.2f}'


def table(rows, cols):
    text = '| '+' | '.join(label for key, label, fmt in cols)+' |\n'
    text += '| '+' | '.join('---' for col in cols)+' |\n'
    for r in rows:
        text += '| '+' | '.join('n/a' if r[key] is None else fmt(r[key]) for key, label, fmt in cols)+' |\n'
    return text+'\n'


def main():
    study = json.loads((OUT/'study.json').read_text())
    audit = json.loads((OUT/'AUDIT.json').read_text())
    rows = study['rows']
    full = [r for r in rows if r['window'] == 'full']
    summaries = study['window_summaries']
    full_summary = [s for s in summaries if s['window'] == 'full']
    text = '# Daily minimum versus maximum: matched reserve frontier\n\n'
    text += (f"Completed {len(rows):,} simulations, equally split between daily minimum and maximum withdrawals, "
        'on identical reserve grids and eight historical windows. Product-specific pipelines and owner funding '
        'are frozen to the prior maximum-frontier settings.\n\n')
    text += ('The main finding is two different reserve regions. Daily minimum has a broad full-history '
        'ongoing-cash plateau around $4,000, but accounts still die there and the book ends partly empty. '
        'Preserving established accounts instead requires roughly $6,700–$7,000 in the windows that include '
        'the March 2026 losses. Minimum does preserve different account balances, but it does not remove '
        'the shared loss exposure or consistently lower the survival boundary.\n\n')
    text += '## Full-history findings\n\n'
    text += table(full_summary, [('product', 'Product', str), ('withdrawal', 'Daily request', str),
        ('best_ongoing_headroom', 'Best tested ongoing reserve', cash), ('best_ongoing', 'Ongoing net', cash),
        ('best_ongoing_alive', 'PAs alive at that reserve', str), ('best_ongoing_deaths', 'All deaths', str),
        ('aged_pa_survival_boundary', 'Tested aged-PA survival boundary', cash)])
    for p in study['reference_spec']['pipelines']:
        a = next(s for s in full_summary if s['product'] == p and s['withdrawal'] == 'minimum')
        b = next(s for s in full_summary if s['product'] == p and s['withdrawal'] == 'maximum')
        text += (f"For {p}, the best tested minimum-policy ongoing cash exceeds the best tested maximum-policy "
            f"ongoing cash by {cash(a['best_ongoing']-b['best_ongoing'])}. Their winning reserves and survival "
            'outcomes differ; this is a comparison of the best settings on the common grid, not a same-reserve effect.\n\n')
    text += ('The aged-PA boundary is the lowest tested reserve from which that reserve and all higher tested '
        'reserves have zero deaths of accounts at least 365 days old, with positive exposure of such accounts. '
        'It is not a no-failure boundary for new PAs, which must first earn their cushion. A missing value '
        'means the tested grid does not establish that condition.\n\n'
        'These pipelines differ from some winners in the broader pipeline search. In particular, the old '
        '25K daily-minimum winner used batched starts, concurrency 10 and a spare target of 10. Here 25K '
        'keeps the maximum study’s seven-day start spacing, concurrency 20 and spare target 2. The old '
        '$597,317 result should not be treated as a control for this different pipeline.\n\n')
    text += '![Paired reserve curves](paired_reserve_frontier.png)\n\n'
    text += '## Fixed-reserve comparisons\n\n'
    selected_h = (3700, 3900, 4000, 5700, 6000, 6500, 6600, 6700, 6800, 7100, 7500)
    for p in study['reference_spec']['pipelines']:
        text += f'### {p}\n\n'
        chosen = sorted([r for r in full if r['product'] == p and r['headroom'] in selected_h],
                        key=lambda r: (r['headroom'], r['withdrawal']))
        text += table(chosen, [('headroom', 'Reserve above floor', cash), ('withdrawal', 'Daily rule', str),
            ('ongoing', 'Ongoing net', cash), ('terminal', 'Closing receipt', cash), ('total', 'Total net', cash),
            ('alive', 'PAs alive', str), ('deaths', 'All deaths', str),
            ('deaths_of_pas_at_least_one_year_old', 'Aged-PA deaths', str)])
    text += ('Net cash is after payout splits and all evaluation/activation spending. It excludes owner '
        'contributions. Ongoing net subtracts all costs from operating receipts; total adds the final permitted '
        'withdrawal. The same trajectory produces both scores. End-of-run profit equity is a separate CSV '
        'column and should not be confused with the permitted closing receipt.\n\n')
    text += '## How wide is the cash plateau?\n\n'
    text += table(full_summary, [('product', 'Product', str), ('withdrawal', 'Rule', str),
        ('reserves_within_one_pct_best_ongoing', 'Tested reserves within 1% of best ongoing cash',
         lambda values: ', '.join(f'${v:,}' for v in values))])
    text += ('These are discrete tested values, not continuous intervals or confidence bands. A near-best '
        'cash reserve can still lose the whole established book. The most profitable reserve is not necessarily '
        'the reserve that best preserves earning capacity.\n\n')
    text += '## Balance dispersion and the March event\n\n'
    chosen = sorted([r for r in full if r['headroom'] in (6500, 6700, 6800)],
                    key=lambda r: (r['product'], r['headroom'], r['withdrawal']))
    text += table(chosen, [('product', 'Product', str), ('headroom', 'Reserve', cash),
        ('withdrawal', 'Rule', str), ('march30_pretrade_alive', 'Live before March 30 trade', str),
        ('march30_pretrade_distinct', 'Different profit balances', str),
        ('deaths_2026_03_30', 'Deaths on March 30', str),
        ('frozen_mean_balance_std_usd', 'Mean spread among frozen-floor PAs', cash),
        ('frozen_identical_balance_fraction', 'Time all frozen-floor balances identical', lambda x: f'{x:.1%}')])
    text += ('Minimum asks for $500 when eligible; maximum asks for all permitted excess above the target. '
        'Daily checks do not guarantee daily payouts. Fixed-size withdrawals can preserve residual balance '
        'differences while maximum withdrawals can reset accounts to the same target. Minimum also retains '
        'more money on some paths, so the fixed-reserve comparison measures both effects together.\n\n'
        'Spread is the cross-account population standard deviation, averaged over event time. The frozen-floor '
        'group contains only live PAs whose failure floor has stopped trailing, reducing the influence of '
        'brand-new accounts. Periods with fewer than two qualifying PAs are excluded from the spread and '
        'synchronization denominators, and their exposure days are reported. The age-based survival measure '
        'and frozen-floor dispersion group are deliberately different concepts. All PAs still share the same '
        'trades; different balances do not create independent trading returns.\n\n'
        'The March 30 final trade’s adverse excursion was $81.50. The previously measured $6,780.10–$6,780.11 '
        'cliff reflects earlier accumulated losses plus that last excursion, not a single huge trade. Zero '
        'deaths on March 30 can also mean the book died earlier; read the pre-trade live count and lifetime '
        'death measures together.\n\n')
    text += '## Comparison at similar actual retained capital\n\n'
    matches = [r for r in study['similar_capital'] if r['window'] == 'full' and
               r['minimum_reserve'] in (3700, 3900, 4000, 6000, 6500, 6700, 6800, 7100, 7500)]
    text += table(matches, [('product', 'Product', str), ('minimum_reserve', 'Minimum reserve', cash),
        ('maximum_reserve', 'Nearest maximum reserve', cash),
        ('per_pa_capital_gap_pct', 'Per-PA capital gap %', str), ('book_capital_gap_pct', 'Book capital gap %', str),
        ('within_tolerance', 'Both within 5%', lambda x: 'yes' if x else 'no'),
        ('minimum_ongoing', 'Minimum ongoing', cash), ('maximum_ongoing', 'Maximum ongoing', cash),
        ('minimum_alive', 'Minimum survivors', str), ('maximum_alive', 'Maximum survivors', str)])
    text += ('For every minimum setting with positive average retained profit, select the maximum setting '
        'in the same product/window minimizing the sum of relative differences in average book profit and '
        'average profit per live PA. A pair is flagged comparable only when both differences are at most 5%, '
        'relative to minimum. No interpolation or invented reserve is used.\n\n'
        'This is an outcome-based descriptive match, not a controlled causal experiment. Similar lifetime '
        'average capital does not guarantee the same capital immediately before a shock, the same account '
        'ages, or the same payout history. It can show whether a difference persists at roughly similar '
        'retention, but cannot assign a percentage of the benefit to desynchronization.\n\n')
    for p in study['reference_spec']['pipelines']:
        m = next(r for r in matches if r['product'] == p and r['minimum_reserve'] == 6800)
        text += (f"For {p}, minimum at $6,800 matches maximum at {cash(m['maximum_reserve'])} within "
            f"{m['per_pa_capital_gap_pct']:.2f}% per PA and {m['book_capital_gap_pct']:.2f}% for the book. "
            f"Minimum delivers {cash(m['minimum_ongoing']-m['maximum_ongoing'])} more ongoing net cash; "
            f"both finish with {m['minimum_alive']} live PAs. This supports examining payout timing and "
            'balance differences further, while retaining the limitations of average-capital matching.\n\n')
    text += '## Replacement demand and retained profit\n\n'
    chosen = sorted([r for r in full if r['headroom'] in (3900, 6700, 6800, 7100)],
                    key=lambda r: (r['product'], r['headroom'], r['withdrawal']))
    text += table(chosen, [('product', 'Product', str), ('headroom', 'Reserve', cash),
        ('withdrawal', 'Rule', str), ('evaluations', 'Eval subscriptions', str),
        ('replacement_wait_median_days', 'Completed median wait, days', str),
        ('replacement_wait_p95_days', 'Completed p95 wait, days', str),
        ('replacements_unfilled', 'Unfilled replacements at end', str),
        ('unfilled_account_days', 'Unfilled replacement PA-days', str),
        ('average_retained_profit_per_live_pa', 'Mean retained profit / live PA', cash)])
    text += ('Median and p95 use completed replacement waits only. Unresolved counts and accumulated '
        'replacement PA-days include censored waits through the horizon. Unused capacity during startup '
        'is reported separately from unmet replacement demand. Actual retained profit integrates settled '
        'equity between trade, payout and decision events. It excludes nominal $25K/$50K balances and is '
        'not a reconstructed intratrade marked-equity path.\n\n')
    text += '## Historical window sensitivity\n\n'
    for p in study['reference_spec']['pipelines']:
        pairs = [(a, next(b for b in summaries if b['product'] == p and b['window'] == a['window']
                         and b['withdrawal'] == 'maximum'))
                 for a in summaries if a['product'] == p and a['withdrawal'] == 'minimum']
        wins = sum(a['best_ongoing'] > b['best_ongoing'] for a, b in pairs)
        losses = ', '.join(a['window'] for a, b in pairs if a['best_ongoing'] < b['best_ongoing'])
        text += (f"For {p}, minimum wins on best tested ongoing cash in {wins} of {len(pairs)} windows. "
            f"Maximum wins in {losses}. These are comparisons after separately selecting each mechanism's "
            'best reserve within each window, not the performance of one fixed reserve across all windows.\n\n')
    text += ('In the January 2023 cold start, both products need $7,000 under minimum versus $6,800 '
        'under maximum to meet the aged-PA survival criterion. Consequently, the full-history 50K '
        '$6,700 minimum-policy boundary is not stable across starting dates.\n\n')
    text += table(summaries, [('product', 'Product', str), ('window', 'Window', str),
        ('withdrawal', 'Daily rule', str), ('best_ongoing_headroom', 'Best ongoing reserve', cash),
        ('best_ongoing', 'Best ongoing net', cash),
        ('aged_pa_survival_boundary', 'Aged-PA survival boundary', cash),
        ('all_deaths_at_boundary', 'All deaths at boundary', str),
        ('mature_pa_days_at_boundary', 'Aged PA-days at boundary', str)])
    text += ('The full history runs January 2020–July 2026. Annual cold starts begin in 2021, 2022, 2023 '
        'and 2024 and end at the same July 2026 horizon. Three two-year windows start in July 2020, July '
        '2022 and July 2024. Every window starts empty with fresh funding and no inherited account equity. '
        'No trade entering before the start or exiting beyond the end is imported.\n\n'
        'These overlapping windows reuse the same history that informed earlier choices. They measure '
        'historical sensitivity, not independent validation or future survival probabilities. No new market '
        'paths or replacement-supply outages are generated in this frontier; those require a separate paired '
        'stress experiment.\n\n')
    text += ('The useful next comparison is a small, preselected stress set: minimum at $4,000 for cash '
        'extraction and around $7,000–$7,500 for established-account survival, with matched maximum controls. '
        'Apply the same replacement interruptions and adverse trade sequences to both mechanisms, and '
        'compare cash, book recovery and capital immediately before each shock. That would test whether '
        'the attractive lower-reserve cash result depends on favorable replacement timing. This frontier '
        'alone does not answer that counterfactual or establish a live trading reserve.\n\n')
    text += '## Frozen assumptions and validation\n\n'
    text += ('Both products use $5,000 initial funding plus $200 per later month, persistent monthly growth '
        'demand, a 20-seat reservation limit, concurrency 20 and two activated spare PAs as the shelf target. '
        'New evaluations start at most every seven days for 25K and every day for 50K. Evaluations reserve '
        'future PA capacity and passed evaluations must activate at the next daily check or be forfeited. '
        'The study keeps the earlier Legacy fees, exposure, payout interpretation and trade-path convention. '
        'This is an operating model, not a reconstruction of all historical firm rules.\n\n'
        'The common grid is $0–$10,000 in $1,000 steps, with $100 steps from $3,000–$4,500 and '
        '$6,000–$7,500, plus the earlier $5,700 maximum-policy winner. The grid has 40 reserves for '
        'each of two products, two mechanisms and eight windows. There is no pipeline retuning or '
        'post-result expansion of the grid.\n\n')
    text += (f"All {audit['runs']:,} runs reconcile economic and owner-cash identities and obey the seat cap. "
        f"{len(audit['maximum_controls'])} maximum-policy rows reproduce every shared numerical field "
        'from the previous frontier. The matched March-review cases also reproduce their cash and survival '
        f"results. {audit['detail_replays_matched']} detailed replays match their frontier rows. "
        f"{audit['prior_result_files_unchanged']} prior result files are unchanged; plain-language navigation "
        'guides may be refreshed separately.\n\n')
    text += ('Files: [all settings](frontier.csv), [same-reserve differences](matched_reserves.csv), '
        '[similar-capital comparisons](similar_capital.csv), [window summaries](window_summaries.csv), '
        '[complete study](study.json), [audit](AUDIT.json). The detailed run folders hold March traces, '
        'account deaths, replacement waits and daily pipeline states. Each has a START_HERE.txt guide.\n')
    (OUT/'REPORT.md').write_text(text, encoding='utf-8')
    print(OUT/'REPORT.md')


if __name__ == '__main__':
    main()
