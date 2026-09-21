"""Independent reconstruction from accepted trades and saved curve observations."""
from bisect import bisect_left
from collections import Counter
from dataclasses import replace
from datetime import datetime
import csv,json,statistics
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT,load_config
from pa_milky.loader import load_trades
from pa_milky.provenance import engine_digest,input_digest,sha256_file
from study_rr_diversification import write_csv

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_curves'


def equal(a,b):
    assert abs(float(a)-float(b))<1e-6,(a,b)


def independent_mdd(values):
    high=0; largest=0
    for v in values:
        if v>high: high=v
        elif high-v>largest: largest=high-v
    return largest


def ranges_peak(length,intervals):
    increments=[0]*(length+1)
    for first,last in intervals:
        increments[max(0,first)]+=1
        increments[min(length,last+1)]-=1
    running=peak=0
    for n in increments[:-1]:running+=n;peak=max(peak,running)
    return peak


def main():
    c=json.loads((ROOT/'contract.json').read_text()); manifest=json.loads((ROOT/'audit.json').read_text())
    assert sha256_file(ROOT/'contract.json')==manifest['contract_sha256']
    assert engine_digest()==c['engine']
    for f,h in c['code'].items():assert sha256_file(PROJECT_ROOT/f)==h
    for f,h in manifest['files'].items():assert sha256_file(ROOT/f)==h
    assert sha256_file(PROJECT_ROOT/'config/tape_coverage.json')==c['coverage_sha256']
    config=load_config(PROJECT_ROOT/c['spec']['scenario'])
    tapes={rr:load_trades(config.sweeps_root,risk_reward=rr) for rr in c['spec']['rr_values']}
    for rr in tapes:assert input_digest(replace(config,risk_reward=rr))==c['inputs'][rr]
    lookup={t.trade_key:t for tape in tapes.values() for t in tape}
    comparisons=list(csv.DictReader((ROOT/'comparison.csv').open()))
    failures=list(csv.DictReader((ROOT/'failure_comparison.csv').open()))
    pair_rows=list(csv.DictReader((ROOT/'pair_diagnostics.csv').open()))
    audited=markers_count=0; exposure=[]
    for cohort in c['cohorts']:
        name=f'{cohort["kind"]}_{cohort["start"][:10]}'
        start=datetime.fromisoformat(cohort['start']); end=datetime.fromisoformat(cohort['end'])
        evidence=json.loads((ROOT/'cohorts'/name/'paths.json').read_text())
        observations=list(csv.DictReader((ROOT/'cohorts'/name/'curves.csv').open()))
        dates=[r['date'] for r in observations]
        paths={rr:[float(r[rr]) for r in observations] for rr in tapes}
        event_deltas={}
        for rr,ids in evidence['selected'].items():
            chosen=[lookup[k] for k in ids]
            assert len(ids)==len(set(ids))
            assert all(start<=t.entry_at<end for t in chosen)
            assert all(a.exit_at<=b.entry_at for a,b in zip(chosen,chosen[1:]))
            daily=Counter(); event_deltas[rr]=Counter(); settled=0; high=0; intervals=[]
            markers={str(b):{'closed_floor':None,'excursion_floor':None,'closed_peak_dd':None} for b in c['spec']['loss_budgets']}
            for t in chosen:
                if t.exit_at>=end:continue
                before=settled/100
                change=round(round(t.gross_pnl_usd-config.commission_per_copy_usd,2)*100)
                settled+=change; close=settled/100
                daily[t.exit_at.date().isoformat()]+=change
                event_deltas[rr][t.exit_at]+=change/100
                high=max(high,close)
                for b in c['spec']['loss_budgets']:
                    conditions={'closed_floor':close<=-b,
                        'excursion_floor':min(before+min(0,t.mae_usd),close)<=-b,
                        'closed_peak_dd':high-close>=b}
                    for method,hit in conditions.items():
                        if hit and markers[str(b)][method] is None:
                            markers[str(b)][method]=t.trade_key
            acc=0
            for i,day in enumerate(dates):acc+=daily[day];equal(paths[rr][i],acc/100)
            for b in c['spec']['loss_budgets']:
                for method,key in markers[str(b)].items():
                    saved=evidence['markers'][rr][str(b)][method]
                    assert (saved['trade_key'] if saved else None)==key
                    if saved:
                        t=lookup[key]
                        assert saved['entry']==t.entry_at.isoformat() and saved['exit']==t.exit_at.isoformat()
                        if saved['kind']!='mae':assert saved['interval_start']==saved['exit']
                        else:assert saved['interval_start']==saved['entry']
                    markers_count+=1
            hours=sum((min(t.exit_at,end)-t.entry_at).total_seconds()/3600 for t in chosen)
            exposure.append(dict(cohort=name,rr=rr,accepted=len(chosen),closed=sum(t.exit_at<end for t in chosen),
                open_at_end=sum(t.exit_at>=end for t in chosen),position_hours=hours,
                calendar_time_occupied_fraction=hours/((end-start).total_seconds()/3600)))
        for r in (x for x in comparisons if x['cohort']==name):
            components=c['portfolios'][r['portfolio']]
            values=[statistics.mean(paths[rr][i] for rr in components) for i in range(len(dates))]
            equal(r['net_pnl'],values[-1]);equal(r['max_drawdown'],independent_mdd(values))
            changes=[values[0],*[b-a for a,b in zip(values,values[1:])]]
            for width in (1,5,20):equal(r[f'worst_{width}d_change'],min(sum(changes[i:i+width]) for i in range(len(changes)-width+1)))
            events=Counter()
            for rr in components:
                for at,change in event_deltas[rr].items():events[at]+=change/len(components)
            acc=0; event_values=[]
            for _,change in sorted(events.items()):acc+=change;event_values.append(acc)
            equal(r['event_realized_max_drawdown'],independent_mdd(event_values))
            if r['portfolio']=='duplicate_rr1':assert values==paths['1.00']
            audited+=1
        for r in (x for x in failures if x['cohort']==name):
            components=c['portfolios'][r['portfolio']]
            points=[evidence['markers'][rr][r['budget']][r['method']] for rr in components]
            points=[m for m in points if m]
            equal(r['fraction_breached'],len(points)/len(components))
            same=Counter((m['window'],m['entry']) for m in points)
            equal(r['max_same_signal_fraction'],max(same.values(),default=0)/len(components))
            assert int(r['recorded_death_dates'])==len({m['exit'][:10] for m in points})
            for width in (1,5,20):
                recorded=[]; possible=[]
                for m in points:
                    exit_i=bisect_left(dates,m['exit'][:10]);entry_i=bisect_left(dates,m['interval_start'][:10])
                    recorded.append((exit_i-width+1,exit_i));possible.append((entry_i-width+1,exit_i))
                equal(r[f'max_recorded_{width}d_fraction'],ranges_peak(len(dates),recorded)/len(components))
                equal(r[f'possible_{width}d_fraction'],ranges_peak(len(dates),possible)/len(components))
        for r in (x for x in pair_rows if x['cohort']==name):
            series=[]
            for rr in (r['left'],r['right']):
                v=paths[rr];series.append([v[0],*[b-a for a,b in zip(v,v[1:])]])
            if r['daily_pnl_correlation']:equal(r['daily_pnl_correlation'],statistics.correlation(*series))
    assert audited==manifest['comparisons']
    write_csv(ROOT/'exposure.csv',exposure)
    result=dict(comparisons_reconstructed=audited,individual_marker_checks=markers_count,
        failure_comparisons_reconstructed=len(failures),pair_correlations_checked=len(pair_rows),
        source_and_artifact_hashes_match=True,duplicate_normalization_checks=manifest['cohorts'],
        exposure_diagnostics_saved=True,auditor_sha256=sha256_file(Path(__file__)))
    (ROOT/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
