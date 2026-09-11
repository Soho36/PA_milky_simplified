"""Paired 25K/50K reserve search under a limited supply of funded accounts."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import csv
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import study_legacy_50k_operating as sim
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.economics import Economics
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.report import write_outputs
from pa_milky.simulator import run_book
from pa_milky.study_reports import write_study_report

SPEC_PATH = PROJECT_ROOT / 'config/studies/legacy_spare_shelf.json'
PRIOR = PROJECT_ROOT / 'results/comparisons/legacy_25k_vs_50k/reserve_by_policy'
SCORES = ('ongoing', 'total')
REPLACE = 'monthly_current_slot_replacements'
LABEL = {'monthly_one': 'Monthly', 'weekly_one': 'Weekly', REPLACE: 'Monthly + replacements'}
# More passes than any book can use in a month: reproduces instant, unlimited supply.
UNLIMITED = 1000


def job(product, initial, monthly, acquisition, rule, cadence, headroom, spares, passes):
    return (product, initial, monthly, acquisition, rule, cadence, headroom, spares, passes)


def evaluate(j, detail=False):
    product, initial, monthly, acq, rule, cadence, headroom, spares, passes = j
    base = sim.C[product]
    pol = WithdrawalPolicy(name=f'{rule}_{cadence}_headroom_{headroom}', cadence=cadence, amount_rule=rule,
                           quantize_to_amount=False, terminal_withdrawal='firm_permitted',
                           min_retained_balance_usd=base.trailing_floor_balance_usd + headroom)
    acquisition = AcquisitionPolicy(acq, initial, monthly, max_live_accounts=sim.P[product]['max_live_accounts'],
                                    spare_capacity=spares, passes_per_month=passes)
    result = run_book(sim.T, replace(base, policy=pol), acquisition=acquisition)
    e = Economics.measure(result)
    cash = result.acquisition.summary()
    assert e.residual_usd == cash['cash_identity_residual_usd'] == 0
    assert cash['net_cash_created_usd'] == result.pocket_usd
    terminal = round(sum(x.received_usd for x in result.terminal_payouts), 2)
    row = {'product': product, 'initial_cash': initial, 'monthly_funding': monthly, 'acquisition': acq,
           'spares': spares, 'passes': passes, 'withdrawal': rule, 'cadence': cadence, 'headroom': headroom,
           'reserve': pol.min_retained_balance_usd, 'fee': base.purchase_fee_usd,
           'accounts': len(result.accounts), 'alive': result.alive_at_horizon,
           'spares_unused': cash['spares_unused_at_end'], 'supply_limited': cash['supply_limited_decisions'],
           'ongoing': round(result.pocket_usd - terminal, 2), 'terminal': terminal, 'total': result.pocket_usd,
           'contributions': cash['owner_contributions_usd'], 'ending_owner_cash': cash['ending_owner_cash_usd'],
           'economics': e.to_payload(), 'job': j}
    return (row, result) if detail else row


def shelves(spec):
    # Weekly-one wants at most five accounts a month (five Mondays), so more
    # passes never bind; monthly-one wants one. Neither gains from spares that
    # take trading slots, so both are run without a shelf.
    out = [(REPLACE, k, r) for k in spec['spares'] for r in spec['passes']]
    out += [('weekly_one', 0, r) for r in sorted({min(r, 5) for r in spec['passes']})]
    return out + [('monthly_one', 0, 1)]


def best(rows, score):
    # Secondary objective, then smaller reserve, for deterministic display only.
    other = 'total' if score == 'ongoing' else 'ongoing'
    return max(rows, key=lambda r: (r[score], r[other], -r['headroom']))


def refinement_jobs(rows, spec):
    groups = {}
    for r in rows:
        key = (r['initial_cash'], r['monthly_funding'], r['acquisition'], r['spares'], r['passes'])
        groups.setdefault(key, {}).setdefault(r['product'], []).append(r)
    jobs = set()
    for (i, m, acq, k, p), by_product in groups.items():
        for group in by_product.values():
            for score in SCORES:
                w = best(group, score)
                for d in range(-spec['refinement_radius'], spec['refinement_radius'] + 1, spec['refinement_step']):
                    if w['headroom'] + d >= 0:
                        jobs.update(job(prod, i, m, acq, w['withdrawal'], w['cadence'], w['headroom'] + d, k, p)
                                    for prod in spec['products'])
    return sorted(jobs)


def capability_best(rows, prod, budget, passes, score='total'):
    """Best bundle for an owner who can pass `passes` accounts a month."""
    pool = [r for r in rows if r['product'] == prod and [r['initial_cash'], r['monthly_funding']] == list(budget)
            and ((r['acquisition'] == REPLACE and r['passes'] == passes)
                 or (r['acquisition'] == 'weekly_one' and r['passes'] == min(passes, 5))
                 or r['acquisition'] == 'monthly_one')]
    return best(pool, score)


def summaries(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r['product'], r['initial_cash'], r['monthly_funding'], r['acquisition'],
                           r['spares'], r['passes']), []).append(r)
    output = []
    for key, group in sorted(groups.items()):
        for score in SCORES:
            w = best(group, score)
            entry = {k: v for k, v in w.items() if k not in ('job', 'economics')}
            entry.update(objective=score, tested_count=len(group),
                         tied_best=sum(r[score] == w[score] for r in group),
                         boundary_best=any(r[score] == w[score] and r['headroom'] in
                                           (min(x['headroom'] for x in group), max(x['headroom'] for x in group))
                                           for r in group))
            output.append(entry)
    return output


def matched_deltas(rows):
    pairs = {}
    for r in rows:
        pairs.setdefault(tuple(r['job'][1:]), {})[r['product']] = r
    output = []
    for key, pair in sorted(pairs.items()):
        assert set(pair) == {'legacy_25k', 'legacy_50k'}, ('unpaired search', key)
        a, b = pair['legacy_25k'], pair['legacy_50k']
        output.append({**dict(zip(('initial_cash', 'monthly_funding', 'acquisition', 'withdrawal', 'cadence',
                                   'headroom', 'spares', 'passes'), key)),
                       'total_25k': a['total'], 'total_50k': b['total'],
                       'total_delta_50k_minus_25k': round(b['total'] - a['total'], 2),
                       'accounts_25k': a['accounts'], 'accounts_50k': b['accounts']})
    return output


def write_csv(path, rows):
    fields = [k for k in rows[0] if k not in ('job', 'economics')]
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: r[k] for k in fields} for r in rows)


def bundle(r):
    shelf = f", {r['spares']} spares" if r['acquisition'] == REPLACE else ''
    return f"{LABEL[r['acquisition']]}{shelf}; {r['withdrawal']} / {r['cadence']}; reserve ${r['reserve']:,.0f}"


def render(rows, spec, prior_best, controls, deltas):
    products = spec['products']
    text = '# Legacy 25K versus 50K under a limited supply of funded accounts\n\n'
    text += (f'{len(rows):,} simulations. {controls} rows that must equal the unlimited-supply study '
             'reproduced it exactly. Both products are tested on exactly the same settings.\n\n')
    text += ('## The question\n\n'
             'The unlimited-supply study let every purchase become a funded account at once. Its '
             'best 25K bundles bought 600+ accounts by replacing deaths immediately. Here funded '
             'accounts come from passed evaluations: at most **N passes per calendar month**, each '
             'paid in full ($200 / $250) when it passes. A pass not needed at once waits dormant on a '
             'shelf of up to K spares, and **spares count toward the 20-account cap**. Spares left at the '
             'end are sunk. See [ASSUMPTIONS.md](../../../../ASSUMPTIONS.md#supply-of-funded-accounts).\n\n'
             f'Replacement purchasing is tested with {spec["spares"]} spares and {spec["passes"]} passes a '
             'month. Weekly and monthly purchasing run without spares as comparators; more than five '
             'passes a month never binds them. Reserves are re-searched for every setting: coarse '
             f'headrooms {spec["headrooms"]} above the frozen floor, then +/-${spec["refinement_radius"]} '
             f'in ${spec["refinement_step"]} steps around each product\'s best bundle, applied to both '
             'products. This is coarser than the unlimited study, which slightly favours its numbers.\n\n'
             '**The pass rate is fixed.** Real passes are lumpy and probably scarcest when the book is '
             'dying, so a fixed rate flatters replacement policies. Read each row as "an owner who can '
             'reliably pass N accounts a month".\n\n')
    text += ('## Files\n\n- [All settings](all_settings.csv), [best by shelf](best_by_shelf.csv), '
             '[matched 50K-minus-25K differences](matched_deltas.csv), [contract and rows](study.json).\n'
             f'- Detailed ledgers for each product\'s best bundle at {spec["ledger_passes"]} passes a month.\n\n')
    for budget in spec['budgets']:
        i, m = budget
        text += f'## ${i:,} initial; ${m:,}/month\n\n'
        a, b = prior_best[('legacy_25k', i, m)], prior_best[('legacy_50k', i, m)]
        text += (f'Unlimited supply (earlier study): 25K ${a["total"]:,.0f} ({a["accounts"]} bought) vs 50K '
                 f'${b["total"]:,.0f} ({b["accounts"]} bought).\n\n')
        text += ('### Best tested bundle by pass rate (terminal-inclusive total)\n\n'
                 '| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | '
                 '**50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |\n'
                 '| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |\n')
        for p in spec['passes']:
            x, y = (capability_best(rows, prod, budget, p) for prod in products)
            text += (f"| {p} | {bundle(x)} | ${x['total']:,.0f} | {x['accounts']} / {x['alive']} | "
                     f"{bundle(y)} | ${y['total']:,.0f} | {y['accounts']} / {y['alive']} | "
                     f"${y['total'] - x['total']:,.0f} |\n")
        text += '\n### Monthly + replacements: best total by spares held\n\n'
        text += ('| Passes / month | ' + ' | '.join(f'**{prod[-3:].upper()} — {k} spares**'
                 for prod in products for k in spec['spares']) + ' |\n')
        text += '| ---: |' + ' ---: |' * (len(products) * len(spec['spares'])) + '\n'
        for p in spec['passes']:
            cells = []
            for prod, k in product(products, spec['spares']):
                w = best([r for r in rows if r['product'] == prod and [r['initial_cash'], r['monthly_funding']] == budget
                          and r['acquisition'] == REPLACE and r['spares'] == k and r['passes'] == p], 'total')
                cells.append(f"${w['total']:,.0f} ({w['accounts']})")
            text += f'| {p} | ' + ' | '.join(cells) + ' |\n'
        text += '\nCells show best total (accounts bought).\n\n'
    text += '## Where 25K catches up\n\n| Budget | Lowest tested pass rate at which the best 25K total beats the best 50K total |\n|---|---|\n'
    for budget in spec['budgets']:
        wins = [p for p in spec['passes'] if capability_best(rows, 'legacy_25k', budget, p)['total']
                > capability_best(rows, 'legacy_50k', budget, p)['total']]
        text += f'| ${budget[0]:,} + ${budget[1]:,}/mo | {f"{wins[0]} passes a month" if wins else "never, up to " + str(max(spec["passes"]))} |\n'
    text += '\n## Matched settings: share where 50K beats 25K\n\nSame budget, purchasing, shelf, withdrawal and headroom; settings where both lose are excluded.\n\n'
    text += '| Passes / month | ' + ' | '.join(LABEL[a] for a in (REPLACE, 'weekly_one')) + ' |\n|---:|---:|---:|\n'
    for p in spec['passes']:
        cells = []
        for acq, pp in ((REPLACE, p), ('weekly_one', min(p, 5))):
            d = [x for x in deltas if x['acquisition'] == acq and x['passes'] == pp
                 and not (x['total_25k'] <= 0 and x['total_50k'] <= 0)]
            cells.append(f"{sum(x['total_delta_50k_minus_25k'] > 0 for x in d) / len(d):.0%} of {len(d)}" if d else 'n/a')
        text += f'| {p} | ' + ' | '.join(cells) + ' |\n'
    text += ('\n## Limits\n\nIn-sample best tested settings on one historical tape, not forecasts. The pass rate '
             'is deterministic and uncorrelated with the book, which flatters replacement policies. '
             'Weekly and monthly purchasing are not given spares. Evaluations are not traded; their cost is '
             'the owner\'s measured average. All other model limits of the unlimited-supply study apply.\n')
    return text


def main(spec_path=SPEC_PATH):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    sim.initialize()
    assert input_digest(sim.C['legacy_25k']) == input_digest(sim.C['legacy_50k'])
    out = (PROJECT_ROOT / spec['output']).resolve()
    assert out.is_relative_to(PROJECT_ROOT / 'results/comparisons')
    out.mkdir(parents=True, exist_ok=True)
    # Office lock files (~$name) exist only while a workbook is open and are unreadable then.
    protected = {str(f): sha256_file(f) for f in (PROJECT_ROOT / 'results').rglob('*')
                 if f.is_file() and not f.is_relative_to(out) and not f.name.startswith('~$')}
    contract = {'spec': spec, 'configs': {k: to_payload(v) for k, v in sim.C.items()},
                'engine': engine_digest(), 'inputs': input_digest(sim.C['legacy_25k']),
                'evaluator_sha256': sha256_file(Path(sim.__file__)), 'runner_sha256': sha256_file(Path(__file__))}
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
    prior = [json.loads(line) for line in (PRIOR / 'checkpoint.jsonl').read_text(encoding='utf-8').splitlines()]
    prior = [r for r in prior if not r['strict_post_payout_balance']]
    prior_rows = {tuple(r['job'][:7]): r for r in prior}
    prior_best = {}
    for r in prior:
        key = (r['product'], r['initial_cash'], r['monthly_funding'])
        if key not in prior_best or (r['total'], r['ongoing']) > (prior_best[key]['total'], prior_best[key]['ongoing']):
            prior_best[key] = r
    coarse = [job(prod, i, m, acq, rule, cad, h, k, p)
              for prod, (i, m), (acq, k, p), rule, cad, h in product(spec['products'], spec['budgets'], shelves(spec),
                  spec['amount_rules'], spec['cadences'], spec['headrooms'])]
    anchors = sorted({job(*r['job'][:7], 0, UNLIMITED) for r in prior_best.values()
                      if [r['initial_cash'], r['monthly_funding']] in spec['budgets']})

    def run(pool, jobs, label):
        missing = sorted(set(jobs) - cache.keys())
        print(f'{label}: {len(missing)} new / {len(jobs)} requested', flush=True)
        with checkpoint.open('a', encoding='utf-8') as handle:
            futures = {pool.submit(evaluate, j): j for j in missing}
            for n, future in enumerate(as_completed(futures), 1):
                r = future.result()
                cache[tuple(r['job'])] = r
                handle.write(json.dumps(r) + '\n')
                handle.flush()
                if n % 100 == 0 or n == len(missing):
                    print(f'{label}: {n}/{len(missing)} completed', flush=True)
        return [cache[j] for j in jobs]

    with ProcessPoolExecutor(max_workers=spec['workers'], initializer=sim.initialize) as pool:
        anchor_rows = run(pool, anchors, 'Unlimited-supply anchors')
        coarse_rows = run(pool, coarse, 'Coarse grid')
        refined = refinement_jobs(coarse_rows, spec)
        run(pool, refined, 'Refinement')
    rows = [cache[j] for j in sorted(set(coarse) | set(refined))]
    # Every row whose supply cannot bind must equal the unlimited-supply study.
    def reproduces(r):
        old = prior_rows[tuple(r['job'][:7])]
        return all(r[k] == old[k] for k in ('ongoing', 'total', 'accounts', 'alive'))

    assert all(reproduces(r) for r in anchor_rows), 'unlimited supply no longer reproduces the earlier winners'
    unbound = [r for r in rows if tuple(r['job'][:7]) in prior_rows and r['spares'] == 0
               and (r['acquisition'] == 'monthly_one' or (r['acquisition'] == 'weekly_one' and r['passes'] >= 5))]
    assert all(reproduces(r) for r in unbound), 'a row whose supply cannot bind moved'
    controls = len(anchor_rows) + len(unbound)
    selected = summaries(rows)
    deltas = matched_deltas(rows)
    write_csv(out / 'all_settings.csv', rows)
    write_csv(out / 'best_by_shelf.csv', selected)
    write_csv(out / 'matched_deltas.csv', deltas)
    (out / 'study.json').write_text(json.dumps({**contract, 'generated_utc': datetime.now(timezone.utc).isoformat(),
        'verified_controls': controls, 'anchors': anchor_rows, 'rows': rows, 'best_by_shelf': selected}, indent=2),
        encoding='utf-8')
    for budget, prod in product(spec['budgets'], spec['products']):
        w = capability_best(rows, prod, budget, spec['ledger_passes'])
        row, result = evaluate(tuple(w['job']), True)
        assert row['total'] == w['total']
        folder = out / f'{prod}__budget_{budget[0]}_{budget[1]}__passes_{spec["ledger_passes"]}__best_total'
        write_outputs(result, folder)
        (folder / 'experiment.json').write_text(json.dumps({'run_config': to_payload(result.config),
            'acquisition': asdict(result.acquisition.policy)}, indent=2), encoding='utf-8')
    write_study_report(out, render(rows, spec, prior_best, controls, deltas))
    assert all(Path(f).is_file() and sha256_file(Path(f)) == h for f, h in protected.items())
    (out / 'preservation_check.json').write_text(json.dumps({'protected_files': len(protected),
        'all_unchanged': True}, indent=2), encoding='utf-8')
    print(f'Completed {len(rows)} paired simulations; {controls} controls verified; prior results unchanged. {out}',
          flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:])
