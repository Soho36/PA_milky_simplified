"""Brick 2: the safety-net gate, the backlog, and what a withdrawal costs."""

from __future__ import annotations

import dataclasses
from datetime import datetime
import unittest

from pa_milky.account import Account
from pa_milky.config import WithdrawalRules
from pa_milky.simulator import run_book
from pa_milky.withdrawals import allowed_amount, run_monthly_decision

from .support import BRICK1, BRICK2, RESULT1, RESULT2
from .test_simulator import trade

RULES = BRICK2.withdrawals
JAN = datetime(2020, 1, 1)
FEB = datetime(2020, 2, 1)


def account(profit: float = 0.0, activated=JAN) -> Account:
    pa = Account(
        account_id=1,
        cohort_month="2020-01",
        activated_at=activated,
        purchase_fee_usd=200.0,
        trailing_drawdown_usd=1500.0,
        frozen_floor_profit_usd=100.0,
        threshold_touch_fails=True,
    )
    if profit:
        pa.apply(
            trade(datetime(2020, 1, 2, 9), datetime(2020, 1, 2, 10), profit),
            commission_usd=0.0,
            path_order="mae_first",
        )
    return pa


class TestConfiguredRules(unittest.TestCase):
    def test_brick2_rules_are_the_ones_the_study_asked_for(self):
        self.assertEqual(RULES.policy, "fixed_monthly")
        self.assertEqual(RULES.amount_usd, 100.0)
        # 25,000 starting balance + 1,500 safety net + the 100 being asked for.
        self.assertEqual(RULES.eligibility_balance_usd, 26_600.0)
        self.assertEqual(RULES.safety_net_balance_usd, 26_500.0)
        self.assertEqual(RULES.shortfall, "accrue_backlog")

    def test_brick1_takes_nothing_out(self):
        self.assertFalse(BRICK1.withdrawals.enabled)


class TestTheGate(unittest.TestCase):
    def test_one_dollar_below_the_gate_pays_nothing(self):
        pa = account(1_599.5)  # balance 26,599.50
        pa.accrue(100.0)
        self.assertEqual(allowed_amount(pa, RULES), 0.0)

    def test_exactly_on_the_gate_pays(self):
        pa = account(1_600.0)  # balance 26,600.00
        pa.accrue(100.0)
        self.assertEqual(allowed_amount(pa, RULES), 100.0)

    def test_a_profitable_account_below_the_gate_still_pays_nothing(self):
        pa = account(1_000.0)
        pa.accrue(100.0)
        self.assertEqual(allowed_amount(pa, RULES), 0.0)

    def test_nothing_is_paid_without_an_entitlement(self):
        pa = account(5_000.0)
        self.assertEqual(allowed_amount(pa, RULES), 0.0)


class TestTheSafetyNet(unittest.TestCase):
    def test_a_backlog_is_capped_by_the_net(self):
        # Owed 500, but only 250 sits above the 26,500 net: pay two whole months.
        pa = account(1_750.0)
        for _ in range(5):
            pa.accrue(100.0)
        self.assertEqual(pa.entitlement_outstanding_usd, 500.0)
        self.assertEqual(allowed_amount(pa, RULES), 200.0)

    def test_a_deep_account_clears_the_whole_backlog_at_once(self):
        pa = account(5_000.0)
        for _ in range(5):
            pa.accrue(100.0)
        self.assertEqual(allowed_amount(pa, RULES), 500.0)

    def test_removing_the_net_removes_the_cap(self):
        rules = dataclasses.replace(RULES, safety_net_balance_usd=None)
        pa = account(1_750.0)
        for _ in range(5):
            pa.accrue(100.0)
        self.assertEqual(allowed_amount(pa, rules), 500.0)


class TestAccrual(unittest.TestCase):
    def test_an_account_earns_nothing_in_its_opening_month(self):
        pa = account(5_000.0, activated=JAN)
        run_monthly_decision([pa], JAN, RULES)
        self.assertEqual(pa.months_accrued, 0)
        self.assertEqual(pa.withdrawn_usd, 0.0)

    def test_the_next_boundary_pays(self):
        pa = account(5_000.0, activated=JAN)
        events = run_monthly_decision([pa], FEB, RULES)
        self.assertEqual(pa.months_accrued, 1)
        self.assertEqual(pa.withdrawn_usd, 100.0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].balance_before_usd, 30_000.0)
        self.assertEqual(events[0].balance_after_usd, 29_900.0)

    def test_an_unpayable_month_stays_owed(self):
        pa = account(0.0, activated=JAN)
        run_monthly_decision([pa], FEB, RULES)
        self.assertEqual(pa.entitlement_outstanding_usd, 100.0)
        self.assertEqual(pa.withdrawn_usd, 0.0)

    def test_skip_mode_lets_a_missed_month_expire(self):
        rules = dataclasses.replace(RULES, shortfall="skip")
        pa = account(0.0, activated=JAN)
        run_monthly_decision([pa], FEB, rules)
        run_monthly_decision([pa], datetime(2020, 3, 1), rules)
        self.assertEqual(pa.months_accrued, 2)
        self.assertEqual(pa.entitlement_outstanding_usd, 100.0)

    def test_dead_accounts_are_skipped_entirely(self):
        pa = account(0.0, activated=JAN)
        pa.alive = False
        run_monthly_decision([pa], FEB, RULES)
        self.assertEqual(pa.months_accrued, 0)


class TestWhatAWithdrawalCosts(unittest.TestCase):
    def test_the_floor_does_not_follow_the_balance_down(self):
        pa = account(5_000.0)
        self.assertEqual(pa.floor_profit_usd, 100.0)
        pa.accrue(100.0)
        pa.withdraw(100.0, FEB)
        self.assertEqual(pa.equity_profit_usd, 4_900.0)
        self.assertEqual(pa.peak_profit_usd, 5_000.0)
        self.assertEqual(pa.floor_profit_usd, 100.0)  # unchanged
        self.assertEqual(pa.headroom_usd, 4_800.0)  # 100 of cushion spent

    def test_under_brick2_rules_a_withdrawal_can_never_kill(self):
        # The gate implies a peak of at least +1,600, so the floor is already
        # frozen at +100; the net stops the balance at 26,500, which is 1,400
        # clear of it. Assert the property over the whole real run.
        for account_state in RESULT2.accounts:
            self.assertNotEqual(account_state.death_reason, "withdrawal_below_threshold")

    def test_a_withdrawal_can_kill_when_the_net_is_removed(self):
        rules = WithdrawalRules(
            policy="fixed_monthly",
            amount_usd=1_600.0,
            eligibility_balance_usd=26_600.0,
            safety_net_balance_usd=None,
            shortfall="accrue_backlog",
        )
        pa = account(1_600.0)
        run_monthly_decision([pa], FEB, rules)
        self.assertFalse(pa.alive)
        self.assertEqual(pa.death_reason, "withdrawal_below_threshold")

    def test_a_withdrawal_beyond_the_entitlement_is_refused(self):
        pa = account(5_000.0)
        pa.accrue(100.0)
        with self.assertRaises(ValueError):
            pa.withdraw(200.0, FEB)


class TestAgainstTheRealTape(unittest.TestCase):
    def test_every_dollar_accrued_is_paid_owed_or_written_off(self):
        accrued = sum(a.entitlement_accrued_usd for a in RESULT2.accounts)
        outstanding = sum(a.entitlement_outstanding_usd for a in RESULT2.accounts)
        self.assertAlmostEqual(accrued, RESULT2.total_withdrawn_usd + outstanding, places=2)

    def test_every_withdrawal_is_a_whole_number_of_months(self):
        for event in RESULT2.withdrawals:
            self.assertEqual(event.amount_usd % 100.0, 0.0)
            self.assertGreaterEqual(event.amount_usd, 100.0)

    def test_no_withdrawal_cuts_into_the_safety_net(self):
        for event in RESULT2.withdrawals:
            self.assertGreaterEqual(event.balance_after_usd, 26_500.0)

    def test_pocket_is_withdrawals_minus_fees(self):
        self.assertEqual(
            RESULT2.pocket_usd,
            round(RESULT2.total_withdrawn_usd - RESULT2.total_purchase_cost_usd, 2),
        )

    def test_taking_money_out_never_saves_an_account(self):
        # Withdrawing only ever spends cushion, so brick 2's survivors must be
        # a subset of brick 1's.
        alive1 = {a.cohort_month for a in RESULT1.alive}
        alive2 = {a.cohort_month for a in RESULT2.alive}
        self.assertTrue(alive2.issubset(alive1), alive2 - alive1)

    def test_withdrawals_are_in_chronological_order(self):
        moments = [event.at for event in RESULT2.withdrawals]
        self.assertEqual(moments, sorted(moments))

    def test_a_zero_amount_override_reproduces_brick_1(self):
        disabled = dataclasses.replace(
            BRICK2, withdrawals=dataclasses.replace(RULES, policy="none", amount_usd=0.0)
        )
        from .support import TRADES

        rerun = run_book(TRADES, disabled)
        self.assertEqual(len(rerun.alive), len(RESULT1.alive))
        self.assertEqual(rerun.copies_filled, RESULT1.copies_filled)
        self.assertEqual(rerun.total_withdrawn_usd, 0.0)


if __name__ == "__main__":
    unittest.main()
