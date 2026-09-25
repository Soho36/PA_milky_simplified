"""72 monthly starts, alternating direct PA purchases, 20 live seats, daily payouts."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from functools import partial
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.account import money
from pa_milky.config import load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.loader import load_trades
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file, tape_coverage
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book, months_in_span
from study_rr_pair_withdrawal_amount import AlternatingRouter
from monthly_pair_support import add_months, book_metrics
from report_names import write_study_report

OUT = ROOT/'results/legacy_25k/monthly_rr_pair_build'
RR = ('0.50','2.50')
BASE = TAPES = END = None
RESERVE = 6800


def boot():
    global BASE, TAPES, END
    BASE = load_config(ROOT/'config/scenarios/full_rulebook_monthly_500.json')
    assert not BASE.rulebook.processing_delay_days
    TAPES = {rr:load_trades(BASE.sweeps_root,strategy='RR',risk_reward=rr) for rr in RR}
    ends = {max(t.exit_at for t in tape) for tape in TAPES.values()}
    assert len(ends)==1
    END = ends.pop()+timedelta(microseconds=1)


def write_csv(path, rows):
    if not rows:
        path.write_text('',encoding='utf-8')
        return
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def evaluate(job):
    start, rule = job
    case = f'{start:%Y-%m}__daily_{rule}'
    tapes = {rr:[t for t in tape if t.entry_at>=start] for rr,tape in TAPES.items()}
    trades = sorted([t for tape in tapes.values() for t in tape],
                    key=lambda t:(t.exit_at,t.entry_at,t.window_order,t.source_row,t.ticket,t.trade_key))
    variants = {t.trade_key:rr for rr,tape in tapes.items() for t in tape}
    assert len(variants)==len(trades)
    assert min(t.entry_at for t in trades).replace(day=1,hour=0,minute=0,second=0,microsecond=0)==start
    policy = WithdrawalPolicy(name=f'daily_{rule}',cadence='daily',amount_rule=rule,
                              shortfall='skip',quantize_to_amount=False,
                              min_retained_balance_usd=BASE.trailing_floor_balance_usd+RESERVE,
                              terminal_withdrawal='none')
    config = replace(BASE,policy=policy,expected_trades=None,risk_reward='0.50/2.50',
                     scenario='monthly_rr_pair_build',brick_name='monthly_rr_pair_build')
    # This allowance guarantees each scheduled direct purchase is affordable.
    # Contributions are not earnings; cash results subtract actual purchase fees.
    acquisition = AcquisitionPolicy('monthly_one',initial_cash_usd=BASE.purchase_fee_usd,
                                     monthly_contribution_usd=BASE.purchase_fee_usd,
                                     max_live_accounts=20,restart_when_empty=False)
    snapshots = []
    def observe(at,accounts,event,trade):
        if event=='horizon' or (event=='decision' and at.day==1):
            live=[a for a in accounts if a.alive]
            snapshots.append(dict(case=case,at=at.isoformat(),alive=len(live),
                                  alive_rr050=sum(a.account_id%2==1 for a in live),
                                  alive_rr250=sum(a.account_id%2==0 for a in live),
                                  purchased=len(accounts),deaths=len(accounts)-len(live),
                                  retained_profit=money(sum(a.equity_profit_usd for a in live))))
    result = run_book(trades,config,acquisition=acquisition,observer=observe,
                       routing=RoutingPolicy(mode='blocked'),
                       router_factory=partial(AlternatingRouter,weights=dict.fromkeys(RR,1),trade_rr=variants))
    assert result.accounts[0].activated_at==start
    assert result.tape_last_exit+timedelta(microseconds=1)==END
    assert not result.terminal_payouts
    economics=Economics.measure(result)
    assert economics.residual_usd==0
    ledger=result.acquisition.summary()
    assert ledger['cash_identity_residual_usd']==0 and ledger['cash_limited_decisions']==0
    assert len(result.accounts)*BASE.purchase_fee_usd==result.total_purchase_cost_usd
    lookup={a.account_id:a for a in result.accounts}
    keys={i:[] for i in lookup};until={}
    for fill in result.routing_fills:
        entry=datetime.fromisoformat(fill['entry_at']);exit_at=datetime.fromisoformat(fill['exit_at'])
        for i in fill['accounts']:
            assert variants[fill['trade_key']]==RR[(i-1)%2]
            assert lookup[i].activated_at<=entry
            assert i not in until or until[i]<=entry
            until[i]=exit_at;keys[i].append(fill['trade_key'])
    assert sum(map(len,keys.values()))==result.copies_filled
    accounts=[]
    for a in result.accounts:
        assert a.trades_taken==len(keys[a.account_id])
        assert a.alive or keys[a.account_id][-1]==a.death_trade_key
        assert a.activated_at.day==1
        accounts.append(dict(case=case,account_id=a.account_id,rr=RR[(a.account_id-1)%2],
                             activated_at=a.activated_at.isoformat(),alive=a.alive,
                             died_at=a.died_at.isoformat() if a.died_at else '',
                             death_trade_key=a.death_trade_key or '',trades=a.trades_taken,
                             balance=a.balance_usd,headroom=a.headroom_usd,received=a.received_usd,
                             trade_keys_sha256=hashlib.sha256(json.dumps(keys[a.account_id]).encode()).hexdigest()))
    for p in result.payouts:
        assert p.balance_after_usd+.001>=policy.min_retained_balance_usd
        if rule=='minimum': assert p.gross_usd==500
    payouts=[dict(case=case,account_id=p.account_id,at=p.at.isoformat(),gross=p.gross_usd,
                  received=p.received_usd,balance_after=p.balance_after_usd) for p in result.payouts]
    purchases=[dict(case=case,**d) for d in result.acquisition.decisions]
    assert len({a['activated_at'] for a in accounts})==len(accounts)
    assert len(purchases)==len(months_in_span(start,END-timedelta(microseconds=1)))
    for d in purchases:
        assert d['bought']==int(d['alive_before']<20)
        assert datetime.fromisoformat(d['at']).day==1
    metrics,episodes=book_metrics(accounts,start,END)
    assert metrics['end_alive']==result.alive_at_horizon
    summary=dict(case=case,start=start.date().isoformat(),policy=rule,**metrics,
                 gross_withdrawn=result.total_withdrawn_usd,received=result.total_received_usd,
                 purchase_cost=result.total_purchase_cost_usd,net_cash=result.pocket_usd,
                 retained_profit=economics.retained_profit_usd,firm_split=economics.firm_split_usd,
                 alive_rr050=sum(a['alive'] and a['rr']=='0.50' for a in accounts),
                 alive_rr250=sum(a['alive'] and a['rr']=='2.50' for a in accounts),
                 copies_checked=result.copies_filled,economic_residual=economics.residual_usd,
                 funding_residual=ledger['cash_identity_residual_usd'])
    checkpoints=[]
    for months in (6,12,24,36):
        end=add_months(start,months)
        if end>END:continue
        m,_=book_metrics(accounts,start,end)
        received=money(sum(p['received'] for p in payouts if datetime.fromisoformat(p['at'])<end))
        checkpoints.append(dict(case=case,start=start.date().isoformat(),policy=rule,months=months,
                                **m,received=received,purchase_cost=m['purchased']*BASE.purchase_fee_usd,
                                net_cash=money(received-m['purchased']*BASE.purchase_fee_usd)))
    return dict(summary=summary,accounts=accounts,payouts=payouts,purchases=purchases,
                snapshots=snapshots,episodes=[dict(case=case,**e) for e in episodes],checkpoints=checkpoints)


def aggregate(rows):
    return dict(cases=len(rows),deaths=sum(r['deaths'] for r in rows),
                mean_deaths=statistics.mean(r['deaths'] for r in rows),
                cases_with_empty=sum(r['empty_episodes']>0 for r in rows),
                empty_episodes=sum(r['empty_episodes'] for r in rows),
                mean_empty_days=statistics.mean(r['empty_days'] for r in rows),
                mean_end_alive=statistics.mean(r['end_alive'] for r in rows),
                reached20=sum(r['reached20'] for r in rows),
                mean_net_cash=statistics.mean(r['net_cash'] for r in rows))


def report(rows,checkpoints,episodes):
    lines=['# Build an alternating RR 0.50 / 2.50 book from zero','',
           '72 starts, one on each month boundary from January 2020 through December 2025. '
           'Two daily payout policies; 144 runs. All run through '+(END-timedelta(microseconds=1)).isoformat(sep=' ')+'.','',
           'Buy one PA immediately and then on each month boundary if fewer than 20 are alive. '
           'Continue monthly purchases after deaths; no intra-month replacement or catch-up batch. '
           'Each actual purchase advances 0.50, 2.50, 0.50, 2.50; a skipped month at capacity does not advance the sequence. '
           'Equal purchases do not maintain an equal live allocation.','',
           'One position at a time per account, one MNQ per trade, $1.05 round-trip commission. '
           'Fresh $25,000 PAs with $1,500 trailing drawdown; retain $31,900 before withdrawing '
           '($6,800 above the frozen $25,100 floor). This reserve is earned, not supplied initially. '
           'Daily minimum asks for $500 without backlog; daily maximum asks for all permitted excess. '
           'Daily checks remain subject to the full historical payout rulebook, with processing delay off. '
           'Direct PA purchases cost $200 and are externally funded. No evaluations or funding restriction. '
           'Net cash is received payouts minus actual purchase fees, excluding unused owner contributions and retained profit. '
           '**No terminal payout or liquidation is counted.**','',
           '## Full available history by start','',
           'Starts have unequal follow-up. These totals describe overlapping historical replays, not independent observations or estimated probabilities.','',
           '| Daily policy | Starts | Mean deaths | Starts with empty book | Empty episodes | Mean empty days | Mean end alive | Reached 20 | Mean net cash |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for rule in ('minimum','maximum'):
        a=aggregate([r for r in rows if r['policy']==rule])
        lines.append(f"| {rule} | {a['cases']} | {a['mean_deaths']:.2f} | {a['cases_with_empty']} | {a['empty_episodes']} | {a['mean_empty_days']:.2f} | {a['mean_end_alive']:.2f} | {a['reached20']} | ${a['mean_net_cash']:,.2f} |")
    lines+=['','## First twelve months: matched follow-up','',
            'Only starts with twelve complete months are included. Later starts are excluded, not counted as surviving a full year.','',
            '| Daily policy | Starts | Mean deaths | Starts with empty book | Empty episodes | Mean empty days | Mean end alive | Mean net cash |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for rule in ('minimum','maximum'):
        a=aggregate([r for r in checkpoints if r['policy']==rule and r['months']==12])
        lines.append(f"| {rule} | {a['cases']} | {a['mean_deaths']:.2f} | {a['cases_with_empty']} | {a['empty_episodes']} | {a['mean_empty_days']:.2f} | {a['mean_end_alive']:.2f} | ${a['mean_net_cash']:,.2f} |")
    lines+=['','## Full-history outcomes by start year','',
            '| Start year | Policy | Mean deaths | Starts with empty book / 12 | Empty episodes | Mean empty days | Mean end alive | Reached 20 / 12 |',
            '|---|---|---:|---:|---:|---:|---:|---:|']
    for year in range(2020,2026):
        for rule in ('minimum','maximum'):
            a=aggregate([r for r in rows if r['policy']==rule and r['start'].startswith(str(year))])
            lines.append(f"| {year} | {rule} | {a['mean_deaths']:.2f} | {a['cases_with_empty']} | {a['empty_episodes']} | {a['mean_empty_days']:.2f} | {a['mean_end_alive']:.2f} | {a['reached20']} |")
    pairs={r['case']:r for r in rows}
    delta=[pairs[f'{y}-{m:02d}__daily_maximum']['deaths']-pairs[f'{y}-{m:02d}__daily_minimum']['deaths'] for y in range(2020,2026) for m in range(1,13)]
    lines+=['','## Paired comparison and episode definition','',
            f"Maximum daily produces fewer deaths in {sum(d<0 for d in delta)} starts, the same in {sum(d==0 for d in delta)}, and more in {sum(d>0 for d in delta)}. Compare policies within the same start date before pooling starts.",'',
            'An empty-book episode is a positive-duration interval with zero live accounts after the first activation. '
            'Startup zero is excluded. A same-timestamp death and purchase are netted; instantaneous zero is not an episode. '
            'An episode still open at the data endpoint is marked censored. Death timestamps are trade-exit proxies; intratrade breach times are not available.','',
            f"Across the replays, {sum(e['historical_peak']<5 for e in episodes)} of {len(episodes)} empty episodes occur before the book has ever reached five live accounts; "
            f"{sum(e['historical_peak']>=10 for e in episodes)} occur after reaching at least ten. These are counts across overlapping runs.",'',
            '## Evidence and reproduction','',
            'See [cases.csv](cases.csv) for every start/policy, [checkpoints.csv](checkpoints.csv) for complete 6/12/24/36-month windows, '
            '[empty_episodes.csv](empty_episodes.csv) for exact gaps and historical peak sizes, '
            '[accounts.csv](accounts.csv) for deaths and r/r assignments, [purchases.csv](purchases.csv), '
            '[payouts.csv](payouts.csv), and [snapshots.csv](snapshots.csv) for monthly capacity. '
            'Input coverage, hashes, policies and checks are in [study.json](study.json).','',
            'Reproduce: `venv/Scripts/python.exe scripts/study_monthly_rr_pair_build.py --workers 4`. '
            'Audit: `venv/Scripts/python.exe scripts/audit_monthly_rr_pair_build.py`. '
            'This two-policy experiment evaluates the requested plan; it does not measure diversification relative to homogeneous controls.']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.workers<1:parser.error('workers must be positive')
    boot();OUT.mkdir(parents=True,exist_ok=True)
    jobs=[(datetime(y,m,1),rule) for y in range(2020,2026) for m in range(1,13) for rule in ('minimum','maximum')]
    combined={k:[] for k in ('summary','accounts','payouts','purchases','snapshots','episodes','checkpoints')}
    with ProcessPoolExecutor(max_workers=args.workers,initializer=boot) as pool:
        for i,data in enumerate(pool.map(evaluate,jobs),1):
            for k in combined:combined[k].extend([data[k]] if k=='summary' else data[k])
            if i%12==0:print(f'Completed {i}/{len(jobs)}',flush=True)
    for key,rows in combined.items():
        name={'summary':'cases','episodes':'empty_episodes'}.get(key,key)
        write_csv(OUT/f'{name}.csv',rows)
    payload=dict(schema='pa_milky.monthly_rr_pair_build.v1',generated_utc=datetime.now(timezone.utc).isoformat(),
                 config=to_payload(BASE),engine=engine_digest(),reserve_headroom=RESERVE,
                 start_months=72,policies=['daily_minimum','daily_maximum'],
                 end_exclusive=END.isoformat(),terminal='none',
                 purchase_rule='one direct PA per month boundary while alive<20; continue after deaths',
                 funding='externally guaranteed $200 per month; no evaluations',
                 assignment='alternate by actual purchase index: 0.50 first, 2.50 second',
                 inputs={rr:dict(digest=input_digest(replace(BASE,risk_reward=rr)),coverage=tape_coverage(t)) for rr,t in TAPES.items()},
                 scripts={n:sha256_file(ROOT/'scripts'/n) for n in ('study_monthly_rr_pair_build.py','monthly_pair_support.py','study_rr_pair_withdrawal_amount.py','report_names.py')},
                 checks=dict(cases=len(jobs),copies=sum(r['copies_checked'] for r in combined['summary']),
                             all_economic_and_funding_residuals_zero=True,all_purchase_and_payout_rules_checked=True),
                 cases=combined['summary'])
    (OUT/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    text=report(combined['summary'],combined['checkpoints'],combined['episodes'])
    write_study_report(OUT,text);print(text,flush=True)


if __name__=='__main__':main()
