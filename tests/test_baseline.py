"""Sealed baselines must still reproduce from today's engine.

This is the guard that makes the brick-by-brick method mean something. Brick 1
is the standard every later brick is measured against, so if a brick-2 change
silently moved a brick-1 number, this fails rather than the standard quietly
becoming whatever the code says today.
"""

from __future__ import annotations

import json
import unittest

from pa_milky.config import config_from_payload, to_payload
from pa_milky.provenance import BASELINE_ROOT, list_baselines, verify

from .support import BRICK1, BRICK2, IDEAL, RESULT1, TRADES


class TestConfigRoundTrip(unittest.TestCase):
    def test_a_config_survives_a_json_round_trip(self):
        # A sealed baseline carries its config as a payload. If that payload
        # did not rehydrate exactly, verification would be checking something
        # other than what was sealed.
        for config in (BRICK1, BRICK2):
            with self.subTest(brick=config.brick):
                self.assertEqual(config_from_payload(to_payload(config)), config)

    def test_a_legacy_payload_without_withdrawals_means_hold(self):
        # Brick 1 was sealed before withdrawals existed. Its flat payload has
        # no withdrawals block at all, and that has to keep meaning "hold".
        legacy = json.loads(
            (BASELINE_ROOT / "brick1_ideal_world" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )["config"]
        self.assertEqual(legacy["withdrawals"]["policy"], "none")
        self.assertFalse(config_from_payload(legacy).policy.enabled)
        # And a payload predating the block entirely still means hold.
        del legacy["withdrawals"]
        self.assertFalse(config_from_payload(legacy).policy.enabled)

    def test_a_legacy_payload_maps_onto_the_rulebook(self):
        # Brick 2's two v1 gates become minimum_balance and a safety net whose
        # encroachment allowance is the distance between them.
        legacy = json.loads(
            (BASELINE_ROOT / "brick2_monthly_100" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )["config"]
        config = config_from_payload(legacy)
        self.assertEqual(config.rulebook.active_keys, ("minimum_balance", "safety_net"))
        gate = config.rulebook.get("minimum_balance")
        net = config.rulebook.get("safety_net")
        self.assertEqual(gate.params["balance_usd"], 26_600.0)
        self.assertEqual(net.params["encroachment_allowance_usd"], 100.0)
        self.assertEqual(config.policy.amount_usd, 100.0)


class TestTheTwoConfigPathsAgree(unittest.TestCase):
    """The scenario schema must reproduce the brick it replaced, exactly."""

    def test_the_ideal_scenario_equals_sealed_brick_one(self):
        from pa_milky.simulator import run_book

        rerun = run_book(TRADES, IDEAL)
        self.assertEqual(len(rerun.alive), len(RESULT1.alive))
        self.assertEqual(rerun.copies_filled, RESULT1.copies_filled)
        self.assertEqual(rerun.total_withdrawn_usd, RESULT1.total_withdrawn_usd)
        self.assertEqual(
            [a.equity_profit_usd for a in rerun.accounts],
            [a.equity_profit_usd for a in RESULT1.accounts],
        )

    def test_the_ideal_scenario_switches_everything_off(self):
        self.assertEqual(IDEAL.rulebook.active_keys, ())
        self.assertFalse(IDEAL.policy.enabled)


class TestSealedBaselines(unittest.TestCase):
    def test_at_least_brick_one_is_sealed(self):
        self.assertIn("brick1_ideal_world", list_baselines())

    def test_every_sealed_baseline_still_reproduces(self):
        for name in list_baselines():
            with self.subTest(baseline=name):
                result = verify(name)
                self.assertTrue(result.ok, result.render())

    def test_brick_one_headline_is_what_the_study_reported(self):
        manifest = json.loads(
            (BASELINE_ROOT / "brick1_ideal_world" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            manifest["headline"],
            {
                "trades_loaded": 12_658,
                "copies_filled": 150_403,
                "accounts_opened": 79,
                "accounts_alive_at_end": 22,
                "accounts_dead": 57,
                "spent_on_accounts_usd": 15_800.0,
                "withdrawn_usd": 0.0,
                "owner_cash_position_usd": -15_800.0,
                "total_balance_usd": 1_038_099.10,
                "total_paper_profit_usd": 488_099.10,
            },
        )

    def test_the_sealed_config_is_embedded_not_referenced(self):
        # Editing config/ must not be able to rewrite a sealed result.
        manifest = json.loads(
            (BASELINE_ROOT / "brick1_ideal_world" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        config = config_from_payload(manifest["config"])
        self.assertFalse(config.policy.enabled)
        self.assertEqual(config.strategy, "RR")
        self.assertEqual(config.risk_reward, "1.00")
        self.assertEqual(config.commission_usd_per_mnq_round_turn, 1.05)
        self.assertEqual(config.path_order, "mae_first")

    def test_the_input_tape_is_pinned_by_hash(self):
        manifest = json.loads(
            (BASELINE_ROOT / "brick1_ideal_world" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["inputs"]["count"], 46)  # 23 windows + 23 stats
        self.assertEqual(len(manifest["inputs"]["combined_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
