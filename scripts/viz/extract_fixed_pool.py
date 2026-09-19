"""Flatten the fixed-R shared routing pool study into one JSON for its page.

Reads comparison.csv, study.json and <folder>__REPORT.generated.md. No re-simulation.

Usage: extract_fixed_pool.py <dest json>
"""
from pathlib import Path
import csv, json, sys

STUDY = Path(r'I:\PycharmProjects\PA_milky_simplified\results\legacy_25k\routing_fixed_pool')
DEST = Path(sys.argv[1])

NUM = {'accounts', 'alive', 'deaths', 'peak_live', 'copies', 'requested_copies', 'purchase_cost_usd',
       'ongoing_net_usd', 'terminal_received_usd', 'total_net_usd', 'start_year', 'R', 'initial_seats',
       'max_live_accounts', 'initial_seat_funding_usd', 'additional_external_funding_usd',
       'total_owner_funding_usd', 'shortfall_seats'}


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
        rows.append(row)

# the premises of the experiment, re-checked before anything is drawn
for r in rows:
    assert r['copies'] == r['requested_copies'], r['case']
    assert r['accounts'] == r['alive'] + r['deaths'], r['case']
    assert r['peak_live'] <= r['max_live_accounts'], r['case']
    assert r['initial_seats'] == 5 * r['R'], r['case']
    assert round(r['initial_seat_funding_usd'] + r['additional_external_funding_usd'], 2) == r['total_owner_funding_usd'], r['case']

study = json.loads((STUDY / 'study.json').read_text(encoding='utf-8'))
report = (STUDY / f'{STUDY.name}__REPORT.generated.md').read_text(encoding='utf-8')
intro = report.split('\n## ', 1)[0].split('\n', 1)[1]
paras = [' '.join(p.split()) for p in intro.split('\n\n') if p.strip()]

dims = {}
for key in ('start_year', 'withdrawal', 'R', 'arm'):
    dims[key] = sorted({r[key] for r in rows}, key=lambda v: (isinstance(v, str), v))

payload = {
    'meta': {
        'title': 'Fixed-R Routing Pools',
        'report_title': report.splitlines()[0].lstrip('# ').strip(),
        'path': 'legacy_25k/routing_fixed_pool',
        'cases': len({r['case'] for r in rows}), 'rows': len(rows),
        'generated_utc': study.get('generated_utc'),
        'verified_controls': study.get('verified_controls'),
        'capacity': study.get('capacity', {}),
        'live_cap': rows[0]['max_live_accounts'],
        'paragraphs': paras,
    },
    'dims': dims,
    'rows': rows,
}
DEST.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
print(f"cases {payload['meta']['cases']} rows {len(rows)} R {dims['R']} arms {dims['arm']} bytes {DEST.stat().st_size}")
print('title:', payload['meta']['report_title'], '| live cap', payload['meta']['live_cap'])
