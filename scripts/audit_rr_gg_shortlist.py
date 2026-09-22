"""Reconstruct shortlist weights and continuity from saved evidence."""
from collections import Counter
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'results/legacy_25k/rr_gg_shortlist'


def read(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((ROOT / 'audit.json').read_text())
    contract = json.loads((ROOT / 'contract.json').read_text())
    assert sha(ROOT / 'contract.json') == audit['contract_sha256']
    for name, digest in audit['files'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in contract['code'].items():
        assert sha(BASE / name) == digest, name
    components = {(r['case'], r['arm']): r['breached'] == 'True' for r in read('isolation_components.csv')}
    daily = read('isolation_daily.csv')
    checks = Counter()
    for r in read('isolation_quarters.csv'):
        members = contract['arms'][r['portfolio']]
        failed = sum(components[r['case'], a] for a in members)
        assert int(r['failed_groups']) == failed
        assert abs(float(r['failed_fraction']) - failed / len(members)) < 1e-10
        assert (r['full_loss'] == 'True') == (failed == len(members))
        values = []
        for d in daily:
            if d['case'] == r['case']:
                value = statistics.mean(float(d[a]) for a in members)
                assert abs(value - float(d[r['portfolio']])) < 1e-7
                values.append(value)
        peak = dd = 0.0
        for value in values:
            peak = max(peak, value)
            dd = max(dd, peak - value)
        assert abs(values[-1] - float(r['net_pnl'])) < 1e-7
        assert abs(dd - float(r['max_drawdown'])) < 1e-7
        checks['quarter_weights_markers_curves'] += 1
    cases = read('operating_comparison.csv')
    for r in cases:
        evidence = json.loads((ROOT / 'operating_cases' / (r['case'] + '.json')).read_text())
        accounts = evidence['accounts']
        end = datetime.fromisoformat(r['tape_last_exit'])
        order = r['assignment_order'].split(';')
        intervals = sorted((datetime.fromisoformat(a['activated_at']),
                            datetime.fromisoformat(a['died_at']) if not a['alive'] else end)
                           for a in accounts)
        union = []
        for start, stop in intervals:
            if union and start <= union[-1][1]:
                union[-1][1] = max(stop, union[-1][1])
            else:
                union.append([start, stop])
        alive = sum(a['alive'] for a in accounts)
        wipes = max(0, len(union) - 1) + int(bool(union) and alive == 0)
        empty = sum((b[0] - a[1]).total_seconds() / 86400 for a, b in zip(union, union[1:]))
        if union:
            empty += (end - union[-1][1]).total_seconds() / 86400
        assert wipes == int(r['book_wipeouts']), r['case']
        assert abs(empty - float(r['days_empty_after_first_activation'])) < .000051, r['case']
        assert (r['continuous_after_activation'] == 'True') == (bool(accounts) and wipes == 0)
        assert int(r['alive']) == alive
        assert int(r['deaths']) == len(accounts) - alive
        assert abs(float(r['receipts']) - float(r['acquisition_costs']) - float(r['net_operating_cash'])) < .001
        # Replay assignments using only account lifetimes, without the routing code.
        for i, a in enumerate(accounts):
            at = a['activated_at']
            live = Counter(b['arm'] for b in accounts[:i]
                           if b['alive'] or b['died_at'] > at)
            expected = min(order, key=lambda arm: live[arm])
            assert a['arm'] == expected, (r['case'], a['account_id'], a['arm'], expected)
        for day in evidence['daily_occupancy']:
            assert sum(day[a] for a in order) == day['alive'] <= 20
        checks['operating_interval_union_and_assignments'] += 1
    assert checks['quarter_weights_markers_curves'] == 208
    assert checks['operating_interval_union_and_assignments'] == 120
    output = dict(status='passed', checks=dict(checks), source_audit_sha256=sha(ROOT / 'audit.json'),
                  auditor_sha256=sha(Path(__file__)))
    (ROOT / 'verification').mkdir(exist_ok=True)
    (ROOT / 'verification/audit.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
