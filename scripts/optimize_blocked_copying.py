"""Joint bounded operating-policy search with cash funding and blocked copying."""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from study_legacy_routing import write_csv, account_rows
from report_names import report_path

SPEC_PATH = PROJECT_ROOT/'config/studies/legacy_25k_blocked_optimization.json'
SPEC = BASE = TAPES = ACQUISITIONS = None
SCORES = ('ongoing', 'total')


def initialize():
    global SPEC, BASE, TAPES, ACQUISITIONS
    SPEC = json.loads(SPEC_PATH.read_text(encoding='utf-8'))
    BASE = load_config(PROJECT_ROOT/SPEC['scenario'])
    tape = load_tape(BASE)
    TAPES = {year: [t for t in tape if t.entry_at.year >= year]
             for year in [2020]+SPEC['transfer_starts']}
    ACQUISITIONS = {a['id']: {k:v for k,v in a.items() if k != 'id'} for a in SPEC['acquisitions']}


def job(acq, seed, rule, cadence, h, *, year=2020, budget=None, amount=0):
    initial, monthly = budget or SPEC['budget']
    return (year, initial, monthly, acq, seed, rule, cadence, h, amount)


def evaluate(j, detail=False):
    year, initial, monthly, acq, seed, rule, cadence, headroom, amount = j
    tape = TAPES[year]
    policy = WithdrawalPolicy(name=f'{rule}_{amount}_{cadence}_h{headroom}',
        cadence=cadence, amount_rule=rule, amount_usd=amount,
        shortfall='accrue_backlog' if rule == 'fixed' else 'skip', quantize_to_amount=False,
        min_retained_balance_usd=BASE.trailing_floor_balance_usd+headroom,
        terminal_withdrawal='firm_permitted')
    config = replace(BASE, expected_trades=len(tape), policy=policy)
    acquisition = AcquisitionPolicy(**ACQUISITIONS[acq], initial_cash_usd=initial,
        monthly_contribution_usd=monthly, max_live_accounts=SPEC['max_live_accounts'])
    peak = 0

    def observe(at, accounts, event, trade):
        nonlocal peak
        if event == 'decision':
            peak = max(peak, sum(a.alive for a in accounts))

    result = run_book(tape, config, acquisition=acquisition, initial_accounts=seed,
                      routing=RoutingPolicy(mode='blocked'), observer=observe)
    cash = result.acquisition.summary()
    economics = Economics.measure(result)
    terminal = round(sum(e.received_usd for e in result.terminal_payouts), 2)
    assert cash['cash_identity_residual_usd'] == economics.residual_usd == 0
    assert cash['net_cash_created_usd'] == result.pocket_usd
    assert peak <= SPEC['max_live_accounts']
    assert min(e['cash_after_usd'] for e in result.acquisition.cash_events) >= 0
    signals = sum(bool(f['accounts']) for f in result.routing_fills)
    row = dict(job=list(j), start_year=year, initial_cash=initial, monthly_funding=monthly,
        acquisition=acq, initial_accounts=seed, withdrawal=rule, cadence=cadence,
        amount=amount, headroom=headroom, reserve=policy.min_retained_balance_usd,
        ongoing=round(result.pocket_usd-terminal, 2), terminal=terminal, total=result.pocket_usd,
        accounts=len(result.accounts), alive=result.alive_at_horizon, deaths=len(result.dead), peak_live=peak,
        spend=result.total_purchase_cost_usd, receipts=result.total_received_usd,
        contributions=cash['owner_contributions_usd'], ending_owner_cash=cash['ending_owner_cash_usd'],
        cash_limited_decisions=cash['cash_limited_decisions'],
        minimum_owner_cash=min(e['cash_after_usd'] for e in result.acquisition.cash_events),
        copies=result.copies_filled, signals_loaded=len(tape), signals_executed=signals,
        signal_participation=signals/len(tape),
        zero_live_signals=sum(f['alive'] == 0 for f in result.routing_fills),
        pending_replacements=result.acquisition.pending_replacements,
        allocation_sha256=result.routing['allocation_sha256'], economics=economics.to_payload())
    return (row, result) if detail else row


def best(rows, score):
    secondary = 'total' if score == 'ongoing' else 'ongoing'
    return min(rows, key=lambda r: (-r[score], -r[secondary], r['spend'], r['headroom'], tuple(r['job'])))


def coarse_jobs():
    return [job(a, s, r, c, h) for a,s,r,c,h in product(ACQUISITIONS, SPEC['initial_accounts'],
        SPEC['amount_rules'], SPEC['cadences'], SPEC['coarse_headrooms'])]


def refined_jobs(rows):
    families = defaultdict(list)
    for r in rows:
        families[(r['acquisition'], r['withdrawal'], r['cadence'])].append(r)
    jobs = set()
    for family in families.values():
        for score in SCORES:
            winner = best(family, score)
            for d in range(-SPEC['refinement_radius'], SPEC['refinement_radius']+1, SPEC['refinement_step']):
                h = winner['headroom']+d
                if 0 <= h <= max(SPEC['coarse_headrooms']):
                    j = list(winner['job']); j[7] = h; jobs.add(tuple(j))
    return sorted(jobs)


def json_write(path, payload):
    path.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')


def export_details(out, label, row):
    actual, result = evaluate(tuple(row['job']), detail=True)
    assert actual == row
    folder = out/label
    folder.mkdir(exist_ok=True)
    json_write(folder/'summary.json', {'row':row, 'config':to_payload(result.config),
                                      'acquisition':asdict(result.acquisition.policy)})
    write_csv(folder/'accounts.csv', account_rows(result))
    write_csv(folder/'payouts.csv', [asdict(e) for e in result.payouts])
    write_csv(folder/'cash.csv', result.acquisition.cash_events)
    write_csv(folder/'decisions.csv', result.acquisition.decisions)
    write_csv(folder/'replacements.csv', result.acquisition.replacement_events)
    write_csv(folder/'blocked_fills.csv', [{**f, 'accounts':';'.join(map(str,f['accounts']))} for f in result.routing_fills])


def render(data):
    text = ('# Blocked copying: operating-policy optimization\n\n'
        '**Primary funding: $1,000 initially plus $200/month.** One MNQ per accepted setup per account; '
        'accounts accept entries only while flat. Cash-funded purchases, 20 live seats, inherited $200 instant funded-seat fee. '
        'Account evaluation costs/delays are not modeled in this search. Both cash objectives exclude owner contributions '
        'and subtract every purchase fee. Total adds one firm-permitted terminal request.\n\n'
        f"Completed {len(data['coarse_jobs']):,} exhaustive coarse-grid combinations, "
        f"{len(set(map(tuple,data['refined_jobs']))-set(map(tuple,data['coarse_jobs']))):,} additional local refinement settings, "
        'and a focused fixed-amount/backlog extension. Starting inventory, purchase family, withdrawal amount family, '
        'cadence and reserve are searched jointly on the coarse grid. Refinement keeps each selected seed fixed. '
        'The result is a best tested policy and an exhaustive-grid optimum within the declared coarse domain, '
        '**not a proven global optimum over arbitrary policies or continuous reserves**.\n\n'
        'Coarse headroom above the $25,100 frozen floor: '+str(SPEC['coarse_headrooms'])+'. '
        'Five initial inventories (1–5), 13 purchase configurations, minimum/maximum withdrawals and three cadences. '
        'Initial inventory replaces the first monthly purchase; weekly purchases can still occur on a Monday. '
        'Replace-N maintains a target of N at daily checks; reinvest budgets its stated fraction of cumulative receipts '
        'and restarts with one account when empty and affordable. Scheduled purchases without replacement clauses '
        'do not automatically replace deaths. The two monthly replacement variants either add replacements to growth '
        'or let a replacement consume an unused current-month slot.\n\n')
    text += '## Winners on the full dataset\n\n'+table(data['winners'])
    text += '## Inherited blocked-copy controls at the primary budget\n\n'+table(data['primary_controls'])
    text += ('## Frozen-policy historical transfers\n\n'
        'Winners are selected only from the primary full-tape search and applied unchanged below. '
        'Later starts overlap the selection dataset; these are historical sensitivity checks, not unseen out-of-sample evidence. '
        'Other budgets receive the same initial seat count and policy, not a new search.\n\n')+table(data['transfers'])
    text += ('## Search and evidence limits\n\n'
        'No search over contract size, signal filters, calendar phase, product, dynamic reserve functions, firm rules '
        'or evaluation supply. Fixed requests accrue monthly even when checks are daily/weekly; the focused fixed-amount '
        'extension is not a complete joint search of those families. Failed-account extrema are booked at exported exits; '
        'pending-order reservation times are absent. Cash and capacity reconcile in every run. Selected details include '
        'accounts, entries, receipts and funding ledgers. Every inherited blocked-copy control reproduces before search. '
        'Ties and tested reserve bounds are in best_by_family.csv. A boundary or near-best setting is not a confidence interval.\n')
    return text


def table(rows):
    text = '| Start | Budget | Seed | Purchases | Withdraw / cadence | Reserve | Bought / deaths | Coverage | Ongoing net | Total net |\n'
    text += '|---:|---|---:|---|---|---:|---:|---:|---:|---:|\n'
    for r in rows:
        text += (f"| {r['start_year']} | {r['initial_cash']} + {r['monthly_funding']}/mo | {r['initial_accounts']} | "
            f"{r['acquisition']} | {r['withdrawal']} {r['amount'] or ''} / {r['cadence']} | ${r['reserve']:,.0f} | "
            f"{r['accounts']} / {r['deaths']} | {r['signal_participation']:.2%} | ${r['ongoing']:,.2f} | ${r['total']:,.2f} |\n")
    return text+'\n'


def main():
    initialize()
    out = PROJECT_ROOT/SPEC['output']; out.mkdir(parents=True, exist_ok=True)
    control_root = PROJECT_ROOT/SPEC['control_output']
    protected = {str(p.relative_to(control_root)):sha256_file(p) for p in control_root.rglob('*') if p.is_file()}
    contract = {'spec':SPEC, 'config':to_payload(BASE), 'engine':engine_digest(), 'inputs':input_digest(BASE),
                'runner_sha256':sha256_file(Path(__file__)),
                'shared_io_sha256':sha256_file(Path(__file__).with_name('study_legacy_routing.py')),
                'protected_controls':protected}
    contract_path = out/'contract.json'
    if contract_path.exists():
        assert json.loads(contract_path.read_text(encoding='utf-8')) == contract, 'Resume contract changed'
    else:
        json_write(contract_path, contract)
    checkpoint = out/'checkpoint.jsonl'
    cache = {tuple(r['job']):r for r in map(json.loads, checkpoint.read_text().splitlines())} if checkpoint.exists() else {}

    def run(pool, jobs, label):
        missing = sorted(set(jobs)-cache.keys())
        print(f'{label}: {len(missing)} new / {len(set(jobs))} requested', flush=True)
        with checkpoint.open('a', encoding='utf-8') as log:
            futures = {pool.submit(evaluate,j):j for j in missing}
            for n,f in enumerate(as_completed(futures),1):
                r = f.result(); cache[tuple(r['job'])] = r
                log.write(json.dumps(r)+'\n'); log.flush()
                if n%25 == 0 or n == len(missing):
                    print(f'{label}: {n}/{len(missing)} complete', flush=True)
        return [cache[j] for j in sorted(set(jobs))]

    with ProcessPoolExecutor(max_workers=SPEC['workers'], initializer=initialize) as pool:
        old = json.loads((control_root/'study.json').read_text(encoding='utf-8'))
        inherited = [r for r in old['rows'] if r['arm'] == 'blocked_copy']
        control_jobs = [job('monthly_plus_replacements',5,'minimum','daily',r['retained_balance_usd']-25100,
                           year=r['start_year'],budget=(r['initial_cash_usd'],r['monthly_contribution_usd'])) for r in inherited]
        control_rows = run(pool, control_jobs, 'Historical controls')
        for old_r,j in zip(inherited,control_jobs):
            r = cache[j]
            for a,b in [('ongoing','ongoing_net_usd'),('total','total_net_usd'),('copies','copies'),
                        ('accounts','accounts'),('alive','alive'),('allocation_sha256','routing')]:
                expected = old_r[b]['allocation_sha256'] if b == 'routing' else old_r[b]
                assert r[a] == expected, (j,a,r[a],expected)
        coarse = coarse_jobs(); coarse_rows = run(pool, coarse, 'Exhaustive coarse grid')
        refined = refined_jobs(coarse_rows); run(pool, refined, 'Per-family reserve refinement')
        searched = set(coarse)|set(refined)
        anchor_jobs = {tuple(best([cache[j] for j in searched],s)['job']) for s in SCORES}
        fixed = {job(j[3],j[4],'fixed',c,h,amount=a) for j in anchor_jobs
                 for c,h,a in product(SPEC['cadences'], SPEC['coarse_headrooms'], SPEC['fixed_amount_screen'])}
        run(pool, fixed, 'Focused fixed-amount extension'); searched |= fixed
        rows = [cache[j] for j in sorted(searched)]
        winners = [best(rows,s) for s in SCORES]
        selected = {tuple(r['job']) for r in winners}
        transfer_jobs = set()
        for j in selected:
            for year in SPEC['transfer_starts']:
                transfer_jobs.add((year,*j[1:]))
            for initial,monthly in SPEC['transfer_budgets']:
                transfer_jobs.add((j[0],initial,monthly,*j[3:]))
        transfers = run(pool, transfer_jobs, 'Frozen policy transfers')
    families = defaultdict(list)
    for r in rows:
        families[(r['acquisition'],r['withdrawal'],r['cadence'],r['amount'])].append(r)
    summaries = []
    for family in families.values():
        for score in SCORES:
            w = best(family,score)
            summaries.append({**w, 'objective':score,'tested_count':len(family),
                'tied_best_settings':sum(r[score] == w[score] for r in family),
                'headroom_min':min(r['headroom'] for r in family),'headroom_max':max(r['headroom'] for r in family),
                'within_one_percent_count':sum(r[score] >= w[score]*.99 for r in family) if w[score]>0 else None})
    for label,rs in [('all_settings',rows),('best_by_family',summaries),('transfers',transfers)]:
        write_csv(out/f'{label}.csv', [{k:v for k,v in r.items() if k not in ('economics','job')} for r in rs])
    details = []
    for n,j in enumerate(sorted(selected),1):
        label = f'winner_{n}'; export_details(out,label,cache[j]); details.append(label)
    primary_controls = [r for r in control_rows if (r['initial_cash'],r['monthly_funding'],r['start_year']) == (*SPEC['budget'],2020)]
    data = {'spec':SPEC,'coarse_jobs':coarse,'refined_jobs':refined,'fixed_jobs':sorted(fixed),
            'rows':rows,'winners':winners,'winner_objectives':list(SCORES),'details':details,
            'primary_controls':primary_controls,'controls':control_rows,'transfers':transfers,
            'generated_utc':datetime.now(timezone.utc).isoformat(),'contract_sha256':sha256_file(contract_path)}
    data['evidence_files'] = {str(p.relative_to(out)).replace('\\','/'):sha256_file(p)
                              for label in details for p in sorted((out/label).iterdir()) if p.is_file()}
    json_write(out/'study.json',data)
    report_path(out, 'REPORT.generated.md').write_text(render(data),encoding='utf-8')
    assert all(sha256_file(control_root/name) == digest for name,digest in protected.items())
    print(f'Completed {len(rows)} search settings, {len(control_rows)} controls, {len(transfers)} transfers. {out}',flush=True)


if __name__ == '__main__':
    main()
