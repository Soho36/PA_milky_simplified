"""Flatten a saved study's settings-and-outcomes rows into one JSON for the explorer page.

Reads saved study.json / CSV files only. No re-simulation.

Usage: extract_study.py <dest dir> [study key ...]
"""
from pathlib import Path
import csv, json, sys

RESULTS = Path(r'I:\PycharmProjects\PA_milky_simplified\results')

# key, folder, source, title, params, metrics, defaults
STUDIES = [
    dict(key='eval_supply', path='comparisons/legacy_25k_vs_50k/eval_supply',
         source=('study.json', 'rows'), title='Evaluation Supply Sweep',
         params=['product', 'initial_cash', 'monthly_funding', 'acquisition', 'spares', 'withdrawal', 'cadence', 'headroom'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'evaluations', 'evaluation_months',
                  'evaluation_resets', 'activated', 'evaluation_fees', 'activation_fees', 'cost_per_funded',
                  'max_passes_in_a_month', 'short_months', 'short_months_without_a_pass', 'spares_unused',
                  'in_flight_at_end', 'ending_owner_cash'],
         default=dict(x='headroom', y='total', color='withdrawal')),
    dict(key='reserve_by_policy', path='comparisons/legacy_25k_vs_50k/reserve_by_policy',
         source=('study.json', 'rows'), title='Reserve by Policy',
         params=['product', 'initial_cash', 'monthly_funding', 'acquisition', 'withdrawal', 'cadence',
                 'headroom', 'strict_post_payout_balance'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'reserve', 'ending_owner_cash'],
         default=dict(x='headroom', y='total', color='withdrawal')),
    dict(key='spare_shelf', path='comparisons/legacy_25k_vs_50k/spare_shelf',
         source=('study.json', 'rows'), title='Spare Shelf Sweep',
         params=['product', 'initial_cash', 'monthly_funding', 'acquisition', 'spares', 'passes',
                 'withdrawal', 'cadence', 'headroom'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'spares_unused', 'supply_limited', 'ending_owner_cash'],
         default=dict(x='spares', y='total', color='passes')),
    dict(key='pipeline_capacity', path='comparisons/legacy_25k_vs_50k/pipeline_capacity',
         source=('csv', 'all_settings.csv'), title='Pipeline Capacity Sweep',
         params=['product', 'withdrawal', 'cadence', 'headroom', 'persistent', 'interval', 'concurrency',
                 'spares', 'reserve_seats', 'initial_cash', 'monthly_funding'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'evaluations', 'deaths', 'spend',
                  'next_check_service', 'unfilled_account_days', 'average_live_accounts', 'zero_live_days',
                  'replacement_wait_median_days', 'replacement_wait_p95_days'],
         default=dict(x='headroom', y='ongoing', color='concurrency')),
    dict(key='reserve_frontier', path='comparisons/legacy_25k_vs_50k/reserve_frontier',
         source=('study.json', 'rows'), title='Maximum Reserve Frontier',
         params=['product', 'window', 'headroom'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'deaths',
                  'deaths_of_pas_at_least_one_year_old', 'deaths_2026_03_30', 'largest_simultaneous_deaths',
                  'average_live_accounts', 'zero_live_days', 'average_retained_profit_per_live_pa',
                  'unfilled_account_days', 'evaluations', 'spend'],
         default=dict(x='headroom', y='ongoing', color='window')),
    dict(key='operating_policies_50k', path='legacy_50k/operating_policies',
         source=('study.json', ['matched_controls', 'reserve_search', 'operating_policies', 'strict_sensitivity']),
         title='Legacy 50K Operating Policies',
         params=['set', 'product', 'initial_cash', 'monthly_funding', 'acquisition', 'withdrawal', 'cadence',
                 'headroom', 'strict_post_payout_balance'],
         metrics=['total', 'ongoing', 'terminal', 'accounts', 'alive', 'reserve', 'ending_owner_cash'],
         default=dict(x='headroom', y='total', color='acquisition')),
    dict(key='account_purchases', path='study__full_rulebook__RR__account_purchases__cash_budgets',
         source=('study.json', 'rows'), title='Account Purchases and Budgets',
         params=['purchase_policy', 'withdrawal_policy', 'initial_cash_usd', 'monthly_contribution_usd'],
         metrics=['combined_net_cash_usd', 'ongoing_net_cash_usd', 'terminal_received_usd', 'accounts_bought',
                  'alive_before_terminal', 'purchase_spend_usd', 'minimum_owner_cash_usd',
                  'cash_limited_decisions', 'capacity_limited_decisions', 'ending_owner_cash_usd'],
         default=dict(x='purchase_policy', y='combined_net_cash_usd', color='withdrawal_policy')),
    dict(key='monthly_replacements_cap20', path='study__full_rulebook__RR__monthly_replacements__cap_20__cash_budgets',
         source=('study.json', 'rows'), title='Monthly Replacements at Cap 20',
         params=['purchase_policy', 'withdrawal_policy', 'initial_cash_usd', 'monthly_contribution_usd'],
         metrics=['combined_net_cash_usd', 'ongoing_net_cash_usd', 'terminal_received_usd', 'accounts_bought',
                  'alive_before_terminal', 'average_live_accounts', 'days_below_cap', 'mean_wait_days',
                  'max_wait_days', 'replacement_purchases', 'unmatched_deaths', 'purchase_spend_usd'],
         default=dict(x='purchase_policy', y='combined_net_cash_usd', color='withdrawal_policy')),
    dict(key='withdrawal_cadence', path='study__full_rulebook__RR__withdrawal_cadence__monthly_purchases',
         source=('study.json', 'rows'), title='Withdrawal Cadence',
         params=['policy', 'cadence', 'retained_balance_usd', 'headroom_usd'],
         metrics=['combined_pocket_usd', 'ongoing_pocket_usd', 'terminal_received_usd', 'alive_before_terminal',
                  'ongoing_payouts', 'terminal_payouts', 'ceiling_capture', 'unextracted_usd',
                  'earnings_vs_benchmark_usd', 'delta_ongoing_vs_monthly_usd', 'delta_combined_vs_monthly_usd'],
         default=dict(x='headroom_usd', y='ongoing_pocket_usd', color='cadence')),
    dict(key='cadence_budgets_cap20', path='study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets',
         source=('study.json', 'rows'), title='Cadence and Budgets at Cap 20',
         params=['purchase_policy', 'withdrawal_policy', 'initial_cash_usd', 'monthly_contribution_usd'],
         metrics=['combined_net_cash_usd', 'ongoing_net_cash_usd', 'terminal_received_usd', 'accounts_bought',
                  'alive_before_terminal', 'purchase_spend_usd', 'minimum_owner_cash_usd',
                  'delta_ongoing_net_cash_usd_vs_monthly', 'delta_combined_net_cash_usd_vs_monthly'],
         default=dict(x='withdrawal_policy', y='combined_net_cash_usd', color='purchase_policy')),
    dict(key='amount_x_cushion', path='study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores',
         source=('study.json', 'rows'), title='Monthly Amount by Cushion',
         params=['policy', 'stage', 'retained_balance_usd', 'headroom_usd', 'trading_neutral'],
         metrics=['combined_pocket_usd', 'ongoing_pocket_usd', 'terminal_received_usd', 'alive_before_terminal',
                  'ongoing_payouts', 'terminal_payouts', 'ceiling_capture', 'unextracted_usd',
                  'profit_before_terminal_usd', 'earnings_vs_benchmark_usd'],
         default=dict(x='headroom_usd', y='ongoing_pocket_usd', color='policy')),
    dict(key='march_failure_review', path='comparisons/legacy_25k_vs_50k/march_failure_review',
         source=('csv', 'baselines.csv'), title='March Failure Review',
         params=['label', 'product', 'rule', 'reserve', 'first_check', 'pause_days'],
         metrics=['total', 'ongoing', 'terminal', 'alive_at_end', 'accounts', 'evaluations', 'pre_event_alive',
                  'deaths_on_event', 'event_deaths_replaced_in_30_days', 'event_deaths_still_unfilled',
                  'deaths', 'next_check_service', 'unfilled_account_days', 'zero_live_days', 'average_live_accounts'],
         default=dict(x='reserve', y='total', color='rule')),
]


def coerce(v):
    if v is None or v == '':
        return None
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        return round(v, 4) if isinstance(v, float) else v
    s = str(v).strip()
    if s in ('True', 'False'):
        return s
    try:
        f = float(s)
        return int(f) if f == int(f) and abs(f) < 1e15 else round(f, 4)
    except ValueError:
        return s


def load_rows(folder, source):
    kind, what = source
    if kind == 'csv':
        with (folder / what).open(encoding='utf-8') as f:
            return list(csv.DictReader(f)), what
    data = json.loads((folder / 'study.json').read_text(encoding='utf-8'))
    if isinstance(what, list):
        out = []
        for key in what:
            for r in data[key]:
                out.append({**r, 'set': key})
        return out, 'study.json (' + ', '.join(what) + ')'
    return data[what], f'study.json ({what})'


def headline(folder):
    p = folder / 'START_HERE.txt'
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8', errors='replace')
    if 'What we learned' in text:
        body = text.split('What we learned', 1)[1]
        body = body.split('How to interpret it', 1)[0]
        return ' '.join(body.split())
    return ''


def build(spec, dest):
    folder = RESULTS / spec['path']
    rows, source_label = load_rows(folder, spec['source'])
    cols, kinds = [], []
    for name in spec['params']:
        if any(name in r for r in rows[:50]):
            cols.append(name); kinds.append('param')
    for name in spec['metrics']:
        if any(name in r for r in rows[:50]):
            cols.append(name); kinds.append('metric')
    data = [[coerce(r.get(c)) for r in rows] for c in cols]

    values = {}
    for c, col in zip(cols, data):
        distinct = sorted({v for v in col if v is not None}, key=lambda v: (isinstance(v, str), v))
        if len(distinct) <= 60:
            values[c] = distinct
    numeric = {c: all(isinstance(v, (int, float)) or v is None for v in col) and any(v is not None for v in col)
               for c, col in zip(cols, data)}

    payload = {
        'meta': {'key': spec['key'], 'title': spec['title'], 'path': spec['path'], 'source': source_label,
                 'rows': len(rows), 'headline': headline(folder),
                 'default': spec['default']},
        'cols': cols, 'kinds': kinds, 'numeric': numeric, 'values': values, 'data': data,
    }
    out = dest / f"study_{spec['key']}.json"
    out.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
    print(f"{spec['key']:28} {len(rows):6,} rows  {len(cols):2} cols  {out.stat().st_size / 1024:8,.0f} KB  <- {source_label}")
    return out


if __name__ == '__main__':
    dest = Path(sys.argv[1])
    wanted = set(sys.argv[2:])
    for spec in STUDIES:
        if wanted and spec['key'] not in wanted:
            continue
        build(spec, dest)
