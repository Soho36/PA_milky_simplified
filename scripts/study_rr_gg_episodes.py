"""Cross-strategy GG/RR failure episodes; r/r is a setting, not a strategy name."""
from collections import Counter,defaultdict
import csv,json,os,statistics,sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT,load_config
from pa_milky.loader import load_trades,WINDOWS
from pa_milky.provenance import sha256_file,engine_digest
from rr_curve_support import select_trades,first_markers,daily_path,curve_metrics,drawdowns
from study_rr_curves import router_selection
from study_rr_episodes import windows,episode_groups,independent_marker

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_gg_episodes'
VALUES=[f'{n/4:.2f}' for n in range(2,15)]
START=datetime(2020,1,1);END=datetime(2026,7,1)


def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def write(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    install=PROJECT_ROOT/'results/legacy_25k/rr_gg_input_update/input_update.json'
    update=json.loads(install.read_text());assert update['applied'] and not update['history_differences']
    for record in update['files']:
        assert sha256_file(PROJECT_ROOT/'1_sweeps'/record['relative'])==record['new_sha256']
    cfg=load_config(PROJECT_ROOT/'config/scenarios/full_rulebook_monthly_500.json')
    tapes={f'{s}:{rr}':load_trades(cfg.sweeps_root,strategy=s,risk_reward=rr)
           for s in ('RR','GG') for rr in VALUES}
    dates=sorted({at.date().isoformat() for tape in tapes.values() for t in tape
                  for at in (t.entry_at,t.exit_at) if START<=at<END})
    write(ROOT/'episode_calendar.csv',[dict(date=d) for d in dates])
    pairs=[(f'RR:{a}',f'GG:{b}') for a in VALUES for b in VALUES]+[('RR:0.50','RR:2.50')]
    continuous={};continuous_metrics=[];checks=Counter()
    for name,tape in tapes.items():
        chosen=select_trades(tape,START,END)
        path=daily_path(chosen,dates,END,cfg.commission_per_copy_usd);continuous[name]=path
        metrics,_=curve_metrics(path,dates,START.isoformat())
        continuous_metrics.append(dict(arm=name,**metrics))
    write(ROOT/'continuous_curves.csv',[dict(date=d,**{k:v[i] for k,v in continuous.items()}) for i,d in enumerate(dates)])
    write(ROOT/'continuous_summary.csv',continuous_metrics)
    prior={(r['case'],r['rr'],r['budget']):r for r in read(PROJECT_ROOT/'results/legacy_25k/rr_episodes/windows.csv')}
    rows=[];events=[];selections={};paircurves=[]
    for months in (1,3,6):
        for start,end in windows(months):
            case=f'{months}m_{start.date()}';period_dates=[d for d in dates if start.date().isoformat()<=d<end.date().isoformat()]
            selections[case]={};paths={};metrics_by_arm={}
            for name,tape in tapes.items():
                strategy,rr=name.split(':');chosen=select_trades(tape,start,end)
                ids=[t.trade_key for t in chosen];selections[case][name]=ids
                if months==3:
                    assert ids==router_selection(tape,start,end)
                    checks['quarter_router_sequences']+=1
                    path=daily_path(chosen,period_dates,end,cfg.commission_per_copy_usd);paths[name]=path
                    metrics_by_arm[name]=curve_metrics(path,period_dates,start.isoformat())[0]
                for budget in (1500,6800):
                    marker=first_markers(chosen,budget,end,cfg.commission_per_copy_usd)['excursion_floor']
                    actual=(marker['trade_key'],marker['interval_start'],marker['exit']) if marker else None
                    assert actual==independent_marker(chosen,budget,end,cfg.commission_per_copy_usd)
                    checks['decimal_first_markers']+=1
                    record=dict(case=case,months=months,start=start.isoformat(),end=end.isoformat(),rr=name,
                        strategy=strategy,risk_reward=rr,budget=budget,eligible=True,breached=bool(marker),
                        trade_key=marker['trade_key'] if marker else '',interval_start=marker['interval_start'] if marker else '',
                        exit=marker['exit'] if marker else '',accepted=len(chosen),closed=sum(t.exit_at<end for t in chosen))
                    if strategy=='RR':
                        old=prior[case,rr,str(budget)]
                        for field in ('trade_key','interval_start','exit'):assert record[field]==old[field]
                        assert str(record['breached'])==old['breached']
                        checks['prior_rr_marker_matches']+=1
                    rows.append(record)
                    if marker:events.append(record)
            if months==3:
                for left,right in pairs:
                    values=[(a+b)/2 for a,b in zip(paths[left],paths[right])]
                    metrics,_=curve_metrics(values,period_dates,start.isoformat())
                    lm=metrics_by_arm[left];rm=metrics_by_arm[right]
                    assert abs(metrics['net_pnl']-(lm['net_pnl']+rm['net_pnl'])/2)<1e-7
                    assert metrics['max_drawdown']<=(lm['max_drawdown']+rm['max_drawdown'])/2+1e-7
                    checks['pair_curve_accounting']+=1
                    paircurves.append(dict(case=case,start=start.isoformat(),left=left,right=right,
                        **metrics,left_pnl=lm['net_pnl'],right_pnl=rm['net_pnl'],
                        left_mdd=lm['max_drawdown'],right_mdd=rm['max_drawdown']))
                for name,m in metrics_by_arm.items():
                    paircurves.append(dict(case=case,start=start.isoformat(),left=name,right=name,
                        **m,left_pnl=m['net_pnl'],right_pnl=m['net_pnl'],left_mdd=m['max_drawdown'],right_mdd=m['max_drawdown']))
            print(case,'26 arms checked',flush=True)
    write(ROOT/'windows.csv',rows);write(ROOT/'breach_events.csv',events);write(ROOT/'quarter_curves.csv',paircurves)
    (ROOT/'selected_trades.json').write_text(json.dumps(selections,separators=(',',':'))+'\n')
    pairrows=[];epairrows=[];episode_rows=[];membership=[];armsummary=[]
    for months in (1,3,6):
        for budget in (1500,6800):
            subset=[r for r in rows if r['months']==months and r['budget']==budget]
            failures={name:{r['case'] for r in subset if r['rr']==name and r['breached']} for name in tapes}
            n=len(list(windows(months)))
            for name,failed in failures.items():armsummary.append(dict(months=months,budget=budget,arm=name,periods=n,failed=len(failed)))
            for left,right in pairs:
                l=failures[left];r=failures[right]
                item=dict(months=months,budget=budget,left=left,right=right,periods=n,
                    left_failed=len(l),right_failed=len(r),both=len(l&r),left_only=len(l-r),right_only=len(r-l),neither=n-len(l|r),
                    jaccard=len(l&r)/len(l|r) if l|r else '',reciprocal=bool(l-r) and bool(r-l),
                    both_cases=';'.join(sorted(l&r)),left_only_cases=';'.join(sorted(l-r)),right_only_cases=';'.join(sorted(r-l)))
                if months==3:
                    for tag,allowed in [('early',{f'3m_{y}-{m:02d}-01' for y in range(2020,2023) for m in (1,4,7,10)}),
                                        ('later',{f'3m_{y}-{m:02d}-01' for y in range(2023,2027) for m in (1,4,7,10) if (y,m)<=(2026,4)})]:
                        item[tag+'_both']=len(l&r&allowed);item[tag+'_left_only']=len((l-r)&allowed);item[tag+'_right_only']=len((r-l)&allowed)
                else:
                    for tag in ('early','later'):
                        for key in ('both','left_only','right_only'):item[tag+'_'+key]=''
                assert item['both']+item['left_only']+item['right_only']+item['neither']==n
                pairrows.append(item)
            for gap in (5,20,40):
                groups=episode_groups([r for r in events if r['months']==months and r['budget']==budget],dates,gap)
                byarm={name:set() for name in tapes}
                for number,g in enumerate(groups,1):
                    label=f'{months}m_b{budget}_g{gap}_e{number:02d}'
                    armset=sorted({r['rr'] for r in g['events']})
                    episode_rows.append(dict(episode=label,months=months,budget=budget,gap=gap,start=g['start'],end=g['end'],
                        arms='/'.join(armset),arm_count=len(armset),events=len(g['events'])))
                    for event in g['events']:
                        byarm[event['rr']].add(label);membership.append(dict(episode=label,**event))
                for left,right in pairs:
                    l=byarm[left];r=byarm[right]
                    epairrows.append(dict(months=months,budget=budget,gap=gap,left=left,right=right,left_episodes=len(l),right_episodes=len(r),
                        shared=len(l&r),left_only=len(l-r),right_only=len(r-l),jaccard=len(l&r)/len(l|r) if l|r else '',
                        reciprocal=bool(l-r) and bool(r-l),shared_ids=';'.join(sorted(l&r)),
                        left_only_ids=';'.join(sorted(l-r)),right_only_ids=';'.join(sorted(r-l))))
    for name,data in [('pair_windows.csv',pairrows),('pair_episodes.csv',epairrows),('episodes.csv',episode_rows),
                      ('episode_membership.csv',membership),('arm_summary.csv',armsummary)]:write(ROOT/name,data)
    screen=[]
    for e in epairrows:
        if e['months']!=3 or e['budget']!=1500 or e['gap']!=20:continue
        p=next(r for r in pairrows if r['months']==3 and r['budget']==1500 and (r['left'],r['right'])==(e['left'],e['right']))
        c=[r for r in paircurves if (r['left'],r['right'])==(e['left'],e['right'])]
        screen.append(dict(left=e['left'],right=e['right'],episode_jaccard=e['jaccard'],shared_episodes=e['shared'],
            left_only_episodes=e['left_only'],right_only_episodes=e['right_only'],reciprocal_episodes=e['reciprocal'],
            both_quarters=p['both'],rr_only_quarters=p['left_only'],other_only_quarters=p['right_only'],
            mean_quarter_pnl=statistics.mean(r['net_pnl'] for r in c),mean_quarter_mdd=statistics.mean(r['max_drawdown'] for r in c),
            mean_left_pnl=statistics.mean(r['left_pnl'] for r in c),mean_right_pnl=statistics.mean(r['right_pnl'] for r in c),
            mean_left_mdd=statistics.mean(r['left_mdd'] for r in c),mean_right_mdd=statistics.mean(r['right_mdd'] for r in c)))
    screen.sort(key=lambda r:(r['episode_jaccard'] if r['episode_jaccard']!='' else 2,r['both_quarters'],r['left'],r['right']))
    write(ROOT/'screen.csv',screen)
    plot(dates,continuous,events,screen)
    report(screen,armsummary,pairrows,epairrows,episode_rows,continuous_metrics,checks)
    input_files={}
    for strategy in ('RR','GG'):
        for rr in VALUES:
            for window in WINDOWS:
                for directory,suffix in [(strategy,''),(strategy+'_stats','_stats')]:
                    p=cfg.sweeps_root/directory/window/f'{window}_{rr}{suffix}.csv'
                    input_files[str(p.relative_to(PROJECT_ROOT))]=sha256_file(p)
    files=[Path(__file__),PROJECT_ROOT/'scripts/audit_rr_gg_episodes.py',
           PROJECT_ROOT/'scripts/study_rr_episodes.py',PROJECT_ROOT/'scripts/study_rr_curves.py',
           PROJECT_ROOT/'scripts/rr_curve_support.py',PROJECT_ROOT/'research/legacy_25k/RR_GG_EPISODES.md',
           PROJECT_ROOT/'config/tape_coverage.json',install]
    manifest=dict(engine=engine_digest(),checks=dict(checks),inputs=input_files,
        code={str(p.relative_to(PROJECT_ROOT)):sha256_file(p) for p in files},
        files={p.name:sha256_file(p) for p in ROOT.iterdir() if p.name not in ('manifest.json','independent_audit.json')})
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(checks),indent=2))


def report(screen,arms,pairs,epairs,episodes,continuous,checks):
    cross=[r for r in screen if r['right'].startswith('GG:')]
    chosen=cross[:8]+[next(r for r in screen if r['right']=='RR:2.50')]
    lines=['# RR–GG cross-strategy failure episodes','',
        'RR and GG name strategies; numeric suffixes give r/r. Exploratory coarse screen: '
        '13 settings per strategy, 169 cross-strategy pairs, 26 homogeneous controls, '
        'and RR:0.50/RR:2.50 as a within-RR benchmark. No RR1000 arm.', '',
        'Accounts start together with one MNQ and $1,500 fixed headroom. Primary evidence '
        'uses 26 non-overlapping quarters from January 2020 through June 2026. No withdrawals, '
        'replacements, pooling or cap. $1.05 commission per completed trade. Monthly and '
        'six-month starts, $6,800 headroom and 5/20/40-date episode gaps are retained.', '',
        '## Lowest observed episode overlaps', '',
        'Sorted by primary episode Jaccard overlap, then both-failed quarter count and arm name. '
        'This is in-sample ranking; adjacent settings and sensitivities matter more than a precise winner. '
        'An episode groups first-breach intervals separated by at most 20 observed dates, '
        'transitively, across all 26 arms. These are strategy-loss episodes, not macroeconomic regimes. '
        'Adding GG can change common episode boundaries; the RR benchmark uses those same boundaries.', '',
        '| RR arm | Other arm | Shared episodes | RR-only episodes | Other-only episodes | Both-failed quarters | Mean quarter P&L | Mean quarter DD |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in chosen:lines.append(f'| {r["left"]} | {r["right"]} | {r["shared_episodes"]} | {r["left_only_episodes"]} | '
        f'{r["right_only_episodes"]} | {r["both_quarters"]}/26 | ${r["mean_quarter_pnl"]:,.0f} | ${r["mean_quarter_mdd"]:,.0f} |')
    lines+=['','Pair curves are equal-weight averages, not sums. Separate accounts still fail '
        'individually. Dollar figures are descriptive means, not forecasts. One-MNQ sizing '
        'does not equalize actual trade count, stop distance or holding time.', '',
        '## Homogeneous controls', '', '| Strategy / r/r | Failed quarters | Full-history net P&L | Full-history realized max DD |',
        '|---|---:|---:|---:|']
    for r in continuous:
        a=next(a for a in arms if a['months']==3 and a['budget']==1500 and a['arm']==r['arm'])
        lines.append(f'| {r["arm"]} | {a["failed"]}/26 | ${r["net_pnl"]:,.0f} | ${r["max_drawdown"]:,.0f} |')
    lines+=['','## Candidate sensitivity', '',
        'Cells are shared / RR-only / other-only episodes. Both exclusive counts must be '
        'positive for observed reciprocal protection. Different counts with different reset '
        'horizons are expected; these periods are not independent observations.', '',
        '| Pair | Window months | Gap 5 | Gap 20 | Gap 40 |', '|---|---:|---|---|---|']
    for candidate in chosen[:3]+chosen[-1:]:
        for months in (1,3,6):
            cells=[]
            for gap in (5,20,40):
                r=next(r for r in epairs if r['months']==months and r['budget']==1500 and r['gap']==gap and
                       (r['left'],r['right'])==(candidate['left'],candidate['right']))
                cells.append(f'{r["shared"]} / {r["left_only"]} / {r["right_only"]}')
            lines.append(f'| {candidate["left"]} / {candidate["right"]} | {months} | '+' | '.join(cells)+' |')
    large=[r for r in arms if r['budget']==6800 and r['failed']]
    lines+=['','## $6,800 fixed-headroom control','',
        'No observed breaches in any arm/partition.' if not large else
        'Observed breaches: '+ '; '.join(f'{r["arm"]}: {r["failed"]}/{r["periods"]} in {r["months"]}-month windows' for r in large), '',
        '## Chronology and the full cross-strategy grid','',
        '![First-breach chronology](first_breaches.png)','', '![Pair overlap grid](pair_overlap.png)','',
        '## Limits and evidence','',
        '- Unclosed boundary positions are uncredited and their full MAE is censored. Exact '
        'intratrade breach times are unknown; first-breach entry-to-exit intervals are preserved.',
        '- Shared episodes can be long because grouping is transitive. All boundaries and '
        'contributing failures are in episodes.csv and episode_membership.csv.',
        '- A mix can look different because one constituent rarely fails or loses money '
        'at other times. Homogeneous controls and period P&L remain visible.',
        '- Earlier/later failures, all pairs, and sensitivity results are retained in '
        'pair_windows.csv, pair_episodes.csv, quarter_curves.csv and screen.csv.',
        '- GG replacement validation and backup history are in ../rr_gg_input_update/input_update.json.',
        f'- Runner checks: {json.dumps(dict(checks),sort_keys=True)}.',
        '- [Independent audit](independent_audit.json) checks input/output hashes, period sets '
        'and graph reconstruction of episode groups.', '',
        'Reproduce: `.\\venv\\Scripts\\python.exe scripts/study_rr_gg_episodes.py`, then '
        '`.\\venv\\Scripts\\python.exe scripts/audit_rr_gg_episodes.py`.','']
    (ROOT/'rr_gg_episodes__REPORT.generated.md').write_text('\n'.join(lines),encoding='utf-8')


def plot(dates,continuous,events,screen):
    cache=PROJECT_ROOT/'outputs/matplotlib-cache';cache.mkdir(parents=True,exist_ok=True);os.environ.setdefault('MPLCONFIGDIR',str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    names=list(continuous)
    fig,ax=plt.subplots(figsize=(13,8),layout='constrained')
    for r in events:
        if r['months']!=3 or r['budget']!=1500:continue
        y=names.index(r['rr']);color='#087e8b' if r['strategy']=='RR' else '#c05621'
        first=datetime.fromisoformat(r['interval_start']);last=datetime.fromisoformat(r['exit'])
        ax.plot([first,last],[y,y],color=color,lw=2);ax.scatter([last],[y],s=14,color=color)
    ax.set_yticks(range(len(names)),names);ax.set_xlim(START,END);ax.grid(alpha=.2)
    ax.set_title('Fresh accounts each quarter: first $1,500 fixed-floor breaches\nSegments = possible breach interval; points = recorded exit proxy')
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for ext in ('png','svg'):fig.savefig(ROOT/f'first_breaches.{ext}',dpi=140,bbox_inches='tight')
    plt.close(fig)
    matrix=np.array([[next(r['episode_jaccard'] for r in screen if r['left']==f'RR:{a}' and r['right']==f'GG:{b}') for b in VALUES] for a in VALUES],dtype=float)
    fig,ax=plt.subplots(figsize=(9,8),layout='constrained')
    mesh=ax.imshow(matrix,vmin=0,vmax=1,cmap='YlOrRd')
    ax.set_xticks(range(13),VALUES);ax.set_yticks(range(13),VALUES)
    ax.set_xlabel('GG r/r');ax.set_ylabel('RR r/r')
    ax.set_title('Shared / either-failed episodes (Jaccard)\nQuarter starts, $1,500 headroom, 20-date gap; lower overlap is lighter')
    for i in range(13):
        for j in range(13):ax.text(j,i,f'{matrix[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if matrix[i,j]>.65 else 'black')
    fig.colorbar(mesh,ax=ax)
    for ext in ('png','svg'):fig.savefig(ROOT/f'pair_overlap.{ext}',dpi=140,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':main()
