"""Classify every empty-book episode in the permutation study and group by first sleeve.

Wipeout classification reuses rr_followup's own definition: an episode counts as a
startup failure when the book had never held five live PAs before it.
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from study_rr_diversification import write_csv

ROOT = PROJECT_ROOT/'results/legacy_25k/wide4_permutations'


def episodes(case):
    """Empty-book episodes with the peak live count that preceded each one."""
    events = Counter()
    for a in case['accounts']:
        events[datetime.fromisoformat(a['activated_at'])] += 1
        if not a['alive']:
            events[datetime.fromisoformat(a['died_at'])] -= 1
    ordered = sorted(events.items())
    live = peak = 0
    out = []
    for i, (at, delta) in enumerate(ordered):
        after = live + delta
        if live > 0 and after == 0:
            reopened = next((t for t, d in ordered[i+1:] if d > 0), None)
            out.append(dict(at=at.isoformat(), live_before_final_loss=live,
                max_live_ever_before=peak,
                startup=peak < 5,
                reopened_at=reopened.isoformat() if reopened else None,
                days_until_reopening=(reopened-at).total_seconds()/86400 if reopened else None))
        peak = max(peak, after); live = after
    return out


def main():
    audit = json.loads((ROOT/'audit.json').read_text())
    spec = json.loads((PROJECT_ROOT/'config/studies/legacy_25k_wide4_permutations.json').read_text())
    order = {k: [d['rr'] for d in v] for k, v in spec['arms'].items()}
    cases = {}
    for name, digest in audit['case_sha256'].items():
        f = ROOT/'cases'/f'{name}.json'
        assert sha256_file(f) == digest, f'case file changed since the audit: {name}'
        cases[name] = json.loads(f.read_text())
    detail = []
    per_run = defaultdict(lambda: dict(startup=0, mature=0))
    for name, case in cases.items():
        row = case['row']
        for e in episodes(case):
            detail.append(dict(case=name, portfolio=row['portfolio'], phase=row['phase'],
                               start_year=row['start_year'], first_sleeve=order[row['portfolio']][0],
                               assignment_order='/'.join(order[row['portfolio']]), **e))
            if row['phase'] == 'operating':
                per_run[name]['startup' if e['startup'] else 'mature'] += 1
    write_csv(ROOT/'wipeout_events.csv', detail)
    per_perm = defaultdict(lambda: dict(startup=0, mature=0, clean=0, empty=0.0, deaths=0))
    for name, case in cases.items():
        row = case['row']
        if row['phase'] != 'operating':
            continue
        p = per_perm[row['portfolio']]
        p['startup'] += per_run[name]['startup']; p['mature'] += per_run[name]['mature']
        p['clean'] += int(row['book_wipeouts'] == 0)
        p['empty'] += row['days_empty_after_first_activation']
        p['deaths'] += row['deaths']
    rows = [dict(portfolio=k, assignment_order='/'.join(order[k]), first_sleeve=order[k][0],
                 clean_starts=v['clean'], startup_wipeouts=v['startup'], mature_wipeouts=v['mature'],
                 empty_days=round(v['empty'], 2), deaths=v['deaths'])
            for k, v in sorted(per_perm.items())]
    write_csv(ROOT/'permutation_summary.csv', rows)
    print(f"{'perm':7} {'order':22} {'clean':>6} {'startup':>8} {'mature':>7} {'emptyDays':>10} {'deaths':>7}")
    print('-'*72)
    for r in rows:
        print(f"{r['portfolio']:7} {r['assignment_order']:22} {r['clean_starts']:>4}/6 "
              f"{r['startup_wipeouts']:>8} {r['mature_wipeouts']:>7} {r['empty_days']:>10.2f} {r['deaths']:>7}")
    print('\nBy first sleeve:')
    by = defaultdict(list)
    for r in rows:
        by[r['first_sleeve']].append(r)
    print(f"  {'first':>6} {'orders':>7} {'clean starts':>14} {'startup':>8} {'mature':>7} {'empty days':>11}")
    for rr in sorted(by, key=float):
        g = by[rr]
        print(f"  {rr:>6} {len(g):>7} {sum(x['clean_starts'] for x in g):>6} of {6*len(g):<5} "
              f"{sum(x['startup_wipeouts'] for x in g):>8} {sum(x['mature_wipeouts'] for x in g):>7} "
              f"{sum(x['empty_days'] for x in g):>11.2f}")


if __name__ == '__main__':
    main()
