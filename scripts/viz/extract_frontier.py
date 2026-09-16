"""Build one JSON for the reserve_frontier_minimum visualization.

Reads the saved study files only (no re-simulation) and cross-checks the 20
detailed run folders against their frontier rows.

Usage: extract_frontier.py <dest json>
"""
from pathlib import Path
import csv, json, sys

STUDY = Path(r'I:\PycharmProjects\PA_milky_simplified\results\comparisons'
             r'\legacy_25k_vs_50k\reserve_frontier_minimum')
DEST = Path(sys.argv[1])

NUM = {'headroom', 'retained_balance_target', 'ongoing', 'terminal', 'total', 'accounts', 'alive',
       'evaluations', 'spend', 'ending_owner_cash', 'deaths', 'deaths_of_pas_at_least_one_year_old',
       'deaths_2026_03_30', 'largest_simultaneous_deaths', 'mature_pa_days', 'next_check_service',
       'replacement_wait_median_days', 'unfilled_account_days', 'zero_live_days',
       'average_live_accounts', 'average_retained_profit_per_live_pa', 'frozen_mean_balance_std_usd',
       'frozen_mean_distinct_balances', 'march30_pretrade_alive', 'replacements_unfilled',
       'terminal_profit_equity_before_withdrawal', 'book_wipes_from_at_least_five_live',
       'book_empty_transitions'}
KEEP = ['product', 'window', 'withdrawal'] + sorted(NUM)


def num(v):
    if v is None or v == '':
        return None
    f = float(v)
    return int(f) if f == int(f) and abs(f) < 1e15 else round(f, 4)


def rows(path):
    with (STUDY / path).open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


frontier = [{k: (num(r[k]) if k in NUM else r[k]) for k in KEEP} for r in rows('frontier.csv')]
print('frontier rows', len(frontier))

windows = [{k: (num(v) if k not in ('product', 'window', 'withdrawal', 'reserves_within_one_pct_best_ongoing') else v)
            for k, v in r.items()} for r in rows('window_summaries.csv')]
for w in windows:
    w['reserves_within_one_pct_best_ongoing'] = json.loads(w['reserves_within_one_pct_best_ongoing'])

similar = [{k: (v if k in ('product', 'window', 'within_tolerance') else num(v)) for k, v in r.items()}
           for r in rows('similar_capital.csv') if r['window'] == 'full']

# ---------------------------------------------------------------- detailed replays
days = None
runs = []
for folder in sorted(p for p in STUDY.iterdir() if p.is_dir()):
    product, rule, reserve = folder.name.split('__')
    headroom = int(reserve.removeprefix('reserve_'))
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    daily = list(csv.DictReader((folder / 'pipeline_daily.csv').open(encoding='utf-8')))
    at = [d['at'][:10] for d in daily]
    if days is None:
        days = at
    assert at == days, folder.name  # every detailed replay is the full window

    match = [r for r in frontier if r['product'] == product and r['window'] == 'full'
             and r['withdrawal'] == rule and r['headroom'] == headroom]
    assert len(match) == 1, folder.name
    for field in ('ongoing', 'total', 'alive', 'deaths', 'accounts'):
        assert match[0][field] == num(summary[field]), (folder.name, field)

    deaths_by_day = {}
    for d in csv.DictReader((folder / 'deaths.csv').open(encoding='utf-8')):
        key = d['died_at'][:10]
        deaths_by_day[key] = deaths_by_day.get(key, 0) + 1
    march = json.loads((folder / 'march30_balances.json').read_text(encoding='utf-8'))

    step = 7
    idx = sorted({*range(0, len(daily), step), len(daily) - 1})
    runs.append({
        'folder': folder.name, 'product': product, 'rule': rule, 'headroom': headroom,
        'retained_balance_target': num(summary['retained_balance_target']),
        'ongoing': num(summary['ongoing']), 'total': num(summary['total']),
        'alive': summary['alive'], 'deaths': summary['deaths'],
        'aged_deaths': summary['deaths_of_pas_at_least_one_year_old'],
        'zero_live_days': num(summary['zero_live_days']),
        'average_live_accounts': num(summary['average_live_accounts']),
        'march30_pretrade_alive': summary['march30_pretrade_alive'],
        'deaths_2026_03_30': summary['deaths_2026_03_30'],
        'largest_simultaneous_deaths': summary['largest_simultaneous_deaths'],
        'retained_per_live_pa': num(summary['average_retained_profit_per_live_pa']),
        'evaluations': summary['evaluations'], 'spend': num(summary['spend']),
        'sample_idx': idx,
        'alive_series': [int(daily[i]['alive']) for i in idx],
        'cash_series': [round(float(daily[i]['cash_usd'])) for i in idx],
        'deaths_by_day': sorted(deaths_by_day.items()),
        'march30': march,
    })
print('detailed runs', len(runs), 'days', len(days))

payload = {
    'meta': {
        'study': 'reserve_frontier_minimum',
        'path': str(STUDY),
        'products': sorted({r['product'] for r in frontier}),
        'windows': list(dict.fromkeys(r['window'] for r in frontier)),
        'rules': sorted({r['withdrawal'] for r in frontier}),
        'grid': sorted({r['headroom'] for r in frontier}),
        'runs': len(frontier),
        'first_day': days[0], 'last_day': days[-1],
    },
    'frontier': frontier,
    'windows': windows,
    'similar_capital': similar,
    'days': days,
    'detail': runs,
}
DEST.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
print('wrote', DEST, DEST.stat().st_size)
