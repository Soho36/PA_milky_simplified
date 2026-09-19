"""The comparison chain runs in two execution modes that must never mix."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import study_legacy_50k_operating as sim
import study_legacy_reserve_comparison as study

NON_BLOCKING_ROWS = ROOT/'results/comparisons/legacy_25k_vs_50k/reserve_by_policy/checkpoint.jsonl'
BLOCKED_ROWS = ROOT/'results/legacy_25k/blocked_optimization/checkpoint.jsonl'


def saved(path, match):
    for line in path.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if match(row):
            return row
    raise LookupError(match)


class ExecutionModeTests(unittest.TestCase):
    def test_missing_mode_means_non_blocking_and_unknown_modes_fail(self):
        self.assertEqual(sim.execution_of({}), 'non_blocking')
        self.assertEqual(sim.execution_of({'execution': 'blocking'}), 'blocking')
        with self.assertRaises(AssertionError):
            sim.execution_of({'execution': 'blocked'})

    def test_modes_write_to_separate_trees(self):
        a, b = (Path(sim.RESULT_ROOTS[m]) for m in ('non_blocking', 'blocking'))
        self.assertFalse(a.is_relative_to(b) or b.is_relative_to(a))
        self.assertIsNone(sim.ROUTINGS['non_blocking'])
        self.assertEqual(sim.ROUTINGS['blocking'].mode, 'blocked')

    def test_a_study_cannot_read_its_predecessor_from_the_other_tree(self):
        blocked = 'results/comparisons_blocking/legacy_25k_vs_50k/reserve_by_policy'
        plain = 'results/comparisons/legacy_25k_vs_50k/reserve_by_policy'
        self.assertEqual(sim.prior_folder({'execution': 'blocking', 'prior': blocked}, 'prior', plain),
                         (ROOT/blocked).resolve())
        self.assertEqual(sim.prior_folder({}, 'prior', plain), (ROOT/plain).resolve())
        with self.assertRaises(AssertionError):
            sim.prior_folder({'execution': 'blocking'}, 'prior', plain)
        with self.assertRaises(AssertionError):
            sim.prior_folder({'prior': blocked}, 'prior', plain)

    def test_blocked_controls_skip_other_seeds_and_detect_drift(self):
        def source(acq, seed=1, ongoing=10.0):
            return {'start_year': 2020, 'initial_accounts': seed, 'amount': 0, 'acquisition': acq,
                    'withdrawal': 'minimum', 'cadence': 'daily', 'headroom': 0, 'initial_cash': 1000,
                    'monthly_funding': 200, 'ongoing': ongoing, 'total': 10.0, 'accounts': 3,
                    'alive': 1, 'reserve': 25100.0, 'allocation_sha256': 'x'}
        ours = {k: source('monthly_one')[k] for k in ('ongoing', 'total', 'accounts', 'alive',
                                                      'reserve', 'allocation_sha256')}
        cache = {sim.job('legacy_25k', 1000, 200, a, 'minimum', 'daily', 0): ours
                 for a in ('monthly_one', 'weekly_one')}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'checkpoint.jsonl'
            spec = {'amount_rules': ['minimum'], 'blocked_controls': {
                'checkpoint': str(path), 'product': 'legacy_25k',
                'acquisitions': ['monthly_one'], 'minimum_matches': 1}}
            rows = [source('monthly_one'), source('monthly_one', seed=5, ongoing=99.0),
                    source('weekly_one', ongoing=99.0)]
            path.write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
            self.assertEqual(study.blocked_controls(cache, spec), 1)
            path.write_text(json.dumps(source('monthly_one', ongoing=11.0)), encoding='utf-8')
            with self.assertRaises(AssertionError):
                study.blocked_controls(cache, spec)

    @unittest.skipUnless(NON_BLOCKING_ROWS.exists() and BLOCKED_ROWS.exists(), 'saved results absent')
    def test_one_evaluator_reproduces_saved_rows_in_both_modes(self):
        job = ('legacy_25k', 1000, 200, 'monthly_current_slot_replacements', 'maximum', 'weekly', 0, False)
        try:
            sim.initialize('non_blocking')
            old = saved(NON_BLOCKING_ROWS, lambda r: tuple(r['job']) == job)
            # Byte-for-byte, as saved: the switch must not change non-blocking rows at all.
            self.assertEqual(json.dumps(sim.evaluate(job)), json.dumps(old))
            sim.initialize('blocking')
            row = sim.evaluate(job)
            old = saved(BLOCKED_ROWS, lambda r: r['job'] == [2020, 1000, 200, job[3], 1, 'maximum', 'weekly', 0, 0])
            for key in ('ongoing', 'total', 'accounts', 'alive', 'allocation_sha256', 'copies',
                        'signals_executed', 'signal_participation'):
                self.assertEqual(row[key], old[key], key)
        finally:
            sim.initialize('non_blocking')


if __name__ == '__main__':
    unittest.main()
