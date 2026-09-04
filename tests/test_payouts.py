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
    CUSHION_FULL,
    FULL,
    IDEAL,
    NO_RULES_500,
    RESULT_CUSHION_FULL,
    RESULT_CUSHION_NO_RULES,
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


class TestDelayedPayoutsAreCausal(unittest.TestCase):
    """A payout landing on the 11th must not see the rest of the month.

    Regression: pending payouts used to be settled in a batch at the next
    monthly boundary and then stamped with their earlier due date, so a request
    due 11 February was decided against the balance as it stood on 1 March.
    """

    @staticmethod
    def _config(delay_days: int):
        from pa_milky.firm import Rulebook

        payload = {
            **NO_RULES_500.rulebook.to_payload(),
            "minimum_balance": {"enabled": True, "balance_usd": 26_600.0},
            "denial_on_shortfall": {"enabled": True},
            "processing_delay": {"enabled": delay_days > 0, "days": delay_days},
        }
        return dataclasses.replace(
            NO_RULES_500,
            rulebook=Rulebook.from_payload(payload),
            commission_usd_per_mnq_round_turn=0.0,
        )

    @staticmethod
    def _tape(loss_exit_day: int):
        from .support import make_trade

        return sorted(
            [
                make_trade(
                    datetime(2020, 1, 2, 9), datetime(2020, 1, 3, 9), 5_000.0, row=1
                ),
                make_trade(
                    datetime(2020, 2, 1, 9),
                    datetime(2020, 2, loss_exit_day, 9),
                    -4_000.0,
                    row=2,
                ),
                # A flat tail so the tape's horizon outlives the due date;
                # otherwise the request expires unsettled and proves nothing.
                make_trade(
                    datetime(2020, 2, 27, 9), datetime(2020, 2, 28, 9), 0.0, row=3
                ),
            ],
            key=lambda t: t.exit_at,
        )

    def test_a_loss_after_the_due_date_cannot_deny_the_payout(self):
        # Request 1 Feb, due 11 Feb, balance $30,000. The loss lands 20 Feb.
        result = run_book(self._tape(loss_exit_day=20), self._config(10))
        self.assertEqual(len(result.payouts), 1)
        event = result.payouts[0]
        self.assertEqual(event.at, datetime(2020, 2, 11))
        self.assertEqual(event.balance_before_usd, 30_000.0)
        self.assertEqual(result.denials, [])

    def test_a_loss_before_the_due_date_does_deny_it(self):
        # Same request, but the loss lands 5 Feb and drops the balance under
        # the gate before the firm approves.
        result = run_book(self._tape(loss_exit_day=5), self._config(10))
        self.assertEqual(result.payouts, [])
        self.assertEqual(len(result.denials), 1)
        self.assertEqual(result.denials[0].blocked_by, "denial_on_shortfall")

    def test_without_a_delay_the_two_tapes_agree(self):
        # With same-instant approval there is no window to fall in, so where
        # the loss lands cannot matter to the payout.
        late = run_book(self._tape(loss_exit_day=20), self._config(0))
        early = run_book(self._tape(loss_exit_day=5), self._config(0))
        self.assertEqual(len(late.payouts), len(early.payouts), 1)
        self.assertEqual(late.payouts[0].gross_usd, early.payouts[0].gross_usd)

    def test_a_request_still_pending_at_the_horizon_is_never_paid(self):
        # Requested 1 March with a 400-day delay: the tape ends first, and
        # there is no evidence about what happened after it.
        result = run_book(self._tape(loss_exit_day=20), self._config(400))
        self.assertEqual(result.payouts, [])
        self.assertEqual(result.requests_unpaid_at_horizon, 1)


class TestPolicyAdaptationChangesTheAblation(unittest.TestCase):
    """An ablation delta belongs to an arm, not to a rule.

    The safety net measures at -$12,500 against a policy with no cushion of its
    own -- which reads as "the firm's rule protects us". Give our own policy a
    $26,100 floor and that entire effect disappears: the rule was standing in
    for a cushion we should have had anyway.
    """

    def test_our_own_cushion_beats_the_unruled_book(self):
        self.assertGreater(
            RESULT_CUSHION_NO_RULES.total_received_usd, RESULT_NO_RULES.total_received_usd
        )

    def test_and_beats_the_full_rulebook_too(self):
        # With a cushion of our own the rulebook is a net cost again, which is
        # the sign the naive comparison reported backwards.
        self.assertGreater(
            RESULT_CUSHION_NO_RULES.total_received_usd, RESULT_FULL.total_received_usd
        )

    def test_the_safety_net_is_worth_nothing_once_we_hold_our_own_floor(self):
        without = dataclasses.replace(
            CUSHION_FULL, rulebook=CUSHION_FULL.rulebook.without("safety_net")
        )
        self.assertEqual(
            run_book(TRADES, without).pocket_usd, RESULT_CUSHION_FULL.pocket_usd
        )

    def test_a_withheld_month_is_counted_not_lost(self):
        # When our own cushion leaves nothing spare we never ask, so the firm
        # denies nothing. That month still has to appear somewhere, or the
        # ledger silently stops reconciling under a cushion.
        import dataclasses as dc

        high = dc.replace(
            FULL, policy=dc.replace(FULL.policy, min_retained_balance_usd=30_000.0)
        )
        result = run_book(TRADES, high)
        months = sum(a.months_accrued for a in result.accounts)
        withheld = sum(a.requests_withheld for a in result.accounts)
        self.assertGreater(withheld, 0)
        self.assertEqual(
            months, len(result.payouts) + len(result.denials) + withheld
        )

    def test_the_firms_rules_already_bind_tighter_than_our_cushion(self):
        # A $500 ask through a $26,600 gate already leaves $26,100, so adding
        # our own $26,100 floor on top of the full rulebook changes nothing.
        self.assertEqual(RESULT_CUSHION_FULL.pocket_usd, RESULT_FULL.pocket_usd)
        self.assertEqual(len(RESULT_CUSHION_FULL.alive), len(RESULT_FULL.alive))
