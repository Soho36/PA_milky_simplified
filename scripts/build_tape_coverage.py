"""Regenerate config/tape_coverage.json from the reference sweep exports.

The coverage manifest is the committed record of how far each hourly window's
tape reaches, measured at one reference risk/reward. `1_sweeps/` is not
committed, so without this file a truncated export is undetectable: a run that
died early carries stats generated from the same short run, so counts and P&L
sums reconcile and the tape loads clean.

Run this only when the exports legitimately change (a longer history, a new
strategy), and say so in the commit. Never run it to silence a failure.
"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import CONFIG_ROOT, load_config
from pa_milky.loader import COVERAGE_PATH, WINDOWS, load_trades

REFERENCE_RISK_REWARD = '1.00'
STRATEGIES = ('RR', 'GG')
TOLERANCE_DAYS = 7


def measure(sweeps_root, strategy, risk_reward=REFERENCE_RISK_REWARD):
    trades = load_trades(sweeps_root, strategy=strategy, risk_reward=risk_reward,
                         check_coverage=False)
    per_window = {}
    for window in WINDOWS:
        rows = [t for t in trades if t.window_id == window]
        per_window[window] = {
            'first_entry': min(t.entry_at for t in rows).isoformat(),
            'last_exit': max(t.exit_at for t in rows).isoformat(),
            'trades': len(rows),
        }
    return per_window


def build(sweeps_root):
    return {
        'schema': 'pa_milky_simplified.tape_coverage.v1',
        'purpose': (
            'How far each hourly window reaches at risk_reward '
            f'{REFERENCE_RISK_REWARD}. loader.load_trades requires every window of every '
            'tape to reach its last_exit here, within tolerance_days. A window that stops '
            'short means the MT5 test ended early -- typically the test account was wiped, '
            'which truncates the export at the worst moment and flatters the setting. '
            'Regenerate with scripts/build_tape_coverage.py only when the exports '
            'legitimately change.'),
        'reference_risk_reward': REFERENCE_RISK_REWARD,
        'tolerance_days': TOLERANCE_DAYS,
        'measured_utc': None,
        'strategies': {s: measure(sweeps_root, s) for s in STRATEGIES},
    }


def main():
    from datetime import datetime, timezone
    sweeps_root = load_config().sweeps_root
    payload = build(sweeps_root)
    payload['measured_utc'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    COVERAGE_PATH.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    total = sum(w['trades'] for s in payload['strategies'].values() for w in s.values())
    print(f'wrote {COVERAGE_PATH.relative_to(CONFIG_ROOT.parent)}: '
          f'{len(payload["strategies"])} strategies, {len(WINDOWS)} windows each, '
          f'{total} reference trades')
    for name, windows in payload['strategies'].items():
        ends = sorted(w['last_exit'] for w in windows.values())
        print(f'  {name}: last exits {ends[0][:10]} .. {ends[-1][:10]}')


if __name__ == '__main__':
    main()
