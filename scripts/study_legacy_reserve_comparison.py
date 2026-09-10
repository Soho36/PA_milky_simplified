"""Paired reserve search with equal coverage per product and resumable evidence."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import csv
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import study_legacy_50k_operating as sim
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.study_reports import write_study_report

SPEC_PATH = PROJECT_ROOT / 'config/studies/legacy_reserve_comparison.json'
SCORES = ('ongoing', 'total')


def family(row):
    return tuple(row[k] for k in ('initial_cash', 'monthly_funding', 'acquisition', 'withdrawal', 'cadence'))


def best(rows, score):
    # Secondary objective, then smaller reserve, for deterministic display only.
    other = 'total' if score == 'ongoing' else 'ongoing'
    return max(rows, key=lambda r: (r[score], r[other], -r['headroom']))


def refinement_jobs(rows, spec):
    grouped = {}
    for r in rows:
        grouped.setdefault(family(r), {}).setdefault(r['product'], []).append(r)
    jobs = set()
    for key, by_product in grouped.items():
        headrooms = set()
        for group in by_product.values():
            for score in SCORES:
                # Flat score plateaus are reported as ties, not thousands of refinements.
                center = best(group, score)['headroom']
                headrooms.update(max(0, center + d) for d in range(
                    -spec['refinement_radius'], spec['refinement_radius'] + 1,
                    spec['refinement_step']))
        for prod, h in product(spec['products'], sorted(headrooms)):
            jobs.add(sim.job(prod, *key, h))
    return sorted(jobs)


def summaries(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r['product'], *family(r)), []).append(r)
    output = []
    for key, group in sorted(groups.items()):
        for score in SCORES:
            winner = best(group, score)
            ties = [r['reserve'] for r in group if r[score] == winner[score]]
            near = sorted(r['reserve'] for r in group
                          if winner[score] > 0 and r[score] >= winner[score] * .99)
            entry = {k: v for k, v in winner.items() if k not in ('job', 'economics')}
            entry.update(objective=score, tested_count=len(group),
                         tested_reserve_min=min(r['reserve'] for r in group),
                         tested_reserve_max=max(r['reserve'] for r in group),
                         tied_best_reserves=sorted(ties), within_one_percent_reserves=near,
                         boundary_best=any(r['headroom'] in (min(x['headroom'] for x in group),
                             max(x['headroom'] for x in group)) and r[score] == winner[score]
                             for r in group))
            output.append(entry)
    return output


def write_csv(path, rows):
    fields = [k for k in rows[0] if k not in ('job', 'economics')]
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(r[k]) if isinstance(r[k], list) else r[k] for k in fields})


def matched_deltas(rows):
    pairs = {}
    for r in rows:
        pairs.setdefault((*family(r), r['headroom']), {})[r['product']] = r
    output = []
    for key, pair in sorted(pairs.items()):
        assert set(pair) == {'legacy_25k', 'legacy_50k'}, ('unpaired search', key)
        a, b = pair['legacy_25k'], pair['legacy_50k']
        output.append({**dict(zip(('initial_cash', 'monthly_funding', 'acquisition', 'withdrawal',
                                  'cadence', 'headroom'), key)),
                       'reserve_25k': a['reserve'], 'reserve_50k': b['reserve'],
                       'ongoing_25k': a['ongoing'], 'ongoing_50k': b['ongoing'],
                       'ongoing_delta_50k_minus_25k': round(b['ongoing'] - a['ongoing'], 2),
                       'total_25k': a['total'], 'total_50k': b['total'],
                       'total_delta_50k_minus_25k': round(b['total'] - a['total'], 2)})
    return output


def render(rows, selected, spec, controls):
    text = '# Legacy 25K versus 50K: best tested reserves by operating policy\n\n'
    text += (f'{len(rows):,} simulations; {len(selected)//2} product/budget/policy families; '
             f'{controls} prior matched controls reproduced. Each paired family tests exactly '
             'the same floor-headroom values for both products.\n\n')
    text += ('## How to read this comparison\n\n'
             'These are in-sample best tested settings, not global optima or expected future earnings. '
             'A reserve is the balance left after a withdrawal, not a trading stop. '
             'Daily minimum means request $500 when eligible and enough balance remains; '
             'maximum means request all excess permitted by the reserve and firm rules. '
             'Checks start in the account\'s second calendar month.\n\n'
             'Same RR tape and exposure, four owner budgets, 20 live accounts, user-specified '
             'seat fees $200 (25K) / $250 (50K). The matched comparison therefore includes cost '
             'as well as account mechanics. Ongoing = receipts during trading minus all purchase fees; '
             'total adds one permitted endpoint request releasing the voluntary reserve. '
             'Owner contributions are excluded from both net scores.\n\n'
             '**Rule interpretation:** both products retain the inherited payout model. '
             'The optional post-payout-six retained minimum is not enabled or re-optimized here. '
             'See [source audit and limitations](../../../../research/legacy_50k/SOURCES.md).\n\n'
             '**Coverage:** minimum and maximum withdrawal families, daily/weekly/monthly checks; '
             'monthly-one, weekly-one and monthly purchases with current-month-slot replacements. '
             'Fixed-amount backlog policies, quarterly schedules, batch purchases and calendar-phase '
             'variation are outside this focused comparison.\n\n')
    text += (f'Common coarse headrooms above the frozen floor: {spec["headrooms"]}. '
             f'Within every budget/purchase/withdrawal/cadence family, refine +/-${spec["refinement_radius"]:,} '
             f'in ${spec["refinement_step"]} steps around each product\'s coarse winner for each objective; '
             'apply the UNION of those values to BOTH products. This is a broad coarse search plus '
             'local refinement, not a continuous or exhaustive $100 grid. Secondary objective, then '
             'lower reserve, breaks display ties. All primary-score ties remain in the data.\n\n'
             'The frozen floors are $25,100 and $50,100: headroom $6,800 means reserves '
             '$31,900 and $56,900. The old 25K cadence study tested $31,600–$32,100 plus '
             'the $30,000 minimum-policy control; its $31,900 result was conditional on that grid.\n\n'
             '## Files\n\n'
             '- [All paired settings](all_settings.csv) and [matched 50K-minus-25K differences](matched_deltas.csv).\n'
             '- [Best reserves by family and objective](best_by_policy.csv), including exact ties, tested bounds '
             'and the explicit list of tested reserves within 1% of the best positive score. '
             'Those lists need not be continuous bands and are not confidence intervals.\n'
             '- [Research contract and evidence](study.json). [Operating notes](HOW_THIS_STUDY_WORKS.md).\n\n')
    for i, m in spec['budgets']:
        text += f'## ${i:,} initial; ${m:,}/month\n\n'
        group = [r for r in rows if (r['initial_cash'], r['monthly_funding']) == (i, m)]
        text += '### Best complete tested bundles\n\n'
        text += '| Objective | Product | Purchases | Withdraw / checks | Reserve | Accounts | Alive | Ongoing | Total |\n|---|---|---|---|---:|---:|---:|---:|---:|\n'
        for score, prod in product(SCORES, spec['products']):
            r = best([r for r in group if r['product'] == prod], score)
            text += f"| {score} | {prod} | {r['acquisition']} | {r['withdrawal']} / {r['cadence']} | ${r['reserve']:,.0f} | {r['accounts']} | {r['alive']} | ${r['ongoing']:,.2f} | ${r['total']:,.2f} |\n"
        for acq in spec['acquisitions']:
            text += f'\n### {acq}: best reserve within each withdrawal policy\n\n'
            text += '| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |\n|---|---|---|---:|---:|---:|---:|---:|---|\n'
            for r in selected:
                if (r['initial_cash'], r['monthly_funding'], r['acquisition']) != (i, m, acq):
                    continue
                text += f"| {r['product']} | {r['withdrawal']} / {r['cadence']} | {r['objective']} | ${r['reserve']:,.0f} | ${r[r['objective']]:,.2f} | {r['accounts']} | {r['alive']} | {len(r['tied_best_reserves'])} | {'yes' if r['boundary_best'] else 'no'} |\n"
        text += '\n'
    text += ('## Limits on interpreting a winner\n\n'
             'A boundary tie warns that some equally best setting touches the tested limits; '
             'it can also mean all reserves produce the same failure path. A unique interior winner '
             'still does not prove a global optimum: untested intervals and other trade histories remain. '
             'Reserves selected on the same tape are subject to selection bias. Near-best results '
             'describe parameter sensitivity on this tape, not robustness to future markets. '
             'Selecting reserves separately measures adaptation; use matched rows for a fixed-policy '
             'account comparison. A higher ongoing score can come with fewer survivors and a lower total.\n')
    return text


def main():
    spec = json.loads(SPEC_PATH.read_text(encoding='utf-8'))
    sim.initialize()
    assert spec['budgets'] == sim.P['legacy_25k']['budgets'] == sim.P['legacy_50k']['budgets']
    assert sim.P['legacy_25k']['max_live_accounts'] == sim.P['legacy_50k']['max_live_accounts'] == 20
    assert input_digest(sim.C['legacy_25k']) == input_digest(sim.C['legacy_50k'])
    out = (PROJECT_ROOT / spec['output']).resolve()
    assert out.is_relative_to(PROJECT_ROOT / 'results/comparisons')
    out.mkdir(parents=True, exist_ok=True)
    protected = {str(f): sha256_file(f) for f in (PROJECT_ROOT/'results').rglob('*')
                 if f.is_file() and not f.is_relative_to(out)}
    contract = {'spec': spec, 'configs': {k: to_payload(v) for k, v in sim.C.items()},
                'engine': engine_digest(), 'inputs': input_digest(sim.C['legacy_25k']),
                'evaluator_sha256': sha256_file(Path(sim.__file__)),
                'runner_sha256': sha256_file(Path(__file__))}
    contract_path = out / 'contract.json'
    if contract_path.exists():
        assert json.loads(contract_path.read_text(encoding='utf-8')) == contract, 'Changed contract; use a new output directory'
    else:
        contract_path.write_text(json.dumps(contract, indent=2), encoding='utf-8')
    checkpoint = out / 'checkpoint.jsonl'
    cache = {}
    if checkpoint.exists():
        for line in checkpoint.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            cache[tuple(r['job'])] = r
    coarse = [sim.job(prod, i, m, a, rule, cadence, h)
              for prod, (i, m), a, rule, cadence, h in product(spec['products'], spec['budgets'],
                  spec['acquisitions'], spec['amount_rules'], spec['cadences'], spec['headrooms'])]

    def run(pool, jobs, label):
        missing = sorted(set(jobs) - cache.keys())
        print(f'{label}: {len(missing)} new / {len(jobs)} requested', flush=True)
        with checkpoint.open('a', encoding='utf-8') as handle:
            futures = {pool.submit(sim.evaluate, j): j for j in missing}
            for n, future in enumerate(as_completed(futures), 1):
                r = future.result()
                cache[tuple(r['job'])] = r
                handle.write(json.dumps(r) + '\n')
                handle.flush()
                if n % 40 == 0 or n == len(missing):
                    print(f'{label}: {n}/{len(missing)} completed', flush=True)
        return [cache[j] for j in jobs]

    with ProcessPoolExecutor(max_workers=spec['workers'], initializer=sim.initialize) as pool:
        coarse_rows = run(pool, coarse, 'Paired coarse grid')
        refined = refinement_jobs(coarse_rows, spec)
        run(pool, refined, 'Paired per-family refinement')
    requested = set(coarse) | set(refined)
    rows = [cache[j] for j in sorted(requested)]
    selected = summaries(rows)
    deltas = matched_deltas(rows)
    assert len(rows) == 2 * len(deltas)
    assert len(selected) == 2 * 2 * 4 * 3 * 2 * 3
    previous = json.loads((PROJECT_ROOT/'results/legacy_50k/operating_policies/study.json').read_text(encoding='utf-8'))
    controls = 0
    for r in previous['matched_controls']:
        actual = cache[tuple(r['job'])]
        assert all(actual[k] == r[k] for k in ('ongoing', 'total', 'accounts', 'alive', 'reserve', 'fee'))
        controls += 1
    write_csv(out/'all_settings.csv', rows)
    write_csv(out/'best_by_policy.csv', selected)
    write_csv(out/'matched_deltas.csv', deltas)
    payload = {**contract, 'generated_utc': datetime.now(timezone.utc).isoformat(),
               'verified_controls': controls, 'rows': rows, 'best_by_policy': selected}
    (out/'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_study_report(out, render(rows, selected, spec, controls))
    assert all(Path(f).is_file() and sha256_file(Path(f)) == h for f, h in protected.items())
    (out/'preservation_check.json').write_text(json.dumps({'protected_files': len(protected),
        'all_unchanged': True}, indent=2), encoding='utf-8')
    print(f'Completed {len(rows)} paired simulations; {controls} controls verified; prior results unchanged. {out}', flush=True)


if __name__ == '__main__':
    main()
