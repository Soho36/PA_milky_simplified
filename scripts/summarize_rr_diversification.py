"""Reader-facing findings, separating the 2020 stress start and March replay."""
from collections import Counter
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/legacy_25k/rr_diversification'


def read_csv(path):
    with path.open(newline='',encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def main():
    rows=read_csv(OUT/'comparison.csv')
    primary=[r for r in rows if r['phase']=='operating' and r['withdrawal']=='minimum' and r['path_order']=='mae_first']
    index={(r['start_year'],r['portfolio']):r for r in primary}
    march=read_csv(OUT/'march_stress/comparison.csv')
    mi={(r['path_order'],r['portfolio']):r for r in march}
    mixture_names=['near','modest','four','wide']
    labels={'rr_1.00':'All 1.00','near':'0.75 / 1.25','modest':'0.50 / 1.50',
            'four':'0.50 / 1.00 / 1.50 / 2.00','wide':'0.50 / 1.50 / 2.50 / 3.50'}
    march_audit={'cases':len(march),'control_reproduced':False,'mixture_march_counts_stable_under_both_orders':True}
    for row in march:
        detail=json.loads((OUT/'march_stress'/f'{row["path_order"]}__{row["portfolio"]}.json').read_text())
        deaths=detail['march_deaths']
        groups=Counter((a['window'],a['signal_entry']) for a in deaths)
        assert len(deaths)==int(row['march_total_deaths'])
        assert max(groups.values(),default=0)==int(row['march_same_signal_peak'])
        assert int(row['march1_cohort_deaths'])<=int(row['march1_alive'])
        if row['portfolio']=='rr_1.00' and row['path_order']=='mae_first':
            assert detail['row']['historical_control_reproduced']
            assert int(row['march1_cohort_deaths'])==20 and int(row['march31_alive'])==0
            march_audit['control_reproduced']=True
    for name in mixture_names:
        for key in ('march1_alive','march1_cohort_deaths','march_same_signal_peak','march31_alive'):
            assert mi['mae_first',name][key]==mi['mfe_first',name][key]
    (OUT/'march_stress/audit.json').write_text(json.dumps(march_audit,indent=2)+'\n')
    lines=['# RR diversification: first findings','',
        '**The tested RR mixtures can spread failures and preserve earning capacity, but do not consistently reduce total mortality or every rolling loss cluster.** The wide mix is a useful candidate for further validation, not an established optimum.','',
        'Completed 286 primary/sensitivity runs plus 26 replays of the documented March 2026 failure. No withdrawal reserve, pipeline or mixture weights were optimized in this study.','',
        '## Data repair','',
        'All 301 replacement RR 16–17 trade/stat pairs passed. Across the complete RR tree, all 6,923 window/parameter pairs reconcile and satisfy the coverage pins. Seventy runs gained missing history. Existing overlapping trades are unchanged. Old files are backed up under `outputs/sweep_backups/20260920T144605-19f5dd/`. GG was not updated.','',
        'RR 1.00 trade bytes are unchanged; only the MT5 Sharpe statistic changed. The explicit input transition preserves historical baseline manifests. Nine sampled RR tapes have 0–15 missing and 0–1 extra entry identities relative to RR1, despite complete date coverage. All common candle ranges match; common negative outcomes match except one trade at each of 0.50/0.75. Native exported offers were used without fabricating missing exits. See `signal_alignment.csv`.','',
        '## The March 2026 failure','',
        'This separate stress replay uses the prior daily-maximum/$5,700 reserve policy, including its original supply settings. The RR1 control exactly reproduces its $215,439.75 ongoing net cash, 111 lifetime deaths, 95,955 trade copies and 20 deaths together on March 26. The primary daily-minimum/$6,800 policy had no March deaths from its 2020 start, so it cannot demonstrate avoidance of that particular event.','',
        '| Equal-weight portfolio | Alive March 1 | March cohort deaths | Largest March same-signal loss | Alive March 31 |',
        '|---|---:|---:|---:|---:|']
    for name in ['rr_1.00']+mixture_names:
        r=mi['mae_first',name]
        lines.append(f'| {labels[name]} | {r["march1_alive"]} | {r["march1_cohort_deaths"]} | {r["march_same_signal_peak"]} | {r["march31_alive"]} |')
    lines += ['',
        'All four mixtures have the same March cohort losses and month-end survivor counts under both MAE-first and MFE-first. This is more than shifting exit timestamps: the surviving accounts remain live at month end. Several homogeneous alternatives also survive this event, so March alone does not prove a benefit from combining them.','',
        '## Primary operating study: 2021–2025 starts','',
        'The fixed baseline uses daily minimum requests, $6,800 headroom, $5,000 initial owner cash plus $200/month, five RR1 evaluations at once, seven-day launch spacing, two spares and a shared 20-seat cap. These starts are shown separately from the 2020 stress start. Each comparison shares its start and remaining history.','',
        '| Fresh start | RR1 / wide total deaths | RR1 / wide wipeouts | RR1 / wide max same-signal deaths | RR1 / wide possible 20-day cluster | RR1 / wide net operating cash |',
        '|---|---:|---:|---:|---:|---:|']
    for year in range(2021,2026):
        base=index[str(year),'rr_1.00']; wide=index[str(year),'wide']
        pair=lambda key: f'{base[key]} / {wide[key]}'
        cash=f'${float(base["net_operating_cash"]):,.0f} / ${float(wide["net_operating_cash"]):,.0f}'
        lines.append(f'| {year} | {pair("deaths")} | {pair("book_wipeouts")} | {pair("max_same_signal_deaths")} | {pair("possible_20d_death_cluster")} | {cash} |')
    lines += ['',
        'The wide mix avoided every modeled empty-book episode in these five starts. RR1 had at least one in four starts. Its same-signal peak improved in four starts and tied in one. However, the possible 20-day peak improved in only two, tied in one and worsened in two. Total deaths were higher in the 2021–2023 starts. This is continuity and concentration improvement with meaningful trade-offs, not uniform safety improvement.','',
        'Higher net cash is shown as a constraint check, not the selection objective. The 2021 wide mix earns less than RR1. The MFE-first 2023 sensitivity also reverses the small cash advantage: wide $162,349 versus RR1 $164,292, while wide still avoids the RR1 empty-book episode. A homogeneous 2.50 portfolio outperforms wide on both deaths and cash from 2023; the mixture is not superior to every constituent.','',
        '## 2020 is a separate stress case','',
        'For the operating 2020 start, RR1 has 63 deaths, a seven-account same-signal peak and two very brief empty-book episodes; wide has 48 deaths, a three-account peak and no empty-book episodes. The possible 20-day peak drops from 13 to 7. Those two RR1 empty episodes total only 0.31 days, so the wipeout count alone exaggerates the practical interruption there.','',
        'In the no-replacement isolation experiment, every fresh 2020 portfolio eventually exhausts its accounts. That does not mean every variant died in COVID: RR1 fails on March 12, 2020, while RR0.50 survives until June 2021. The mixes preserve some accounts after the initial shock, but eventually need replacement supply. Isolation starts in 2021 and 2025 also eventually exhaust all tested portfolios, so failure is not confined to 2020.','',
        '## What this establishes','',
        'Different RR settings provide a real mechanism for different account histories: different outcomes, different exits and different subsequent acceptance of signals. Within this historical model, simple mixtures can preserve part of the earning portfolio through a shock that wipes out an all-1.00 book.','',
        'It does not establish a universal best mixture or future failure probability. Historical starts overlap. Deaths use exported extrema at exit rather than exact intratrade crossings; same-signal grouping and conservative interval bounds address but do not eliminate that limitation. Evaluation-supply outcomes also depend on assumed extrema ordering.','',
        'The next validation should freeze a small candidate set, retain the homogeneous constituents as controls, and test genuinely new history or common calendar-block stresses without independently shuffling accounts. There is no evidence here to justify optimizing finely spaced RR values or precise weights.','',
        '## Evidence','',
        '- `rr_diversification__REPORT.generated.md`: full main tables and mixture comparisons.',
        '- `comparison.csv` and `deltas_vs_rr1.csv`: all 286 main runs.',
        '- `march_stress/march_stress__REPORT.generated.md`: all homogeneous and mixed March controls.',
        '- `independent_audit.json`: all 6,704 death records and rolling cohort/interval metrics independently reconstructed.',
        '- `audit.json`: 110 homogeneous controls reproduce the established simulator; 14,385,023 trade copies checked.',
        '- `input_update.json`, `contract.json` and `cases/`: input provenance, fixed study definition and account-level evidence.','']
    (OUT/'rr_diversification__FINDINGS.generated.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Wrote findings and audited all 26 March cases.')


if __name__=='__main__':
    main()
