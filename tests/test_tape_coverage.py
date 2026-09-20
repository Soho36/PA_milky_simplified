"""A short export must be refused, not silently believed.

Per-window reconciliation against each ``_stats`` file cannot see a truncated
run: the stats come from the same short run, so counts and P&L agree. These
tests pin the separate coverage guard, and the margin it relies on.
"""

from __future__ import annotations

from copy import deepcopy
import csv
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pa_milky.config import load_config
from pa_milky.loader import (
    COVERAGE_PATH,
    COVERAGE_SCHEMA,
    SOURCE_TIME_FORMAT,
    STATS_COLUMNS,
    WINDOWS,
    coverage_shortfalls,
    load_tape,
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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            path.write_text(json.dumps({"schema": "something.else"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                read_coverage(path)

    def test_absent_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, "Missing tape coverage"):
                read_coverage(Path(tmp) / "coverage.json")

    def test_missing_reference_cannot_disable_shortfall_detection(self):
        with self.assertRaisesRegex(ValueError, "Missing tape coverage"):
            coverage_shortfalls("RR", {"1-2": datetime(2020, 1, 1)}, None)


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

    def test_an_unmeasured_strategy_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "strategy ZZ"):
            coverage_shortfalls("ZZ", self.reached, COVERAGE)

    def test_invalid_tolerance_cannot_disable_shortfall_detection(self):
        for tolerance in (float("nan"), float("inf"), -1):
            with self.subTest(tolerance=tolerance):
                coverage = deepcopy(COVERAGE)
                coverage["tolerance_days"] = tolerance
                with self.assertRaisesRegex(ValueError, "tolerance_days"):
                    coverage_shortfalls("RR", self.reached, coverage)


class TestLoaderEnforcement(unittest.TestCase):
    def test_the_configured_tape_still_loads(self):
        trades = load_trades(
            CONFIG.sweeps_root, strategy=CONFIG.strategy, risk_reward=CONFIG.risk_reward
        )
        self.assertEqual(len(trades), CONFIG.expected_trades)


class TestSyntheticCoverage(unittest.TestCase):
    """Coverage regressions independent of the real exports awaiting repair."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.coverage_path = self.root / "coverage.json"
        last_exit = datetime(2026, 7, 10, 12)
        self.coverage = {
            "schema": COVERAGE_SCHEMA,
            "reference_risk_reward": "1.00",
            "tolerance_days": 7,
            "strategies": {
                "RR": {w: {"last_exit": last_exit.isoformat()} for w in WINDOWS}
            },
        }
        self.write_coverage()
        self.rows = [
            ["1", "2020.01.02 10:00:00", "2020.01.02 11:00:00", "-1", "2", "2", "10"],
            ["2", (last_exit - timedelta(hours=1)).strftime(SOURCE_TIME_FORMAT),
             last_exit.strftime(SOURCE_TIME_FORMAT), "-1", "3", "3", "10"],
        ]
        for window in WINDOWS:
            self.write_window(window, self.rows)
        guard = patch("pa_milky.loader.COVERAGE_PATH", self.coverage_path)
        guard.start()
        self.addCleanup(guard.stop)

    def write_coverage(self):
        self.coverage_path.write_text(json.dumps(self.coverage), encoding="utf-8")

    def write_window(self, window, rows):
        trades_path = self.root / "RR" / window / f"{window}_2.50.csv"
        stats_path = self.root / "RR_stats" / window / f"{window}_2.50_stats.csv"
        trades_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        with trades_path.open("w", encoding="utf-16", newline="") as handle:
            csv.writer(handle, delimiter="\t").writerows(rows)
        stats = dict.fromkeys(STATS_COLUMNS, "0")
        stats.update(
            run_tag=window, risk_reward="2.50", trades=str(len(rows)),
            net_profit=str(sum((Decimal(row[5]) for row in rows), Decimal(0))),
        )
        with stats_path.open("w", encoding="utf-16", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=STATS_COLUMNS, delimiter="\t")
            writer.writeheader()
            writer.writerow(stats)

    def load(self, **kwargs):
        return load_trades(self.root, strategy="RR", risk_reward="2.50", **kwargs)

    def test_complete_exports_load(self):
        self.assertEqual(len(self.load()), 2 * len(WINDOWS))

    def test_a_truncated_export_is_refused(self):
        self.write_window("16-17", self.rows[:1])
        with self.assertRaises(ValueError) as caught:
            self.load()
        message = str(caught.exception)
        self.assertIn("16-17", message)
        self.assertIn("days short", message)
        self.assertIn("test deposit", message)

    def test_the_refused_tape_still_reconciles_against_its_own_stats(self):
        # The point of the guard: nothing else about this tape looks wrong.
        self.write_window("16-17", self.rows[:1])
        trades = self.load(check_coverage=False)
        self.assertEqual(len(trades), 2 * len(WINDOWS) - 1)
        self.assertEqual({t.window_id for t in trades}, set(WINDOWS))

    def test_an_empty_window_is_rejected_without_pinned_trade_counts(self):
        self.write_window("16-17", [])
        config = replace(CONFIG, sweeps_root=self.root, strategy="RR", risk_reward="2.50",
                         expected_trades=None, expected_windows=None)
        with self.assertRaisesRegex(ValueError, "no trades observed.*16-17"):
            load_tape(config)
        # Confirm the zero-count, zero-P&L stats reconcile independently.
        self.assertEqual(len(self.load(check_coverage=False)), 2 * (len(WINDOWS) - 1))

    def test_missing_manifest_is_rejected_unless_explicitly_bypassed(self):
        self.coverage_path.unlink()
        with self.assertRaisesRegex(FileNotFoundError, "Missing tape coverage"):
            self.load()
        self.assertEqual(len(self.load(check_coverage=False)), 2 * len(WINDOWS))

    def test_missing_strategy_pin_is_rejected(self):
        del self.coverage["strategies"]["RR"]
        self.write_coverage()
        with self.assertRaisesRegex(ValueError, "strategy RR"):
            self.load()

    def test_missing_window_pin_is_rejected(self):
        del self.coverage["strategies"]["RR"]["16-17"]
        self.write_coverage()
        with self.assertRaisesRegex(ValueError, "missing last_exit coverage pins.*16-17"):
            self.load()

    def test_missing_last_exit_pin_is_rejected(self):
        self.coverage["strategies"]["RR"]["16-17"] = {}
        self.write_coverage()
        with self.assertRaisesRegex(ValueError, "missing last_exit coverage pins.*16-17"):
            self.load()


if __name__ == "__main__":
    unittest.main()
