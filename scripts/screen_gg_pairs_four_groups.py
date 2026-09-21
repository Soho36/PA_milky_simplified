"""Read-only GG-pair and 5/5/5/5 failure screen from audited RR/GG evidence."""
from collections import Counter
import csv,hashlib,json
from itertools import combinations
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
SOURCE=PROJECT/'results/legacy_25k/rr_gg_episodes'
OUT=SOURCE/'gg_pairs_four_groups'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    with (SOURCE/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def write(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    spec=dict(rr_groups=['RR:0.50','RR:2.50'],gg_values=[f'GG:{n/4:.2f}' for n in range(2,15)],
        seats_per_group=5,period_months=[1,3,6],budgets=[1500,6800],
        scope='All 78 GG pairs, plus each paired with fixed RR0.50/RR2.50; no policy or deployment simulation.',
        metrics='Separate individual GG failures, reciprocal unique periods, all-four failures and seat-loss distributions; no tuning.')
    specpath=OUT/'design.json'
    if specpath.exists():assert json.loads(specpath.read_text())==spec
    else:specpath.write_text(json.dumps(spec,indent=2)+'\n')
    manifest=json.loads((SOURCE/'manifest.json').read_text())
    for name in ('windows.csv','episode_membership.csv','continuous_summary.csv'):
        assert sha(SOURCE/name)==manifest['files'][name]
    windows=read('windows.csv');members=read('episode_membership.csv')
    results=[];episode_results=[];baseline=[];distributions=[];check_count=0
    gg_pairs=list(combinations(spec['gg_values'],2));rr_low,rr_high=spec['rr_groups']
    for months in spec['period_months']:
        for budget in spec['budgets']:
            rows=[r for r in windows if int(r['months'])==months and int(r['budget'])==budget]
            cases=sorted({r['case'] for r in rows})
            failed={arm:{r['case'] for r in rows if r['rr']==arm and r['breached']=='True'}
                    for arm in [*spec['rr_groups'],*spec['gg_values']]}
            rrl=failed[rr_low];rrh=failed[rr_high];joint_rr=rrl&rrh
            base_losses=[10*(case in rrl)+10*(case in rrh) for case in cases]
            baseline.append(dict(months=months,budget=budget,periods=len(cases),
                all_dead=len(joint_rr),mean_seats_lost=sum(base_losses)/len(cases),
                at_least10=sum(n>=10 for n in base_losses),at_least15=sum(n>=15 for n in base_losses),
                all_dead_cases=';'.join(sorted(joint_rr))))
            for low,high in gg_pairs:
                l=failed[low];h=failed[high];all_four=joint_rr&l&h
                losses=[5*sum(case in failed[arm] for arm in (rr_low,rr_high,low,high)) for case in cases]
                assert sum(losses)==5*sum(len(failed[arm]) for arm in (rr_low,rr_high,low,high))
                assert sum(n==20 for n in losses)==len(all_four)
                check_count+=1
                counts=Counter(losses)
                r=dict(months=months,budget=budget,gg_lower=low,gg_higher=high,periods=len(cases),
                    gg_low_failed=len(l),gg_high_failed=len(h),gg_both=len(l&h),
                    gg_low_only=len(l-h),gg_high_only=len(h-l),
                    gg_jaccard=len(l&h)/len(l|h) if l|h else '',
                    gg_reciprocal=bool(l-h) and bool(h-l),
                    all_four_fail=len(all_four),rr_complete_loss_periods_rescued=len(joint_rr-all_four),
                    mean_seats_lost=sum(losses)/len(cases),
                    delta_mean_seats_lost=sum(losses)/len(cases)-sum(base_losses)/len(cases),
                    at_least10=sum(n>=10 for n in losses),at_least15=sum(n>=15 for n in losses),
                    all_four_cases=';'.join(sorted(all_four)),rescued_cases=';'.join(sorted(joint_rr-all_four)))
                results.append(r)
                distributions.append(dict(months=months,budget=budget,gg_lower=low,gg_higher=high,
                    **{f'quarters_or_periods_losing_{n}_seats':counts[n] for n in (0,5,10,15,20)}))
            for gap in (5,20,40):
                prefix=f'{months}m_b{budget}_g{gap}_'
                failure_episodes={arm:{r['episode'] for r in members if r['rr']==arm and r['episode'].startswith(prefix)}
                                  for arm in [*spec['rr_groups'],*spec['gg_values']]}
                rr_both=failure_episodes[rr_low]&failure_episodes[rr_high]
                for low,high in gg_pairs:
                    l=failure_episodes[low];h=failure_episodes[high];all_four=rr_both&l&h
                    episode_results.append(dict(months=months,budget=budget,gap=gap,gg_lower=low,gg_higher=high,
                        gg_shared=len(l&h),gg_low_only=len(l-h),gg_high_only=len(h-l),
                        gg_reciprocal=bool(l-h) and bool(h-l),
                        rr_both_episodes=len(rr_both),all_four_episodes=len(all_four),
                        rr_joint_episodes_rescued=len(rr_both-all_four)))
    for name,rows in [('pair_periods.csv',results),('pair_episodes.csv',episode_results),
                      ('rr_baseline.csv',baseline),('seat_loss_distributions.csv',distributions)]:write(name,rows)
    primary=[r for r in results if r['months']==3 and r['budget']==1500]
    ranked=sorted(primary,key=lambda r:(r['all_four_fail'],r['mean_seats_lost'],r['gg_lower'],r['gg_higher']))
    lines=['# GG pairs and the proposed five-account groups','',
        'This uses the existing audited historical paths. Accounts start identically, with '
        '$1,500 fixed headroom; no withdrawals, replacements or deployment sequence. Four '
        'different strategy/settings represent four synchronized groups of five accounts, '
        'not twenty independent outcomes. Failure totals below are by period end, not same-day losses.', '',
        '## Primary quarterly result','',
        f'All {len(primary)} distinct GG pairs were checked alongside fixed RR r/r 0.50 and 2.50. '
        f'The number of all-four-failed quarters ranges from {min(r["all_four_fail"] for r in primary)} '
        f'to {max(r["all_four_fail"] for r in primary)} out of 26. '
        f'{sum(r["rr_complete_loss_periods_rescued"]>0 for r in primary)} pairs rescue any quarter '
        'where both RR groups fail.', '',
        f'{sum(r["gg_reciprocal"] for r in primary)} of 78 GG pairs show GG-only failures '
        'on both sides in the quarterly test. Reciprocal GG-pair behavior alone does not '
        'establish that the GG groups protect against the RR groups.', '',
        '| GG settings added | GG lower failures | GG higher failures | GG both | Lower-only / higher-only | All four fail | Mean seats lost per quarter |',
        '|---|---:|---:|---:|---:|---:|---:|']
    chosen=ranked[:5]
    reciprocal=sorted((r for r in primary if r['gg_reciprocal']),key=lambda r:(r['gg_jaccard'],r['mean_seats_lost']))
    for r in reciprocal[:2]:
        if r not in chosen:chosen.append(r)
    for r in chosen:lines.append(f'| {r["gg_lower"]} + {r["gg_higher"]} | {r["gg_low_failed"]} | '
        f'{r["gg_high_failed"]} | {r["gg_both"]} | {r["gg_low_only"]} / {r["gg_high_only"]} | '
        f'{r["all_four_fail"]}/26 | {r["mean_seats_lost"]:.2f} |')
    b=next(r for r in baseline if r['months']==3 and r['budget']==1500)
    lines+=['',f'The 10 RR0.50 + 10 RR2.50 baseline loses an average of '
        f'{b["mean_seats_lost"]:.2f} seats per quarter and all 20 in {b["all_dead"]}/26 quarters. '
        f'Its complete-loss quarters are {b["all_dead_cases"]}. The lowest-mean-loss four-group '
        'row is selected on this same history; it is not an independent recommendation.', '',
        '## Complete-loss sensitivity','',
        '| Period length | RR-only baseline all-dead periods | Four-group minimum–maximum | GG pairs rescuing any RR all-dead period |',
        '|---|---:|---:|---:|']
    for months in (1,3,6):
        rs=[r for r in results if r['months']==months and r['budget']==1500]
        b=next(r for r in baseline if r['months']==months and r['budget']==1500)
        lines.append(f'| {months} months | {b["all_dead"]}/{b["periods"]} | '
            f'{min(r["all_four_fail"] for r in rs)}–{max(r["all_four_fail"] for r in rs)} | '
            f'{sum(r["rr_complete_loss_periods_rescued"]>0 for r in rs)} / 78 |')
    lines+=['','The full CSVs retain both budgets, all period lengths, grouping gaps and '
        '0/5/10/15/20-seat loss distributions. Do not interpret fewer full losses in one '
        'reset horizon as a general solution to synchronized deaths. Five-seat groups can '
        'reduce losses when only one group fails, while several groups can still fail together.', '',
        'The 20-account cap here only determines allocation weights. This is not a test '
        'of assembling or maintaining twenty live accounts under real purchase and withdrawal policies.', '',
        f'{check_count} portfolio loss totals independently agree with constituent-set counts. '
        'Source CSV hashes are verified against the earlier study. No source tapes were changed.', '']
    (OUT/'gg_pairs_four_groups__REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    audit=dict(source_manifest_sha256=sha(SOURCE/'manifest.json'),script_sha256=sha(Path(__file__)),
        checked_portfolios=check_count,files={p.name:sha(p) for p in OUT.iterdir() if p.name!='manifest.json'})
    (OUT/'manifest.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('\n'.join(lines[:17]))


if __name__=='__main__':main()
