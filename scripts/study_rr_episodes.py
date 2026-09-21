"""Non-overlapping failure opportunities and common dated episode groups."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
import csv
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from itertools import combinations
import json
import math
import os
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import Trade, load_trades, STATS_COLUMNS, SOURCE_TIME_FORMAT
from pa_milky.provenance import sha256_file, engine_digest
from rr_curve_support import select_trades, daily_path, first_markers, drawdowns, curve_metrics
from study_rr_curves import router_selection

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_episodes'
SOURCE=PROJECT_ROOT/'results/legacy_25k/rr_curves'
FINITE=[f'{n/4:.2f}' for n in range(2,15)]
START=datetime(2020,1,1)
END=datetime(2026,7,1)
BUDGETS=(1500,6800)


def read_csv(path, encoding='utf-8', delimiter=','):
    with path.open(encoding=encoding,newline='') as f:
        return list(csv.DictReader(f,delimiter=delimiter))


def write_csv(path, rows, fields=None):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]))
        w.writeheader();w.writerows(rows)


def load_session(reference):
    path=PROJECT_ROOT/'1_sweeps/RR/1000_1000.00.csv'
    stats_path=PROJECT_ROOT/'1_sweeps/RR_stats/1000_1000.00_stats.csv'
    stats=read_csv(stats_path,encoding='utf-16',delimiter='\t')
    assert len(stats)==1 and tuple(stats[0])==STATS_COLUMNS
    stats=stats[0]
    assert stats['run_tag']=='1000' and Decimal(stats['risk_reward'])==1000
    with path.open(encoding='utf-16',newline='') as f:
        raw=[r for r in csv.reader(f,delimiter='\t') if any(x.strip() for x in r)]
    trades=[];over=[];unmatched=[];ratios=[]
    byentry={t.entry_at:t for t in reference}
    assert len(byentry)==len(reference)
    for i,r in enumerate(raw,1):
        assert len(r)==7
        ticket=int(r[0]);entry=datetime.strptime(r[1],SOURCE_TIME_FORMAT);exit=datetime.strptime(r[2],SOURCE_TIME_FORMAT)
        mae,mfe,pnl,candle=map(float,r[3:])
        assert all(math.isfinite(v) for v in (mae,mfe,pnl,candle))
        assert exit>=entry and candle>0 and mae<=pnl<=mfe and mfe>=0
        assert exit.strftime('%H:%M:%S')=='23:30:00' or abs(pnl+2*candle)<1e-8
        ratios.append(mfe/(2*candle))
        t=Trade(f'RR1000:all:{i}:{ticket}','all_hours',0,i,ticket,entry,exit,mae,mfe,pnl,candle)
        trades.append(t)
        record=dict(ticket=ticket,entry=entry.isoformat(),exit=exit.isoformat(),pnl=pnl,candle_range=candle)
        if entry.date()!=exit.date():over.append(record)
        if entry not in byentry:unmatched.append(record)
        else:assert byentry[entry].candle_range==candle
    trades.sort(key=lambda t:t.entry_at)
    assert len({t.ticket for t in trades})==len(trades)==len({t.entry_at for t in trades})
    assert all(a.exit_at<=b.entry_at for a,b in zip(trades,trades[1:]))
    pnls=[Decimal(r[5]) for r in raw]
    assert len(raw)==int(stats['trades'])
    assert sum(pnls)==Decimal(stats['net_profit'])
    assert sum(p for p in pnls if p>0)==Decimal(stats['gross_profit'])
    assert sum(p for p in pnls if p<0)==Decimal(stats['gross_loss'])
    assert max(ratios)<1000
    assert max(t.exit_at for t in trades)>=max(t.exit_at for t in reference)
    # Check the tester's gross realized drawdown independently of net commissions.
    cumulative=Decimal(0);peak=Decimal(0);maxdd=Decimal(0)
    for t in trades:
        cumulative+=Decimal(str(t.gross_pnl_usd));peak=max(peak,cumulative);maxdd=max(maxdd,peak-cumulative)
    assert maxdd==Decimal(stats['balance_dd'])
    expected_months={f'{y}-{m:02d}' for y in range(2020,2027) for m in range(1,13) if (y,m)<=(2026,7)}
    assert {t.entry_at.strftime('%Y-%m') for t in trades}==expected_months
    report=dict(status='internally reconciled; exploratory all-hours arm',trades=len(trades),
        gross_pnl=str(sum(pnls)),gross_realized_max_drawdown=str(maxdd),
        first_entry=trades[0].entry_at.isoformat(),last_exit=max(t.exit_at for t in trades).isoformat(),
        exits_at_2330=sum(t.exit_at.strftime('%H:%M:%S')=='23:30:00' for t in trades),
        other_exits_at_original_stop=sum(t.exit_at.strftime('%H:%M:%S')!='23:30:00' for t in trades),
        maximum_recorded_mfe_R=max(ratios),observed_target_hits=0,cross_date_positions=len(over),
        longest_hold_calendar_days=max((t.exit_at-t.entry_at).total_seconds()/86400 for t in trades),
        entries_matched_to_rr1=len(trades)-len(unmatched),entries_absent_from_rr1=len(unmatched),
        matched_stop_ranges_equal=True,months_present=len(expected_months),
        user_confirmed='All hours together; other entry/stop settings unchanged.',
        limitations=['No EA or tester log supplied; exit reasons inferred from exact price/clock equality.',
                     '73 cross-date positions contradict an unconditional same-day flat interpretation.',
                     'Already non-overlapping all-hours tape; entry opportunity set differs from window exports.'],
        files={str(p.relative_to(PROJECT_ROOT)):sha256_file(p) for p in (path,stats_path)})
    write_csv(ROOT/'session_cross_date_positions.csv',over)
    write_csv(ROOT/'session_unmatched_entries.csv',unmatched)
    (ROOT/'session_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return trades,report


def windows(months):
    date=START
    while date<END:
        ordinal=date.year*12+date.month-1+months
        stop=datetime(ordinal//12,ordinal%12+1,1)
        if stop<=END:yield date,stop
        date=stop


def independent_marker(selected,budget,end,commission):
    settled=Decimal(0)
    for t in selected:
        if t.exit_at>=end:continue
        before=settled
        settled+=(Decimal(str(t.gross_pnl_usd))-Decimal(str(commission))).quantize(Decimal('.01'))
        adverse=before+min(Decimal(str(t.mae_usd)),Decimal(0))
        if min(adverse,settled)<=-budget:
            return t.trade_key, (t.entry_at if adverse<=-budget else t.exit_at).isoformat(),t.exit_at.isoformat()
    return None


def episode_groups(events,dates,gap):
    groups=[]
    for event in sorted(events,key=lambda r:(r['interval_start'],r['exit'],r['rr'])):
        if not groups or max(0,bisect_left(dates,event['interval_start'][:10])-bisect_right(dates,groups[-1]['end'][:10]))>gap:
            groups.append(dict(start=event['interval_start'],end=event['exit'],events=[]))
        group=groups[-1];group['end']=max(group['end'],event['exit']);group['events'].append(event)
    return groups


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    old_contract=json.loads((SOURCE/'contract.json').read_text())
    old_audit=json.loads((SOURCE/'audit.json').read_text())
    assert engine_digest()==old_contract['engine']
    assert sha256_file(SOURCE/'contract.json')==old_audit['contract_sha256']
    for f,h in old_contract['code'].items():assert sha256_file(PROJECT_ROOT/f)==h
    for f,h in old_audit['files'].items():assert sha256_file(SOURCE/f)==h
    cfg=load_config(PROJECT_ROOT/'config/scenarios/full_rulebook_monthly_500.json')
    tapes={rr:load_trades(cfg.sweeps_root,risk_reward=rr) for rr in FINITE}
    tapes['1000'],validation=load_session(tapes['1.00'])
    input_files=dict(validation['files'])
    for rr in FINITE:
        for window in range(1,24):
            for directory,suffix in [('RR',''),('RR_stats','_stats')]:
                p=cfg.sweeps_root/directory/f'{window}-{window+1}'/f'{window}-{window+1}_{rr}{suffix}.csv'
                input_files[str(p.relative_to(PROJECT_ROOT))]=sha256_file(p)
    dates=sorted({at.date().isoformat() for tape in tapes.values() for t in tape
                  for at in (t.entry_at,t.exit_at) if START<=at<END})
    episode_dates=sorted({at.date().isoformat() for rr in FINITE for t in tapes[rr]
                          for at in (t.entry_at,t.exit_at) if START<=at<END})
    write_csv(ROOT/'episode_calendar.csv',[dict(date=d) for d in episode_dates])
    oldpaths=json.loads((SOURCE/'cohorts/full_2020-01-01/paths.json').read_text())
    oldcurves=read_csv(SOURCE/'cohorts/full_2020-01-01/curves.csv')
    oldend=datetime.fromisoformat(oldpaths['end']);olddates=[r['date'] for r in oldcurves]
    continuous=[]; continuous_metrics=[]; checks=Counter();selected_evidence={}
    dd_by_rr={}
    for rr,tape in tapes.items():
        selected=select_trades(tape,START,oldend)
        assert [t.trade_key for t in selected]==router_selection(tape,START,oldend)
        checks['full_router_matches']+=1
        if rr in FINITE:
            assert [t.trade_key for t in selected]==oldpaths['selected'][rr]
            oldvalues=daily_path(selected,olddates,oldend,cfg.commission_per_copy_usd)
            assert all(abs(v-float(r[rr]))<1e-7 for v,r in zip(oldvalues,oldcurves))
            checks['source_full_curve_and_selection_matches']+=1
        path=daily_path(selected,dates,END,cfg.commission_per_copy_usd)
        dd=drawdowns(path);dd_by_rr[rr]=dd
        for date,value,drawdown in zip(dates,path,dd):
            continuous.append(dict(date=date,rr=rr,pnl=value,drawdown=drawdown,deep=drawdown>=1500))
        metrics,_=curve_metrics(path,dates,START.isoformat())
        continuous_metrics.append(dict(rr=rr,**metrics))
    write_csv(ROOT/'continuous_curves.csv',continuous)
    write_csv(ROOT/'continuous_summary.csv',continuous_metrics)
    rows=[];events=[]
    for months in (1,3,6):
        for start,end in windows(months):
            case=f'{months}m_{start.date()}'
            selected_evidence[case]={}
            for rr,tape in tapes.items():
                incoming=[t for t in tape if t.entry_at<start<t.exit_at] if rr=='1000' else []
                selected=select_trades(tape,start,end)
                if months==3:
                    assert [t.trade_key for t in selected]==router_selection(tape,start,end)
                    checks['quarter_router_matches']+=1
                selected_evidence[case][rr]=[t.trade_key for t in selected]
                for budget in BUDGETS:
                    marker=first_markers(selected,budget,end,cfg.commission_per_copy_usd)['excursion_floor']
                    reference=independent_marker(selected,budget,end,cfg.commission_per_copy_usd)
                    actual=(marker['trade_key'],marker['interval_start'],marker['exit']) if marker else None
                    assert actual==reference
                    checks['decimal_first_marker_matches']+=1
                    row=dict(case=case,months=months,start=start.isoformat(),end=end.isoformat(),rr=rr,
                        budget=budget,eligible=not incoming,incoming_trade=incoming[0].trade_key if incoming else '',
                        accepted=len(selected),closed=sum(t.exit_at<end for t in selected),
                        breached=bool(marker) if not incoming else '',
                        trade_key=marker['trade_key'] if marker and not incoming else '',
                        interval_start=marker['interval_start'] if marker and not incoming else '',
                        exit=marker['exit'] if marker and not incoming else '')
                    rows.append(row)
                    if row['breached']:events.append(row)
            print(case,'checked',flush=True)
    write_csv(ROOT/'windows.csv',rows)
    write_csv(ROOT/'breach_events.csv',events)
    (ROOT/'selected_trades.json').write_text(json.dumps(selected_evidence,separators=(',',':'))+'\n')
    # The exact accepted source records make the first-marker evidence independently reproducible.
    records=[]
    for rr,tape in tapes.items():
        for t in tape:
            r=asdict(t);r['entry_at']=t.entry_at.isoformat();r['exit_at']=t.exit_at.isoformat()
            records.append(dict(rr=rr,**r))
    write_csv(ROOT/'native_trades.csv',records)
    pair_rows=[];episode_rows=[];membership=[];episode_pairs=[];summary=[]
    for months in (1,3,6):
        for budget in BUDGETS:
            subset=[r for r in rows if r['months']==months and r['budget']==budget]
            per_rr={rr:{r['case']:r for r in subset if r['rr']==rr} for rr in tapes}
            for rr,bycase in per_rr.items():
                valid=[r for r in bycase.values() if r['eligible']]
                summary.append(dict(months=months,budget=budget,rr=rr,eligible=len(valid),
                    excluded=len(bycase)-len(valid),failed=sum(bool(r['breached']) for r in valid)))
            for left,right in combinations(tapes,2):
                valid=[case for case in per_rr[left] if per_rr[left][case]['eligible'] and per_rr[right][case]['eligible']]
                l={case for case in valid if per_rr[left][case]['breached']};r={case for case in valid if per_rr[right][case]['breached']}
                counts=dict(both=len(l&r),left_only=len(l-r),right_only=len(r-l),neither=len(valid)-len(l|r))
                assert sum(counts.values())==len(valid)
                checks['pair_partition_checks']+=1
                deep_l=[x>=1500 for x in dd_by_rr[left]];deep_r=[x>=1500 for x in dd_by_rr[right]]
                deep_both=sum(a and b for a,b in zip(deep_l,deep_r));deep_union=sum(a or b for a,b in zip(deep_l,deep_r))
                pair_rows.append(dict(months=months,budget=budget,left=left,right=right,eligible=len(valid),
                    left_failed=len(l),right_failed=len(r),**counts,
                    failed_window_jaccard=len(l&r)/len(l|r) if l|r else '',
                    right_given_left=len(l&r)/len(l) if l else '',left_given_right=len(l&r)/len(r) if r else '',
                    continuous_deep_dd_jaccard=deep_both/deep_union if deep_union else '',
                    both_cases=';'.join(sorted(l&r)),left_only_cases=';'.join(sorted(l-r)),right_only_cases=';'.join(sorted(r-l))))
            for gap in (5,20,40):
                groups=episode_groups([r for r in events if r['months']==months and r['budget']==budget and r['rr'] in FINITE],episode_dates,gap)
                rr_groups={rr:set() for rr in FINITE}
                for number,group in enumerate(groups,1):
                    label=f'{months}m_b{budget}_g{gap}_e{number:02d}'
                    members=sorted({r['rr'] for r in group['events']},key=float)
                    episode_rows.append(dict(episode=label,months=months,budget=budget,gap=gap,
                        start=group['start'],end=group['end'],rr_count=len(members),rrs='/'.join(members),
                        events=len(group['events']),cases=';'.join(sorted({r['case'] for r in group['events']}))))
                    for event in group['events']:
                        rr_groups[event['rr']].add(label)
                        membership.append(dict(episode=label,**event))
                for left,right in combinations(FINITE,2):
                    l=rr_groups[left];r=rr_groups[right]
                    episode_pairs.append(dict(months=months,budget=budget,gap=gap,left=left,right=right,
                        left_episodes=len(l),right_episodes=len(r),shared=len(l&r),left_only=len(l-r),right_only=len(r-l),
                        jaccard=len(l&r)/len(l|r) if l|r else '',
                        reciprocal=bool(l-r) and bool(r-l),shared_ids=';'.join(sorted(l&r)),
                        left_only_ids=';'.join(sorted(l-r)),right_only_ids=';'.join(sorted(r-l))))
    for name,data in [('pair_windows.csv',pair_rows),('episodes.csv',episode_rows),('episode_membership.csv',membership),
                      ('pair_episodes.csv',episode_pairs),('rr_failure_summary.csv',summary)]:write_csv(ROOT/name,data)
    plot(dates,dd_by_rr,events,episode_rows)
    report(validation,summary,pair_rows,episode_rows,episode_pairs,checks)
    code=[Path(__file__),PROJECT_ROOT/'scripts/rr_curve_support.py',PROJECT_ROOT/'scripts/study_rr_curves.py',
          PROJECT_ROOT/'scripts/audit_rr_episodes.py',
          PROJECT_ROOT/'research/legacy_25k/RR_EPISODES.md']
    manifest=dict(engine=engine_digest(),source_audit_sha256=sha256_file(SOURCE/'audit.json'),
        code={str(p.relative_to(PROJECT_ROOT)):sha256_file(p) for p in code},inputs=input_files,
        checks=dict(checks),files={p.name:sha256_file(p) for p in ROOT.iterdir()
                                 if p.name not in ('manifest.json','independent_audit.json')})
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(checks),indent=2))


def report(validation,summary,pairs,episodes,epairs,checks):
    primary=[r for r in summary if r['months']==3 and r['budget']==1500]
    selected=[('0.50','2.50'),('0.50','2.25'),('1.00','2.25'),('1.00','1.75'),('0.50','1.75'),('0.50','3.50')]
    lines=['# Do RR settings fail in different historical episodes?', '',
        '**Yes, there is reciprocal historical failure-episode separation. RR0.50/2.50 '
        'has the lowest primary episode overlap among the 78 finite-RR pairs screened; '
        'RR0.50/2.25 is nearby. This remains an exploratory comparison, not a proven optimal mix.**', '',
        'Primary test: 26 non-overlapping calendar quarters, January 2020–June 2026. '
        'Every period starts each account flat with $1,500 fixed headroom. No operating policies. '
        'Monthly and six-month partitions and $6,800 headroom are retained as sensitivities. '
        'These are historical counts, not independent future failure probabilities.', '',
        'Only trades completed before a window ends contribute realized P&L and excursion '
        'breaches; boundary positions stay open and their full MAE is censored because its '
        'timing is unknown. This matters especially for the long-held RR1000 positions.', '',
        '## RR1000 validation', '',
        f'- {validation["trades"]:,} trades reconcile with counts, gross profits/losses and tester realized drawdown.',
        f'- {validation["exits_at_2330"]:,} exits occur at 23:30; the other {validation["other_exits_at_original_stop"]:,} '
        'match the original stop loss. Exit reasons are inferred from clock and P&L, not an explicit reason field.',
        f'- Maximum exported MFE is {validation["maximum_recorded_mfe_R"]:.2f}R, below the 1000R target. No target hits are observed.',
        f'- {validation["cross_date_positions"]} positions cross dates; maximum holding time is '
        f'{validation["longest_hold_calendar_days"]:.2f} days. This is the observed tape, not proof of an unconditional daily-flat rule.',
        f'- {validation["entries_absent_from_rr1"]:,} entries are absent from the RR1 source-window union; all '
        f'{validation["entries_matched_to_rr1"]:,} matched entries have identical stop ranges. '
        'The user confirms all hours were enabled together and other entry/stop settings were unchanged.',
        '- RR1000 is a separate, already non-overlapping all-hours arm. Windows starting while its '
        'recorded position is open are excluded from fresh-flat comparisons; counterfactual signals are unavailable.', '',
        'The longest hold runs from **2025-03-11 04:07:40 to 2025-03-31 14:29:20**. '
        'Other long holds include 2022-03-15 to 2022-03-28, 2023-03-13 to 2023-03-27, '
        'and 2024-03-15 to 2024-04-01. These dates make session-clock handling worth '
        'checking in the EA/tester, but the export alone does not establish the cause. '
        'The 73 cross-date trades contribute $15,148.50 of the $47,157.50 gross P&L; '
        'their behavior is material. They are retained, not silently dropped or altered.', '',
        '## Concrete separation, beyond a few different exit dates', '',
        '- May–June 2021 and October 2023: RR0.50 breaches, while RR2.50 survives each entire corresponding quarter.',
        '- March 2020, January 2022 and March 2026: RR2.50 breaches, while RR0.50 survives each entire corresponding quarter.',
        '- July–August 2024 and April 2025: both breach in the same common episode.',
        '- May versus June 2022 is less decisive: both fail in the same quarter. A 20-date grouping '
        'separates their breaches, while 40 dates merges them. The other examples above do not '
        'depend on counting that May/June split as two episodes.', '',
        '## Individual failures', '', '| RR | Eligible quarters | Failed quarters | Excluded quarters |',
        '|---|---:|---:|---:|']
    for r in primary:lines.append(f'| {r["rr"]} | {r["eligible"]} | {r["failed"]} | {r["excluded"]} |')
    lines+=['','At $6,800 headroom there are no observed eligible-window breaches in any '
        'of the three partitions, including the observed RR1000 arm. That control cannot rank episode overlap.', '',
        'RR1000 fails in 8/24 eligible quarters. Every one of RR2.50\'s six failed quarters '
        'on those dates also fails under RR1000; RR1000 adds two more. At this threshold '
        'and horizon it provides no reciprocal failed-quarter protection against RR2.50. '
        'The daily-close implementation qualification remains separate from this observed result.']
    lines+=['','## Same quarter versus different quarters','',
        'The four columns below partition eligible quarters. Both failing in one quarter does '
        'not imply one-day synchronization; the dated episode comparison follows.', '',
        '| Pair | Eligible | Both fail | Only left | Only right | Neither |', '|---|---:|---:|---:|---:|---:|']
    for left,right in selected+[(rr,'1000') for rr in ['0.50','0.75','1.00','1.75','2.25','2.50']]:
        r=next(r for r in pairs if r['months']==3 and r['budget']==1500 and r['left']==left and r['right']==right)
        lines.append(f'| {left} / {right} | {r["eligible"]} | {r["both"]} | {r["left_only"]} | {r["right_only"]} | {r["neither"]} |')
    lines+=['','## Common dated episodes','',
        'Pool first-breach intervals across all 13 finite RRs, then merge intervals separated '
        'by no more than 20 observed trading dates. Transitive merging can join a prolonged '
        'stress period. Boundaries are common to every pair, and RR1000 cannot move them. '
        'These are loss episodes in this strategy history, not independently identified macroeconomic regimes.', '',
        '| Episode | First possible breach | Last possible breach | RRs failing |', '|---|---|---|---|']
    for r in episodes:
        if r['months']==3 and r['budget']==1500 and r['gap']==20:
            lines.append(f'| {r["episode"]} | {r["start"][:10]} | {r["end"][:10]} | {r["rrs"]} |')
    lines+=['','| Pair | Shared episodes | Only left | Only right | Reciprocal unique episodes? |',
        '|---|---:|---:|---:|---|']
    for left,right in selected:
        r=next(r for r in epairs if r['months']==3 and r['budget']==1500 and r['gap']==20 and r['left']==left and r['right']==right)
        lines.append(f'| {left} / {right} | {r["shared"]} | {r["left_only"]} | {r["right_only"]} | {r["reciprocal"]} |')
    lines+=['','## Boundary and grouping sensitivity','',
        'Each cell is shared / left-only / right-only episode counts. A pair with zero '
        'unique episodes on one side does not demonstrate reciprocal episode diversification.', '',
        '| Pair | Window months | Gap 5 | Gap 20 | Gap 40 |', '|---|---:|---|---|---|']
    for left,right in selected:
        for months in (1,3,6):
            cells=[]
            for gap in (5,20,40):
                r=next(r for r in epairs if r['months']==months and r['budget']==1500 and r['gap']==gap and r['left']==left and r['right']==right)
                cells.append(f'{r["shared"]} / {r["left_only"]} / {r["right_only"]}')
            lines.append(f'| {left} / {right} | {months} | '+' | '.join(cells)+' |')
    lines+=['','## Chronology','', '![First breaches by common quarter start](quarter_failures.png)', '',
        '![Continuous realized drawdown stress](drawdown_stress.png)', '',
        'The second chart marks continuous realized drawdown of at least $1,500 from the '
        'earned peak. It shows recurring stress, not account deaths. Continuous deep-drawdown '
        'overlap is saved in pair_windows.csv as a supplementary diagnostic.', '',
        '## Evidence and verification','',
        '- windows.csv and breach_events.csv retain eligibility, first-breach intervals and trade identities.',
        '- episodes.csv and episode_membership.csv retain every episode boundary and all contributing events.',
        '- pair_windows.csv and pair_episodes.csv retain all pairs and sensitivity combinations.',
        '- native_trades.csv and selected_trades.json retain reproducible source and selection evidence.',
        '- Cross-date positions and unmatched RR1000 entries are exported separately; no source files were altered.',
        f'- Checks: {json.dumps(dict(checks),sort_keys=True)}.',
        '- Input, code and output hashes are recorded in manifest.json. Original finite-RR paths '
        'and selections reproduce the frozen study; first breaches are checked with separate Decimal accounting.', '',
        '- [Independent audit](independent_audit.json) reconstructs episode groups as connected '
        'components of an interval graph and checks all failed-window and episode-pair set counts.', '',
        'Reproduce with `.\\venv\\Scripts\\python.exe scripts/study_rr_episodes.py`, followed by '
        '`.\\venv\\Scripts\\python.exe scripts/audit_rr_episodes.py`.','']
    (ROOT/'rr_episodes__REPORT.generated.md').write_text('\n'.join(lines),encoding='utf-8')


def plot(dates,dds,events,episodes):
    cache=PROJECT_ROOT/'outputs/matplotlib-cache';cache.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    rrs=list(dds)
    fig,ax=plt.subplots(figsize=(13,6),layout='constrained')
    for group in episodes:
        if group['months']==3 and group['budget']==1500 and group['gap']==20:
            ax.axvspan(datetime.fromisoformat(group['start']),datetime.fromisoformat(group['end']),color='#dddddd',alpha=.5)
    for event in events:
        if event['months']!=3 or event['budget']!=1500:continue
        y=rrs.index(event['rr']);x0=datetime.fromisoformat(event['interval_start']);x1=datetime.fromisoformat(event['exit'])
        color='#c05621' if event['rr']=='1000' else '#087e8b'
        ax.plot([x0,x1],[y,y],color=color,lw=3);ax.scatter([x1],[y],color=color,s=18)
    ax.set_yticks(range(len(rrs)),rrs);ax.set_ylabel('RR (1000 = observed all-hours arm)')
    ax.set_title('First $1,500 fixed-floor breaches: fresh accounts each quarter\nPoints = exit proxy; segments = possible breach interval; grey = common finite-RR episode',fontsize=11)
    ax.set_xlim(START,END);ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(alpha=.2);ax.set_xlabel('Recorded date')
    for ext in ('png','svg'):fig.savefig(ROOT/f'quarter_failures.{ext}',dpi=150,bbox_inches='tight')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(13,5.7),layout='constrained')
    arr=np.array([[min(v/1500,3) for v in dds[rr]] for rr in rrs])
    x=[mdates.date2num(datetime.fromisoformat(d)) for d in dates]
    mesh=ax.pcolormesh(x,np.arange(len(rrs)),arr,shading='nearest',cmap='YlOrRd',vmin=0,vmax=3,rasterized=True)
    ax.set_yticks(range(len(rrs)),rrs);ax.set_ylabel('RR');ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_title('Continuous January-2020 paths: realized drawdown / $1,500\nStress diagnostic, not fixed-floor account deaths; colors capped at 3×',fontsize=11)
    fig.colorbar(mesh,ax=ax,label='Drawdown / $1,500')
    for ext in ('png','svg'):fig.savefig(ROOT/f'drawdown_stress.{ext}',dpi=150,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':main()
