"""Independent graph/set audit of common episode grouping and pair counts."""
from bisect import bisect_left,bisect_right
from collections import defaultdict
import csv,json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_episodes'


def read(name):
    with (ROOT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    for group,base in [('code',PROJECT_ROOT),('inputs',PROJECT_ROOT),('files',ROOT)]:
        for name,digest in manifest[group].items():assert sha256_file(base/name)==digest,name
    rows=read('windows.csv');events=read('breach_events.csv');episodes=read('episodes.csv')
    members=read('episode_membership.csv');epairs=read('pair_episodes.csv');pairs=read('pair_windows.csv')
    dates=[r['date'] for r in read('episode_calendar.csv')]
    identity=lambda r:(r['months'],r['budget'],r['case'],r['rr'],r['trade_key'])
    assert {identity(r) for r in rows if r['eligible']=='True' and r['breached']=='True'}=={identity(r) for r in events}
    graph_checks=0
    for months in ('1','3','6'):
        for budget in ('1500','6800'):
            native=[r for r in events if r['months']==months and r['budget']==budget and r['rr']!='1000']
            for gap in (5,20,40):
                # All interval pairs form graph edges, then connected components;
                # independent of the study's sorted, transitive sweep implementation.
                parent=list(range(len(native)))
                def root(i):
                    while parent[i]!=i:i=parent[i]
                    return i
                for i,a in enumerate(native):
                    for j in range(i):
                        b=native[j]
                        left,right=(a,b) if a['interval_start']<=b['interval_start'] else (b,a)
                        between=max(0,bisect_left(dates,right['interval_start'][:10])-bisect_right(dates,left['exit'][:10]))
                        if between<=gap:parent[root(i)]=root(j)
                groups=defaultdict(set)
                for i,r in enumerate(native):groups[root(i)].add(identity(r))
                actual=defaultdict(set)
                for r in members:
                    if r['months']==months and r['budget']==budget and f'_g{gap}_' in r['episode']:
                        actual[r['episode']].add(identity(r))
                assert {frozenset(v) for v in groups.values()}=={frozenset(v) for v in actual.values()}
                for e in episodes:
                    if e['months']==months and e['budget']==budget and e['gap']==str(gap):
                        contributing=[r for r in members if r['episode']==e['episode']]
                        assert min(r['interval_start'] for r in contributing)==e['start']
                        assert max(r['exit'] for r in contributing)==e['end']
                graph_checks+=1
    for p in pairs:
        subset=[r for r in rows if r['months']==p['months'] and r['budget']==p['budget']]
        l={r['case']:r for r in subset if r['rr']==p['left'] and r['eligible']=='True'}
        r={r['case']:r for r in subset if r['rr']==p['right'] and r['eligible']=='True'}
        valid=set(l)&set(r);left={c for c in valid if l[c]['breached']=='True'};right={c for c in valid if r[c]['breached']=='True'}
        for field,value in dict(eligible=len(valid),left_failed=len(left),right_failed=len(right),both=len(left&right),
                               left_only=len(left-right),right_only=len(right-left),neither=len(valid-(left|right))).items():
            assert int(p[field])==value
    membership=defaultdict(set)
    for r in members:membership[r['rr']].add(r['episode'])
    for p in epairs:
        prefix=f'{p["months"]}m_b{p["budget"]}_g{p["gap"]}_'
        l={e for e in membership[p['left']] if e.startswith(prefix)}
        r={e for e in membership[p['right']] if e.startswith(prefix)}
        for field,value in dict(left_episodes=len(l),right_episodes=len(r),shared=len(l&r),left_only=len(l-r),right_only=len(r-l)).items():
            assert int(p[field])==value
        assert (p['reciprocal']=='True')==(bool(l-r) and bool(r-l))
    result=dict(graph_groupings_verified=graph_checks,window_pairs_verified=len(pairs),
                episode_pairs_verified=len(epairs),source_output_hashes_match=True,
                auditor_sha256=sha256_file(Path(__file__)))
    (ROOT/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
