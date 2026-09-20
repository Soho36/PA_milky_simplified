"""Frozen RR composition/count and per-account reserve-ladder comparisons."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime
from functools import partial
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.loader import load_trades
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import mortality_metrics, signal_key
from pa_milky.simulator import run_book
from rr_followup_support import Sleeves, SleeveRouter, LadderPolicy
from study_rr_diversification import write_csv

PROFILE = PROJECT_ROOT/'config/studies/legacy_25k_rr_followup.json'
SPEC = PARENT = BASE = EVAL = TAPES = OUT = None


def initialize():
    global SPEC, PARENT, BASE, EVAL, TAPES, OUT
    SPEC = json.loads(PROFILE.read_text())
    PARENT = json.loads((PROJECT_ROOT/SPEC['parent_spec']).read_text())
    BASE = load_config(PROJECT_ROOT/PARENT['scenario'])
    EVAL = EvaluationSpec(**json.loads((PROJECT_ROOT/PARENT['evaluation_spec']).read_text())['evaluations']['legacy_25k'])
    TAPES = {rr:load_trades(BASE.sweeps_root, strategy='RR', risk_reward=rr) for rr in SPEC['rr_values']}
    OUT = PROJECT_ROOT/SPEC['output']


def arms():
    return {**{f'rr_{rr}':[{'rr':rr,'offset':0}] for rr in SPEC['rr_values']}, **SPEC['arms']}


def jobs():
    primary = [('primary',phase,year,'mae_first',name) for year in SPEC['starts']
               for phase in ('isolation','operating') for name in arms()]
    march = [('march','operating',2020,order,name) for order in ('mae_first','mfe_first') for name in arms()]
    sensitivity = [('primary','operating',year,'mfe_first',name) for year in SPEC['mfe_starts']
                   for name in ['rr_1.00',*SPEC['arms']]]
    return primary + march + sensitivity


def case_name(job):
    return '__'.join(map(str, job))


def prior_check(job, result, account_rows):
    experiment,phase,year,order,name = job
    name = 'wide' if name == 'wide4' else name
    root = PROJECT_ROOT/PARENT['output']
    if experiment == 'march':
        file = root/'march_stress'/f'{order}__{name}.json'
        if not file.exists():
            return False
        old = json.loads(file.read_text())['row']
        assert result.pocket_usd == old['net_operating_cash']
        assert len(result.dead) == old['deaths'] and result.alive_at_horizon == old['alive']
    else:
        file = root/'cases'/f'{phase}__{year}__minimum__{order}__{name}.json'
        if not file.exists():
            return False
        old = json.loads(file.read_text())
        for new, previous in zip(account_rows, old['accounts'], strict=True):
            for key in ('account_id','rr','activated_at','alive','died_at','death_trade_key',
                        'trades','ending_balance','ending_headroom','received_payouts'):
                assert new[key] == previous[key], (job,key,new[key],previous[key])
        assert result.pocket_usd == old['row']['net_operating_cash']
        assert result.copies_filled == old['row']['copies']
    return True


def evaluate(job):
    experiment, phase, year, order, name = job
    center = 5700 if experiment == 'march' else PARENT['headroom']
    definitions = [dict(rr=s['rr'],reserve=round(center+s['offset'],2)) for s in arms()[name]]
    sleeves = Sleeves(definitions)
    rule = 'maximum' if experiment == 'march' else 'minimum'
    policy = LadderPolicy(sleeves=sleeves, floor_balance=BASE.trailing_floor_balance_usd,
        name=f'{name}_{rule}', cadence='daily', amount_rule=rule, terminal_withdrawal='none')
    config = replace(BASE, policy=policy, path_order=order, expected_trades=None, expected_windows=None)
    if experiment == 'march':
        acq = AcquisitionPolicy('monthly_current_slot_replacements',5000,200,max_live_accounts=20,
            spare_capacity=2,evaluation=EVAL,evaluations_at_once=20,persistent_demand=True,
            evaluation_start_interval_days=7,evaluations_reserve_seats=True,activate_on_first_check=True)
    else:
        acq = (AcquisitionPolicy('monthly_current_slot_replacements',evaluation=EVAL,**PARENT['operating'])
               if phase == 'operating' else None)
    variants = {d['rr'] for d in definitions} | ({'1.00'} if acq else set())
    tapes = {rr:[t for t in TAPES[rr] if t.entry_at.year >= year] for rr in variants}
    trades = sorted([t for tape in tapes.values() for t in tape],
        key=lambda t:(t.exit_at,t.entry_at,t.window_order,t.source_row,t.ticket,t.trade_key))
    trade_rr = {t.trade_key:rr for rr,tape in tapes.items() for t in tape}
    assert len(trade_rr) == len(trades)
    lookup = {t.trade_key:t for t in trades}
    daily = []
    snapshots = []
    def observe(at, accounts, event, trade):
        if event != 'decision':
            return
        sleeves.assign(accounts)  # assign newborns before their first payout/entry
        live = [a for a in accounts if a.alive]
        if not live:
            return
        balances = Counter(a.headroom_usd for a in live)
        n = len(live)
        record = dict(at=at.isoformat(), alive=n,
            occupied_sleeves=len({sleeves.assigned[a.account_id] for a in live}),
            distinct_headrooms=len(balances), largest_equal_headroom=max(balances.values()),
            effective_headroom_groups=round(n*n/sum(v*v for v in balances.values()),6),
            total_headroom=round(sum(a.headroom_usd for a in live),2),
            total_positive_equity=round(sum(max(0,a.equity_profit_usd) for a in live),2))
        daily.append(record)
        if at.day == 1 or (at.year==2026 and at.month==3 and at.day in (20,23,26,27,31)):
            snap = dict(record)
            if at.year == 2026 and at.month == 3:
                snap['accounts'] = [dict(id=a.account_id,sleeve=sleeves.assigned[a.account_id],
                    rr=sleeves.definition(a.account_id)['rr'],headroom=a.headroom_usd,
                    reserve=sleeves.definition(a.account_id)['reserve']) for a in live]
            snapshots.append(snap)
    result = run_book(trades,config,acquisition=acq,fixed_accounts=20 if phase=='isolation' else None,
        observer=observe,routing=RoutingPolicy(mode='blocked'),
        router_factory=partial(SleeveRouter,sleeves=sleeves,
            weights=dict(Counter(d['rr'] for d in definitions)),trade_rr=trade_rr),
        evaluation_tape=tapes['1.00'] if acq else None)
    assert Economics.measure(result).residual_usd == 0
    account_lookup = {a.account_id:a for a in result.accounts}
    copies = Counter(); until = {}; participants = defaultdict(lambda:defaultdict(set))
    for fill in result.routing_fills:
        trade = lookup[fill['trade_key']]
        for aid in fill['accounts']:
            a = account_lookup[aid]; d = sleeves.definition(aid)
            assert d['rr'] == fill['rr']
            assert a.activated_at <= trade.entry_at and (a.alive or a.died_at >= trade.exit_at)
            assert until.get(aid,trade.entry_at) <= trade.entry_at
            until[aid] = trade.exit_at; copies[aid] += 1
            participants[signal_key(trade)][sleeves.assigned[aid]].add(aid)
    assert sum(copies.values()) == result.copies_filled
    assert all(copies[a.account_id] == a.trades_taken for a in result.accounts)
    for payout in result.payouts:
        # Both protocols have zero processing delay. The actual paid balance
        # must respect this account's own target, not the portfolio average.
        assert payout.balance_after_usd + .005 >= BASE.trailing_floor_balance_usd+sleeves.definition(payout.account_id)['reserve']
    ledger = result.acquisition.summary() if acq else {}
    if acq:
        assert ledger['cash_identity_residual_usd'] == 0
        assert min(e['cash_after_usd'] for e in result.acquisition.cash_events) >= 0
        assert len(result.accounts)+result.unused_spares == ledger['evaluations_activated']
        assert all(d['alive']+d['spares']+d['in_flight'] <= acq.max_live_accounts
                   and d['subscriptions'] <= acq.evaluations_at_once for d in result.acquisition.pipeline_daily)
    account_rows = []
    loss_groups = defaultdict(Counter)
    day_groups = defaultdict(Counter)
    for a in result.accounts:
        t = lookup.get(a.death_trade_key)
        group = sleeves.assigned[a.account_id]
        if t:
            loss_groups[signal_key(t)][group] += 1
            day_groups[a.died_at.date().isoformat()][group] += 1
        account_rows.append(dict(account_id=a.account_id,sleeve=group,**sleeves.definition(a.account_id),
            activated_at=a.activated_at.isoformat(),alive=a.alive,died_at=a.died_at.isoformat() if t else None,
            death_entry_at=t.entry_at.isoformat() if t else None,death_window=t.window_id if t else None,
            death_trade_key=a.death_trade_key,trades=a.trades_taken,ending_balance=a.balance_usd,
            ending_headroom=a.headroom_usd,received_payouts=a.received_usd))
    signal_losses = []
    for (window,entry),groups in sorted(loss_groups.items()):
        exposed = participants[(window,entry)]
        assert all(n <= len(exposed[g]) for g,n in groups.items())
        signal_losses.append(dict(window=window,entry=entry.isoformat(),deaths=dict(groups),
                                  copiers={g:len(ids) for g,ids in exposed.items()}))
    same_max = max((sum(g.values()) for g in loss_groups.values()),default=0)
    calendar = [t for tape in TAPES.values() for t in tape if t.entry_at.year >= year]
    metrics = mortality_metrics(result,calendar)
    assert same_max == metrics['max_same_signal_deaths']
    prior = prior_check(job,result,account_rows)
    march1,april1 = datetime(2026,3,1),datetime(2026,4,1)
    march_cohort = [a for a in result.accounts if a.activated_at<=march1 and (a.alive or a.died_at>=march1)]
    march_deaths = [a for a in result.dead if march1<=a.died_at<april1]
    row = dict(case=case_name(job),experiment=experiment,phase=phase,start_year=year,path_order=order,
        portfolio=name,nominal_sleeves=len(definitions),rr_count=len({d['rr'] for d in definitions}),
        rr_width=round(max(float(d['rr']) for d in definitions)-min(float(d['rr']) for d in definitions),2),
        mean_target=sum(d['reserve'] for d in definitions)/len(definitions),
        net_operating_cash=result.pocket_usd,receipts=result.total_received_usd,total_costs=result.total_purchase_cost_usd,
        copies=result.copies_filled,prior_control_reproduced=prior,**metrics,
        largest_within_sleeve_signal_loss=max((n for g in loss_groups.values() for n in g.values()),default=0),
        max_sleeves_lost_same_signal=max(map(len,loss_groups.values()),default=0),
        multi_sleeve_signal_events=sum(len(g)>1 for g in loss_groups.values()),
        max_sleeves_lost_same_day=max(map(len,day_groups.values()),default=0),
        multi_sleeve_day_events=sum(len(g)>1 for g in day_groups.values()),
        sleeve_loss_events=sum(map(len,loss_groups.values())),
        full_copier_sleeve_loss_events=sum(n==len(participants[key][g]) for key,groups in loss_groups.items() for g,n in groups.items()),
        observed_live_days=len(daily),mean_live_accounts=sum(d['alive'] for d in daily)/len(daily) if daily else 0,
        mean_occupied_sleeves=sum(d['occupied_sleeves'] for d in daily)/len(daily) if daily else 0,
        mean_equal_headroom_fraction=sum(d['largest_equal_headroom']/d['alive'] for d in daily)/len(daily) if daily else 0,
        mean_effective_headroom_groups=sum(d['effective_headroom_groups'] for d in daily)/len(daily) if daily else 0,
        mean_total_headroom=sum(d['total_headroom'] for d in daily)/len(daily) if daily else 0,
        mean_total_positive_equity=sum(d['total_positive_equity'] for d in daily)/len(daily) if daily else 0,
        march1_alive=len(march_cohort),march_cohort_deaths=sum(not a.alive and a.died_at<april1 for a in march_cohort),
        march_total_deaths=len(march_deaths),
        march31_alive=sum(a.activated_at<april1 and (a.alive or a.died_at>=april1) for a in result.accounts))
    evidence = dict(row=row,definitions=definitions,accounts=account_rows,signal_losses=signal_losses,
        day_losses=dict(day_groups),snapshots=snapshots,acquisition=ledger,
        audit=dict(copies_checked=result.copies_filled,assignment_and_overlap_checked=True,
                   reserve_enforced_on_payouts=len(result.payouts),cash_reconciled=True))
    path = OUT/'cases'/f'{row["case"]}.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)
    return row


def alignment():
    reference = {signal_key(t):t for t in TAPES['1.00']}
    rows = []
    for rr,tape in TAPES.items():
        observed = {signal_key(t):t for t in tape}
        assert len(observed) == len(tape)
        common = reference.keys() & observed.keys()
        mismatch = sum(reference[k].candle_range != observed[k].candle_range for k in common)
        assert mismatch == 0
        rows.append(dict(rr=rr,trades=len(tape),missing_vs_rr1=len(reference.keys()-observed.keys()),
            extra_vs_rr1=len(observed.keys()-reference.keys()),common_candle_range_mismatches=mismatch,
            last_exit=max(t.exit_at for t in tape).isoformat()))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--limit',type=int)
    args = parser.parse_args()
    initialize()
    (OUT/'cases').mkdir(parents=True,exist_ok=True)
    contract = dict(spec=SPEC,parent_spec=PARENT,base_config=to_payload(BASE),engine=engine_digest(),
        code={f:sha256_file(PROJECT_ROOT/f) for f in ['scripts/study_rr_followup.py','scripts/rr_followup_support.py',
              'scripts/study_rr_diversification.py','research/legacy_25k/RR_FOLLOWUP.md']},
        inputs={rr:input_digest(replace(BASE,risk_reward=rr)) for rr in SPEC['rr_values']},
        coverage_sha256=sha256_file(PROJECT_ROOT/'config/tape_coverage.json'))
    file = OUT/'contract.json'
    if file.exists():
        assert json.loads(file.read_text()) == contract, 'Contract changed; preserve old results before changing the design'
    else:
        file.write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    write_csv(OUT/'signal_alignment.csv',alignment())
    selected = jobs()[:args.limit] if args.limit else jobs()
    done = {}
    for job in selected:
        saved = OUT/'cases'/f'{case_name(job)}.json'
        if saved.exists():
            done[case_name(job)] = json.loads(saved.read_text())['row']
    pending = [j for j in selected if case_name(j) not in done]
    print(f'{len(selected)} requested; {len(done)} complete; {len(pending)} pending',flush=True)
    with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize) as pool:
        futures = {pool.submit(evaluate,j):j for j in pending}
        for future in as_completed(futures):
            row = future.result(); done[row['case']] = row
            print(f'{len(done)}/{len(selected)} {row["case"]}: deaths={row["deaths"]}, wipeouts={row["book_wipeouts"]}, signal={row["max_same_signal_deaths"]}',flush=True)
    write_csv(OUT/'comparison.csv',[done[case_name(j)] for j in selected])
    if len(selected) == len(jobs()):
        audit = dict(runs=len(done),prior_controls_reproduced=sum(r['prior_control_reproduced'] for r in done.values()),
            copies_checked=sum(r['copies'] for r in done.values()),contract_sha256=sha256_file(file),
            case_sha256={name:sha256_file(OUT/'cases'/f'{name}.json') for name in done})
        (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
        print({k:v for k,v in audit.items() if k!='case_sha256'},flush=True)


if __name__ == '__main__':
    main()
