"""Build the human-readable reserve report from completed, sealed results."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/comparisons/legacy_25k_vs_50k/reserve_frontier'


def money(x):
    return f'${x:,.2f}'


def table(rows, columns):
    text = '| '+' | '.join(label for key, label, fmt in columns)+' |\n'
    text += '| '+' | '.join('---' for c in columns)+' |\n'
    for row in rows:
        text += '| '+' | '.join('n/a' if row[key] is None else fmt(row[key]) for key, label, fmt in columns)+' |\n'
    return text+'\n'


def main():
    study = json.loads((OUT/'study.json').read_text())
    audit = json.loads((OUT/'AUDIT.json').read_text())
    rows = study['rows']
    full = [r for r in rows if r['window'] == 'full']
    text = '# Fixed daily-maximum reserve frontier\n\n'
    text += (f"Completed {len(rows)} simulations: two products, eight historical windows, frozen pipelines. "
        'The primary model reserves a PA slot for every in-flight evaluation and requires activation '
        'at the first daily check after passing. An unaffordable pass is abandoned.\n\n'
        '**Finding:** the March 2026 survival cliff is a common loss affecting synchronized PA balances. '
        'The exact full-tape boundary is a retrospective diagnostic, not a dollar-precise operating recommendation. '
        'Above it, distinguish nearly flat total cash from declining ongoing cash.\n\n')
    text += '## Frozen design and meanings\n\n'
    text += ('Both products start with $5,000 and receive $200 in each later calendar month; one monthly growth order '
        'persists until filled, with death replacements taking priority. Live trading PAs + activated dormant spares '
        '+ in-flight evaluations cannot exceed 20. Both use at most 20 concurrent evaluation subscriptions and a '
        'target of two **already activated** spare PAs. New evaluation starts are spaced seven days apart for 25K '
        'and one day apart for 50K. These settings are frozen from the prior shared-seat daily-maximum search; '
        'they are not optimized again here.\n\n'
        'The reserve is the withdrawal target above the frozen failure floor, not a guaranteed minimum balance '
        'through subsequent losses. A $6,800 reserve means a $31,900 nominal balance target for 25K or $56,900 '
        'for 50K: $6,900 profit equity above starting balance, with a failure floor at +$100. '
        'Daily checks request the maximum permitted by the inherited payout model; they do not guarantee a payout every day.\n\n'
        'Ongoing net cash = received operating withdrawals after the split minus all evaluation and activation fees. '
        'Total net cash adds the model-permitted terminal withdrawal. Owner contributions are financing, not profit. '
        'Terminal profit equity is reported separately in the CSV and is not all necessarily withdrawable.\n\n'
        'The common reserve grid is $0–$10,000 in $1,000 steps, supplemented by $5,500–$8,000 in $100 steps. '
        'Full-tape diagnostics add $10 steps inside the known cliff and two cent-level checks inferred from the '
        'previous $6,700 failure. These extra points deliberately use hindsight.\n\n')
    text += '## March 30, 2026: the exact event\n\n'
    trace_rows = []
    for product in study['spec']['pipelines']:
        for h in (6700, 6780.1, 6780.11, 6800):
            folder = OUT/f'{product}__shared_seats__reserve_{h}'
            trace = list(csv.DictReader((folder/'march_trade_trace.csv').open(newline='')))
            event = [r for r in trace if r['trade_key'] == 'RR1.00:3-4:558:2084']
            assert len(event) == 20
            assert len({r['adverse_equity'] for r in event}) == 1
            trace_rows.append({'product': product, 'reserve': h, 'at': event[0]['at'],
                'before': float(event[0]['equity_before']), 'mae': float(event[0]['mae']),
                'adverse': float(event[0]['adverse_equity']),
                'floor': float(event[0]['floor_after']),
                'failed': sum(r['alive_after'] == 'False' for r in event)})
    text += table(trace_rows, [('product', 'Product', str), ('reserve', 'Reserve', money),
        ('before', 'Profit equity before trade / PA', money), ('mae', 'Trade MAE', money),
        ('adverse', 'Adverse profit equity / PA', money), ('floor', 'Failure floor', money),
        ('failed', 'PAs failing', str)])
    text += ('All rows refer to the same tape trade, `RR1.00:3-4:558:2084`, recorded at its '
        'exit on 2026-03-30 at 06:00. The intratrade breach itself has no finer timestamp in these exports. '
        'Touching the +$100 floor fails. The one-cent separation demonstrates the simulator threshold and '
        'rounding, not predictive precision. The $6,800 reserve leaves only $19.89 above the inferred '
        'minimum passing reserve in this replay.\n\n'
        'The accounts share the same trades and withdrawal rule. Once balances converge, twenty accounts '
        'do not provide twenty independent chances of surviving that loss. A count of twenty deaths here '
        'is one common shock, not twenty independent observations.\n\n')
    text += '## Full-history frontier\n\n'
    text += ('The highest **ongoing** net cash on the tested full-history grid occurs at **$5,700** for both '
        'products. That policy loses the established book in 2026. At $6,800, less cash has been received during '
        'operation, but all 20 trading PAs remain alive at the horizon, with much larger closing withdrawals. '
        'A reserve selected for survival is therefore a different choice from the best operating-cash result.\n\n')
    columns = [('headroom', 'Reserve', money), ('ongoing', 'Ongoing net', money),
        ('terminal', 'Closing cash', money), ('total', 'Total net', money), ('deaths', 'PA deaths', str),
        ('evaluations', 'Eval subscriptions', str), ('alive', 'PAs alive at end', str)]
    for product in study['spec']['pipelines']:
        text += f'### {product}\n\n'
        family = sorted((r for r in full if r['product'] == product), key=lambda r: r['headroom'])
        selected = [r for r in family if r['headroom'] in (0, 3000, 5000, 5700, 6000, 6500, 6700, 6800, 7000, 7100, 7500, 8000, 9000, 10000)]
        text += table(selected, columns)
        base = next(r for r in family if r['headroom'] == 6800)
        margin_rows = []
        for h in (7000, 7500, 8000):
            r = next(r for r in family if r['headroom'] == h)
            margin_rows.append({'headroom': h, 'margin': round(h-6780.11, 2),
                'ongoing_cost': round(base['ongoing']-r['ongoing'], 2),
                'terminal_change': round(r['terminal']-base['terminal'], 2),
                'total_change': round(r['total']-base['total'], 2),
                'retained': r['average_retained_profit_per_live_pa']})
        text += 'Cost of keeping extra cushion relative to $6,800, over the entire historical run:\n\n'
        text += table(margin_rows, [('headroom', 'Reserve', money), ('margin', 'Above observed passing boundary', money),
            ('ongoing_cost', 'Ongoing cash deferred/reduced', money), ('terminal_change', 'Change in closing cash', money),
            ('total_change', 'Change in total net', money), ('retained', 'Mean retained profit / live PA', money)])
        text += (f"At $6,800, the last PA death is **{base['last_death']}**, with "
            f"{base['deaths_of_pas_at_least_one_year_old']} deaths of PAs aged at least one year. "
            f"Mean retained profit is {money(base['average_retained_profit_book'])} across the live book, "
            f"or {money(base['average_retained_profit_per_live_pa'])} per live PA. "
            f"Mean actual floor headroom is {money(base['average_actual_cushion_per_live_pa'])} per live PA.\n\n")
    text += '## Replacement service and retained capital\n\n'
    chosen = sorted((r for r in full if r['headroom'] in (6700, 6800, 7500, 8000)),
                    key=lambda r: (r['product'], r['headroom']))
    text += table(chosen, [('product', 'Product', str), ('headroom', 'Reserve', money),
        ('replacement_wait_median_days', 'Completed wait median, days', str),
        ('replacement_wait_p95_days', 'Completed wait p95, days', str),
        ('replacements_unfilled', 'Unresolved replacements', str),
        ('unfilled_account_days', 'Unfilled replacement PA-days', str),
        ('average_retained_profit_book', 'Mean retained book profit', money)])
    text += ('Replacement waits are FIFO, measured from actual recorded PA death to replacement deployment. '
        'Median and p95 include only completed waits; unresolved counts and accumulated waiting days include '
        'censored deaths at the horizon. They must be read together. `vacant_capacity_days_including_startup` '
        'also counts seats not yet demanded during the gradual monthly build, so it is not interchangeable '
        'with replacement downtime.\n\n'
        'Retained capital integrates settled profit equity between trade settlements, payout settlements and '
        'daily decisions, before terminal liquidation. It excludes the nominal $25K/$50K balance and dormant '
        'spares with zero profit. Per-PA averages divide by actual live PA-days. Signed profit, positive-only '
        'profit, and actual drawdown headroom are separate CSV columns. Intratrade marked equity cannot be '
        'time-weighted from MAE/MFE exports because the intratrade timing is unknown.\n\n')
    text += '## Historical window sensitivity\n\n'
    text += ('The 2024 cold starts expose a higher boundary in 25K: one PA older than a year fails '
        'on March 24, 2026 with a $6,800 target. **$7,100 is the first common-grid reserve after which '
        'there are no aged-PA deaths** in those windows (only $100 resolution here). The 50K '
        '2026-containing windows reach that condition at $6,800. This is direct evidence that $6,800 '
        'is not a universal boundary even on the same historical tape.\n\n')
    window_rows = []
    for b in study['boundaries']:
        h = b['deaths_of_pas_at_least_one_year_old_stable_zero_from']
        r = next((r for r in rows if r['product'] == b['product'] and r['window'] == b['window'] and r['headroom'] == h), None)
        window_rows.append({**b,
            'deaths_of_pas_at_least_one_year_old_stable_zero_from': h if r and r['mature_pa_days'] > 0 else None,
            'all_deaths_at_boundary': r['deaths'] if r else None,
            'mature_exposure': r['mature_pa_days'] if r else None})
    text += table(window_rows, [('product', 'Product', str), ('window', 'Cold-start window', str),
        ('deaths_of_pas_at_least_one_year_old_stable_zero_from', 'No aged-PA deaths from tested reserve', money),
        ('all_deaths_at_boundary', 'All PA deaths at that reserve', str),
        ('mature_exposure', 'PA-days aged at least a year', str),
        ('best_ongoing_headroom', 'Best tested ongoing reserve', money)])
    text += ('The boundary column is the lowest **tested** reserve from which this and all higher tested reserves '
        'have no deaths of PAs aged at least 365 days. This separates established-account survival from fragile '
        'new accounts that have not accumulated their target cushion. It does not mean no deaths of any age. '
        'Read the exposure column: low mature exposure is weak evidence, and zero exposure provides none. '
        'The early two-year windows show n/a because their raw zero-death condition starts at a reserve '
        'where no PA lives long enough to enter the aged group; that is not evidence that a zero reserve is safe. '
        'The CSV also reports deaths after the first and second system years and their last dates.\n\n'
        'Each window restarts empty with the same cash and contribution schedule; there is no inherited PA '
        'inventory or equity. Annual cold starts end in July 2026. The three two-year windows run July 2020–June '
        '2022, July 2022–June 2024, and July 2024–June 2026. Trades entering before a start or exiting beyond a '
        'window are excluded. Comparisons are within windows; absolute cash differs with duration. '
        'These windows overlap and reuse data that informed the strategy and reserve search. They show '
        'historical sensitivity, not independent validation or future survival probabilities.\n\n')
    text += '## Activation assumptions and implementation checks\n\n'
    text += ('`shared_seats` is the requested conservative operating policy: reserve capacity before evaluations '
        'pass. It is stronger than merely enforcing a deadline; a deadline by itself does not make running '
        'evaluations occupy PA seats. The new `activate_on_first_check` option also eliminates indefinite '
        'waiting for activation cash. Its default remains off so previous studies preserve their behavior.\n\n'
        'Current official Legacy documentation permits passed evaluations to remain active with monthly '
        'renewal payments until PA payment. Its 48-hour wording concerns renewal refunds. '
        '[Legacy activation documentation](https://apextraderfunding.com/help-center/legacy-evaluation-accounts/how-to-activate-your-legacy-pa/). '
        'The newer EOD/Intraday products instead have a seven-calendar-day activation deadline. '
        '[New-product activation deadline](https://apextraderfunding.com/help-center/billing/pa-activation-process-deadline-explained/). '
        'A three-day deadline was not verified. These pages were checked on 2026-09-15; this study uses '
        'the requested first-daily-check assumption, not those current product rules.\n\n'
        'Historical evaluation sizing, fees, drawdown handling, payout restrictions and terminal interpretation '
        'remain those of the preceding Legacy study. Activation fees stay $125 for both products for comparability. '
        'The simulator is not a reconstruction of every historical or current firm rule.\n\n')
    cash_changed = [r for r in full if r['passes_forfeited_cash']]
    text += (f"In {len(cash_changed)} full-history settings a passed evaluation was forfeited for lack of activation cash. "
        'These effects can move results relative to the older free-wait model and make reserve responses nonmonotonic. '
        'Per-setting forfeits, subscription resets, monthly fees and activation delays are in `frontier.csv`.\n\n'
        f"All {audit['runs']} runs reconcile cash and economics and obey the reserved-seat cap. "
        f"{len(audit['historical_controls'])} inherited-policy controls reproduce every shared saved field. "
        f"Eight detailed trace replays match their frontier rows. {audit['protected_files_unchanged']} "
        'pre-existing result files are unchanged. The contract records input, engine, runner and configuration hashes '
        'and rejects a resume under changed assumptions.\n\n')
    text += ('An output-only repair omitted the nested date-keyed daily P&L dictionary from the flat death CSV. '
        '`OUTPUT_EXPORT_FIX.json` verifies that this was the sole source change, that all numerical functions '
        'are unchanged, and that the completed checkpoint was preserved. The original runner and contract '
        'are archived alongside the repair record.\n\n')
    text += ('## How to use these results\n\n'
        'Treat the observed threshold as a historical stress level. Compare a margin above it against cash deferred '
        'and replacement losses, rather than choosing the best cent from this tape. A flat total-cash curve alone '
        'does not establish a flat operating-cash curve. Keep newborn-account survival and evaluation financing '
        'separate from the mature-account cushion question.\n\n'
        'A further robustness test should perturb the loss sequence while preserving blocks of trades and common '
        'shocks across PAs, and test execution/commission stress under frozen policies. Shuffling each PA '
        'independently would erase the synchronized failure risk found here. Any such resampling remains a '
        'stress experiment; a genuinely untouched future period is needed for out-of-sample evidence.\n\n'
        'Files: [complete frontier](frontier.csv), [window boundaries](boundaries.csv), '
        '[machine-readable study](study.json), [audit](AUDIT.json). Detail folders contain the March trade '
        'trace, PA deaths, evaluation histories, replacement waits and daily pipeline states.\n')
    (OUT/'REPORT.md').write_text(text, encoding='utf-8')
    print(OUT/'REPORT.md')


if __name__ == '__main__':
    main()
