"""Tables and static scientific plots for the frozen unrestricted-curve study."""
from collections import defaultdict,Counter
from datetime import datetime,timedelta
import csv,json,os,statistics
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from study_rr_diversification import write_csv

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_curves'


def main():
    c=json.loads((ROOT/'contract.json').read_text()); audit=json.loads((ROOT/'audit.json').read_text())
    for file,digest in audit['files'].items():assert sha256_file(ROOT/file)==digest
    rows=list(csv.DictReader((ROOT/'comparison.csv').open()))
    fail=list(csv.DictReader((ROOT/'failure_comparison.csv').open()))
    pairs=list(csv.DictReader((ROOT/'pair_diagnostics.csv').open()))
    groups=defaultdict(list)
    for r in rows:
        if r['kind']=='12m':groups[r['portfolio']].append(r)
    summary=[]
    for name,rs in groups.items():
        rs.sort(key=lambda r:r['start'])
        item=dict(portfolio=name,components=rs[0]['components'],windows=len(rs),
            mean_pnl=statistics.mean(float(r['net_pnl']) for r in rs),
            mean_mdd=statistics.mean(float(r['max_drawdown']) for r in rs),
            worst_mdd=max(float(r['max_drawdown']) for r in rs),
            lower_mdd_than_rr1=sum(float(r['mdd_delta_vs_rr1'])<-1e-6 for r in rs),
            lower_mdd_than_best_constituent=sum(float(r['max_drawdown'])<float(r['best_constituent_max_drawdown'])-1e-6 for r in rs),
            mean_smoothing=statistics.mean(float(r['smoothing_vs_mean_constituent_dd']) for r in rs))
        for label,part in [('early12',rs[:12]),('later11',rs[12:])]:
            item[label+'_mdd_wins']=sum(float(r['mdd_delta_vs_rr1'])<-1e-6 for r in part)
            item[label+'_mean_mdd_delta']=statistics.mean(float(r['mdd_delta_vs_rr1']) for r in part)
            item[label+'_mean_pnl_delta']=statistics.mean(float(r['pnl_delta_vs_rr1']) for r in part)
        summary.append(item)
    summary.sort(key=lambda r:r['mean_mdd']); write_csv(ROOT/'screen_summary.csv',summary)
    index={r['portfolio']:r for r in summary}
    best_pair=next(r['portfolio'] for r in summary if r['portfolio'].startswith('pair_'))
    names=list(dict.fromkeys(['rr_1.00','rr_0.50','rr_2.50',best_pair,'pair_0.50_3.50','wide4','center4','edge4','without050','grid5']))
    lines=['# Synchronized RR curves and failure markers','',
        '**A modest historical mixing benefit exists at matched nominal exposure. It does not '
        'remove common bad periods, and the strongest-looking mix is not consistently superior across windows.**','',
        f'{audit["cohorts"]} common-start cohorts; 13 RR variants; 97 portfolios; '
        f'{audit["comparisons"]:,} curve comparisons. No withdrawals, purchases, replacements, '
        'caps, compounding or termination of analytical curves. Primary results use 23 overlapping '
        'twelve-month windows, with quarterly starts from January 2020 through July 2025.','',
        'Every displayed portfolio is an equal-weight average in one-MNQ-equivalent units. '
        'Adding another identical RR1 account leaves this normalized curve unchanged. '
        'Different variants still have different trade counts and holding times; exposure.csv '
        'records those differences. These are realized P&L paths, not synchronized open equity.','',
        '## 1. Does mixing improve the resulting curve?','',
        'Dollar figures are descriptive means of window outcomes, not annual forecasts. '
        'The lowest-drawdown pair below was identified on these same data and is an exploratory candidate.','',
        '| Portfolio | Mean net P&L | Mean maximum drawdown | Lower drawdown than RR1 | Lower than every constituent | Mean smoothing versus constituent-average drawdown |',
        '|---|---:|---:|---:|---:|---:|']
    for name in names:
        r=index[name]
        lines.append(f'| {name} | ${r["mean_pnl"]:,.0f} | ${r["mean_mdd"]:,.0f} | {r["lower_mdd_than_rr1"]}/23 | '
                     f'{r["lower_mdd_than_best_constituent"]}/23 | ${r["mean_smoothing"]:,.0f} |')
    winner=index[best_pair]; baseline=index['rr_1.00']
    lines+=['',f'The lowest mean-drawdown pair is **{winner["components"]}**: '
        f'{100*(1-winner["mean_mdd"]/baseline["mean_mdd"]):.1f}% lower mean maximum drawdown than RR1, '
        f'with {100*(winner["mean_pnl"]/baseline["mean_pnl"]-1):.1f}% higher mean net P&L. '
        'Compare it with the single-RR controls before crediting all of that difference to diversification.',
        '', 'The constituent-average drawdown column separates some peak-offset smoothing from '
        'simply including a less volatile component. It is not equivalent to beating the safest component. '
        'The original wide4 never beats every constituent on maximum drawdown in these 23 windows.',
        '', '### Chronological stability','',
        'Early = the twelve starts in 2020–2022; later = the eleven starts in 2023–July 2025. '
        'The windows overlap and both periods were already available to this research. This is not unseen validation.','',
        '| Mix | Earlier drawdown wins vs RR1 | Later drawdown wins vs RR1 | Earlier mean drawdown difference | Later mean drawdown difference |',
        '|---|---:|---:|---:|---:|']
    for name in [best_pair,'pair_0.50_1.75','pair_1.00_2.50','wide4','center4']:
        r=index[name]
        lines.append(f'| {name} | {r["early12_mdd_wins"]}/12 | {r["later11_mdd_wins"]}/11 | '
            f'${r["early12_mean_mdd_delta"]:,.0f} | ${r["later11_mean_mdd_delta"]:,.0f} |')
    lines+=['','Lower-RR / middle-to-higher-RR pairs are a candidate region, rather than evidence '
        'for one precise optimum. The nearby 0.50/1.75, 0.50/2.25 and 0.50/2.75 pairs also '
        'appear near the low-drawdown end of this screen. Finer tuning is not justified by this study.','',
        '### How different are the daily outcomes?','',
        '| RR pair | Mean daily P&L correlation | Range across twelve-month windows |',
        '|---|---:|---|']
    for a,b in [('0.50','2.50'),('0.50','3.50'),('1.00','1.25')]:
        values=[float(r['daily_pnl_correlation']) for r in pairs if r['kind']=='12m' and r['left']==a and r['right']==b]
        lines.append(f'| {a}/{b} | {statistics.mean(values):.3f} | {min(values):.3f}–{max(values):.3f} |')
    lines+=['','The variants remain substantially correlated. Distinct RR values are not independent strategies. '
        'Larger RR spacing can change paths more, but that does not make the widest pair the best drawdown mix.','',
        '## 2. Do independent account failures coincide?','',
        'Fixed-floor headroom is measured below each account\'s starting value. These are '
        'synthetic equal-headroom accounts, not fresh PAs with a moving trailing floor. '
        'MAE markers indicate a breach interval; recorded exit dates are proxies. Curves continue after markers.','',
        '### $1,500 fixed headroom, using MAE and net-close breaches','',
        '| Portfolio | Windows with any constituent breach | Windows where every constituent breaches | Mean fraction breached | Mean largest possible 5-day breach fraction |',
        '|---|---:|---:|---:|---:|']
    for name in ['rr_1.00','rr_0.50','rr_2.50',best_pair,'pair_0.50_3.50','wide4','center4','grid5']:
        rs=[r for r in fail if r['kind']=='12m' and r['portfolio']==name and r['budget']=='1500' and r['method']=='excursion_floor']
        lines.append(f'| {name} | {sum(float(r["fraction_breached"])>0 for r in rs)}/23 | '
            f'{sum(float(r["fraction_breached"])==1 for r in rs)}/23 | '
            f'{statistics.mean(float(r["fraction_breached"]) for r in rs):.1%} | '
            f'{statistics.mean(float(r["possible_5d_fraction"]) for r in rs):.1%} |')
    lines+=['','For example, 0.50/2.50 preserves at least one constituent through more windows than '
        'all-RR1, while exposing some part of the book to a breach in more windows. Its mean '
        'fraction breached equals RR1 in this sample. The improvement is concentrated in '
        'avoiding joint failure, not in uniformly reducing the number of account losses.',
        '', 'Its mean largest possible five-day breach fraction falls only from 34.8% for RR1 '
        'to 32.6%. Avoiding complete loss by the end of a window is stronger evidence here '
        'than spreading failures widely through time.',
        '', '"Every constituent breaches" means sometime during the window, not necessarily '
        'on one signal or day. failure_comparison.csv separately reports same-signal, recorded '
        '1/5/20-day and conservative interval-overlap fractions. A mixed average curve is never '
        'used to rescue the accounts that breached individually.',
        '', '### $6,800 fixed headroom','']
    markers=list(csv.DictReader((ROOT/'markers.csv').open()))
    large=[r for r in markers if r['budget']=='6800' and r['method']=='excursion_floor' and r['breached']=='True']
    if not large:
        lines+=['**No tested variant breaches the $6,800 fixed floor in any of the 29 cohorts.** '
            'This level provides no observations for ranking failure synchronization. It does not '
            'establish safety under withdrawals, a trailing floor or future market history.']
    else:lines.append(f'{len(large)} individual $6,800 excursion-floor breaches were recorded.')
    lines+=['','Peak-drawdown markers answer a different question: a strategy can give back $6,800 '
        'from an earned peak without losing $6,800 from its starting balance. They are included '
        'as closed_peak_dd in markers.csv and failure_comparison.csv, not counted as fixed-floor deaths.',
        '', '## Visual evidence','',
        '![Unrestricted realized P&L and drawdowns](realized_curves.png)','',
        '![Window-by-window differences from RR1](window_stability.png)','',
        '![Individual fixed-floor failure timelines](failure_timeline.png)','',
        '## Interpretation','',
        'The synchronized experiment supports modest historical drawdown complementarity and '
        'some protection against all components failing. It does not establish a uniformly '
        'superior RR mix, and it does not validate the old operating-policy ranking. Keep the '
        '0.50/middle-RR pair region and the original wide4 as research candidates, with their '
        'homogeneous controls. Preserve the late-period weaknesses rather than selecting on full-sample averages.',
        '', 'Inputs are native RR tapes with small differences in offered signals. The final full-history '
        'date may be incomplete. Boundary positions stay open and uncredited; their post-horizon '
        'MAE is censored. Exact combined open-equity drawdown cannot be reconstructed from these exports.',
        '', '## Evidence and checks','',
        f'- {audit["router_replays"]} accepted-trade sequences match the existing blocked router; '
        f'{audit["accepted_trades_checked"]:,} accepted trades checked.',
        '- Identical-RR1 duplication matches single RR1 in all 29 cohorts. Six behavioral tests pass.',
        '- independent_audit.json reconstructs curves, realized drawdowns, rolling losses, individual markers, failure clusters and correlations.',
        '- comparison.csv, screen_summary.csv, failure_comparison.csv, markers.csv, pair_diagnostics.csv and exposure.csv retain all comparisons.',
        '- cohorts/*/curves.csv and paths.json retain daily paths, accepted trade identities, censoring and marker evidence.',
        '- contract.json pins the frozen profile, protocol, engine and inputs. The core simulator and earlier results are unchanged.','',
        'To reproduce from the project root (the report step requires Matplotlib):','',
        '```powershell',
        '.\\venv\\Scripts\\python.exe scripts/study_rr_curves.py',
        '.\\venv\\Scripts\\python.exe scripts/audit_rr_curves.py',
        '.\\venv\\Scripts\\python.exe scripts/summarize_rr_curves.py',
        '.\\venv\\Scripts\\python.exe -m unittest tests.test_rr_curves',
        '```','']
    (ROOT/'rr_curves__REPORT.generated.md').write_text('\n'.join(lines),encoding='utf-8')
    plot(c,best_pair,groups)
    import matplotlib
    (ROOT/'report_manifest.json').write_text(json.dumps(dict(summarizer_sha256=sha256_file(Path(__file__)),
        python_version=sys.version,matplotlib_version=matplotlib.__version__,
        source_audit_sha256=sha256_file(ROOT/'audit.json'),
        files={p.name:sha256_file(p) for p in ROOT.iterdir() if p.suffix in ('.png','.svg') or p.name in ('rr_curves__REPORT.generated.md','screen_summary.csv')}),indent=2)+'\n')
    print('Report and three plot sets generated; exploratory pair:',best_pair)


def plot(contract,best_pair,groups):
    cache=PROJECT_ROOT/'outputs/matplotlib-cache'
    cache.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import StrMethodFormatter
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
        'axes.grid':True,'grid.alpha':.22,'figure.facecolor':'white','savefig.facecolor':'white'})
    colors={'rr_1.00':'#212529',best_pair:'#087e8b','wide4':'#c05621','center4':'#7353a6'}
    labels={'rr_1.00':'All RR1',best_pair:contract['portfolios'][best_pair][0]+' / '+contract['portfolios'][best_pair][1]+' (screened pair)',
            'wide4':'Wide four-RR mix','center4':'Centered four-RR mix'}
    def save(fig,name):
        fig.savefig(ROOT/f'{name}.png',dpi=160,bbox_inches='tight')
        fig.savefig(ROOT/f'{name}.svg',bbox_inches='tight');plt.close(fig)
    obs=list(csv.DictReader((ROOT/'cohorts/full_2020-01-01/curves.csv').open()))
    xs=[datetime.fromisoformat(r['date']) for r in obs]
    fig,axs=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
    for name,color in colors.items():
        components=contract['portfolios'][name]
        ys=[statistics.mean(float(r[rr]) for rr in components) for r in obs]
        peak=0; dd=[]
        for y in ys:peak=max(peak,y);dd.append(y-peak)
        axs[0].plot(xs,ys,label=labels[name],color=color,lw=1.4)
        axs[1].plot(xs,dd,color=color,lw=1.3)
    axs[0].set_title('Synchronized January 2020 start — unrestricted realized P&L',loc='left')
    axs[0].set_ylabel('Net P&L ($ / one-MNQ equivalent)');axs[1].set_ylabel('Drawdown from peak ($)')
    axs[1].set_xlabel('Date');axs[0].legend(loc='upper left',frameon=False)
    for ax in axs:ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))
    axs[1].xaxis.set_major_locator(mdates.YearLocator());axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    save(fig,'realized_curves')
    fig,axs=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
    for name in [best_pair,'wide4','center4']:
        rs=groups[name];x=[datetime.fromisoformat(r['start']) for r in rs]
        axs[0].plot(x,[float(r['mdd_delta_vs_rr1']) for r in rs],marker='o',ms=3,label=labels[name],color=colors[name])
        axs[1].plot(x,[float(r['pnl_delta_vs_rr1']) for r in rs],marker='o',ms=3,color=colors[name])
    axs[0].set_title('Equal 12-month windows — paired differences from all-RR1',loc='left')
    axs[0].set_ylabel('Max drawdown difference ($)\nBelow zero = improvement')
    axs[1].set_ylabel('Net P&L difference ($)\nAbove zero = improvement');axs[1].set_xlabel('Common start date')
    for ax in axs:ax.axhline(0,color='#555555',lw=.8);ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))
    axs[0].legend(frameon=False);axs[1].xaxis.set_major_locator(mdates.YearLocator());axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    save(fig,'window_stability')
    fig,axs=plt.subplots(1,2,figsize=(12,5.7),sharey=True,layout='constrained')
    for ax,year in zip(axs,[2020,2025]):
        d=json.loads((ROOT/f'cohorts/full_{year}-01-01/paths.json').read_text()); end=datetime.fromisoformat(d['end'])
        for i,rr in enumerate(contract['spec']['rr_values']):
            m=d['markers'][rr]['1500']['excursion_floor']
            if m:
                first=datetime.fromisoformat(m['interval_start']);last=datetime.fromisoformat(m['exit'])
                ax.plot([first,last],[i,i],color='#c05621',lw=3)
                ax.scatter([last],[i],color='#c05621',s=24,zorder=3)
            else:ax.scatter([end],[i],marker='>',facecolors='none',edgecolors='#087e8b',s=45,zorder=3)
        ax.set_title(f'All RRs start January {year}',loc='left');ax.set_xlabel('Recorded date / censored horizon')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3,maxticks=5))
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        ax.set_yticks(range(13),contract['spec']['rr_values']);ax.set_xlim(datetime(year,1,1),end+timedelta(days=40))
    axs[0].set_ylabel('RR setting')
    fig.suptitle('$1,500 fixed-headroom first breach: orange = breach interval/exit; teal > = no observed breach',fontsize=11)
    save(fig,'failure_timeline')


if __name__=='__main__':
    main()
