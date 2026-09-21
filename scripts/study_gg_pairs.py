"""GG-to-GG only: native synchronized curves and GG-only failure episode groups."""
from collections import defaultdict,Counter
from datetime import datetime
from itertools import combinations
import csv,json,os,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT,load_config
from pa_milky.loader import load_trades
from pa_milky.provenance import sha256_file
from rr_curve_support import select_trades,daily_path,curve_metrics,first_markers
from study_rr_episodes import episode_groups,windows

SOURCE=PROJECT_ROOT/'results/legacy_25k/rr_gg_episodes'
OUT=PROJECT_ROOT/'results/legacy_25k/gg_pairs'
VALUES=[f'{i/4:.2f}' for i in range(2,15)]


def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    design=dict(strategy='GG',rr_values=VALUES,pair_weights=[.5,.5],
        periods_months=[1,3,6],budgets=[1500,6800],episode_gaps=[5,20,40],
        scope='GG-to-GG only; 78 pairs and 13 homogeneous controls; no RR pairing or four-group portfolio selection.',
        calendar='January 2020 through June 2026; fixed $1500 headroom primary; fresh synchronized starts; no policies.')
    p=OUT/'design.json'
    if p.exists():assert json.loads(p.read_text())==design
    else:p.write_text(json.dumps(design,indent=2)+'\n')
    manifest=json.loads((SOURCE/'manifest.json').read_text())
    for name in ('windows.csv','quarter_curves.csv'):
        assert sha256_file(SOURCE/name)==manifest['files'][name]
    for name,digest in manifest['inputs'].items():
        if name.replace('\\','/').startswith(('1_sweeps/GG/','1_sweeps/GG_stats/')):
            assert sha256_file(PROJECT_ROOT/name)==digest
    rows=[r for r in read(SOURCE/'windows.csv') if r['strategy']=='GG']
    # Rename the arm identifier to r/r within this strictly single-strategy study.
    for r in rows:r['rr']=r['risk_reward']
    cfg=load_config(PROJECT_ROOT/'config/scenarios/full_rulebook_monthly_500.json')
    tapes={rr:load_trades(cfg.sweeps_root,strategy='GG',risk_reward=rr) for rr in VALUES}
    dates=sorted({at.date().isoformat() for tape in tapes.values() for t in tape for at in (t.entry_at,t.exit_at)
                  if datetime(2020,1,1)<=at<datetime(2026,7,1)})
    pairs=list(combinations(VALUES,2));period_pairs=[];episode_pairs=[];episode_rows=[];members=[]
    for months in (1,3,6):
        for budget in (1500,6800):
            part=[r for r in rows if int(r['months'])==months and int(r['budget'])==budget]
            n=len({r['case'] for r in part})
            sets={rr:{r['case'] for r in part if r['rr']==rr and r['breached']=='True'} for rr in VALUES}
            for left,right in pairs:
                l=sets[left];r=sets[right]
                period_pairs.append(dict(months=months,budget=budget,left=left,right=right,periods=n,
                    left_failed=len(l),right_failed=len(r),both=len(l&r),left_only=len(l-r),right_only=len(r-l),neither=n-len(l|r),
                    reciprocal=bool(l-r) and bool(r-l),jaccard=len(l&r)/len(l|r) if l|r else '',
                    both_cases=';'.join(sorted(l&r)),left_only_cases=';'.join(sorted(l-r)),right_only_cases=';'.join(sorted(r-l))))
            for gap in (5,20,40):
                groups=episode_groups([r for r in part if r['breached']=='True'],dates,gap)
                by_rr={rr:set() for rr in VALUES}
                for i,g in enumerate(groups,1):
                    label=f'{months}m_b{budget}_g{gap}_e{i:02d}'
                    episode_rows.append(dict(episode=label,months=months,budget=budget,gap=gap,start=g['start'],end=g['end'],
                        rrs='/'.join(sorted({r['rr'] for r in g['events']},key=float))))
                    for event in g['events']:
                        by_rr[event['rr']].add(label);members.append(dict(episode=label,**event))
                for left,right in pairs:
                    l=by_rr[left];r=by_rr[right]
                    episode_pairs.append(dict(months=months,budget=budget,gap=gap,left=left,right=right,
                        shared=len(l&r),left_only=len(l-r),right_only=len(r-l),reciprocal=bool(l-r) and bool(r-l),
                        jaccard=len(l&r)/len(l|r) if l|r else ''))
    prior={(r['case'],r['left'].split(':')[1]):r for r in read(SOURCE/'quarter_curves.csv') if r['left']==r['right'] and r['left'].startswith('GG:')}
    oldmarkers={(r['case'],r['rr'],r['budget']):r for r in rows}
    curves=[];check=Counter()
    for start,end in windows(3):
        case=f'3m_{start.date()}';calendar=[d for d in dates if str(start.date())<=d<str(end.date())];paths={};single={}
        for rr,tape in tapes.items():
            chosen=select_trades(tape,start,end)
            paths[rr]=daily_path(chosen,calendar,end,cfg.commission_per_copy_usd)
            single[rr]=curve_metrics(paths[rr],calendar,start.isoformat())[0]
            for key in ('net_pnl','max_drawdown'):
                assert abs(single[rr][key]-float(prior[case,rr][key]))<1e-7
            for budget in (1500,6800):
                marker=first_markers(chosen,budget,end,cfg.commission_per_copy_usd)['excursion_floor']
                old=oldmarkers[case,rr,str(budget)]
                assert (marker['trade_key'] if marker else '')==old['trade_key']
                check['prior_marker_matches']+=1
            check['prior_single_curve_matches']+=1
            curves.append(dict(case=case,left=rr,right=rr,**single[rr]))
        for left,right in pairs:
            path=[(a+b)/2 for a,b in zip(paths[left],paths[right])]
            m=curve_metrics(path,calendar,start.isoformat())[0]
            assert abs(m['net_pnl']-(single[left]['net_pnl']+single[right]['net_pnl'])/2)<1e-7
            assert m['max_drawdown']<=(single[left]['max_drawdown']+single[right]['max_drawdown'])/2+1e-7
            curves.append(dict(case=case,left=left,right=right,**m));check['pair_curve_checks']+=1
    summary=[]
    for left,right in [*[(rr,rr) for rr in VALUES],*pairs]:
        c=[r for r in curves if (r['left'],r['right'])==(left,right)]
        failure={rr:{r['case'] for r in rows if r['months']=='3' and r['budget']=='1500' and r['rr']==rr and r['breached']=='True'} for rr in (left,right)}
        l=failure[left];r=failure[right]
        summary.append(dict(left=left,right=right,mean_quarter_pnl=statistics.mean(r['net_pnl'] for r in c),
            mean_quarter_mdd=statistics.mean(r['max_drawdown'] for r in c),
            left_failed=len(l),right_failed=len(r),both=len(l&r),left_only=len(l-r),right_only=len(r-l),
            mean_fraction_failed=(len(l)+len(r))/52))
    summary.sort(key=lambda r:(r['both'],r['mean_fraction_failed'],r['mean_quarter_mdd']))
    for name,data in [('windows.csv',rows),('pair_windows.csv',period_pairs),('pair_episodes.csv',episode_pairs),
        ('episodes.csv',episode_rows),('episode_membership.csv',members),('quarter_curves.csv',curves),('summary.csv',summary)]:write(name,data)
    # Independent membership/set counting of every episode pair.
    for p in episode_pairs:
        prefix=f'{p["months"]}m_b{p["budget"]}_g{p["gap"]}_'
        l={m['episode'] for m in members if m['rr']==p['left'] and m['episode'].startswith(prefix)}
        r={m['episode'] for m in members if m['rr']==p['right'] and m['episode'].startswith(prefix)}
        assert (p['shared'],p['left_only'],p['right_only'])==(len(l&r),len(l-r),len(r-l));check['episode_pair_checks']+=1
    headline(summary,period_pairs,episode_pairs,check)
    code=[Path(__file__),PROJECT_ROOT/'scripts/rr_curve_support.py',PROJECT_ROOT/'scripts/study_rr_episodes.py']
    seal=dict(source_manifest_sha256=sha256_file(SOURCE/'manifest.json'),checks=dict(check),
        code={str(p.relative_to(PROJECT_ROOT)):sha256_file(p) for p in code},
        files={p.name:sha256_file(p) for p in OUT.iterdir() if p.name!='manifest.json'})
    (OUT/'manifest.json').write_text(json.dumps(seal,indent=2)+'\n')
    print(json.dumps(dict(check),indent=2))


def headline(summary,periods,episodes,check):
    selected=[('1.00','1.00'),('1.25','1.25'),('1.50','1.50'),('0.50','1.00'),('0.50','1.25'),('0.50','1.75'),('0.50','3.25'),('0.50','3.50'),('1.25','1.50')]
    ranked=sorted([r for r in summary if r['left']!=r['right']],key=lambda r:r['mean_quarter_mdd'])
    for r in ranked[:3]:
        if (r['left'],r['right']) not in selected:selected.append((r['left'],r['right']))
    primary=[r for r in periods if r['months']==3 and r['budget']==1500]
    lines=['# GG-to-GG diversification only','',
        'This study selects GG r/r settings independently. It contains no RR-to-GG ranking, '
        'four-group selection or decision about splitting capital between strategies.', '',
        '**GG has some reciprocal historical failure separation, but this screen does not '
        'establish a pair superior to its strongest individual GG controls.** GG 0.50/1.00 '
        'ties for the lowest primary episode-overlap ratio with GG 0.50/3.25 and GG 0.50/3.50. '
        'The first pair loses both components in five quarters, while the latter two do so '
        'in six. GG 1.25 alone also fails in five quarters, with fewer individual losses '
        'and higher average P&L. Different objective choices therefore select different settings.', '',
        'All 78 distinct pairs from 13 r/r settings (0.50–3.50 by 0.25), plus 13 homogeneous '
        'GG controls. Equal-weight paths, one MNQ per account, $1.05 commission, fresh synchronized '
        'starts with $1,500 fixed headroom, no operating policies. Primary: 26 quarters, January '
        '2020–June 2026. Monthly/six-month resets and $6,800 are saved as sensitivities. '
        'Episode boundaries and their trading-date calendar use GG exclusively.', '',
        f'{sum(r["reciprocal"] for r in primary)} of 78 pairs have unique failed quarters on '
        'both sides. The minimum both-failed quarter count among pairs is '
        f'{min(r["both"] for r in primary)}/26. Read each constituent control before crediting '
        'a mixture with protection.', '',
        '| GG r/r settings | Lower fails | Higher fails | Both fail | Lower-only / higher-only | Mean fraction lost | Mean quarter P&L | Mean quarter realized DD |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for left,right in selected:
        r=next(r for r in summary if (r['left'],r['right'])==(left,right))
        label=left+' alone' if left==right else left+' / '+right
        lines.append(f'| {label} | {r["left_failed"]} | {r["right_failed"]} | {r["both"]}/26 | '
            f'{r["left_only"]} / {r["right_only"]} | {r["mean_fraction_failed"]:.1%} | '
            f'${r["mean_quarter_pnl"]:,.0f} | ${r["mean_quarter_mdd"]:,.0f} |')
    lines+=['','"Both fail" means by quarter end, not necessarily on the same date. Homogeneous '
        'rows show duplicated identical accounts; the same count in both columns is not '
        'two separate observations. P&L/DD are normalized, not sums over account counts.', '',
        '## GG-only episode sensitivity','',
        'Cells are shared / lower-only / higher-only episodes. Episodes pool GG first-breach '
        'intervals, with 5/20/40-observed-date gaps and transitive merging. These are dated '
        'strategy-loss episodes, not identified economic regimes.', '',
        '| GG pair | Window months | Gap 5 | Gap 20 | Gap 40 |','|---|---:|---|---|---|']
    for left,right in [('0.50','1.00'),('0.50','1.25'),('0.50','1.75'),('1.25','1.50')]:
        for months in (1,3,6):
            cells=[]
            for gap in (5,20,40):
                r=next(r for r in episodes if r['months']==months and r['budget']==1500 and r['gap']==gap and (r['left'],r['right'])==(left,right))
                cells.append(f'{r["shared"]} / {r["left_only"]} / {r["right_only"]}')
            lines.append(f'| {left} / {right} | {months} | '+' | '.join(cells)+' |')
    lines+=['','The same history informed the earlier studies; this is exploratory, not unseen '
        'validation. Curve smoothing and reciprocal failure protection are different outcomes. '
        'Do not label two GG bands diversified merely because their r/r numbers differ. '
        'Unclosed boundary trades and their full MAE remain censored.', '',
        'Source hashes are checked. Existing GG single curves and first markers reproduce '
        'exactly. Pair P&L and drawdown bounds are checked, and episode counts are reconstructed '
        f'from membership sets. Checks: {json.dumps(dict(check),sort_keys=True)}.', '',
        'Reproduce: `.\\venv\\Scripts\\python.exe scripts/study_gg_pairs.py`.','']
    (OUT/'gg_pairs__REPORT.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()
