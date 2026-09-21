"""All 24 startup assignment orders of the wide4 sleeve set.

`wide4`'s 6/6 continuity in rr_followup was measured for one order of its four RR
groups. `grid20` against its reversed order differs in five of six starts while its
isolation runs stay bit-identical, so order effects in the operating layer are large
enough to move a ranking. This runs the whole permutation group so the headline is
either robust to that choice or known not to be.

Nothing here is new modelling. It imports `study_rr_followup.evaluate` unchanged and
only supplies a different arm list, so every metric, assertion and evidence file is
produced by the same code path. `rr_values` stays at all 36 because the rolling-window
metrics take their date grid from the union of loaded tapes; trimming it would silently
change the numbers. perm01 is the order rr_followup used and must reproduce it exactly.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import study_rr_followup as base
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from study_rr_diversification import write_csv

PROFILE = PROJECT_ROOT/'config/studies/legacy_25k_wide4_permutations.json'


def boot():
    """Point the shared runner at this study's profile, in the parent and every worker."""
    base.PROFILE = PROFILE
    base.initialize()


def permutations():
    return list(json.loads(PROFILE.read_text())['arms'])


def jobs():
    # Primary policy only: the question is continuity under the operating book, and
    # isolation is carried as the control that must not move.
    return [('primary', phase, year, 'mae_first', name)
            for year in base.SPEC['starts']
            for phase in ('isolation', 'operating')
            for name in permutations()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    boot()
    out = base.OUT
    (out/'cases').mkdir(parents=True, exist_ok=True)
    contract = dict(spec=base.SPEC, parent_spec=base.PARENT, base_config=to_payload(base.BASE),
        engine=engine_digest(),
        code={f: sha256_file(PROJECT_ROOT/f) for f in
              ['scripts/study_wide4_permutations.py', 'scripts/study_rr_followup.py',
               'scripts/rr_followup_support.py', 'scripts/study_rr_diversification.py']},
        inputs={rr: input_digest(replace(base.BASE, risk_reward=rr)) for rr in base.SPEC['rr_values']},
        coverage_sha256=sha256_file(PROJECT_ROOT/'config/tape_coverage.json'))
    file = out/'contract.json'
    if file.exists():
        assert json.loads(file.read_text()) == contract, \
            'Contract changed; preserve old results before changing the design'
    else:
        file.write_text(json.dumps(contract, indent=2)+'\n', encoding='utf-8')

    selected = jobs()[:args.limit] if args.limit else jobs()
    done = {}
    for job in selected:
        saved = out/'cases'/f'{base.case_name(job)}.json'
        if saved.exists():
            done[base.case_name(job)] = json.loads(saved.read_text())['row']
    pending = [j for j in selected if base.case_name(j) not in done]
    print(f'{len(selected)} requested; {len(done)} complete; {len(pending)} pending', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=boot) as pool:
        futures = {pool.submit(base.evaluate, j): j for j in pending}
        for future in as_completed(futures):
            row = future.result(); done[row['case']] = row
            print(f'{len(done)}/{len(selected)} {row["case"]}: '
                  f'deaths={row["deaths"]}, wipeouts={row["book_wipeouts"]}, '
                  f'empty={row["days_empty_after_first_activation"]:.2f}', flush=True)
    write_csv(out/'comparison.csv', [done[base.case_name(j)] for j in selected])
    if len(selected) == len(jobs()):
        audit = dict(runs=len(done), copies_checked=sum(r['copies'] for r in done.values()),
            contract_sha256=sha256_file(file),
            case_sha256={name: sha256_file(out/'cases'/f'{name}.json') for name in done})
        (out/'audit.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
        print({k: v for k, v in audit.items() if k != 'case_sha256'}, flush=True)


if __name__ == '__main__':
    main()
