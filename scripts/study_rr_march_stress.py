"""Replay the previously documented March 2026 wipeout with frozen RR mixes.

This is a labeled historical stress case, not a reserve or pipeline search.
"""
from collections import Counter
from dataclasses import replace
from datetime import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import study_rr_diversification as study
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.economics import Economics
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, sha256_file
from pa_milky.rr_diversification import run_rr_book, mortality_metrics


def main():
    study.initialize()
    out=study.OUT/'march_stress'; out.mkdir(exist_ok=True)
    source=study.PROJECT_ROOT/'results/comparisons_blocking/legacy_25k_vs_50k/march_failure_review/baselines.csv'
    import csv
    with source.open() as handle:
        historical=next(r for r in csv.DictReader(handle) if r['label']=='legacy_25k_maximum_5700')
    acq=AcquisitionPolicy('monthly_current_slot_replacements',5000,200,max_live_accounts=20,
        spare_capacity=2,evaluation=study.EVAL,evaluations_at_once=20,persistent_demand=True,
        evaluation_start_interval_days=7,evaluations_reserve_seats=True,activate_on_first_check=True)
    policy=WithdrawalPolicy(name='march_frozen_maximum_daily_h5700',cadence='daily',amount_rule='maximum',
        min_retained_balance_usd=study.BASE.trailing_floor_balance_usd+5700,quantize_to_amount=False,
        terminal_withdrawal='none')
    contract={'source_sha256':sha256_file(source),'source_control':historical,'engine':engine_digest(),
              'primary_contract_sha256':sha256_file(study.OUT/'contract.json'),
              'runner_sha256':sha256_file(Path(__file__)),
              'note':'Exact former 25K 5700 daily-maximum stress policy; evaluation RR1 fixed; no terminal cash. Two extreme-order assumptions, no tuning.'}
    path=out/'contract.json'
    if path.exists():
        assert json.loads(path.read_text())==contract
    else:
        path.write_text(json.dumps(contract,indent=2)+'\n')
    rows=[]
    lookup={t.trade_key:t for tape in study.TAPES.values() for t in tape}
    all_trades=list(lookup.values())
    for order in ('mae_first','mfe_first'):
        for name,weights in study.portfolios().items():
            saved=out/f'{order}__{name}.json'
            if saved.exists():
                rows.append(json.loads(saved.read_text())['row']); continue
            snapshots=[]
            def observe(at,accounts,event,trade):
                if event=='decision' and at.year==2026 and (at.day==1 or at.strftime('%m-%d') in ('03-26','03-27','03-31')):
                    live=[a for a in accounts if a.alive]
                    snapshots.append({'at':at.isoformat(),'alive':len(live),
                        'distinct_balances':len({a.balance_usd for a in live}),
                        'headrooms':[a.headroom_usd for a in live]})
            result=run_rr_book(study.TAPES,replace(study.BASE,policy=policy,path_order=order),weights,
                               acquisition=acq,observer=observe)
            assert Economics.measure(result).residual_usd==0
            assert result.acquisition.summary()['cash_identity_residual_usd']==0
            assigned=result.routing['account_rr']; until={}; count=0
            for fill in result.routing_fills:
                t=lookup[fill['trade_key']]
                for account in fill['accounts']:
                    assert assigned[account]==fill['rr'] and until.get(account,t.entry_at)<=t.entry_at
                    until[account]=t.exit_at; count+=1
            assert count==result.copies_filled
            march1=datetime(2026,3,1); april1=datetime(2026,4,1); event=datetime(2026,3,26)
            cohort=[a for a in result.accounts if a.activated_at<=march1 and (a.alive or a.died_at>=march1)]
            march=[a for a in result.dead if march1<=a.died_at<april1]
            groups=Counter((lookup[a.death_trade_key].window_id,lookup[a.death_trade_key].entry_at.isoformat()) for a in march)
            after_received=round(sum(p.received_usd for p in result.payouts if p.at>=event),2)
            after_cost=round(-sum(e['amount_usd'] for e in result.acquisition.cash_events
                                   if e['at']>=event.isoformat() and e['amount_usd']<0),2)
            row={'portfolio':name,'path_order':order,'march1_alive':len(cohort),
                 'march1_cohort_deaths':sum(not a.alive and a.died_at<april1 for a in cohort),
                 'march_total_deaths':len(march),'march_same_signal_peak':max(groups.values(),default=0),
                 'march31_alive':sum(a.activated_at<april1 and (a.alive or a.died_at>=april1) for a in result.accounts),
                 'net_cash_after_march26':round(after_received-after_cost,2),
                 'net_operating_cash':result.pocket_usd,**mortality_metrics(result,all_trades)}
            if name=='rr_1.00' and order=='mae_first':
                assert result.pocket_usd==float(historical['ongoing'])
                assert len(result.dead)==int(historical['deaths']) and result.alive_at_horizon==int(historical['alive_at_end'])
                assert result.copies_filled==int(historical['copies'])
                assert Counter(str(a.died_at) for a in march)==json.loads(historical['march_death_clusters'])
                row['historical_control_reproduced']=True
            saved.write_text(json.dumps({'row':row,'snapshots':snapshots,
                'march_deaths':[{'id':a.account_id,'rr':assigned[a.account_id],'died_at':a.died_at.isoformat(),
                    'signal_entry':lookup[a.death_trade_key].entry_at.isoformat(),
                    'window':lookup[a.death_trade_key].window_id} for a in march]},indent=2)+'\n')
            rows.append(row)
            print(f'{order} {name}: March cohort {row["march1_cohort_deaths"]}/{row["march1_alive"]}, same-signal {row["march_same_signal_peak"]}, March31 live {row["march31_alive"]}',flush=True)
    study.write_csv(out/'comparison.csv',rows)
    lines=['# RR mixtures on the documented March 2026 wipeout','',
        'The RR1 control reproduces the earlier $5,700 daily-maximum policy: 20 deaths together on March 26. This is a separate historical stress case; the primary $6,800 policy has no March deaths from its 2020 start.','',
        '| Portfolio | Alive March 1 | March cohort deaths | Largest March same-signal loss | Alive March 31 | Net cash after March 26 |',
        '|---|---:|---:|---:|---:|---:|']
    for row in rows:
        if row['path_order']=='mae_first':
            lines.append(f'| {row["portfolio"]} | {row["march1_alive"]} | {row["march1_cohort_deaths"]} | {row["march_same_signal_peak"]} | {row["march31_alive"]} | ${row["net_cash_after_march26"]:,.2f} |')
    lines += ['', 'RR selection and weights match the primary study and were not changed for this stress case. Full-history variant replays generate their own pre-March balances; they do not receive the RR1 book state for free. Exact intratrade death times remain unknown. All figures exclude terminal withdrawals.','']
    (out/'march_stress__REPORT.generated.md').write_text('\n'.join(lines))


if __name__=='__main__':
    main()
