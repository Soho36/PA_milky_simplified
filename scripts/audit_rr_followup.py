"""Independently reconstruct follow-up death clusters from saved account records."""
from bisect import bisect_left
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date, datetime
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import load_trades
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from audit_rr_diversification import interval_counts


def audit_case(evidence, lookup, dates):
    row=evidence['row']; accounts=evidence['accounts']; definitions=evidence['definitions']
    dead=[a for a in accounts if not a['alive']]
    assert len(accounts)==row['accounts'] and len(dead)==row['deaths']
    assert len(accounts)-len(dead)==row['alive']
    for snapshot in evidence['snapshots']:
        if 'accounts' not in snapshot:
            continue
        heads=Counter(a['headroom'] for a in snapshot['accounts'])
        n=len(snapshot['accounts'])
        assert n==snapshot['alive']
        assert len(heads)==snapshot['distinct_headrooms']
        assert max(heads.values())==snapshot['largest_equal_headroom']
        assert round(n*n/sum(v*v for v in heads.values()),6)==snapshot['effective_headroom_groups']
        assert round(sum(a['headroom'] for a in snapshot['accounts']),2)==snapshot['total_headroom']
    assert sum(a['trades'] for a in accounts)==row['copies']
    assert round(sum(a['received_payouts'] for a in accounts),2)==row['receipts']
    assert round(row['receipts']-row['total_costs'],2)==row['net_operating_cash']
    for account in accounts:
        definition=definitions[account['sleeve']]
        assert account['rr']==definition['rr'] and account['reserve']==definition['reserve']
    # Replay assignment from activation order and contemporaneous living groups.
    live_counts=Counter(); assigned=[]
    for account in accounts:
        live_counts=Counter(a['sleeve'] for a in assigned
            if a['alive'] or a['died_at']>account['activated_at'])
        expected=min(range(len(definitions)),key=lambda g:live_counts[g])
        assert account['sleeve']==expected,(row['case'],account['account_id'])
        assigned.append(account)
    signals=defaultdict(Counter); days=defaultdict(Counter)
    for account in dead:
        trade=lookup[account['death_trade_key']]
        assert trade.entry_at.isoformat()==account['death_entry_at']
        assert trade.exit_at.isoformat()==account['died_at']
        assert trade.window_id==account['death_window']
        signals[(account['death_window'],account['death_entry_at'])][account['sleeve']]+=1
        days[account['died_at'][:10]][account['sleeve']]+=1
    assert {k:{str(g):n for g,n in v.items()} for k,v in days.items()}==evidence['day_losses']
    assert max((sum(g.values()) for g in signals.values()),default=0)==row['max_same_signal_deaths']
    assert sum(sum(g.values())>1 for g in signals.values())==row['same_signal_multi_death_events']
    assert max((n for g in signals.values() for n in g.values()),default=0)==row['largest_within_sleeve_signal_loss']
    assert max(map(len,signals.values()),default=0)==row['max_sleeves_lost_same_signal']
    assert sum(len(g)>1 for g in signals.values())==row['multi_sleeve_signal_events']
    assert max(map(len,days.values()),default=0)==row['max_sleeves_lost_same_day']
    assert sum(len(g)>1 for g in days.values())==row['multi_sleeve_day_events']
    assert len(signals)==len(evidence['signal_losses'])
    full=events=0
    for saved in evidence['signal_losses']:
        losses=signals[(saved['window'],saved['entry'])]
        assert {str(g):n for g,n in losses.items()}==saved['deaths']
        for group,n in losses.items():
            copiers=saved['copiers'][str(group)]
            assert n<=copiers
            events+=1; full+=n==copiers
    assert events==row['sleeve_loss_events'] and full==row['full_copier_sleeve_loss_events']
    size=len(dates)
    born=[bisect_left(dates,date.fromisoformat(a['activated_at'][:10])) for a in accounts]
    died=[bisect_left(dates,date.fromisoformat(a['died_at'][:10])) if not a['alive'] else size for a in accounts]
    entry=[bisect_left(dates,date.fromisoformat(a['death_entry_at'][:10])) if not a['alive'] else size for a in accounts]
    population=interval_counts(size,zip(born,died))
    for width in (1,5,20):
        losses=interval_counts(size,[(max(b,d-width+1),d) for b,d in zip(born,died) if d<size])
        raw=interval_counts(size,[(d-width+1,d) for d in died if d<size])
        possible=interval_counts(size,[(e-width+1,d) for e,d in zip(entry,died) if d<size])
        fractions=[lost/n if n else 0 for lost,n in zip(losses,population)]
        assert max(losses,default=0)==row[f'worst_{width}d_cohort_deaths']
        assert round(max(fractions,default=0),6)==row[f'worst_{width}d_fraction']
        assert max(raw,default=0)==row[f'peak_{width}d_replacement_demand']
        assert max(possible,default=0)==row[f'possible_{width}d_death_cluster']
        episodes=i=0
        while i<size:
            if population[i]>=5 and fractions[i]>=.5:
                episodes+=1; i+=width
            else:
                i+=1
        assert episodes==row[f'half_loss_{width}d_episodes_min5']
    # Independent piecewise-constant account-count reconstruction.
    changes=Counter()
    for a in accounts:
        changes[datetime.fromisoformat(a['activated_at'])]+=1
        if not a['alive']: changes[datetime.fromisoformat(a['died_at'])]-=1
    end=max(t.exit_at for t in lookup.values() if t.entry_at.year>=row['start_year'])
    live=wipeouts=0; intervals=[]; last=None; started=False
    for at,delta in sorted(changes.items()):
        if at>end: continue
        if started and live==0 and last is not None: intervals.append((at-last).total_seconds()/86400)
        after=live+delta
        if live>0 and after==0: wipeouts+=1
        started=started or after>0
        live=after; last=at
    if started and live==0: intervals.append((end-last).total_seconds()/86400)
    assert wipeouts==row['book_wipeouts']
    assert round(sum(intervals),4)==row['days_empty_after_first_activation']
    march='2026-03-01T00:00:00'; april='2026-04-01T00:00:00'
    cohort=[a for a in accounts if a['activated_at']<=march and (a['alive'] or a['died_at']>=march)]
    assert len(cohort)==row['march1_alive']
    assert sum(not a['alive'] and a['died_at']<april for a in cohort)==row['march_cohort_deaths']
    assert sum(march<=a['died_at']<april for a in dead)==row['march_total_deaths']
    assert sum(a['activated_at']<april and (a['alive'] or a['died_at']>=april) for a in accounts)==row['march31_alive']
    if row['phase']=='isolation':
        assert len(accounts)==20 and len({a['activated_at'] for a in accounts})==1
        assert all(n==20//len(definitions) for n in Counter(a['sleeve'] for a in accounts).values())
    else:
        assert evidence['acquisition']['cash_identity_residual_usd']==0
        assert evidence['acquisition']['net_cash_created_usd']==row['net_operating_cash']
    return len(dead)


def main():
    root=PROJECT_ROOT/'results/legacy_25k/rr_followup'
    contract=json.loads((root/'contract.json').read_text())
    assert engine_digest()==contract['engine']
    for file,digest in contract['code'].items(): assert sha256_file(PROJECT_ROOT/file)==digest
    assert sha256_file(PROJECT_ROOT/'config/tape_coverage.json')==contract['coverage_sha256']
    config=load_config(PROJECT_ROOT/contract['parent_spec']['scenario'])
    tapes={rr:load_trades(config.sweeps_root,risk_reward=rr) for rr in contract['spec']['rr_values']}
    for rr in tapes: assert input_digest(replace(config,risk_reward=rr))==contract['inputs'][rr]
    reference={(t.window_id,t.entry_at):t for t in tapes['1.00']}
    alignment=[]
    for rr,tape in tapes.items():
        observed={(t.window_id,t.entry_at):t for t in tape}
        common=reference.keys() & observed.keys()
        differences=[dict(window=k[0],entry=k[1].isoformat(),rr1_pnl=reference[k].gross_pnl_usd,
                          variant_pnl=observed[k].gross_pnl_usd) for k in sorted(common)
                     if reference[k].gross_pnl_usd<0 and observed[k].gross_pnl_usd<0
                     and reference[k].gross_pnl_usd!=observed[k].gross_pnl_usd]
        alignment.append(dict(rr=rr,shared_negative_outcome_differences=differences,
            missing=[f'{w}@{at.isoformat()}' for w,at in sorted(reference.keys()-observed.keys())],
            extra=[f'{w}@{at.isoformat()}' for w,at in sorted(observed.keys()-reference.keys())]))
    (root/'source_alignment_details.json').write_text(json.dumps(alignment,indent=2)+'\n')
    lookup={t.trade_key:t for tape in tapes.values() for t in tape}
    calendars={year:sorted({v.date() for t in lookup.values() if t.entry_at.year>=year for v in (t.entry_at,t.exit_at)})
               for year in contract['spec']['starts']}
    manifest=json.loads((root/'audit.json').read_text())
    assert sha256_file(root/'contract.json')==manifest['contract_sha256']
    deaths=0; cases={}
    for name,digest in manifest['case_sha256'].items():
        path=root/'cases'/f'{name}.json'
        assert sha256_file(path)==digest
        evidence=json.loads(path.read_text())
        cases[name]=evidence
        try:
            deaths+=audit_case(evidence,lookup,calendars[evidence['row']['start_year']])
        except AssertionError:
            print('FAILED',name,flush=True)
            raise
    assert len(manifest['case_sha256'])==manifest['runs']
    reverse_pairs=0
    for year in contract['spec']['starts']:
        for arm in ('grid20','ladder20'):
            prefix=f'primary__isolation__{year}__mae_first__'
            forward=cases[prefix+arm]; reverse=cases[prefix+arm+'_reverse']
            for key in ('net_operating_cash','receipts','total_costs','copies','deaths','alive',
                        'max_same_signal_deaths','possible_20d_death_cluster','book_wipeouts'):
                assert forward['row'][key]==reverse['row'][key]
            def outcomes(case):
                return Counter((a['rr'],a['reserve'],a['died_at'],a['ending_balance'],a['received_payouts'])
                               for a in case['accounts'])
            assert outcomes(forward)==outcomes(reverse)
            reverse_pairs+=1
    result=dict(runs=manifest['runs'],deaths_reconciled=deaths,assignments_reconstructed=True,
        within_and_cross_sleeve_deaths_reconstructed=True,rolling_and_interval_metrics_reconstructed=True,
        wipeout_durations_reconstructed=True,march_cohorts_reconstructed=True,source_and_case_hashes_match=True,
        isolation_assignment_order_pairs_matched=reverse_pairs,
        auditor_sha256=sha256_file(Path(__file__)))
    (root/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
