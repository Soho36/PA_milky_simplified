"""Transfer all equal cash winners, preserving the completed search contract."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path

import optimize_blocked_copying as search
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from study_legacy_routing import write_csv


def main():
    search.initialize()
    root = PROJECT_ROOT/search.SPEC['output']
    data = json.loads((root/'study.json').read_text(encoding='utf-8'))
    protected = {str(p.relative_to(root)):sha256_file(p) for p in root.rglob('*')
                 if p.is_file() and p.name not in {'ties.json','tied_transfers.csv'}}
    ties = [r for r in data['rows'] if any(r[s] == max(x[s] for x in data['rows']) for s in search.SCORES)]
    jobs = set()
    for r in ties:
        j = tuple(r['job'])
        jobs |= {(y,*j[1:]) for y in search.SPEC['transfer_starts']}
        jobs |= {(j[0],i,m,*j[3:]) for i,m in search.SPEC['transfer_budgets']}
    previous = {tuple(r['job']):r for r in data['transfers']}
    missing = sorted(jobs-previous.keys())
    with ProcessPoolExecutor(max_workers=search.SPEC['workers'], initializer=search.initialize) as pool:
        for r in pool.map(search.evaluate,missing):
            previous[tuple(r['job'])] = r
    rows = [previous[j] for j in sorted(jobs)]
    for r in rows:
        assert r['economics']['residual_usd'] == 0
        assert r['minimum_owner_cash'] >= 0 and r['peak_live'] <= 20
        assert any(r['job'][3:] == t['job'][3:] for t in ties)
    payload = {'generated_utc':datetime.now(timezone.utc).isoformat(),
               'selection':'All full-tape primary-budget ties for either cash objective; no retuning on transfers',
               'search_sha256':sha256_file(root/'study.json'),
               'runner_sha256':sha256_file(Path(__file__)), 'ties':ties,'transfers':rows,
               'original_artifacts_preserved':protected}
    assert all(sha256_file(root/name) == digest for name,digest in protected.items())
    (root/'ties.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    write_csv(root/'tied_transfers.csv',[{k:v for k,v in r.items() if k not in {'job','economics'}} for r in rows])
    print(f'{len(ties)} co-winners, {len(rows)} frozen transfers; original artifacts preserved',flush=True)
    for r in rows:
        if (r['initial_cash'],r['monthly_funding']) == tuple(search.SPEC['budget']):
            print(r['job'],r['total'],flush=True)


if __name__ == '__main__':
    main()
