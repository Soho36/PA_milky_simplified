"""A short export must be refused, not silently believed.

Per-window reconciliation against each ``_stats`` file cannot see a truncated
run: the stats come from the same short run, so counts and P&L agree. These
tests pin the separate coverage guard, and the margin it relies on.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import json
import unittest

from pa_milky.config import load_config
from pa_milky.loader import (
    COVERAGE_PATH,
    COVERAGE_SCHEMA,
    WINDOWS,
    coverage_shortfalls,
    load_trades,
    read_coverage,
)

CONFIG = load_config()
COVERAGE = read_coverage()


class TestCoverageManifest(unittest.TestCase):
    def test_manifest_is_committed_and_current(self):
        self.assertTrue(COVERAGE_PATH.is_file(), COVERAGE_PATH)
        self.assertEqual(COVERAGE["schema"], COVERAGE_SCHEMA)
        self.assertEqual(COVERAGE["reference_risk_reward"], "1.00")

    def test_every_window_of_every_strategy_is_pinned(self):
        for strategy, windows in COVERAGE["strategies"].items():
            self.assertEqual(set(windows), set(WINDOWS), strategy)
            for window, row in windows.items():
                self.assertGreater(row["trades"], 0, f"{strategy}/{window}")
                self.assertLess(
                    datetime.fromisoformat(row["first_entry"]),
                    datetime.fromisoformat(row["last_exit"]),
                    f"{strategy}/{window}",
                )

    def test_unsupported_schema_is_rejected(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            path.write_text(json.dumps({"schema": "something.else"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                read_coverage(path)

    def test_absent_manifest_reads_as_none_and_checks_nothing(self):
        from pathlib import Path

        self.assertIsNone(read_coverage(Path("nowhere") / "coverage.json"))
        self.assertEqual(coverage_shortfalls("RR", {"1-2": datetime(2020, 1, 1)}, None), [])


class TestShortfallDetection(unittest.TestCase):
    def setUp(self):
        self.reached = {
            window: datetime.fromisoformat(row["last_exit"])
            for window, row in COVERAGE["strategies"]["RR"].items()
        }

    def test_the_reference_itself_has_no_shortfall(self):
        self.assertEqual(coverage_shortfalls("RR", self.reached, COVERAGE), [])

    def test_a_window_cut_short_is_reported_with_its_gap(self):
        reached = dict(self.reached)
        reached["16-17"] -= timedelta(days=400)
        shortfalls = coverage_shortfalls("RR", reached, COVERAGE)
        self.assertEqual([row[0] for row in shortfalls], ["16-17"])
        self.assertAlmostEqual(shortfalls[0][3], 400.0, places=6)

    def test_tolerance_absorbs_a_different_exit_but_not_a_truncation(self):
        # A different risk/reward exits the same entries at different moments, so
        # the final trade may settle a little either side of the reference.
        tolerance = COVERAGE["tolerance_days"]
        inside = dict(self.reached)
        inside["5-6"] -= timedelta(days=tolerance)
        self.assertEqual(coverage_shortfalls("RR", inside, COVERAGE), [])
        outside = dict(self.reached)
        outside["5-6"] -= timedelta(days=tolerance + 1)
        self.assertEqual(len(coverage_shortfalls("RR", outside, COVERAGE)), 1)

    def test_ending_later_than_the_reference_is_fine(self):
        later = {w: t + timedelta(days=90) for w, t in self.reached.items()}
        self.assertEqual(coverage_shortfalls("RR", later, COVERAGE), [])

    def test_an_unmeasured_strategy_is_not_a_failure(self):
        self.assertEqual(coverage_shortfalls("ZZ", self.reached, COVERAGE), [])


class TestLoaderEnforcement(unittest.TestCase):
    def test_the_configured_tape_still_loads(self):
        trades = load_trades(
            CONFIG.sweeps_root, strategy=CONFIG.strategy, risk_reward=CONFIG.risk_reward
        )
        self.assertEqual(len(trades), CONFIG.expected_trades)

    def test_a_truncated_export_is_refused(self):
        # RR 2.50 stops in May 2022 for window 16-17: the MT5 test account was
        # wiped at about -$4,917 and the run ended there.
        with self.assertRaises(ValueError) as caught:
            load_trades(CONFIG.sweeps_root, strategy="RR", risk_reward="2.50")
        message = str(caught.exception)
        self.assertIn("16-17", message)
        self.assertIn("days short", message)
        self.assertIn("test deposit", message)

    def test_the_refused_tape_still_reconciles_against_its_own_stats(self):
        # The point of the guard: nothing else about this tape looks wrong.
        trades = load_trades(
            CONFIG.sweeps_root, strategy="RR", risk_reward="2.50", check_coverage=False
        )
        self.assertEqual(len(trades), 12090)
        self.assertEqual({t.window_id for t in trades}, set(WINDOWS))


if __name__ == "__main__":
    unittest.main()
