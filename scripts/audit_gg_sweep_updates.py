"""Audit the effective full GG grid, then optionally install two backed-up windows."""
import argparse,csv,json,math,shutil,sys
from dataclasses import replace
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT,load_config
from pa_milky.loader import WINDOWS,STATS_COLUMNS,SOURCE_TIME_FORMAT,read_coverage,load_trades
from pa_milky.provenance import sha256_file,input_digest,_digest_tree

BASE=PROJECT_ROOT/'1_sweeps'
UPDATES=PROJECT_ROOT/'1_sweeps_partial_updates_GG'
OUT=PROJECT_ROOT/'results/legacy_25k/rr_gg_input_update'
VALUES=[f'{i/100:.2f}' for i in range(50,351)]
CHANGED=('13-14','16-17')


def record_gg1_transition(report):
    """Only the unchanged GG r/r=1.00 tape is simulation-equivalent."""
    for r in report['replacement_pairs']:
        if r['rr']=='1.00':
            assert r['old_trades']==r['new_trades'] and set(r['stats_changed'])<={'sharpe'}
    files={}
    for window in WINDOWS:
        root=Path(report['backup']) if window in CHANGED else BASE
        for directory,suffix in [('GG',''),('GG_stats','_stats')]:
            files[f'{directory}/{window}']=root/directory/window/f'{window}_1.00{suffix}.csv'
        if window in CHANGED:
            assert sha256_file(files[f'GG/{window}'])==sha256_file(BASE/'GG'/window/f'{window}_1.00.csv')
    before=_digest_tree(files)
    after=input_digest(replace(load_config(),strategy='GG',risk_reward='1.00'))
    ledger_path=PROJECT_ROOT/'results/INPUT_CHANGES.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'transitions':[]}
    if not any(r['old_combined_sha256']==before['combined_sha256'] and r['new_combined_sha256']==after['combined_sha256'] for r in ledger['transitions']):
        ledger['transitions'].append(dict(old_combined_sha256=before['combined_sha256'],new_combined_sha256=after['combined_sha256'],
            simulation_equivalent=True,reason='GG r/r=1.00 trade bytes unchanged; only unused MT5 Sharpe statistics changed in windows 13-14 and 16-17. Other GG r/r replacements are not declared equivalent.',
            evidence='results/legacy_25k/rr_gg_input_update/input_update.json',backup=report['backup']))
        ledger_path.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
    report.update(gg1_input_digest_before=before,gg1_input_digest_after=after,
                  gg1_simulation_equivalent=True,auditor_sha256=sha256_file(Path(__file__)))


def read_pair(root,window,rr,strict=True):
    trade=root/'GG'/window/f'{window}_{rr}.csv'
    stat=root/'GG_stats'/window/f'{window}_{rr}_stats.csv'
    with trade.open(encoding='utf-16',newline='') as f:
        rows=[r for r in csv.reader(f,delimiter='\t') if any(x.strip() for x in r)]
    with stat.open(encoding='utf-16',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t');assert tuple(reader.fieldnames)==STATS_COLUMNS,stat
        stats=list(reader)
    assert len(stats)==1,stat
    s=stats[0]
    if strict:
        assert rows and all(len(r)==7 for r in rows),trade
        assert s['run_tag']==window and math.isclose(float(s['risk_reward']),float(rr),rel_tol=0,abs_tol=1e-12),stat
        assert int(s['trades'])==len(rows),f'count mismatch: {trade}'
        pnl=[Decimal(r[5]) for r in rows]
        assert sum(pnl)==Decimal(s['net_profit']),f'net mismatch: {trade}'
        assert sum(x for x in pnl if x>0)==Decimal(s['gross_profit']),f'gross gain mismatch: {trade}'
        assert sum(x for x in pnl if x<0)==Decimal(s['gross_loss']),f'gross loss mismatch: {trade}'
        assert len({r[0] for r in rows})==len(rows)==len({r[1] for r in rows}),f'duplicate: {trade}'
        for r in rows:
            int(r[0]);entry=datetime.strptime(r[1],SOURCE_TIME_FORMAT);exit=datetime.strptime(r[2],SOURCE_TIME_FORMAT)
            numbers=list(map(Decimal,r[3:]))
            assert all(x.is_finite() for x in numbers),trade
            mae,mfe,p,candle=numbers
            assert exit>=entry and candle>0 and mae<=p<=mfe and mfe>=0,trade
    return rows,s,trade,stat


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    evidence=OUT/'input_update.json'
    if evidence.exists() and json.loads(evidence.read_text()).get('applied'):
        prior=json.loads(evidence.read_text())
        for r in prior['files']:
            assert sha256_file(BASE/r['relative'])==r['new_sha256']
            assert sha256_file(Path(prior['backup'])/r['relative'])==r['old_sha256']
        record_gg1_transition(prior)
        evidence.write_text(json.dumps(prior,indent=2)+'\n')
        print('Installed GG update and original backups verified; no additional mutation.');return
    assert {p.name for p in (UPDATES/'GG').iterdir() if p.is_dir()}==set(CHANGED)
    assert {p.name for p in (UPDATES/'GG_stats').iterdir() if p.is_dir()}==set(CHANGED)
    files=[];run_ids=set()
    for window in CHANGED:
        old=json.loads((BASE/'GG'/window/'_manifest.json').read_text())
        new=json.loads((UPDATES/'GG'/window/'_manifest.json').read_text())
        assert new['complete'] and new['files_collected']==new['expected']==301
        for k in ('strategy','expert','symbol','period','from','to','model','rr_start','rr_stop','rr_step'):
            assert old[k]==new[k],(window,k)
        assert new['strategy']=='GG'
        run_ids.add(new['run_id'])
        for directory,suffix in [('GG',''),('GG_stats','_stats')]:
            names={p.name for p in (UPDATES/directory/window).glob('*.csv')}
            assert names=={f'{window}_{rr}{suffix}.csv' for rr in VALUES},(directory,window)
        paths=[p for directory in ('GG','GG_stats') for p in (UPDATES/directory/window).iterdir() if p.is_file()]
        for p in paths:
            relative=p.relative_to(UPDATES).as_posix()
            assert (BASE/relative).exists(),relative
            files.append(dict(relative=relative,old_sha256=sha256_file(BASE/relative),new_sha256=sha256_file(p)))
    assert len(run_ids)==1
    coverage=read_coverage();records=[];count=0;problems=[]
    for window in WINDOWS:
        root=UPDATES if window in CHANGED else BASE
        for rr in VALUES:
            rows,stats,trade,stat=read_pair(root,window,rr)
            last=datetime.strptime(max(r[2] for r in rows),SOURCE_TIME_FORMAT)
            required=datetime.fromisoformat(coverage['strategies']['GG'][window]['last_exit'])
            assert (required-last).total_seconds()/86400<=coverage['tolerance_days'],f'truncated: {trade}'
            count+=1
            if window in CHANGED:
                old,oldstats,_,_=read_pair(BASE,window,rr,strict=False)
                newmap={r[1]:r[1:] for r in rows}
                differences=[r for r in old if newmap.get(r[1])!=r[1:]]
                record=dict(window=window,rr=rr,old_trades=len(old),new_trades=len(rows),
                    old_last_exit=max(r[2] for r in old),new_last_exit=max(r[2] for r in rows),
                    historical_value_differences=len(differences),
                    stats_changed=[k for k in stats if stats[k]!=oldstats[k]])
                records.append(record)
                if differences:problems.append(dict(window=window,rr=rr,old_rows=differences[:5]))
        print(f'validated GG {window}: 301 complete trade/stat pairs',flush=True)
    report=dict(schema='gg_sweep_update.v1',checked_utc=datetime.now(timezone.utc).isoformat(),applied=False,
        effective_pairs_checked=count,updated_windows=list(CHANGED),replacement_pairs=records,files=files,
        extended_runs=sum(r['new_trades']>r['old_trades'] for r in records),history_differences=problems,
        coverage_sha256=sha256_file(PROJECT_ROOT/'config/tape_coverage.json'))
    evidence.write_text(json.dumps(report,indent=2)+'\n')
    assert not problems,'Historical trade values differ; see audit evidence before applying.'
    if args.apply:
        rr_before=input_digest(load_config())
        backup=(PROJECT_ROOT/'outputs/sweep_backups'/('GG_'+next(iter(run_ids)))).resolve()
        assert backup.is_relative_to((PROJECT_ROOT/'outputs/sweep_backups').resolve())
        for r in files:
            rel=Path(r['relative']);destination=(BASE/rel).resolve();source=(UPDATES/rel).resolve();saved=(backup/rel).resolve()
            assert destination.is_relative_to(BASE.resolve()) and source.is_relative_to(UPDATES.resolve()) and saved.is_relative_to(backup)
            assert sha256_file(destination)==r['old_sha256'] and sha256_file(source)==r['new_sha256']
            saved.parent.mkdir(parents=True,exist_ok=True)
            if saved.exists():assert sha256_file(saved)==r['old_sha256']
            else:shutil.copy2(destination,saved)
        installed=[]
        try:
            for r in files:
                relative=r['relative'];installed.append(relative)
                shutil.copy2(UPDATES/relative,BASE/relative)
                assert sha256_file(BASE/relative)==r['new_sha256']
            for rr in ['0.50','0.75','1.00','1.25','1.50','1.75','2.00','2.25','2.50','2.75','3.00','3.25','3.50']:
                load_trades(BASE,strategy='GG',risk_reward=rr)
            assert input_digest(load_config())==rr_before,'Unrelated RR inputs changed'
        except BaseException:
            for relative in installed:shutil.copy2(backup/relative,BASE/relative)
            raise
        report.update(applied=True,backup=str(backup),installed_files=len(files),rr_inputs_unchanged=True,
            source_staging_retained=True,post_install_13_coarse_tapes_loaded=True)
        record_gg1_transition(report)
        evidence.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['applied','effective_pairs_checked','extended_runs']}))


if __name__=='__main__':main()
