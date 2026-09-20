"""Validate the RR 16-17 replacement and, explicitly, install it with a backup."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import WINDOWS, STATS_COLUMNS, SOURCE_TIME_FORMAT, read_coverage
from pa_milky.provenance import input_digest, sha256_file

VALUES = [f'{n / 100:.2f}' for n in range(50, 351)]
OUT = PROJECT_ROOT / 'results/legacy_25k/rr_diversification'


def read_pair(root, window, rr):
    path = root / 'RR' / window / f'{window}_{rr}.csv'
    statpath = root / 'RR_stats' / window / f'{window}_{rr}_stats.csv'
    with path.open(encoding='utf-16', newline='') as handle:
        rows = [r for r in csv.reader(handle, delimiter='\t') if any(x.strip() for x in r)]
    with statpath.open(encoding='utf-16', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        assert tuple(reader.fieldnames) == STATS_COLUMNS, statpath
        stats_rows = list(reader)
    assert len(stats_rows) == 1, statpath
    stats = stats_rows[0]
    assert rows and all(len(r) == 7 for r in rows), path
    assert int(stats['trades']) == len(rows), f'{path}: count mismatch'
    assert sum((Decimal(r[5]) for r in rows), Decimal(0)) == Decimal(stats['net_profit']), path
    assert stats['run_tag'] == window and math.isclose(float(stats['risk_reward']), float(rr)), path
    assert len({r[0] for r in rows}) == len(rows), f'{path}: duplicate ticket'
    assert len({r[1] for r in rows}) == len(rows), f'{path}: duplicate entry'
    assert all(r[1] <= r[2] for r in rows), f'{path}: reversed interval'
    assert all(all(Decimal(x).is_finite() for x in r[3:]) for r in rows), path
    assert all(Decimal(r[3]) <= Decimal(r[5]) <= Decimal(r[4]) and Decimal(r[4]) >= 0
               for r in rows), f'{path}: excursions do not bracket P&L'
    return rows, stats, path, statpath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    base = PROJECT_ROOT / '1_sweeps'
    updates = PROJECT_ROOT / '1_sweeps_partial_updates'
    existing = OUT / 'input_update.json'
    if existing.exists():
        prior = json.loads(existing.read_text())
        if prior.get('applied'):
            for row in prior['replacement_pairs']:
                for kind in ('trade', 'stats'):
                    relative = Path(row[f'{kind}_path'])
                    expected = row[f'new_{kind}_sha256']
                    assert sha256_file(base/relative) == expected, 'Installed inputs changed since the recorded update'
                    assert sha256_file(updates/relative) == expected, 'A new update needs a separate audit/backup record'
            print('The recorded replacement is already installed; all 602 file hashes verified. Original audit and backup preserved.')
            return
    coverage = read_coverage()
    before = input_digest(load_config())
    report = {'schema': 'rr_sweep_update.v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'applied': False, 'rr_values': VALUES, 'updated_window': '16-17', 'pairs_checked': 0,
              'replacement_pairs': [], 'input_digest_before_rr1': before}
    for window in WINDOWS:
        for rr in VALUES:
            root = updates if window == '16-17' else base
            rows, stats, path, statpath = read_pair(root, window, rr)
            last = datetime.strptime(max(r[2] for r in rows), SOURCE_TIME_FORMAT)
            required = datetime.fromisoformat(coverage['strategies']['RR'][window]['last_exit'])
            assert (required - last).total_seconds() / 86400 <= coverage['tolerance_days'], path
            report['pairs_checked'] += 1
            if window != '16-17':
                continue
            oldpath, oldstats = base / path.relative_to(updates), base / statpath.relative_to(updates)
            with oldpath.open(encoding='utf-16', newline='') as handle:
                oldrows = [r for r in csv.reader(handle, delimiter='\t') if any(x.strip() for x in r)]
            newmap = {r[1]: r[1:] for r in rows}
            assert all(newmap.get(r[1]) == r[1:] for r in oldrows), f'{path}: historical trades changed'
            with oldstats.open(encoding='utf-16', newline='') as handle:
                oldstat = next(csv.DictReader(handle, delimiter='\t'))
            changed_stats = {k: [oldstat[k], stats[k]] for k in stats if stats[k] != oldstat[k]}
            record = {'rr': rr, 'old_trades': len(oldrows), 'new_trades': len(rows),
                      'last_exit': last.isoformat(), 'existing_trades_unchanged': True,
                      'trade_path': path.relative_to(updates).as_posix(),
                      'stats_path': statpath.relative_to(updates).as_posix(),
                      'old_trade_sha256': sha256_file(oldpath), 'new_trade_sha256': sha256_file(path),
                      'old_stats_sha256': sha256_file(oldstats), 'new_stats_sha256': sha256_file(statpath),
                      'changed_stats': changed_stats}
            if rr == '1.00':
                assert record['old_trade_sha256'] == record['new_trade_sha256']
                assert set(changed_stats) <= {'sharpe'}, changed_stats
            report['replacement_pairs'].append(record)
        print(f'validated RR {window}: {len(VALUES)} pairs', flush=True)
    if args.apply:
        run_id = json.loads((updates/'RR/16-17/_manifest.json').read_text())['run_id']
        backup = PROJECT_ROOT / 'outputs' / 'sweep_backups' / run_id
        for record in report['replacement_pairs']:
            for kind in ('trade', 'stats'):
                relative = Path(record[f'{kind}_path'])
                destination, source, saved = base/relative, updates/relative, backup/relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                if saved.exists():
                    assert sha256_file(saved) == record[f'old_{kind}_sha256'], saved
                else:
                    shutil.copy2(destination, saved)
                shutil.copy2(source, destination)
                assert sha256_file(destination) == record[f'new_{kind}_sha256']
        manifest = Path('RR/16-17/_manifest.json')
        if (base/manifest).exists() and not (backup/manifest).exists():
            shutil.copy2(base/manifest, backup/manifest)
        shutil.copy2(updates/manifest, base/manifest)
        report.update(applied=True, backup=str(backup), input_digest_after_rr1=input_digest(load_config()))
        ledger_path = PROJECT_ROOT / 'results/INPUT_CHANGES.json'
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
            'purpose': 'Explicit input replacements with unchanged simulator-consumed values; original inputs remain backed up.',
            'transitions': []}
        ledger['transitions'].append({
            'old_combined_sha256': before['combined_sha256'],
            'new_combined_sha256': report['input_digest_after_rr1']['combined_sha256'],
            'simulation_equivalent': True,
            'reason': 'RR 1.00 trade bytes unchanged; only the MT5 Sharpe statistic changed after a larger test deposit. Loader/simulator do not consume Sharpe.',
            'evidence': 'results/legacy_25k/rr_diversification/input_update.json',
            'backup': str(backup),
        })
        ledger_path.write_text(json.dumps(ledger, indent=2)+'\n', encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'input_update.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pairs_checked': report['pairs_checked'], 'applied': report['applied'],
                      'extended_runs': sum(r['new_trades'] > r['old_trades'] for r in report['replacement_pairs'])}))


if __name__ == '__main__':
    main()
