"""Paired 25K/50K reserve search when funded accounts come from evaluations traded on the tape."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from itertools import product
from pathlib import Path
import csv
import json
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import study_legacy_50k_operating as sim
from study_legacy_spare_shelf import LABEL, REPLACE, best, write_csv
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec, Router, add_months, run_episode
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.report import write_outputs
from pa_milky.simulator import run_book
from pa_milky.study_reports import write_study_report

SPEC_PATH = PROJECT_ROOT / 'config/studies/legacy_eval_supply.json'
PRIOR = PROJECT_ROOT / 'results/comparisons/legacy_25k_vs_50k/reserve_by_policy'
SCORES = ('ongoing', 'total')
SPEC = None


def initialize(spec_path=SPEC_PATH):
    global SPEC
    sim.initialize()
    SPEC = json.loads(Path(spec_path).read_text(encoding='utf-8'))


def evaluation_spec(product):
    return EvaluationSpec(**SPEC['evaluations'][product])


def job(product, initial, monthly, acquisition, rule, cadence, headroom, spares):
    return (product, initial, monthly, acquisition, rule, cadence, headroom, spares)


def evaluate(j, detail=False):
    product, initial, monthly, acq, rule, cadence, headroom, spares = j
    base = sim.C[product]
    pol = WithdrawalPolicy(name=f'{rule}_{cadence}_headroom_{headroom}', cadence=cadence, amount_rule=rule,
                           quantize_to_amount=False, terminal_withdrawal='firm_permitted',
                           min_retained_balance_usd=base.trailing_floor_balance_usd + headroom)
    acquisition = AcquisitionPolicy(acq, initial, monthly, max_live_accounts=sim.P[product]['max_live_accounts'],
                                    spare_capacity=spares, evaluation=evaluation_spec(product),
                                    evaluations_at_once=SPEC['evaluations_at_once'])
    result = run_book(sim.T, replace(base, policy=pol), acquisition=acquisition)
    e = Economics.measure(result)
    ledger = result.acquisition
    cash = ledger.summary()
    assert e.residual_usd == cash['cash_identity_residual_usd'] == 0
    assert cash['net_cash_created_usd'] == result.pocket_usd
    assert round(cash['evaluation_fees_usd'] + cash['activation_fees_usd'], 2) == cash['purchase_spend_usd']
    terminal = round(sum(x.received_usd for x in result.terminal_payouts), 2)
    passes = Counter(f'{x.passed_at:%Y-%m}' for x in ledger.evaluations if x.passed_at)
    short = {d['at'][:7] for d in ledger.decisions if d.get('supply_limited')}
    funded = cash['evaluations_activated']
    row = {'product': product, 'initial_cash': initial, 'monthly_funding': monthly, 'acquisition': acq,
           'spares': spares, 'withdrawal': rule, 'cadence': cadence, 'headroom': headroom,
           'reserve': pol.min_retained_balance_usd, 'accounts': len(result.accounts),
           'alive': result.alive_at_horizon, 'evaluations': cash['evaluations_started'],
           'evaluation_months': cash['evaluation_months_paid'], 'evaluation_resets': cash['evaluation_resets'],
           'activated': funded, 'evaluation_fees': cash['evaluation_fees_usd'],
           'activation_fees': cash['activation_fees_usd'],
           'cost_per_funded': round(cash['purchase_spend_usd'] / funded, 2) if funded else None,
           'max_passes_in_a_month': max(passes.values(), default=0), 'short_months': len(short),
           'short_months_without_a_pass': sum(1 for m in short if not passes.get(m)),
           'spares_unused': cash['spares_unused_at_end'], 'in_flight_at_end': cash['evaluations_in_flight_at_end'],
           'ongoing': round(result.pocket_usd - terminal, 2), 'terminal': terminal, 'total': result.pocket_usd,
           'contributions': cash['owner_contributions_usd'], 'ending_owner_cash': cash['ending_owner_cash_usd'],
           'economics': e.to_payload(), 'job': j}
    return (row, result) if detail else row


def combos(spec):
    return [(acq, k) for acq, ks in spec['acquisitions'].items() for k in ks]


def refinement_jobs(rows, spec):
    groups = {}
    for r in rows:
        key = (r['initial_cash'], r['monthly_funding'], r['acquisition'], r['spares'])
        groups.setdefault(key, {}).setdefault(r['product'], []).append(r)
    jobs = set()
    for (i, m, acq, k), by_product in groups.items():
        for group in by_product.values():
            for score in SCORES:
                w = best(group, score)
                for d in range(-spec['refinement_radius'], spec['refinement_radius'] + 1, spec['refinement_step']):
                    if w['headroom'] + d >= 0:
                        jobs.update(job(prod, i, m, acq, w['withdrawal'], w['cadence'], w['headroom'] + d, k)
                                    for prod in spec['products'])
    return sorted(jobs)


def matched_deltas(rows):
    pairs = {}
    for r in rows:
        pairs.setdefault(tuple(r['job'][1:]), {})[r['product']] = r
    output = []
    for key, pair in sorted(pairs.items()):
        assert set(pair) == {'legacy_25k', 'legacy_50k'}, ('unpaired search', key)
        a, b = pair['legacy_25k'], pair['legacy_50k']
        output.append({**dict(zip(('initial_cash', 'monthly_funding', 'acquisition', 'withdrawal', 'cadence',
                                   'headroom', 'spares'), key)),
                       'total_25k': a['total'], 'total_50k': b['total'],
                       'total_delta_50k_minus_25k': round(b['total'] - a['total'], 2),
                       'accounts_25k': a['accounts'], 'accounts_50k': b['accounts'],
                       'cost_per_funded_25k': a['cost_per_funded'], 'cost_per_funded_50k': b['cost_per_funded']})
    return output


def reconciliation(spec):
    """One evaluation started on every weekday with a full horizon: the EODMAE episode."""
    trades = sim.T
    router = Router(trades)
    horizon = spec['reconciliation']['horizon_days']
    first, last = min(t.entry_at for t in trades), max(t.exit_at for t in trades)
    starts, day = [], datetime(first.year, first.month, first.day)
    while day + timedelta(days=horizon) <= last:
        if day.weekday() < 5:
            starts.append(day)
        day += timedelta(days=1)
    out = {}
    for prod in spec['products']:
        es, base = evaluation_spec(prod), sim.C[prod]
        ref = spec['reconciliation']['eodmae'][prod]
        assert ref['contracts'] == es.contracts
        runs = [run_episode(trades, router, es, s, commission_per_mnq=base.commission_usd_per_mnq_round_turn,
                            path_order=base.path_order, horizon_days=horizon) for s in starts]
        days = [(p - s).total_seconds() / 86400 for (p, _), s in zip(runs, starts) if p]
        spent = sum(months * es.monthly_fee_usd + (es.activation_fee_usd if p else 0) for p, months in runs)
        out[prod] = {'contracts': es.contracts, 'starts': len(starts),
                     'activation_rate': round(len(days) / len(starts), 4),
                     'first_month_rate': round(sum(1 for (p, _), s in zip(runs, starts)
                                                   if p and p < add_months(s, 1)) / len(starts), 4),
                     'median_days': round(statistics.median(days), 2) if days else None,
                     'cost_per_activation': round(spent / len(days), 2) if days else None,
                     'eodmae': ref}
    return out


def bundle(r):
    return (f"{combo_label(r['acquisition'], r['spares'])}; {r['withdrawal']} / {r['cadence']}; "
            f"reserve ${r['reserve']:,.0f}")


def combo_label(acq, k):
    # Every purchase policy is tested with every spare setting, so always say which.
    return f'{LABEL[acq]}, {k} spares'


def render(rows, spec, prior_best, recon, deltas, controls):
    text = '# Legacy 25K versus 50K when funded accounts come from evaluations\n\n'
    text += (f'{len(rows):,} simulations. With evaluations switched off, the engine still reproduces the '
             f'{controls} headline winners of the unlimited-supply study exactly.\n\n')
    text += ('## How supply works here\n\nEvery funded account comes from an evaluation traded on the same RR '
             'signals, one position at a time, so the target-to-drawdown ratio plays out on the actual trades.\n\n'
             '| Product | Evaluation size | Target / drawdown | Ratio | Monthly fee | Activation |\n'
             '|---|---:|---:|---:|---:|---:|\n')
    for prod in spec['products']:
        x = spec['evaluations'][prod]
        text += (f"| {prod} | {x['contracts']} MNQ | ${x['profit_target_usd']:,} / ${x['trailing_drawdown_usd']:,} | "
                 f"{x['profit_target_usd'] / x['trailing_drawdown_usd']:.1f} | ${x['monthly_fee_usd']} | "
                 f"${x['activation_fee_usd']} |\n")
    text += ('\n- The drawdown trails peak equity, open profit included, and never freezes. An evaluation passes '
             'when a closed balance reaches the target.\n'
             '- The fee is paid at the start and at each monthly renewal. A blown evaluation waits for renewal, '
             'which resets it.\n'
             f"- Up to {spec['evaluations_at_once']} evaluations run at once, started only while the book is short: "
             'deaths not yet replaced, a missed scheduled purchase, or spares below target. An evaluation no '
             'longer needed is cancelled at renewal. Each one in flight holds one of the 20 seats.\n'
             '- A pass is activated at the next daily check and joins the spare shelf; the purchase policy '
             'deploys it from there.\n'
             '- Fees and pass timing come from the tape instead of the $200 / $250 average. Funded accounts keep '
             'every earlier convention, including taking every overlapping signal.\n\n')
    text += ('## Check against EODMAE\n\nOne evaluation started on every weekday with a full '
             f"{spec['reconciliation']['horizon_days']}-day horizon, renewed until it passes.\n\n"
             '| Evaluation | Starts | Passed in 180 days | EODMAE, worst point first | Passed in the first month | '
             'EODMAE, resolved paths | Median days | EODMAE, resolved paths | Cost per activation |\n'
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|\n')
    for prod, r in recon.items():
        e = r['eodmae']
        text += (f"| {prod} × {r['contracts']} MNQ | {r['starts']:,} | {r['activation_rate']:.1%} | "
                 f"{e['activation_rate_mae_first']:.1%} | {r['first_month_rate']:.1%} | "
                 f"{e['first_cycle_rate_resolved']:.1%} | {r['median_days']:.1f} | {e['median_days_resolved']:.1f} | "
                 f"${r['cost_per_activation']:,.0f} |\n")
    text += ('\nThis project assumes the worst point of every trade comes first, so the comparable EODMAE pass '
             'rate is its worst-point-first bound. EODMAE resolves most trades from their exit instead, and its '
             '30-day cycles leave a trade spanning a renewal unbooked, so small differences are expected.\n\n')
    for budget in spec['budgets']:
        i, m = budget
        text += f'## ${i:,} initial; ${m:,}/month\n\n'
        a, b = prior_best[('legacy_25k', i, m)], prior_best[('legacy_50k', i, m)]
        text += (f"Unlimited supply at $200 / $250 a seat (earlier study): 25K ${a['total']:,.0f} "
                 f"({a['accounts']} bought) vs 50K ${b['total']:,.0f} ({b['accounts']} bought).\n\n")
        text += ('| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | '
                 'Cost per funded account | Most passes in a month | Short months without a pass |\n'
                 '|---|---|---:|---:|---:|---:|---:|---:|\n')
        winners = {}
        for prod in spec['products']:
            w = winners[prod] = best([r for r in rows if r['product'] == prod
                                      and [r['initial_cash'], r['monthly_funding']] == budget], 'total')
            cost = f"${w['cost_per_funded']:,.0f}" if w['cost_per_funded'] else 'n/a'
            text += (f"| {prod} | {bundle(w)} | ${w['total']:,.0f} | {w['accounts']} / {w['alive']} | "
                     f"{w['evaluations']} / {w['evaluation_months']} | {cost} | {w['max_passes_in_a_month']} | "
                     f"{w['short_months_without_a_pass']} of {w['short_months']} |\n")
        text += f"\n50K minus 25K: ${winners['legacy_50k']['total'] - winners['legacy_25k']['total']:,.0f}.\n\n"
    text += '## Best total by purchasing and spares\n\n'
    cs = combos(spec)
    text += '| Budget | Product | ' + ' | '.join(combo_label(a, k) for a, k in cs) + ' |\n'
    text += '|---|---|' + '---:|' * len(cs) + '\n'
    for budget, prod in product(spec['budgets'], spec['products']):
        cells = []
        for acq, k in cs:
            w = best([r for r in rows if r['product'] == prod and [r['initial_cash'], r['monthly_funding']] == budget
                      and r['acquisition'] == acq and r['spares'] == k], 'total')
            cells.append(f"${w['total']:,.0f} ({w['accounts']})")
        text += f"| ${budget[0]:,} + ${budget[1]:,}/mo | {prod} | " + ' | '.join(cells) + ' |\n'
    text += '\nCells show best total (accounts funded).\n\n'
    text += ('## Matched settings: share where 50K beats 25K\n\nSame budget, purchasing, spares, withdrawal and '
             'headroom; settings where both lose are excluded.\n\n| Purchasing | 50K ahead |\n|---|---:|\n')
    for acq, k in cs:
        d = [x for x in deltas if x['acquisition'] == acq and x['spares'] == k
             and not (x['total_25k'] <= 0 and x['total_50k'] <= 0)]
        share = f"{sum(x['total_delta_50k_minus_25k'] > 0 for x in d) / len(d):.0%} of {len(d)}" if d else 'n/a'
        text += f'| {combo_label(acq, k)} | {share} |\n'
    text += ('\n## Limits\n\nIn-sample best tested settings on one historical tape, not forecasts. Evaluations '
             'assume the worst point of each trade comes first, like the funded accounts; EODMAE shows the '
             'favourable-first bound 2–3 points lower. Evaluations trade one position at a time while funded '
             'accounts take every overlapping signal, as the owner trades them. All other limits of the earlier '
             'studies apply.\n')
    return text


def write_evaluations(path, ledger):
    fields = ['eval_id', 'started_at', 'state', 'months_paid', 'resets', 'trades_taken', 'passed_at', 'ended_at']
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: getattr(e, k) for k in fields} for e in ledger.evaluations)


def main(spec_path=SPEC_PATH):
    initialize(spec_path)
    spec = SPEC
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
    prior_best = {}
    for r in prior:
        key = (r['product'], r['initial_cash'], r['monthly_funding'])
        if not r['strict_post_payout_balance'] and (key not in prior_best or (r['total'], r['ongoing'])
                                                     > (prior_best[key]['total'], prior_best[key]['ongoing'])):
            prior_best[key] = r
    coarse = [job(prod, i, m, acq, rule, cad, h, k)
              for prod, (i, m), (acq, k), rule, cad, h in product(spec['products'], spec['budgets'], combos(spec),
                  spec['amount_rules'], spec['cadences'], spec['headrooms'])]

    def run(pool, jobs, label):
        missing = sorted(set(jobs) - cache.keys())
        print(f'{label}: {len(missing)} new / {len(jobs)} requested', flush=True)
        with checkpoint.open('a', encoding='utf-8') as handle:
            futures = {pool.submit(evaluate, j): j for j in missing}
            for n, future in enumerate(as_completed(futures), 1):
                r = future.result()
                cache[tuple(r['job'])] = r
                handle.write(json.dumps(r, default=str) + '\n')
                handle.flush()
                if n % 100 == 0 or n == len(missing):
                    print(f'{label}: {n}/{len(missing)} completed', flush=True)
        return [cache[j] for j in jobs]

    with ProcessPoolExecutor(max_workers=spec['workers'], initializer=initialize,
                             initargs=(str(spec_path),)) as pool:
        # Evaluations off: the engine must still reproduce the unlimited-supply winners.
        winners = sorted({tuple(r['job']) for r in prior_best.values()
                          if [r['initial_cash'], r['monthly_funding']] in spec['budgets']})
        replays = list(pool.map(sim.evaluate, winners))
        by_job = {tuple(r['job']): r for r in prior}
        assert all(all(x[k] == by_job[tuple(x['job'])][k] for k in ('ongoing', 'total', 'accounts', 'alive'))
                   for x in replays), 'the engine no longer reproduces the unlimited-supply winners'
        print(f'Unlimited-supply winners reproduced: {len(replays)}', flush=True)
        recon = reconciliation(spec)
        print('Reconciliation:', json.dumps({k: {x: v[x] for x in ('activation_rate', 'median_days')}
                                             for k, v in recon.items()}), flush=True)
        coarse_rows = run(pool, coarse, 'Coarse grid')
        refined = refinement_jobs(coarse_rows, spec)
        run(pool, refined, 'Refinement')
    rows = [cache[j] for j in sorted(set(coarse) | set(refined))]
    deltas = matched_deltas(rows)
    write_csv(out / 'all_settings.csv', rows)
    write_csv(out / 'matched_deltas.csv', deltas)
    (out / 'reconciliation.json').write_text(json.dumps(recon, indent=2), encoding='utf-8')
    (out / 'study.json').write_text(json.dumps({**contract, 'generated_utc': datetime.now(timezone.utc).isoformat(),
        'verified_controls': len(replays), 'reconciliation': recon, 'rows': rows}, indent=2, default=str),
        encoding='utf-8')
    for budget, prod in product(spec['budgets'], spec['products']):
        w = best([r for r in rows if r['product'] == prod and [r['initial_cash'], r['monthly_funding']] == budget], 'total')
        row, result = evaluate(tuple(w['job']), True)
        assert row['total'] == w['total']
        folder = out / f'{prod}__budget_{budget[0]}_{budget[1]}__best_total'
        write_outputs(result, folder)
        write_evaluations(folder / 'evaluations.csv', result.acquisition)
        (folder / 'experiment.json').write_text(json.dumps({'run_config': to_payload(result.config),
            'acquisition': asdict(result.acquisition.policy)}, indent=2), encoding='utf-8')
    write_study_report(out, render(rows, spec, prior_best, recon, deltas, len(replays)))
    assert all(Path(f).is_file() and sha256_file(Path(f)) == h for f, h in protected.items())
    (out / 'preservation_check.json').write_text(json.dumps({'protected_files': len(protected),
        'all_unchanged': True}, indent=2), encoding='utf-8')
    print(f'Completed {len(rows)} paired simulations; prior results unchanged. {out}', flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:])
