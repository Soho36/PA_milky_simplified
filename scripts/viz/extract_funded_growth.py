"""Flatten the funded-growth routing study into one JSON for its page.

Reads comparison.csv and REPORT.generated.md. No re-simulation.

Usage: extract_funded_growth.py <dest json>
"""
from pathlib import Path
import csv, json, sys

STUDY = Path(r'I:\PycharmProjects\PA_milky_simplified\results\legacy_25k\routing_funded_growth')
DEST = Path(sys.argv[1])

TEXT = {'case', 'arm', 'acquisition', 'routing'}


def num(v):
    f = float(v)
    return int(f) if f == int(f) and abs(f) < 1e15 else round(f, 6)


rows = []
with (STUDY / 'comparison.csv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        row = {}
        for k, v in r.items():
            if v in ('', None):
                row[k] = None
            elif k in TEXT:
                row[k] = v
            elif v in ('True', 'False'):
                row[k] = v == 'True'
            else:
                try:
                    row[k] = num(v)
                except ValueError:
                    row[k] = v
        rows.append(row)

cases = {}
for r in rows:
    cases.setdefault(r['case'], {})[r['arm']] = r

# the study's own comparison columns must agree with the arms as saved
for case, arms in cases.items():
    ref = arms.get('unlimited_reference')
    blocked = arms.get('blocked_copy')
    assert ref and blocked, case
    for r in arms.values():
        assert round(r['total_net_usd'] - ref['total_net_usd'], 2) == round(r['delta_total_vs_unlimited_usd'], 2), case
        assert round(r['total_net_usd'] - blocked['total_net_usd'], 2) == round(r['delta_total_vs_blocked_usd'], 2), case
        assert abs(r['copies'] / ref['copies'] - r['copies_vs_unlimited_ratio']) < 1e-6, case
        assert 0 <= r['signal_participation'] <= 1 and 0 <= r['requested_copy_coverage'] <= 1, case
        assert r['peak_live'] <= r['max_live_accounts'], case
        assert r['accounts'] == r['alive'] + r['deaths'], case

report = (STUDY / 'REPORT.generated.md')
paras = []
if report.exists():
    text = report.read_text(encoding='utf-8')
    intro = text.split('\n## ', 1)[0].split('\n', 1)[1]
    paras = [' '.join(p.split()) for p in intro.split('\n\n') if p.strip()]

dims = {}
for key in ('start_year', 'initial_cash_usd', 'monthly_contribution_usd', 'retained_balance_usd', 'arm'):
    dims[key] = sorted({r[key] for r in rows}, key=lambda v: (isinstance(v, str), v))

payload = {
    'meta': {
        'title': 'Funded Growth Routing',
        'path': 'legacy_25k/routing_funded_growth',
        'cases': len(cases), 'rows': len(rows),
        'live_cap': rows[0]['max_live_accounts'],
        'initial_accounts': rows[0]['initial_accounts'],
        'acquisition': rows[0]['acquisition'],
        'signals_loaded': rows[0]['signals_loaded'],
        'paragraphs': paras,
    },
    'dims': dims,
    'rows': rows,
}
DEST.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
print(f"cases {len(cases)} rows {len(rows)} arms {dims['arm']}")
print(f"dims: start {dims['start_year']} initial {dims['initial_cash_usd']} monthly {dims['monthly_contribution_usd']} retain {dims['retained_balance_usd']}")
print(f"paragraphs {len(paras)} | bytes {DEST.stat().st_size}")
