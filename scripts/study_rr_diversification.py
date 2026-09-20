"""Run the frozen RR mortality-diversification study, with resumable evidence."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.loader import load_trades
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import run_rr_book, mortality_metrics, signal_key
from pa_milky.simulator import run_book

PROFILE_PATH = PROJECT_ROOT/'config/studies/legacy_25k_rr_diversification.json'
SPEC = BASE = TAPES = EVAL = OUT = None


def initialize():
    global SPEC, BASE, TAPES, EVAL, OUT
    SPEC = json.loads(PROFILE_PATH.read_text())
    BASE = load_config(PROJECT_ROOT/SPEC['scenario'])
    OUT = PROJECT_ROOT/SPEC['output']
    TAPES = {rr:load_trades(BASE.sweeps_root, strategy='RR', risk_reward=rr) for rr in SPEC['rr_values']}
    EVAL = EvaluationSpec(**json.loads((PROJECT_ROOT/SPEC['evaluation_spec']).read_text())['evaluations']['legacy_25k'])


def portfolios():
    return {**{f'rr_{rr}':{rr:1} for rr in SPEC['rr_values']}, **SPEC['mixtures']}


def jobs():
    return [(phase, year, rule, path_order, name)
            for rule, path_order, years in [
                ('minimum','mae_first',SPEC['starts']),
                ('maximum','mae_first',SPEC['maximum_withdrawal_starts']),
                ('minimum','mfe_first',SPEC['mfe_first_starts'])]
            for year in years for phase in ('isolation','operating') for name in portfolios()]


def case_name(job):
    return '__'.join(map(str,job))


def audit_fills(result, tapes):
    lookup = {t.trade_key:t for tape in tapes.values() for t in tape}
    accounts = {a.account_id:a for a in result.accounts}
    assigned = result.routing['account_rr']
    until = {}
    copies = Counter()
    for fill in result.routing_fills:
        trade = lookup[fill['trade_key']]
        rr = fill['rr']
        for account_id in fill['accounts']:
            account = accounts[account_id]
            assert assigned[account_id] == rr
            assert account.activated_at <= trade.entry_at
            assert until.get(account_id, trade.entry_at) <= trade.entry_at
            assert account.died_at is None or account.died_at >= trade.exit_at
            until[account_id] = trade.exit_at
            copies[account_id] += 1
    assert sum(copies.values()) == result.copies_filled
    assert all(copies[a.account_id] == a.trades_taken for a in result.accounts)
    assert Economics.measure(result).residual_usd == 0
    if result.acquisition:
        ledger = result.acquisition
        assert ledger.summary()['cash_identity_residual_usd'] == 0
        assert min(e['cash_after_usd'] for e in ledger.cash_events) >= 0
        assert len(result.accounts)+result.unused_spares == ledger.summary()['evaluations_activated']
        assert all(d['alive']+d['spares']+d['in_flight'] <= SPEC['operating']['max_live_accounts']
                   and d['subscriptions'] <= SPEC['operating']['evaluations_at_once']
                   for d in ledger.pipeline_daily)


def evaluate(job):
    phase, year, rule, path_order, name = job
    weights = portfolios()[name]
    tapes = {rr:[t for t in tape if t.entry_at.year >= year] for rr,tape in TAPES.items()}
    policy = WithdrawalPolicy(name=f'{rule}_daily_h{SPEC["headroom"]}',cadence='daily',
        amount_rule=rule,min_retained_balance_usd=BASE.trailing_floor_balance_usd+SPEC['headroom'],
        terminal_withdrawal='none')
    config = replace(BASE, policy=policy, path_order=path_order, expected_trades=None, expected_windows=None)
    acq = (AcquisitionPolicy('monthly_current_slot_replacements',evaluation=EVAL,**SPEC['operating'])
           if phase == 'operating' else None)
    result = run_rr_book(tapes,config,weights,acquisition=acq,
                         fixed_accounts=SPEC['isolation_accounts'] if phase == 'isolation' else None)
    audit_fills(result,tapes)
    # Homogeneous controls must be exact replays of the established engine.
    control_match = None
    if len(weights) == 1:
        rr = next(iter(weights))
        if phase == 'isolation' or rr == '1.00':
            control = run_book(tapes[rr],config,acquisition=acq,
                fixed_accounts=SPEC['isolation_accounts'] if phase == 'isolation' else None,
                routing=RoutingPolicy(mode='blocked'))
            assert result.accounts == control.accounts and result.payouts == control.payouts
            assert result.copies_filled == control.copies_filled
            if acq:
                assert result.acquisition.summary() == control.acquisition.summary()
            control_match = True
    trade_lookup = {t.trade_key:t for tape in tapes.values() for t in tape}
    calendar_tape = [t for rr in SPEC['rr_values'] for t in tapes[rr]]
    metrics = mortality_metrics(result,calendar_tape)
    accepted = {signal_key(trade_lookup[f['trade_key']]) for f in result.routing_fills if f['accounts']}
    offered = {signal_key(t) for rr in weights for t in tapes[rr]}
    ledger = result.acquisition.summary() if result.acquisition else {}
    row = dict(case=case_name(job), phase=phase, start_year=year, withdrawal=rule,path_order=path_order,
        portfolio=name,weights=weights,net_operating_cash=result.pocket_usd,receipts=result.total_received_usd,
        total_costs=result.total_purchase_cost_usd,copies=result.copies_filled,
        distinct_signals=len(accepted),signal_participation=len(accepted)/len(offered),
        homogeneous_control_matched=control_match,evaluation_months=ledger.get('evaluation_months_paid',0),
        rr_deaths=dict(Counter(result.routing['account_rr'][a.account_id] for a in result.dead)),
        **metrics)
    account_rows = []
    for account in result.accounts:
        death_trade = trade_lookup.get(account.death_trade_key)
        account_rows.append(dict(account_id=account.account_id,rr=result.routing['account_rr'][account.account_id],
            activated_at=account.activated_at.isoformat(),alive=account.alive,
            died_at=account.died_at.isoformat() if account.died_at else None,
            death_entry_at=death_trade.entry_at.isoformat() if death_trade else None,
            death_window=death_trade.window_id if death_trade else None,
            death_trade_key=account.death_trade_key,trades=account.trades_taken,
            ending_balance=account.balance_usd,ending_headroom=account.headroom_usd,
            gross_payouts=account.gross_paid_usd,received_payouts=account.received_usd))
    evidence={'row':row,'accounts':account_rows,'acquisition':ledger,
              'audit':{'no_overlapping_positions':True,'rr_assignments_match':True,
                       'cash_and_economics_reconcile':True,'copies_checked':result.copies_filled},
              'monthly_payouts':dict(Counter())}
    by_month = Counter()
    for payout in result.payouts:
        by_month[payout.at.strftime('%Y-%m')] += payout.received_usd
    evidence['monthly_payouts'] = {k:round(v,2) for k,v in sorted(by_month.items())}
    (OUT/'cases'/f'{row["case"]}.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return row


def write_csv(path,rows):
    if not rows:
        return
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def alignment():
    reference = {signal_key(t):t for t in TAPES['1.00']}
    rows=[]
    for rr,tape in TAPES.items():
        observed = {signal_key(t):t for t in tape}
        assert len(observed)==len(tape)
        common = reference.keys() & observed.keys()
        row=dict(rr=rr,trades=len(tape),shared_entries=len(common),missing_vs_rr1=len(reference.keys()-observed.keys()),
            extra_vs_rr1=len(observed.keys()-reference.keys()),
            common_candle_range_mismatches=sum(reference[k].candle_range!=observed[k].candle_range for k in common),
            common_loser_amount_mismatches=sum(reference[k].gross_pnl_usd!=observed[k].gross_pnl_usd for k in common
                if reference[k].gross_pnl_usd<0 and observed[k].gross_pnl_usd<0),
            last_exit=max(t.exit_at for t in tape).isoformat(),
            missing_signals=[f'{w}@{at.isoformat()}' for w,at in sorted(reference.keys()-observed.keys())])
        assert row['common_candle_range_mismatches']==0
        rows.append(row)
    return rows


def report(rows):
    primary = [r for r in rows if r['withdrawal']=='minimum' and r['path_order']=='mae_first']
    index={(r['phase'],r['start_year'],r['withdrawal'],r['path_order'],r['portfolio']):r for r in rows}
    deltas=[]
    for row in rows:
        baseline=index[tuple(row[k] for k in ('phase','start_year','withdrawal','path_order'))+('rr_1.00',)]
        delta={k:row[k] for k in ('case','phase','start_year','withdrawal','path_order','portfolio')}
        for key in ('net_operating_cash','deaths','book_wipeouts','days_empty_after_first_activation',
                    'max_same_signal_deaths','possible_20d_death_cluster','half_loss_20d_episodes_min5'):
            delta[key+'_delta_vs_rr1']=round(row[key]-baseline[key],4)
        deltas.append(delta)
    write_csv(OUT/'comparison.csv',rows)
    write_csv(OUT/'deltas_vs_rr1.csv',deltas)
    lines=['# RR diversification: clustered deaths','',
        f'{len(rows)} frozen historical runs. Daily minimum/$6,800 headroom is primary; maximum-daily and MFE-first are sensitivities.',
        'No RR weights, reserve or supply policy were optimized. Cash is net of all acquisition/evaluation fees, excludes owner contributions and excludes terminal receipts.','',
        '## Main comparisons','',
        'Death dates are exported-exit proxies. Same-signal deaths and possible interval clusters must be considered alongside rolling exit-timed losses.','']
    for phase in ('isolation','operating'):
        for year in (2020,2023):
            lines += [f'### {phase}, fresh {year} start','',
                '| Portfolio | Net cash | Deaths | Alive | Wipeouts | Empty days | Max same-signal deaths | Possible 20-day cluster | Half-loss 20-day episodes |',
                '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
            for r in primary:
                if r['phase']==phase and r['start_year']==year:
                    lines.append(f'| {r["portfolio"]} | ${r["net_operating_cash"]:,.0f} | {r["deaths"]} | {r["alive"]} | {r["book_wipeouts"]} | {r["days_empty_after_first_activation"]:.1f} | {r["max_same_signal_deaths"]} | {r["possible_20d_death_cluster"]} | {r["half_loss_20d_episodes_min5"]} |')
            lines.append('')
    lines += ['## Mixture comparisons across primary start dates','',
              '| Phase | Mix | Lower same-signal peak vs RR1 | Lower possible 20-day peak vs RR1 | Fewer wipeouts vs RR1 | Higher net cash vs RR1 |',
              '|---|---|---:|---:|---:|---:|']
    for phase in ('isolation','operating'):
        for name in SPEC['mixtures']:
            selected=[r for r in primary if r['phase']==phase and r['portfolio']==name]
            counts=[]
            for key,higher in [('max_same_signal_deaths',False),('possible_20d_death_cluster',False),
                               ('book_wipeouts',False),('net_operating_cash',True)]:
                counts.append(sum((r[key]>index[(phase,r['start_year'],'minimum','mae_first','rr_1.00')][key]) if higher
                                  else (r[key]<index[(phase,r['start_year'],'minimum','mae_first','rr_1.00')][key]) for r in selected))
            lines.append(f'| {phase} | {name} | '+ ' | '.join(f'{n}/{len(selected)}' for n in counts)+' |')
    lines += ['', '## Interpretation limits','',
        '- A homogeneous RR may be safer than a mixture; compare mixtures with all their constituents before attributing a benefit to mixing.',
        '- Small native entry-set differences remain and are listed in signal_alignment.csv. No absent outcome was fabricated.',
        '- Observed trade dates define rolling trading-day windows. Fractions use the cohort alive at the window start; replacement demand includes all deaths.',
        '- Real intratrade threshold crossing times are unknown. Same-signal grouping and interval bounds do not reconstruct them.',
        '- Fresh starts overlap the selection history and differ in duration. Results do not estimate independent probabilities or future annual income.',
        '- The supply policy is inherited and frozen, including its fee/rule assumptions; this study does not verify current firm terms.',
        '', 'Every run checks assignment RR, no overlap, cash/economic reconciliation and evaluation seat limits. Homogeneous isolation controls and operating RR1 also reproduce the existing engine exactly.',
        '', 'Files: comparison.csv, deltas_vs_rr1.csv, signal_alignment.csv, contract.json, audit.json and per-case account/death ledgers in cases/.','']
    (OUT/'rr_diversification__REPORT.generated.md').write_text('\n'.join(lines),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int)
    parser.add_argument('--limit',type=int,help='Smoke test only; full report is produced only for a complete run')
    args=parser.parse_args()
    initialize()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'cases').mkdir(exist_ok=True)
    contract={'spec':SPEC,'base_config':to_payload(BASE),'engine':engine_digest(),
              'runner_sha256':sha256_file(Path(__file__)),
              'inputs':{rr:input_digest(replace(BASE,risk_reward=rr)) for rr in SPEC['rr_values']},
              'coverage_sha256':sha256_file(PROJECT_ROOT/'config/tape_coverage.json')}
    path=OUT/'contract.json'
    if path.exists():
        assert json.loads(path.read_text())==contract,'Study contract changed; preserve old results before a new run'
    else:
        path.write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    write_csv(OUT/'signal_alignment.csv',alignment())
    selected=jobs()[:args.limit] if args.limit else jobs()
    completed={}
    for job in selected:
        file=OUT/'cases'/f'{case_name(job)}.json'
        if file.exists():
            completed[case_name(job)]=json.loads(file.read_text())['row']
    pending=[j for j in selected if case_name(j) not in completed]
    print(f'{len(selected)} requested; {len(completed)} already complete; {len(pending)} pending',flush=True)
    with ProcessPoolExecutor(max_workers=args.workers or SPEC['workers'],initializer=initialize) as executor:
        futures={executor.submit(evaluate,j):j for j in pending}
        for future in as_completed(futures):
            row=future.result(); completed[row['case']]=row
            print(f'{len(completed)}/{len(selected)} {row["case"]}: cash={row["net_operating_cash"]:.0f}, deaths={row["deaths"]}, same-signal={row["max_same_signal_deaths"]}',flush=True)
    if len(selected)==len(jobs()):
        rows=[completed[case_name(j)] for j in jobs()]
        report(rows)
        audit={'runs':len(rows),'homogeneous_controls_reproduced':sum(r['homogeneous_control_matched'] is True for r in rows),
               'trade_copies_checked':sum(r['copies'] for r in rows),
               'case_sha256':{r['case']:sha256_file(OUT/'cases'/f'{r["case"]}.json') for r in rows},
               'contract_sha256':sha256_file(path)}
        (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in audit.items() if k!='case_sha256'}),flush=True)


if __name__=='__main__':
    main()
