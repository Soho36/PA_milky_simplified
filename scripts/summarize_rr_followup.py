"""Generate comparisons from the complete frozen follow-up; never select new arms."""
from collections import Counter
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT
from pa_milky.provenance import sha256_file
from study_rr_diversification import write_csv

ROOT=PROJECT_ROOT/'results/legacy_25k/rr_followup'


def main():
    contract=json.loads((ROOT/'contract.json').read_text())
    audit=json.loads((ROOT/'audit.json').read_text())
    spec=contract['spec']
    cases={}
    for name,digest in audit['case_sha256'].items():
        file=ROOT/'cases'/f'{name}.json'
        assert sha256_file(file)==digest
        cases[name]=json.loads(file.read_text())
    rows=[c['row'] for c in cases.values()]
    index={(r['experiment'],r['phase'],r['start_year'],r['path_order'],r['portfolio']):r for r in rows}
    def get(name,year=2023,phase='operating',experiment='primary',order='mae_first'):
        return index[(experiment,phase,year,order,name)]
    def vector(name,key,years=range(2020,2026),**kwargs):
        return ' / '.join(str(get(name,y,**kwargs)[key]) for y in years)
    names=['rr_1.00',*spec['arms']]
    deltas=[]; constituents=[]
    keys=('book_wipeouts','days_empty_after_first_activation','deaths','max_same_signal_deaths',
          'possible_20d_death_cluster','net_operating_cash','mean_total_positive_equity')
    for r in rows:
        prefix=tuple(r[k] for k in ('experiment','phase','start_year','path_order'))
        baseline=index[prefix+('rr_1.00',)]
        deltas.append(dict(case=r['case'],**{k+'_delta_vs_rr1':round(r[k]-baseline[k],4) for k in keys}))
        if r['portfolio'] in spec['arms']:
            for rr in sorted({s['rr'] for s in spec['arms'][r['portfolio']]}):
                control=index.get(prefix+(f'rr_{rr}',))
                if control:
                    constituents.append(dict(case=r['case'],constituent=rr,
                        **{k+'_delta_vs_constituent':round(r[k]-control[k],4) for k in keys}))
    write_csv(ROOT/'deltas_vs_rr1.csv',deltas)
    write_csv(ROOT/'constituent_comparisons.csv',constituents)
    wipeout_details=[]
    for case in cases.values():
        events=Counter()
        for a in case['accounts']:
            events[datetime.fromisoformat(a['activated_at'])]+=1
            if not a['alive']: events[datetime.fromisoformat(a['died_at'])]-=1
        ordered=sorted(events.items()); live=peak=0; history=[]
        for i,(at,delta) in enumerate(ordered):
            after=live+delta
            if live>0 and after==0:
                start=at-timedelta(days=20)
                preceding=[(t,n) for t,n in history if t<=start]
                recent=[n for t,n in history if t>start]
                recent.append(preceding[-1][1] if preceding else 0)
                reopened=next((t for t,d in ordered[i+1:] if d>0),None)
                wipeout_details.append(dict(case=case['row']['case'],at=at.isoformat(),
                    live_before_final_loss=live,max_live_ever_before=peak,
                    max_live_preceding_20_calendar_days=max(recent,default=0),
                    reopened_at=reopened.isoformat() if reopened else None,
                    days_until_reopening=(reopened-at).total_seconds()/86400 if reopened else None))
            peak=max(peak,after); live=after; history.append((at,after))
    write_csv(ROOT/'wipeout_events.csv',wipeout_details)
    lines=['# RR composition, group count and reserve ladders: complete comparisons','',
        f'{len(rows)} historical runs. {audit["prior_controls_reproduced"]} prior controls reproduced; '
        f'{audit["copies_checked"]:,} trade copies checked. Core engine unchanged.','',
        'No arm or reserve value was changed after results were observed. Primary daily minimum / '
        '$6,800 mean target and March daily maximum / $5,700 mean target have different frozen '
        'evaluation-supply policies. Cash excludes terminal withdrawals and owner contributions.','',
        '## Frozen arms','',
        '| Arm | RR groups | RR range | Reserve offsets |', '|---|---:|---|---|']
    for name in names:
        ds=([dict(rr='1.00',offset=0)] if name=='rr_1.00' else spec['arms'][name])
        rrs=[float(d['rr']) for d in ds]; offsets=[d['offset'] for d in ds]
        lines.append(f'| {name} | {len(set(rrs))} | {min(rrs):.2f}–{max(rrs):.2f} | ${min(offsets):,.0f} to ${max(offsets):,.0f} ({len(set(offsets))} targets) |')
    lines+=['','center4 has half the wide4 range; edge4 keeps endpoints, count and mean fixed. '
        'without050 is a single-constituent ablation that also changes mean/range. '
        'Group-count contrasts necessarily change constituents. Reverse arms change assignment order only.','',
        '## Primary operating: continuity across starts','',
        'Vectors are 2020 / 2021 / 2022 / 2023 / 2024 / 2025; histories overlap and are not independent samples.','',
        '| Arm | Wipeouts by start | Max same-signal deaths by start | Possible 20-day cluster by start |',
        '|---|---|---|---|']
    for name in names:
        lines.append(f'| {name} | {vector(name,"book_wipeouts")} | {vector(name,"max_same_signal_deaths")} | {vector(name,"possible_20d_death_cluster")} |')
    lines+=['','Wipeout counts include small startup books. `wipeout_events.csv` records the '
        'live count before the final loss, the preceding 20-calendar-day peak, the lifetime '
        'peak reached before each episode, and the time until reopening. A one-seat final '
        'loss can follow an earlier cluster, so the last-seat count alone is insufficient.','',
        '### Empty duration and startup context, primary operating','',
        '| Arm | Total empty days across six overlapping starts | Wipeouts before ever reaching five PAs | Other wipeouts |',
        '|---|---:|---:|---:|']
    for name in names:
        selected=[get(name,y) for y in range(2020,2026)]
        ids={r['case'] for r in selected}
        events=[e for e in wipeout_details if e['case'] in ids]
        lines.append(f'| {name} | {sum(r["days_empty_after_first_activation"] for r in selected):.2f} | '
                     f'{sum(e["max_live_ever_before"]<5 for e in events)} | {sum(e["max_live_ever_before"]>=5 for e in events)} |')
    lines+=['','## Primary operating: 2021–2025 paired comparisons','',
        'Counts below are descriptive comparisons with RR1 across five overlapping starts. '
        'Cash ranges contain paired cash differences, not independent expected returns.','',
        '| Arm | Starts with no wipeout | Lower / equal / higher 20-day cluster | Cash difference range |',
        '|---|---:|---|---:|']
    for name in names:
        selected=[get(name,y) for y in range(2021,2026)]
        diffs=[r['possible_20d_death_cluster']-get('rr_1.00',r['start_year'])['possible_20d_death_cluster'] for r in selected]
        cash=[r['net_operating_cash']-get('rr_1.00',r['start_year'])['net_operating_cash'] for r in selected]
        lines.append(f'| {name} | {sum(r["book_wipeouts"]==0 for r in selected)}/5 | '
            f'{sum(d<0 for d in diffs)} / {sum(d==0 for d in diffs)} / {sum(d>0 for d in diffs)} | ${min(cash):,.0f} to ${max(cash):,.0f} |')
    lines+=['','## Group count: 2023 isolation and operating','',
        'A one-account RR group can lose only one copier, but several groups can lose on the same '
        'signal. A full copier-group loss means all actual copiers of that signal in that group died; '
        'it does not mean all nominal seats were present or exposed.','',
        '| Phase | Arm | Mean occupied groups on live days | Within-group peak | Portfolio signal peak | Most groups losing on one signal | Full copier-group loss events / group loss events | Possible 20-day cluster |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for phase in ('isolation','operating'):
        for name in ['rr_1.00','extremes2','wide4','grid5','grid10','grid20','grid20_reverse','ladder4','ladder20']:
            r=get(name,phase=phase)
            lines.append(f'| {phase} | {name} | {r["mean_occupied_sleeves"]:.2f} | {r["largest_within_sleeve_signal_loss"]} | '
                f'{r["max_same_signal_deaths"]} | {r["max_sleeves_lost_same_signal"]} | '
                f'{r["full_copier_sleeve_loss_events"]} / {r["sleeve_loss_events"]} | {r["possible_20d_death_cluster"]} |')
    lines+=['','## Reserve control: actual capital and dispersion, 2023 operating','',
        'Daily averages condition on days with at least one live PA. Positive account equity is '
        'profit retained inside live PAs, not withdrawable cash. Effective headroom groups = '
        'N² / sum(equal-headroom group size²). It is descriptive, not independent risk capacity.','',
        '| Arm | Wipeouts | Empty days | Deaths | Mean live PAs | Mean effective headroom groups | Mean retained positive equity | Net operating cash |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name in ['rr_1.00','uniform_low','uniform_high','ladder4','ladder20','ladder20_reverse','wide4','grid20']:
        r=get(name)
        lines.append(f'| {name} | {r["book_wipeouts"]} | {r["days_empty_after_first_activation"]:.2f} | {r["deaths"]} | '
            f'{r["mean_live_accounts"]:.2f} | {r["mean_effective_headroom_groups"]:.2f} | '
            f'${r["mean_total_positive_equity"]:,.0f} | ${r["net_operating_cash"]:,.0f} |')
    lines+=['','## March stress replay','',
        '| Arm | March 1 alive | March cohort deaths | March 31 alive | March same-signal peak | March 1 distinct / effective headroom groups |',
        '|---|---:|---:|---:|---:|---|']
    for name in names:
        r=get(name,2020,experiment='march')
        c=cases[r['case']]
        snap=next((s for s in c['snapshots'] if s['at']=='2026-03-01T00:00:00'),None)
        groups=Counter((a['death_window'],a['death_entry_at']) for a in c['accounts']
                       if not a['alive'] and a['died_at'].startswith('2026-03'))
        dispersion=f'{snap["distinct_headrooms"]} / {snap["effective_headroom_groups"]:.2f}' if snap else '0 / 0'
        lines.append(f'| {name} | {r["march1_alive"]} | {r["march_cohort_deaths"]} | {r["march31_alive"]} | '
                     f'{max(groups.values(),default=0)} | {dispersion} |')
    lines+=['','### Actual March timing and capital, MAE-first','',
        'Dates below are recorded exit-day proxies; counts across different originating '
        'signals provide evidence beyond merely delaying the exit of one losing trade. '
        'Earlier deaths at low reserve levels are part of the trade-off.','',
        '| Arm | March death dates (day: count) | Largest recorded daily loss | March 1 retained positive equity |',
        '|---|---|---:|---:|']
    march_records=[]
    for name in names:
        r=get(name,2020,experiment='march'); c=cases[r['case']]
        dead=[a for a in c['accounts'] if not a['alive'] and a['died_at'].startswith('2026-03')]
        dates=Counter(a['died_at'][:10] for a in dead)
        snap=next((s for s in c['snapshots'] if s['at']=='2026-03-01T00:00:00'),None)
        timing=', '.join(f'{day[-2:]}: {n}' for day,n in sorted(dates.items())) or 'none'
        capital=snap['total_positive_equity'] if snap else 0
        lines.append(f'| {name} | {timing} | {max(dates.values(),default=0)} | ${capital:,.2f} |')
    for c in cases.values():
        if c['row']['experiment']=='march':
            for a in c['accounts']:
                if not a['alive'] and a['died_at'].startswith('2026-03'):
                    march_records.append(dict(case=c['row']['case'],**{k:a[k] for k in (
                        'account_id','sleeve','rr','reserve','death_window','death_entry_at','died_at')}))
    write_csv(ROOT/'march_deaths.csv',march_records)
    lines+=['','## Intratrade-order sensitivity','',
        'Entries below show MAE-first → MFE-first. Each column is a within-policy paired replay.','',
        '| Arm | 2020 primary wipeouts | 2023 primary wipeouts | 2020 primary 20-day peak | 2023 primary 20-day peak | March cohort deaths |',
        '|---|---|---|---|---|---|']
    for name in names:
        cells=[]
        for year,key,experiment in [(2020,'book_wipeouts','primary'),(2023,'book_wipeouts','primary'),
            (2020,'possible_20d_death_cluster','primary'),(2023,'possible_20d_death_cluster','primary'),
            (2020,'march_cohort_deaths','march')]:
            cells.append(f'{get(name,year,experiment=experiment)[key]} → {get(name,year,experiment=experiment,order="mfe_first")[key]}')
        lines.append(f'| {name} | '+ ' | '.join(cells)+' |')
    lines+=['','## Homogeneous constituent controls','',
        '| RR | Primary operating wipeouts, 2020–2025 | Isolation deaths, 2020–2025 | March deaths, MAE-first |',
        '|---|---|---|---:|']
    for rr in spec['rr_values']:
        name=f'rr_{rr}'
        lines.append(f'| {rr} | {vector(name,"book_wipeouts")} | {vector(name,"deaths",phase="isolation")} | {get(name,2020,experiment="march")["march_cohort_deaths"]} |')
    lines+=['','## Interpretation boundaries','',
        '- Neither more labels nor more distinct balances establishes independent failures. Use portfolio loss clusters and empty duration.',
        '- Same-signal grouping uses originating window and entry. Recorded days use exit proxies; interval clusters are conservative bounds, not exact crossing times.',
        '- Twenty groups cannot guarantee twenty funded PAs. Assignment order can matter while the book is underfilled; reverse arms expose that sensitivity.',
        '- Equal mean reserve targets do not equalize realized retained capital, withdrawals or replacement funding. Uniform reserve endpoints are controls, not an optimization.',
        '- Do not compare the best constituent selected after seeing a period with a precommitted mixture as if both had been chosen prospectively.',
        '- RR tapes have small entry-set differences; signal_alignment.csv records them. Cash and evaluation supply retain historical assumptions.',
        '- These are overlapping historical experiments. Results do not establish a universally optimal count, reserve or RR setting.',
        '', 'Evidence: comparison.csv, deltas_vs_rr1.csv, constituent_comparisons.csv, contract.json, '
        'audit.json, independent_audit.json, signal_alignment.csv and cases/.','']
    (ROOT/'rr_followup__REPORT.generated.md').write_text('\n'.join(lines),encoding='utf-8')
    (ROOT/'report_manifest.json').write_text(json.dumps(dict(
        summarizer_sha256=sha256_file(Path(__file__)),report_sha256=sha256_file(ROOT/'rr_followup__REPORT.generated.md'),
        source_audit_sha256=sha256_file(ROOT/'audit.json')),indent=2)+'\n')
    print('Generated report for',len(rows),'runs')


if __name__=='__main__':
    main()
