"""Synchronized unrestricted RR paths, normalized mixtures and shadow breaches."""
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta
from itertools import combinations
import json
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT,load_config,to_payload
from pa_milky.loader import load_trades
from pa_milky.provenance import engine_digest,input_digest,sha256_file
from pa_milky.routing import TradeRouter,RoutingPolicy
from study_rr_diversification import write_csv
from rr_curve_support import select_trades,daily_path,net_cents,curve_metrics,first_markers,failure_metrics,pair_metrics,drawdowns

PROFILE=PROJECT_ROOT/'config/studies/legacy_25k_rr_curves.json'


def router_selection(tape,start,end):
    ordered=sorted([t for t in tape if start<=t.entry_at<end],
                   key=lambda t:(t.exit_at,t.entry_at,t.window_order,t.source_row,t.ticket,t.trade_key))
    router=TradeRouter(ordered,RoutingPolicy(mode='blocked'))
    account=SimpleNamespace(account_id=1,alive=True,activated_at=start,headroom_usd=0,
                            apply=lambda *args,**kwargs:True)
    index=0
    while index<len(ordered) or router.next_entry is not None:
        at=ordered[index].exit_at if index<len(ordered) else None
        if at is not None and ordered[index].entry_at==at and index not in router.assignments:
            at=None
        entry=router.next_entry
        if entry is not None and (at is None or entry<at):
            router.enter([account])
        else:
            router.exit(index,ordered[index],commission=0,path_order='mae_first'); index+=1
    return [f['trade_key'] for f in router.fills if f['accounts']]


def cohorts(spec,end):
    result=[]
    for y in range(2020,2026):
        for m in (1,4,7,10):
            start=datetime(y,m,1)
            if start>datetime.fromisoformat(spec['quarterly_last_start']):continue
            stop=datetime(y+1,m,1)
            assert stop<=end
            result.append(('12m',start,stop))
    result += [('full',datetime(y,1,1),end) for y in spec['full_start_years']]
    return result


def portfolios(spec):
    return {**{f'rr_{rr}':[rr] for rr in spec['rr_values']},
        **{f'pair_{a}_{b}':[a,b] for a,b in combinations(spec['rr_values'],2)},
        **spec['mixtures'],'duplicate_rr1':['1.00','1.00']}


def main():
    spec=json.loads(PROFILE.read_text()); cfg=load_config(PROJECT_ROOT/spec['scenario'])
    root=PROJECT_ROOT/spec['output']; root.mkdir(parents=True,exist_ok=True)
    tapes={rr:load_trades(cfg.sweeps_root,risk_reward=rr) for rr in spec['rr_values']}
    end=max(t.exit_at for tape in tapes.values() for t in tape)+timedelta(microseconds=1)
    arms=portfolios(spec)
    contract=dict(spec=spec,base_config=to_payload(cfg),engine=engine_digest(),
        code={p:sha256_file(PROJECT_ROOT/p) for p in ['scripts/study_rr_curves.py','scripts/rr_curve_support.py',
            'scripts/study_rr_diversification.py','research/legacy_25k/RR_CURVES.md']},
        inputs={rr:input_digest(replace(cfg,risk_reward=rr)) for rr in tapes},
        coverage_sha256=sha256_file(PROJECT_ROOT/'config/tape_coverage.json'),
        portfolios=arms,cohorts=[dict(kind=k,start=s.isoformat(),end=e.isoformat()) for k,s,e in cohorts(spec,end)])
    contract_path=root/'contract.json'
    if contract_path.exists(): assert json.loads(contract_path.read_text())==contract,'Frozen contract changed'
    else: contract_path.write_text(json.dumps(contract,indent=2)+'\n')
    reference={(t.window_id,t.entry_at):t for t in tapes['1.00']}
    alignment=[]
    for rr,tape in tapes.items():
        seen={(t.window_id,t.entry_at):t for t in tape}; common=reference.keys()&seen.keys()
        assert len(seen)==len(tape)
        assert all(reference[k].candle_range==seen[k].candle_range for k in common)
        alignment.append(dict(rr=rr,missing=len(reference.keys()-seen.keys()),extra=len(seen.keys()-reference.keys()),
            common_negative_outcome_differences=sum(reference[k].gross_pnl_usd<0 and seen[k].gross_pnl_usd<0
                and reference[k].gross_pnl_usd!=seen[k].gross_pnl_usd for k in common)))
    write_csv(root/'alignment.csv',alignment)
    rows=[]; failures=[]; marker_rows=[]; pairs=[]; hashes={}; selected_count=0
    for kind,start,stop in cohorts(spec,end):
        case=f'{kind}_{start.date().isoformat()}'; dest=root/'cohorts'/case; dest.mkdir(parents=True,exist_ok=True)
        dates=sorted({v.date().isoformat() for tape in tapes.values() for t in tape
                      for v in (t.entry_at,t.exit_at) if start<=v<stop})
        paths={}; selections={}; markers={}; event_changes={}; counts={}
        for rr,tape in tapes.items():
            selected=select_trades(tape,start,stop)
            assert [t.trade_key for t in selected]==router_selection(tape,start,stop)
            selections[rr]=[t.trade_key for t in selected]
            assert all(a.exit_at<=b.entry_at for a,b in zip(selected,selected[1:]))
            paths[rr]=daily_path(selected,dates,stop,cfg.commission_per_copy_usd)
            closed=[t for t in selected if t.exit_at<stop]
            assert round(paths[rr][-1]*100)==sum(net_cents(t,cfg.commission_per_copy_usd) for t in closed)
            counts[rr]=dict(accepted=len(selected),closed=len(closed),open_at_end=len(selected)-len(closed))
            selected_count+=len(selected)
            event_changes[rr]=Counter()
            for t in closed: event_changes[rr][t.exit_at]+=net_cents(t,cfg.commission_per_copy_usd)/100
            markers[rr]={}
            for budget in spec['loss_budgets']:
                markers[rr][str(budget)]=first_markers(selected,budget,stop,cfg.commission_per_copy_usd)
                for method,m in markers[rr][str(budget)].items():
                    marker_rows.append(dict(cohort=case,rr=rr,budget=budget,method=method,
                        breached=m is not None,horizon_open_trade_censored=counts[rr]['open_at_end'],**(m or {})))
        write_csv(dest/'curves.csv',[dict(date=d,**{rr:paths[rr][i] for rr in paths}) for i,d in enumerate(dates)])
        evidence=dict(kind=kind,start=start.isoformat(),end=stop.isoformat(),counts=counts,
                      selected=selections,markers=markers)
        (dest/'paths.json').write_text(json.dumps(evidence,indent=2)+'\n')
        single={rr:curve_metrics(v,dates,start.isoformat())[0] for rr,v in paths.items()}
        for a,b in combinations(paths,2):
            pairs.append(dict(cohort=case,kind=kind,start=start.date().isoformat(),left=a,right=b,
                              **pair_metrics(paths[a],paths[b])))
        for name,components in arms.items():
            curve=[sum(paths[rr][i] for rr in components)/len(components) for i in range(len(dates))]
            metrics,episodes=curve_metrics(curve,dates,start.isoformat())
            events=Counter()
            for rr in components:
                for at,change in event_changes[rr].items():events[at]+=change/len(components)
            event_values=[]; running=0
            for at,change in sorted(events.items()):
                running+=change; event_values.append(running)
            assert abs(running-metrics['net_pnl'])<1e-7
            mdds=[single[rr]['max_drawdown'] for rr in components]
            pnls=[single[rr]['net_pnl'] for rr in components]
            weighted_dd=sum(mdds)/len(mdds)
            assert metrics['max_drawdown']<=weighted_dd+1e-7
            if name=='duplicate_rr1':
                assert curve==paths['1.00'] and metrics==single['1.00']
            rows.append(dict(cohort=case,kind=kind,start=start.date().isoformat(),end=stop.isoformat(),
                portfolio=name,components='/'.join(components),**metrics,
                event_realized_max_drawdown=max(drawdowns(event_values),default=0),
                mean_constituent_max_drawdown=weighted_dd,
                smoothing_vs_mean_constituent_dd=weighted_dd-metrics['max_drawdown'],
                best_constituent_max_drawdown=min(mdds),max_constituent_net_pnl=max(pnls),
                mdd_delta_vs_rr1=metrics['max_drawdown']-single['1.00']['max_drawdown'],
                pnl_delta_vs_rr1=metrics['net_pnl']-single['1.00']['net_pnl']))
            for budget in spec['loss_budgets']:
                for method in ('closed_floor','excursion_floor','closed_peak_dd'):
                    failures.append(dict(cohort=case,kind=kind,start=start.date().isoformat(),portfolio=name,
                        budget=budget,method=method,**failure_metrics(components,
                            {rr:markers[rr][str(budget)][method] for rr in set(components)},dates)))
        for file in dest.iterdir():hashes[str(file.relative_to(root))]=sha256_file(file)
        print(f'{case}: {len(dates)} dates; {len(arms)} portfolios; router and normalization checks passed',flush=True)
    for name,data in [('comparison.csv',rows),('failure_comparison.csv',failures),('markers.csv',marker_rows),('pair_diagnostics.csv',pairs)]:
        write_csv(root/name,data); hashes[name]=sha256_file(root/name)
    audit=dict(cohorts=len(contract['cohorts']),variants=len(tapes),portfolios=len(arms),comparisons=len(rows),
        shadow_comparisons=len(failures),router_replays=len(contract['cohorts'])*len(tapes),
        accepted_trades_checked=selected_count,duplicate_controls_matched=len(contract['cohorts']),
        contract_sha256=sha256_file(contract_path),files=hashes)
    (root/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print({k:v for k,v in audit.items() if k!='files'},flush=True)


if __name__=='__main__':main()
