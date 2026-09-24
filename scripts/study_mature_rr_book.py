"""Pre-owned 20-seat RR books, fixed allocations, matched equity and recovery."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime
from functools import partial
import argparse
import csv
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import PROJECT_ROOT, load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec
from pa_milky.loader import WINDOWS, load_trades
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, sha256_file
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import RRRouter
from mature_book_support import calendar_runner, endow, capacity_metrics
from study_rr_episodes import windows

ROOT = PROJECT_ROOT / 'results/legacy_25k/mature_rr_book'
PROTOCOL = PROJECT_ROOT / 'research/legacy_25k/MATURE_RR_BOOK.md'
PARENT_PATH = PROJECT_ROOT / 'config/studies/legacy_25k_rr_diversification.json'
END = datetime(2026, 7, 1)
ARMS = {'pair': {'0.50': 10, '2.50': 10},
        'middle10': {'0.50': 9, '2.50': 9, '1.00': 2},
        'middle20': {'0.50': 8, '2.50': 8, '1.00': 4},
        'rr050': {'0.50': 20}, 'rr100': {'1.00': 20}, 'rr250': {'2.50': 20}}
BASE = PARENT = EVAL = TAPES = PRIOR = None


def read(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def boot():
    global BASE, PARENT, EVAL, TAPES, PRIOR
    PARENT = json.loads(PARENT_PATH.read_text())
    BASE = load_config(PROJECT_ROOT / PARENT['scenario'])
    EVAL = EvaluationSpec(**json.loads((PROJECT_ROOT / PARENT['evaluation_spec']).read_text())['evaluations']['legacy_25k'])
    TAPES = {rr: load_trades(BASE.sweeps_root, risk_reward=rr) for rr in ('0.50','1.00','2.50')}
    PRIOR = {(r['risk_reward'],r['case']):r for r in read(PROJECT_ROOT / 'results/legacy_25k/rr_gg_episodes/windows.csv')
             if r['strategy']=='RR' and r['months']=='3' and r['budget']=='1500'}


def evaluate(job):
    name, headroom, phase, start, stress_end = job
    horizon = stress_end if phase == 'hold' else min(datetime(start.year+1,start.month,1), END)
    case = f'{name}__h{headroom}__{phase}__{start.date()}'
    weights = ARMS[name]
    tapes = {rr:[t for t in tape if start <= t.entry_at < horizon] for rr,tape in TAPES.items()}
    trades = sorted([t for tape in tapes.values() for t in tape],
                    key=lambda t:(t.exit_at,t.entry_at,t.window_order,t.source_row,t.ticket,t.trade_key))
    lookup = {t.trade_key:t for t in trades}
    trade_rr = {t.trade_key:rr for rr,tape in tapes.items() for t in tape}
    assert len(lookup)==len(trades)==len(trade_rr)
    policy = WithdrawalPolicy() if phase == 'hold' else WithdrawalPolicy(
        name='mature_daily_minimum',cadence='daily',amount_rule='minimum',
        min_retained_balance_usd=BASE.trailing_floor_balance_usd+6800,terminal_withdrawal='none')
    config = replace(BASE,policy=policy,expected_trades=None,expected_windows=None,
                     purchase_fee_usd=0 if phase=='hold' else BASE.purchase_fee_usd)
    acquisition = None if phase=='hold' else AcquisitionPolicy(
        'monthly_current_slot_replacements',evaluation=EVAL,**PARENT['operating'])
    router_box = {}
    def factory(*args,**kwargs):
        r = RRRouter(*args,weights=weights,trade_rr=trade_rr,**kwargs)
        router_box['router']=r
        return r
    initialized=False
    initial=[]
    snapshots=[]
    def observe(at,accounts,event,trade):
        nonlocal initialized
        if event=='decision' and not initialized:
            assert at==start
            endow(accounts,start,headroom,BASE.frozen_floor_profit_usd)
            initialized=True
            router_box['router'].assign(accounts)
            assert Counter(router_box['router'].account_rr.values())==Counter(weights)
            initial.extend(dict(id=a.account_id,rr=router_box['router'].account_rr[a.account_id],
                                balance=a.balance_usd,headroom=a.headroom_usd,floor=a.floor_profit_usd,
                                peak=a.peak_profit_usd,payout_count=a.payout_count,prior_days=len(a.day_pnl_usd))
                           for a in accounts)
        if event in ('decision','horizon'):
            router_box['router'].assign(accounts)
            live=[a for a in accounts if a.alive]
            counts=Counter(router_box['router'].account_rr[a.account_id] for a in live)
            snapshots.append(dict(at=at.isoformat(),alive=len(live),original_alive=sum(a.account_id<=20 for a in live),
                                  **{f'rr_{rr}':counts[rr] for rr in ('0.50','1.00','2.50')},
                                  retained_equity=round(sum(a.equity_profit_usd for a in live),2)))
    runner=calendar_runner(start,horizon)
    result=runner(trades,config,acquisition=acquisition,fixed_accounts=20 if phase=='hold' else None,
                  observer=observe,routing=RoutingPolicy(mode='blocked'),router_factory=factory,
                  evaluation_tape=tapes['1.00'] if acquisition else None)
    assert initialized and result.tape_first_entry==start
    initial_equity=20*(headroom+BASE.frozen_floor_profit_usd)
    assert abs(Economics.measure(result).residual_usd-initial_equity)<.001
    router=router_box['router']; counts=Counter(); until={}; pending=0
    accounts={a.account_id:a for a in result.accounts}
    for fill in result.routing_fills:
        t=lookup[fill['trade_key']]
        for aid in fill['accounts']:
            a=accounts[aid]
            assert router.account_rr[aid]==trade_rr[t.trade_key]
            assert a.activated_at<=t.entry_at and until.get(aid,t.entry_at)<=t.entry_at
            assert a.alive or a.died_at>=t.exit_at
            until[aid]=t.exit_at
            if t.exit_at<horizon: counts[aid]+=1
            else: pending+=1
    assert sum(counts.values())==result.copies_filled
    assert all(a.trades_taken==counts[a.account_id] for a in result.accounts)
    assert all(p.balance_after_usd+.005>=BASE.trailing_floor_balance_usd+6800 for p in result.payouts)
    ledger=result.acquisition.summary() if acquisition else {}
    if acquisition:
        assert ledger['cash_identity_residual_usd']==0
        assert len(accounts)+result.unused_spares-20==ledger['evaluations_activated']
        assert min(e['cash_after_usd'] for e in result.acquisition.cash_events)>=0
        assert all(d['alive']+d['spares']+d['in_flight']<=20 and d['subscriptions']<=5
                   for d in result.acquisition.pipeline_daily)
    rows=[dict(account_id=a.account_id,rr=router.account_rr[a.account_id],original=a.account_id<=20,
               activated_at=a.activated_at.isoformat(),alive=a.alive,
               died_at=a.died_at.isoformat() if not a.alive else None,death_trade_key=a.death_trade_key,
               balance=a.balance_usd,headroom=a.headroom_usd,received=a.received_usd,trades=a.trades_taken)
          for a in result.accounts]
    prior_checks=0
    if phase=='hold' and headroom==1500:
        for a in rows:
            old=PRIOR[a['rr'],f'3m_{start.date()}']
            assert a['alive']==(old['breached']=='False')
            assert (a['death_trade_key'] or '')==old['trade_key']
            assert (a['died_at'] or '')==old['exit']
            prior_checks+=1
    metrics=capacity_metrics(rows,start,horizon,stress_end)
    recoveries=metrics.pop('recoveries')
    original_stress=sum(a['original'] and (a['alive'] or datetime.fromisoformat(a['died_at'])>=stress_end) for a in rows)
    record=dict(case=case,portfolio=name,headroom=headroom,phase=phase,start=start.isoformat(),
                stress_end=stress_end.isoformat(),end=horizon.isoformat(),followup_days=(horizon-start).days,
                complete_12m=phase=='recovery' and horizon==datetime(start.year+1,start.month,1),
                initial_equity=initial_equity,original_survivors_quarter=original_stress,
                original_survivors_end=sum(a['original'] and a['alive'] for a in rows),
                original_deaths=sum(a['original'] and not a['alive'] for a in rows),
                replacement_deaths=sum(not a['original'] and not a['alive'] for a in rows),
                replacement_accounts=len(rows)-20,**metrics,receipts=result.total_received_usd,
                replacement_costs=result.total_purchase_cost_usd,forward_net_cash=result.pocket_usd,
                retained_equity=result.equity_at_horizon_usd,
                end_allocation_matches_target=Counter(a['rr'] for a in rows if a['alive'])==Counter(weights),
                owner_contributions=ledger.get('owner_contributions_usd',0),
                cash_limited_decisions=ledger.get('cash_limited_decisions',0),
                ending_owner_cash=ledger.get('ending_owner_cash_usd',0),
                copies=result.copies_filled,open_account_positions_at_horizon=pending,
                prior_marker_checks=prior_checks)
    evidence=dict(row=record,initial_accounts=initial,accounts=rows,recovery_episodes=recoveries,
                  snapshots=snapshots,acquisition=ledger,
                  audit=dict(endowment_adjusted_economics=True,settled_copies_checked=result.copies_filled,
                             capacity_and_reserve_checked=True,nonoverlap_and_assignment_checked=True))
    (ROOT/'cases'/f'{case}.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return record


def summaries(rows):
    out=[]
    for phase in ('hold','recovery'):
        for h in (6800,1500):
            for name in ARMS:
                r=[x for x in rows if x['phase']==phase and x['headroom']==h and x['portfolio']==name]
                loss=[x for x in r if x['had_loss']]
                restored=[x for x in loss if x['first_restored']]
                out.append(dict(phase=phase,headroom=h,portfolio=name,cases=len(r),
                                first_quarter_full_loss=sum(x['original_survivors_quarter']==0 for x in r),
                                mean_original_survivors_quarter=statistics.mean(x['original_survivors_quarter'] for x in r),
                                cases_with_loss=len(loss),first_recovered_cases=len(restored),
                                first_unrecovered_cases=len(loss)-len(restored),
                                median_first_recovery_days=statistics.median(x['first_recovery_days'] for x in restored) if restored else '',
                                wipeout_cases=sum(x['wipeouts']>0 for x in r),
                                complete_12m_cases=sum(x['complete_12m'] for x in r),
                                **{f'mean_{key}':statistics.mean(x[key] for x in r) for key in
                                   ('min_live','empty_days','days_below_5','days_below_10','days_below_20',
                                    'original_deaths','replacement_deaths','forward_net_cash','replacement_costs',
                                    'receipts','retained_equity','cash_limited_decisions')},
                                worst_min_live=min(x['min_live'] for x in r)))
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    boot();(ROOT/'cases').mkdir(parents=True,exist_ok=True)
    oldroot=PROJECT_ROOT/'results/legacy_25k/rr_gg_episodes'
    old=json.loads((oldroot/'manifest.json').read_text())
    assert old['engine']==engine_digest()
    assert sha256_file(oldroot/'windows.csv')==old['files']['windows.csv']
    paths=[BASE.sweeps_root/d/w/f'{w}_{rr}{suffix}.csv' for rr in TAPES for w in WINDOWS
           for d,suffix in [('RR',''),('RR_stats','_stats')]]
    inputs={p.relative_to(PROJECT_ROOT).as_posix():sha256_file(p) for p in paths}
    assert all(old['inputs'].get(p,old['inputs'].get(str(Path(p))))==h for p,h in inputs.items())
    code=[Path(__file__),PROTOCOL,PROJECT_ROOT/'scripts/mature_book_support.py',PARENT_PATH,
          PROJECT_ROOT/PARENT['scenario'],PROJECT_ROOT/PARENT['evaluation_spec'],PROJECT_ROOT/'config/tape_coverage.json']
    contract=dict(arms=ARMS,headrooms=[6800,1500],config=to_payload(BASE),parent=PARENT,engine=engine_digest(),
                  inputs=inputs,code={p.relative_to(PROJECT_ROOT).as_posix():sha256_file(p) for p in code})
    cp=ROOT/'contract.json'
    if cp.exists(): assert json.loads(cp.read_text())==contract,'Frozen contract changed'
    else: cp.write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    jobs=[(name,h,phase,start,end) for start,end in windows(3) for h in (1500,6800)
          for phase in ('hold','recovery') for name in ARMS]
    selected=jobs[:args.limit] if args.limit else jobs
    results=[]
    with ProcessPoolExecutor(max_workers=4,initializer=boot) as pool:
        for future in as_completed([pool.submit(evaluate,job) for job in selected]):
            r=future.result();results.append(r)
            if len(results)%24==0 or len(results)==len(selected):
                print(f'{len(results)}/{len(selected)} {r["case"]}: original quarter survivors={r["original_survivors_quarter"]}, min live={r["min_live"]}',flush=True)
    if args.limit:
        print('Limited verification complete; no full summary written',flush=True);return
    results.sort(key=lambda r:r['case']);write(ROOT/'comparison.csv',results)
    summary=summaries(results);write(ROOT/'summary.csv',summary)
    complete=[r for r in results if r['phase']=='recovery' and r['complete_12m']]
    write(ROOT/'complete_12m.csv',complete)
    assert len(results)==624 and len(complete)==276
    assert all(sha256_file(PROJECT_ROOT/p)==h for p,h in inputs.items())
    assert all(sha256_file(PROJECT_ROOT/p)==h for p,h in contract['code'].items())
    audit=dict(status='passed',cases=624,prior_account_markers_reproduced=sum(r['prior_marker_checks'] for r in results),
               account_trade_copies_checked=sum(r['copies'] for r in results),contract_sha256=sha256_file(cp),
               files={p.relative_to(ROOT).as_posix():sha256_file(p) for p in [ROOT/'comparison.csv',ROOT/'summary.csv',ROOT/'complete_12m.csv',*sorted((ROOT/'cases').glob('*.json'))]})
    (ROOT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='files'},indent=2))


if __name__=='__main__':main()
