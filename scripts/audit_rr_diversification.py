"""Independently reconcile saved RR mortality metrics and pinned study inputs."""
from bisect import bisect_left
from collections import Counter
from dataclasses import replace
from datetime import date, datetime
from itertools import accumulate
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import load_trades
from pa_milky.provenance import engine_digest, input_digest, sha256_file


def interval_counts(size, ranges):
    change=[0]*(size+1)
    for left,right in ranges:
        if left<=right and left<size and right>=0:
            change[max(0,left)]+=1
            change[min(size,right+1)]-=1
    return list(accumulate(change))[:size]


def main():
    root=PROJECT_ROOT/'results/legacy_25k/rr_diversification'
    contract=json.loads((root/'contract.json').read_text())
    spec=contract['spec']
    config=load_config(PROJECT_ROOT/spec['scenario'])
    assert contract['engine']==engine_digest()
    assert contract['runner_sha256']==sha256_file(PROJECT_ROOT/'scripts/study_rr_diversification.py')
    assert contract['coverage_sha256']==sha256_file(PROJECT_ROOT/'config/tape_coverage.json')
    tapes={rr:load_trades(config.sweeps_root,risk_reward=rr) for rr in spec['rr_values']}
    for rr in tapes:
        assert input_digest(replace(config,risk_reward=rr))==contract['inputs'][rr]
    lookup={t.trade_key:t for tape in tapes.values() for t in tape}
    audit=json.loads((root/'audit.json').read_text())
    assert audit['contract_sha256']==sha256_file(root/'contract.json')
    total_deaths=0
    checked=0
    for name,digest in audit['case_sha256'].items():
        path=root/'cases'/f'{name}.json'
        assert sha256_file(path)==digest,path
        evidence=json.loads(path.read_text()); row=evidence['row']; accounts=evidence['accounts']
        assert row['accounts']==len(accounts)
        dead=[a for a in accounts if not a['alive']]
        assert row['deaths']==len(dead) and row['alive']==len(accounts)-len(dead)
        assert sum(a['trades'] for a in accounts)==row['copies']
        assert round(sum(a['received_payouts'] for a in accounts),2)==row['receipts']
        assert round(row['receipts']-row['total_costs'],2)==row['net_operating_cash']
        assert all(a['rr'] in row['weights'] for a in accounts)
        assert Counter(a['rr'] for a in dead)==row['rr_deaths']
        for account in dead:
            trade=lookup[account['death_trade_key']]
            assert trade.entry_at.isoformat()==account['death_entry_at']
            assert trade.exit_at.isoformat()==account['died_at']
            assert trade.window_id==account['death_window']
        same=Counter((a['death_window'],a['death_entry_at']) for a in dead)
        assert max(same.values(),default=0)==row['max_same_signal_deaths']
        assert sum(n>1 for n in same.values())==row['same_signal_multi_death_events']
        dates=sorted({v.date() for t in lookup.values() if t.entry_at.year>=row['start_year']
                      for v in (t.entry_at,t.exit_at)})
        size=len(dates)
        born=[bisect_left(dates,date.fromisoformat(a['activated_at'][:10])) for a in accounts]
        died=[bisect_left(dates,date.fromisoformat(a['died_at'][:10])) if not a['alive'] else size
              for a in accounts]
        entry=[bisect_left(dates,date.fromisoformat(a['death_entry_at'][:10])) if not a['alive'] else size
               for a in accounts]
        population=interval_counts(size,zip(born,died))
        for width in (1,5,20):
            losses=interval_counts(size,[(max(b,d-width+1),d) for b,d in zip(born,died) if d<size])
            raw=interval_counts(size,[(d-width+1,d) for d in died if d<size])
            possible=interval_counts(size,[(e-width+1,d) for e,d in zip(entry,died) if d<size])
            fractions=[lost/n if n else 0 for lost,n in zip(losses,population)]
            assert max(losses,default=0)==row[f'worst_{width}d_cohort_deaths'],name
            assert round(max(fractions,default=0),6)==row[f'worst_{width}d_fraction'],name
            assert max(raw,default=0)==row[f'peak_{width}d_replacement_demand'],name
            assert max(possible,default=0)==row[f'possible_{width}d_death_cluster'],name
            episodes=0; i=0
            while i<size:
                if population[i]>=5 and fractions[i]>=.5:
                    episodes+=1; i+=width
                else:
                    i+=1
            assert episodes==row[f'half_loss_{width}d_episodes_min5'],name
        if row['phase']=='isolation':
            assert len(accounts)==spec['isolation_accounts']
            assert len({a['activated_at'] for a in accounts})==1
            assert row['total_costs']==len(accounts)*config.purchase_fee_usd
        else:
            ledger=evidence['acquisition']
            assert ledger['cash_identity_residual_usd']==0
            assert ledger['net_cash_created_usd']==row['net_operating_cash']
        total_deaths+=len(dead); checked+=1
    assert checked==audit['runs']
    result={'runs':checked,'death_records_reconciled':total_deaths,
            'rolling_cohorts_independently_reconstructed':True,
            'interval_bounds_independently_reconstructed':True,
            'source_hashes_match':True,'case_hashes_match':True}
    (root/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
