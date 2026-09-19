"""Flatten a matched-exposure routing study into one JSON for its page.

Reads comparison.csv, study.json and <folder>__REPORT.generated.md. No re-simulation.

Usage: extract_routing.py <study folder name> <dest json>
   e.g. extract_routing.py routing_capacity_reuse routing.json
"""
from pathlib import Path
import csv, json, sys

ROOT = Path(r'I:\PycharmProjects\PA_milky_simplified\results\legacy_25k')
FOLDER = sys.argv[1]
STUDY = ROOT / FOLDER
DEST = Path(sys.argv[2])

NUM = {'accounts', 'alive', 'deaths', 'peak_live', 'copies', 'purchase_cost_usd', 'ongoing_net_usd',
       'terminal_received_usd', 'total_net_usd', 'start_year', 'initial_cash_usd',
       'monthly_contribution_usd', 'reference_copies', 'emergency_seats', 'extra_purchase_cost_usd',
       'additional_external_funding_usd', 'delta_ongoing_usd', 'delta_total_usd',
       'previous_accounts', 'previous_total_net_usd', 'delta_vs_previous_routed_usd', 'shortfall_seats'}


def num(v):
    f = float(v)
    return int(f) if f == int(f) and abs(f) < 1e15 else round(f, 2)


rows = []
with (STUDY / 'comparison.csv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        row = {}
        for k, v in r.items():
            if k == 'demand_sha256':
                continue
            row[k] = None if v in ('', None) else (num(v) if k in NUM else v)
        row['exceeds_20_live'] = row.get('exceeds_20_live') == 'True'
        row['copies_matched'] = row['copies'] == row['reference_copies']
        rows.append(row)

study = json.loads((STUDY / 'study.json').read_text(encoding='utf-8'))
report = (STUDY / f'{STUDY.name}__REPORT.generated.md').read_text(encoding='utf-8')
title_line = report.splitlines()[0].lstrip('# ').strip()
intro = report.split('\n## ', 1)[0].split('\n', 1)[1]
paras = [' '.join(p.split()) for p in intro.split('\n\n') if p.strip()]

refs = {r['case']: r for r in rows if r['arm'] == 'reference'}
assert refs, 'no reference arm'
assert all(r['copies_matched'] for r in rows), 'a routed arm did not match reference copies'
for r in rows:
    if r['arm'] != 'reference':
        assert round(r['total_net_usd'] - refs[r['case']]['total_net_usd'], 2) == r['delta_total_usd'], r['case']

dims = {}
for key in ('start_year', 'initial_cash_usd', 'monthly_contribution_usd', 'purchase_policy', 'withdrawal', 'arm'):
    dims[key] = sorted({r[key] for r in rows}, key=lambda v: (isinstance(v, str), v))

has_prev = any(r.get('previous_accounts') is not None for r in rows)
payload = {
    'meta': {
        'title': 'Matched-Exposure Routing',
        'report_title': title_line,
        'path': f'legacy_25k/{FOLDER}',
        'cases': len(refs), 'rows': len(rows),
        'generated_utc': study.get('generated_utc'),
        'verified_controls': study.get('verified_controls'),
        'capacity': study.get('capacity', {}),
        'paragraphs': paras,
        'has_previous': has_prev,
        'procurement': sorted({r['procurement'] for r in rows if r.get('procurement')}),
    },
    'dims': dims,
    'rows': rows,
}
DEST.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
print(f'{FOLDER}: cases {len(refs)} rows {len(rows)} prev_cols {has_prev} bytes {DEST.stat().st_size}')
print('report title:', title_line)
print('procurement:', payload['meta']['procurement'])
