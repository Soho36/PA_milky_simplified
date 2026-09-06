"""Measuring a rule two ways, and telling blocked access from destroyed value."""

from __future__ import annotations

import dataclasses
import unittest

from pa_milky.ablation import (
    Arm,
    ablation_payload,
    best_over_cushions,
    cushion_grid,
    run_ablation,
    run_adapted_ablation,
)

from .support import FULL, TRADES

# One small grid, reused: the point is the method, not another full search.
# $29,600 is $4,500 of headroom, the level the consistency-free book prefers.
SMALL_GRID = [None, 27_100.0, 30_100.0]
REFINED_GRID = SMALL_GRID + [29_600.0]

# Every search in this module runs once, here. Each arm is a full pass over the
# tape, so recomputing them per test costs minutes.
BASELINE, ARMS = run_ablation(TRADES, FULL)
BY_RULE = {arm.rule: arm for arm in ARMS}
ADAPTED_SMALL = run_adapted_ablation(TRADES, FULL, levels=SMALL_GRID)
ADAPTED_REFINED = run_adapted_ablation(TRADES, FULL, levels=REFINED_GRID)
SMALL_DELTAS = {row["rule"]: row["delta_vs_best_usd"] for row in ADAPTED_SMALL["arms"]}
REFINED_DELTAS = {row["rule"]: row["delta_vs_best_usd"] for row in ADAPTED_REFINED["arms"]}


class TestCushionGrid(unittest.TestCase):
    def test_levels_are_headroom_above_the_frozen_floor(self):
        levels = cushion_grid(FULL, span_usd=1_500.0, step_usd=500.0)
        self.assertEqual(levels, [None, 25_100.0, 25_600.0, 26_100.0, 26_600.0])
        self.assertEqual(FULL.trailing_floor_balance_usd, 25_100.0)

    def test_the_headline_cushion_is_five_thousand_of_headroom(self):
        # $30,100 retained is $5,000 above the floor, not above the start.
        self.assertEqual(30_100.0 - FULL.trailing_floor_balance_usd, 5_000.0)
        self.assertEqual(30_000.0 - FULL.trailing_floor_balance_usd, 4_900.0)


class TestValueDecomposition(unittest.TestCase):
    """Pocket alone cannot say whether a rule blocked access or destroyed value."""

    baseline, arms, by_rule = BASELINE, ARMS, BY_RULE

    def test_value_is_pocket_plus_what_is_still_standing(self):
        for arm in [self.baseline, *self.arms]:
            self.assertAlmostEqual(
                arm.value_usd, arm.pocket_usd + arm.stranded_usd, places=2
            )

    def test_an_inert_rule_moves_neither_pocket_nor_value_nor_a_single_fate(self):
        for key in ("minimum_payout", "profit_split", "trading_days"):
            arm = self.by_rule[key]
            self.assertEqual(arm.pocket_usd, self.baseline.pocket_usd, key)
            self.assertEqual(arm.value_usd, self.baseline.value_usd, key)
            self.assertEqual(arm.fates_changed_against(self.baseline), 0, key)

    def test_consistencys_pocket_gain_exceeds_its_value_gain(self):
        # The arithmetic only. It was once read as "the rule mostly blocks
        # access, and the money was still sitting in the accounts" -- which a
        # per-account split disproves: every dollar of the gain, and every
        # dollar of the retained difference, lives in the seven accounts whose
        # fate changed. See TestWhereTheDeltaLives below.
        arm = self.by_rule["consistency"]
        gained_pocket = arm.pocket_usd - self.baseline.pocket_usd
        gained_value = arm.value_usd - self.baseline.value_usd
        self.assertGreater(gained_pocket, 0)
        self.assertGreater(gained_pocket, 2 * gained_value)

    def test_the_safety_net_destroys_value_when_removed_not_merely_access(self):
        # Removing it loses more value than pocket, and moves several fates:
        # that money was never earned, not merely left behind.
        arm = self.by_rule["safety_net"]
        lost_pocket = self.baseline.pocket_usd - arm.pocket_usd
        lost_value = self.baseline.value_usd - arm.value_usd
        self.assertGreater(lost_value, lost_pocket)
        self.assertGreater(arm.fates_changed_against(self.baseline), 0)

    def test_every_arm_reconciles_owner_cash(self):
        for arm in [self.baseline, *self.arms]:
            self.assertEqual(arm.economics.residual_usd, 0)
            self.assertEqual(arm.economics.bridge_against(
                self.baseline.economics)["residual_usd"], 0)

    def test_the_payload_carries_both_deltas_and_the_fate_count(self):
        payload = ablation_payload(self.baseline, self.arms)
        for row in payload["arms"]:
            self.assertIn("delta_pocket_usd", row)
            self.assertIn("delta_value_usd", row)
            self.assertIn("fates_changed", row)
            self.assertIn("withheld", row)


class TestWhereTheDeltaLives(unittest.TestCase):
    """For these selected rules on this fixed arm, cash deltas occur in
    changed-fate accounts. This is an empirical observation, not an invariant:
    profit split can change cash without changing any account fate.
    """

    @staticmethod
    def _split(rule: str):
        import dataclasses as dc

        from pa_milky.simulator import run_book

        base = run_book(TRADES, FULL)
        arm = run_book(TRADES, dc.replace(FULL, rulebook=FULL.rulebook.without(rule)))
        same = changed = 0.0
        for before, after in zip(base.accounts, arm.accounts):
            delta = after.received_usd - before.received_usd
            if (before.died_at, before.alive) == (after.died_at, after.alive):
                same += delta
            else:
                changed += delta
        return round(same, 2), round(changed, 2), arm.pocket_usd - base.pocket_usd

    def test_consistency_moves_no_cash_in_an_account_that_survives_the_same(self):
        same, changed, total = self._split("consistency")
        self.assertEqual(same, 0.0)
        self.assertAlmostEqual(changed, total, places=2)

    def test_nor_does_the_safety_net(self):
        same, changed, total = self._split("safety_net")
        self.assertEqual(same, 0.0)
        self.assertAlmostEqual(changed, total, places=2)


class TestFirmMoneyIsTwoMeasures(unittest.TestCase):
    """Booked deficits are distinct from gross payouts exceeding booked earnings."""

    def test_they_are_reported_separately(self):
        econ = BASELINE.economics
        self.assertGreater(econ.firm_capital_consumed_usd, 25_000.0)
        self.assertEqual(econ.withdrawals_financed_by_firm_usd, 0.0)

    def test_a_losing_account_that_never_paid_us_financed_nothing(self):
        # The whole consumed figure sits in accounts that never paid out, so
        # none of our cash came from the firm's capital. Reading the consumed
        # number as a subsidy to the pocket would be wrong.
        from pa_milky.simulator import run_book

        result = run_book(TRADES, FULL)
        consumed_by_non_payers = sum(
            max(0.0, -a.equity_profit_usd)
            for a in result.accounts
            if a.gross_paid_usd == 0
        )
        self.assertAlmostEqual(
            consumed_by_non_payers, BASELINE.economics.firm_capital_consumed_usd, places=2
        )

    def test_the_six_identity_terms_still_bridge_the_pocket(self):
        # The two firm-money measures are descriptive and must not leak into
        # the bridge, or contributions would stop summing to the delta.
        for arm in ARMS:
            bridge = arm.economics.bridge_against(BASELINE.economics)
            self.assertEqual(len(bridge["contributions_usd"]), 6)
            self.assertEqual(bridge["residual_usd"], 0)


class TestAdaptedPolicyEffect(unittest.TestCase):
    def test_the_search_returns_the_best_level_in_the_grid(self):
        best_pocket, best_level = best_over_cushions(TRADES, FULL, SMALL_GRID)
        for level in SMALL_GRID:
            arm = dataclasses.replace(
                FULL,
                policy=dataclasses.replace(FULL.policy, min_retained_balance_usd=level),
            )
            from pa_milky.simulator import run_book

            self.assertLessEqual(run_book(TRADES, arm).pocket_usd, best_pocket)
        self.assertIn(best_level, SMALL_GRID)

    def test_adapting_never_does_worse_than_the_fixed_policy(self):
        # The fixed policy is a member of the search space only if its own
        # cushion is in the grid; None is, so the best must beat it.
        best_pocket, _ = best_over_cushions(TRADES, FULL, SMALL_GRID)
        self.assertGreaterEqual(best_pocket, BASELINE.pocket_usd)

    def test_a_coarse_grid_can_report_a_rule_as_helping_us(self):
        # A constraint should never narrow what is achievable, so every delta
        # ought to be non-negative. Two are not, and the reason matters: when a
        # rule is removed the best cushion MOVES, and a three-level grid cannot
        # follow it. The arm is left stuck at a cushion that suited the
        # un-ablated book.
        self.assertLess(SMALL_DELTAS["consistency"], 0)
        self.assertLess(SMALL_DELTAS["maximum_payout"], 0)

    def test_and_refining_the_grid_removes_it(self):
        # $29,600 is $4,500 of headroom, where the consistency-free book peaks.
        # Adding that one level turns the delta non-negative: the negative
        # number was a fact about the search, not about the firm.
        self.assertGreaterEqual(REFINED_DELTAS["consistency"], 0)
        self.assertGreaterEqual(REFINED_DELTAS["maximum_payout"], 0)

    def test_the_two_modes_answer_different_questions(self):
        # Fixed policy says the safety net is worth -$12,500 to us. Adapted
        # policy says it constrains us by nothing at all. Both are true.
        fixed_cost = BASELINE.pocket_usd - BY_RULE["safety_net"].pocket_usd
        self.assertGreater(fixed_cost, 10_000.0)
        self.assertLess(abs(SMALL_DELTAS["safety_net"]), abs(fixed_cost))
        self.assertEqual(SMALL_DELTAS["safety_net"], 0.0)


if __name__ == "__main__":
    unittest.main()
