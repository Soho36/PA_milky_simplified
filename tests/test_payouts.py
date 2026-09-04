"""The monthly decision, our policy, and the clock the day rules need."""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
import unittest

from pa_milky.clock import EuropeTallinn, in_session, label_anomaly, trading_day
from pa_milky.payouts import run_monthly_decision
from pa_milky.policy import WithdrawalPolicy
from pa_milky.simulator import run_book

from .support import (
    BRICK2,
    FULL,
    IDEAL,
    NO_RULES_500,
    RESULT1,
    RESULT2,
    RESULT_FULL,
    RESULT_NO_RULES,
    TRADES,
    bank_days,
    make_account,
)

JAN = datetime(2020, 1, 1)
FEB = datetime(2020, 2, 1)


class TestClock(unittest.TestCase):
    def test_the_trading_day_is_the_labels_own_date(self):
        # The exported labels are already Europe/Tallinn wall clock, so
        # attaching the zone cannot move the calendar date.
        self.assertEqual(trading_day(datetime(2020, 3, 29, 3, 30)), date(2020, 3, 29))

    def test_summer_and_winter_offsets(self):
        zone = EuropeTallinn()
        self.assertEqual(zone.utcoffset(datetime(2020, 7, 1, 12)).seconds // 3600, 3)
        self.assertEqual(zone.utcoffset(datetime(2020, 1, 1, 12)).seconds // 3600, 2)

    def test_dst_anomalies_are_nameable(self):
        self.assertEqual(label_anomaly(datetime(2020, 3, 29, 3, 30)), "nonexistent")
        self.assertEqual(label_anomaly(datetime(2020, 10, 25, 3, 30)), "ambiguous")
        self.assertIsNone(label_anomaly(datetime(2020, 6, 1, 12)))

    def test_the_real_tape_has_no_dst_anomalies(self):
        for trade in TRADES:
            self.assertIsNone(label_anomaly(trade.entry_at), trade.trade_key)
            self.assertIsNone(label_anomaly(trade.exit_at), trade.trade_key)

    def test_the_session_window_describes_rather_than_filters(self):
        # The parent kept these; so do we. They are authoritative completed
        # fills, not data errors.
        self.assertEqual(sum(1 for t in TRADES if not in_session(t.entry_at)), 2)
        self.assertEqual(sum(1 for t in TRADES if not in_session(t.exit_at)), 11)


class TestPolicy(unittest.TestCase):
    def test_a_held_book_never_asks(self):
        self.assertFalse(IDEAL.policy.enabled)
        self.assertEqual(RESULT1.payouts, [])
        self.assertEqual(RESULT1.total_withdrawn_usd, 0.0)

    def test_a_fixed_policy_asks_for_its_backlog(self):
        policy = WithdrawalPolicy(
            name="t", cadence="calendar_month", amount_usd=500.0,
            amount_rule="fixed", shortfall="accrue_backlog",
        )
        account = make_account()
        account.accrue(500.0)
        account.accrue(500.0)
        self.assertEqual(policy.requested_usd(account, firm_minimum_usd=500.0), 1_000.0)

    def test_a_maximum_policy_asks_for_everything(self):
        policy = WithdrawalPolicy(
            name="t", cadence="calendar_month", amount_rule="maximum",
        )
        account = make_account(5_000.0)
        self.assertGreater(policy.requested_usd(account, firm_minimum_usd=500.0), 1e6 - 1)

    def test_quantizing_rounds_down_to_whole_asks(self):
        policy = WithdrawalPolicy(
            name="t", cadence="calendar_month", amount_usd=500.0, amount_rule="fixed",
        )
        quantize = policy.quantizer()
        self.assertEqual(quantize(499.99), 0.0)
        self.assertEqual(quantize(500.0), 500.0)
        self.assertEqual(quantize(1_499.0), 1_000.0)

    def test_a_maximum_policy_does_not_quantize(self):
        policy = WithdrawalPolicy(
            name="t", cadence="calendar_month", amount_rule="maximum",
        )
        self.assertIsNone(policy.quantizer())

    def test_an_account_earns_nothing_in_its_opening_month(self):
        account = make_account(5_000.0, activated=JAN)
        run_monthly_decision([account], JAN, NO_RULES_500, [])
        self.assertEqual(account.months_accrued, 0)

    def test_the_next_boundary_pays(self):
        account = make_account(5_000.0, activated=JAN)
        payouts, denials = run_monthly_decision([account], FEB, NO_RULES_500, [])
        self.assertEqual(len(payouts), 1)
        self.assertEqual(denials, [])
        self.assertEqual(payouts[0].gross_usd, 500.0)
        self.assertEqual(payouts[0].balance_after_usd, 29_500.0)


class TestDecisionLedger(unittest.TestCase):
    def test_every_account_month_is_either_paid_or_denied(self):
        decided = sum(a.months_accrued for a in RESULT_FULL.accounts)
        self.assertEqual(decided, len(RESULT_FULL.payouts) + len(RESULT_FULL.denials))

    def test_every_denial_names_a_rule_that_is_switched_on(self):
        active = set(FULL.rulebook.active_keys)
        for event in RESULT_FULL.denials:
            self.assertIn(event.blocked_by, active | {"capped_to_zero", "trailing_floor"})
            for key in event.blockers:
                self.assertIn(key, active | {"capped_to_zero", "trailing_floor"})

    def test_the_first_blocker_is_one_of_the_blockers(self):
        for event in RESULT_FULL.denials:
            self.assertIn(event.blocked_by, event.blockers)

    def test_entitlement_reconciles(self):
        accrued = sum(a.entitlement_accrued_usd for a in RESULT_FULL.accounts)
        outstanding = sum(a.entitlement_outstanding_usd for a in RESULT_FULL.accounts)
        self.assertAlmostEqual(
            accrued, RESULT_FULL.total_withdrawn_usd + outstanding, places=2
        )


class TestFullRulebookAgainstTheTape(unittest.TestCase):
    def test_no_payout_ever_reaches_the_trailing_floor(self):
        for event in RESULT_FULL.payouts:
            self.assertGreater(event.balance_after_usd, 25_100.0)

    def test_no_payout_is_below_the_firms_minimum(self):
        for event in RESULT_FULL.payouts:
            self.assertGreaterEqual(event.gross_usd, 500.0)

    def test_the_first_three_payouts_respect_the_safety_net(self):
        for event in RESULT_FULL.payouts:
            if event.payout_number <= 3:
                self.assertGreaterEqual(event.balance_after_usd, 26_100.0)

    def test_the_first_five_payouts_respect_the_maximum(self):
        for event in RESULT_FULL.payouts:
            if event.payout_number <= 5:
                self.assertLessEqual(event.gross_usd, 1_500.0)

    def test_the_500_policy_never_reaches_the_uncapped_regime(self):
        # A $500 ask that clears in most months never builds a backlog past
        # the $1,500 cap, so the cap's expiry after payout five is not what
        # limits this scenario. Stated as a fact about this run.
        self.assertTrue(all(e.gross_usd <= 1_500.0 for e in RESULT_FULL.payouts))

    def test_the_rulebook_protects_us_from_our_own_extraction(self):
        # The obvious expectation -- rules can only cost us -- is false here,
        # and this test exists to keep that finding from being lost.
        #
        # With every rule off, a $500 request is capped only by the trailing
        # threshold, so the book pays itself down to a few dollars above death
        # and the accounts do not survive to pay again. The safety net refuses
        # exactly that trade. Rules on extracts MORE.
        self.assertGreater(
            RESULT_FULL.total_received_usd, RESULT_NO_RULES.total_received_usd
        )
        self.assertGreater(len(RESULT_FULL.alive), len(RESULT_NO_RULES.alive))
        lowest_unruled = min(e.balance_after_usd for e in RESULT_NO_RULES.payouts)
        lowest_ruled = min(e.balance_after_usd for e in RESULT_FULL.payouts)
        self.assertLess(lowest_unruled, 25_200.0)
        self.assertGreater(lowest_ruled, 25_800.0)

    def test_switching_every_rule_off_is_not_the_same_as_holding(self):
        self.assertGreater(RESULT_NO_RULES.total_withdrawn_usd, 0.0)
        self.assertEqual(RESULT1.total_withdrawn_usd, 0.0)

    def test_the_split_never_bit_on_this_tape(self):
        # No single account was ever paid $25,000 cumulatively, so the 90%
        # tier is unreached. Stated as a fact about this run, not a rule.
        self.assertLess(max(a.gross_paid_usd for a in RESULT_FULL.accounts), 25_000.0)
        self.assertEqual(RESULT_FULL.total_received_usd, RESULT_FULL.total_withdrawn_usd)


class TestProcessingDelay(unittest.TestCase):
    def test_a_delay_moves_the_cash_but_not_the_decision(self):
        delayed = dataclasses.replace(
            NO_RULES_500,
            rulebook=NO_RULES_500.rulebook.__class__.from_payload(
                {
                    **NO_RULES_500.rulebook.to_payload(),
                    "processing_delay": {"enabled": True, "days": 10},
                }
            ),
        )
        result = run_book(TRADES, delayed)
        self.assertTrue(result.payouts)
        # Requests are decided on the first of a month; with a ten-day delay
        # the cash lands on the eleventh.
        self.assertTrue(all(event.at.day == 11 for event in result.payouts))

    def test_brick2_had_no_delay(self):
        self.assertEqual(BRICK2.rulebook.processing_delay_days, 0)
        self.assertTrue(all(event.at.day == 1 for event in RESULT2.payouts))


if __name__ == "__main__":
    unittest.main()
