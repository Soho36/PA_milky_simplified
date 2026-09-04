"""Each firm rule, tested against the sentence it came from.

Quotations are from the parent project's `rules/Payout_rules.txt`, which is the
supplied Apex payout document for 25K Rithmic accounts.
"""

from __future__ import annotations

from datetime import datetime
import unittest

from pa_milky.firm import RULE_TYPES, RequestContext, Rulebook

from .support import FULL, bank_days, make_account, make_trade

AT = datetime(2020, 2, 1)
BOOK = FULL.rulebook


def context(account, requested=500.0, payout_number=None) -> RequestContext:
    return RequestContext(
        account=account,
        at=AT,
        requested_usd=requested,
        payout_number=payout_number or account.payout_count + 1,
        starting_balance_usd=25_000.0,
        trailing_floor_balance_usd=25_100.0,
    )


def eligible_account(profit: float = 5_000.0, days: int = 10):
    """An account that passes every day-based gate, so one rule can be isolated.

    The profit is spread evenly across ten trading days, which clears the
    eight-day and five-profitable-day gates and keeps the largest day at about
    a tenth of the total -- comfortably inside the 30% consistency rule.
    """

    account = make_account()
    even = round(profit / days, 2)
    spread = [even] * (days - 1)
    spread.append(round(profit - sum(spread), 2))
    bank_days(account, spread)
    return account


class TestRulebookShape(unittest.TestCase):
    def test_every_rule_is_present_and_switchable(self):
        self.assertEqual(set(BOOK.rules), set(RULE_TYPES))
        self.assertEqual(len(RULE_TYPES), 10)

    def test_a_rulebook_must_declare_every_rule(self):
        with self.assertRaises(ValueError):
            Rulebook.from_payload({"minimum_balance": {"enabled": True, "balance_usd": 1.0}})

    def test_unknown_rules_are_rejected(self):
        with self.assertRaises(ValueError):
            Rulebook.from_payload({"no_such_rule": {"enabled": True}})

    def test_without_switches_exactly_one_rule_off(self):
        ablated = BOOK.without("consistency")
        self.assertFalse(ablated.is_on("consistency"))
        self.assertEqual(
            set(BOOK.active_keys) - set(ablated.active_keys), {"consistency"}
        )


class TestMinimumBalance(unittest.TestCase):
    """"Your account must meet the required minimum balance" -- $26,600 at 25K."""

    def test_one_cent_below_the_gate_blocks(self):
        account = eligible_account(1_599.99)
        self.assertTrue(BOOK.get("minimum_balance").blocks(context(account)))

    def test_exactly_on_the_gate_passes(self):
        account = eligible_account(1_600.0)
        self.assertEqual(account.balance_usd, 26_600.0)
        self.assertFalse(BOOK.get("minimum_balance").blocks(context(account)))

    def test_the_gate_does_not_move_with_the_amount_requested(self):
        account = eligible_account(1_600.0)
        rule = BOOK.get("minimum_balance")
        self.assertFalse(rule.blocks(context(account, requested=500.0)))
        self.assertFalse(rule.blocks(context(account, requested=1_500.0)))


class TestDayGates(unittest.TestCase):
    """"8 Trading Days" and "Profit on 5 Days" of $50 or more."""

    def test_seven_days_is_not_enough(self):
        account = make_account()
        bank_days(account, [100.0] * 7)
        self.assertTrue(BOOK.get("trading_days").blocks(context(account)))

    def test_eight_days_clears_it(self):
        account = make_account()
        bank_days(account, [100.0] * 8)
        self.assertFalse(BOOK.get("trading_days").blocks(context(account)))

    def test_four_profitable_days_is_not_enough(self):
        account = make_account()
        bank_days(account, [60.0] * 4 + [10.0] * 4)
        self.assertTrue(BOOK.get("profitable_days").blocks(context(account)))

    def test_fifty_dollars_exactly_counts(self):
        account = make_account()
        bank_days(account, [50.0] * 5 + [1.0] * 3)
        self.assertFalse(BOOK.get("profitable_days").blocks(context(account)))

    def test_forty_nine_fifty_does_not(self):
        account = make_account()
        bank_days(account, [49.5] * 5 + [1.0] * 3)
        self.assertTrue(BOOK.get("profitable_days").blocks(context(account)))

    def test_several_trades_on_one_day_are_one_day(self):
        account = make_account()
        for row in range(4):
            account.apply(
                make_trade(
                    datetime(2020, 1, 3, 9 + row), datetime(2020, 1, 3, 10 + row), 30.0, row=row
                ),
                commission_usd=0.0,
                path_order="mae_first",
            )
        self.assertEqual(account.trading_days_since_payout, 1)
        # ... and the day's profit is the sum, so it clears the $50 threshold.
        self.assertEqual(account.profitable_days_since_payout(50.0), 1)


class TestConsistency(unittest.TestCase):
    """The 30% windfall rule: highest profit day / 0.3 is the profit required."""

    def test_the_firms_own_worked_example(self):
        # "if your highest profit day ... was $1,500 ... you would have to have
        # at least $5,000 in total profit".
        rule = BOOK.get("consistency")
        account = make_account()
        bank_days(account, [1_500.0, 1_500.0, 1_000.0, 500.0, 400.0])
        self.assertEqual(account.best_day_since_payout_usd, 1_500.0)
        self.assertEqual(account.balance_usd, 29_900.0)  # $4,900 profit
        self.assertTrue(rule.blocks(context(account)))
        bank_days(account, [100.0], start_day=20)  # profit now exactly $5,000
        self.assertFalse(rule.blocks(context(account)))

    def test_a_flat_book_with_no_winning_day_is_never_blocked(self):
        account = make_account()
        bank_days(account, [-10.0] * 5)
        self.assertFalse(BOOK.get("consistency").blocks(context(account)))

    def test_it_stops_applying_from_the_sixth_payout(self):
        rule = BOOK.get("consistency")
        account = make_account()
        bank_days(account, [1_500.0, 100.0])
        self.assertTrue(rule.applies(context(account, payout_number=5)))
        self.assertFalse(rule.applies(context(account, payout_number=6)))

    def test_an_approved_payout_resets_the_window(self):
        account = eligible_account(5_000.0)
        self.assertGreater(account.best_day_since_payout_usd, 0)
        account.pay_out(500.0, 500.0, AT)
        self.assertEqual(account.best_day_since_payout_usd, 0.0)
        self.assertEqual(account.trading_days_since_payout, 0)


class TestSafetyNet(unittest.TestCase):
    """First three payouts: encroach by at most one $500 minimum."""

    def test_at_the_net_exactly_five_hundred_is_allowed(self):
        account = eligible_account(1_600.0)  # balance 26,600
        self.assertEqual(BOOK.get("safety_net").cap(context(account)), 500.0)

    def test_a_larger_request_needs_the_excess_fully_covered(self):
        # The firm's example scaled to 25K: for $1,200 the balance must be
        # $26,600 + $700 = $27,300, leaving $26,100.
        account = eligible_account(2_300.0)  # balance 27,300
        self.assertEqual(BOOK.get("safety_net").cap(context(account)), 1_200.0)

    def test_it_expires_after_the_third_payout(self):
        account = eligible_account(1_600.0)
        rule = BOOK.get("safety_net")
        self.assertTrue(rule.applies(context(account, payout_number=3)))
        self.assertFalse(rule.applies(context(account, payout_number=4)))


class TestPayoutSizeLimits(unittest.TestCase):
    def test_the_maximum_is_fifteen_hundred_for_the_first_five(self):
        account = eligible_account(20_000.0)
        rule = BOOK.get("maximum_payout")
        self.assertEqual(rule.cap(context(account)), 1_500.0)
        self.assertTrue(rule.applies(context(account, payout_number=5)))
        self.assertFalse(rule.applies(context(account, payout_number=6)))

    def test_a_request_the_caps_shrink_below_the_minimum_is_refused(self):
        # Balance 26,600: the net allows exactly $500, which is the minimum, so
        # this passes. One dollar less of profit and there is nothing to take.
        account = eligible_account(1_600.0)
        self.assertTrue(BOOK.decide(context(account, requested=500.0)).approved)
        account = eligible_account(1_599.0)
        decision = BOOK.decide(context(account, requested=500.0))
        self.assertFalse(decision.approved)
        self.assertEqual(decision.blocked_by, "minimum_balance")


class TestProfitSplit(unittest.TestCase):
    """"100% of the first $25,000 per account, and 90% of the profit after"."""

    def test_below_the_threshold_we_keep_everything(self):
        account = eligible_account(20_000.0)
        self.assertEqual(BOOK.get("profit_split").received(1_500.0, context(account)), 1_500.0)

    def test_above_the_threshold_we_keep_ninety_percent(self):
        account = eligible_account(20_000.0)
        account.gross_paid_usd = 25_000.0
        self.assertEqual(BOOK.get("profit_split").received(1_000.0, context(account)), 900.0)

    def test_a_payout_straddling_the_threshold_is_split_in_two(self):
        account = eligible_account(20_000.0)
        account.gross_paid_usd = 24_500.0
        # $500 at 100% plus $500 at 90%.
        self.assertEqual(BOOK.get("profit_split").received(1_000.0, context(account)), 950.0)

    def test_the_competing_reading_is_available_as_a_mode(self):
        rule = type(BOOK.get("profit_split"))(
            key="profit_split",
            enabled=True,
            params={
                "mode": "after_n_payouts",
                "reduced_rate": 0.9,
                "full_rate_from_payout": 6,
                "full_rate_threshold_usd": 25_000.0,
            },
        )
        account = eligible_account(20_000.0)
        self.assertEqual(rule.received(1_000.0, context(account, payout_number=5)), 900.0)
        self.assertEqual(rule.received(1_000.0, context(account, payout_number=6)), 1_000.0)


class TestTrailingFloorIsNotSwitchable(unittest.TestCase):
    def test_a_payout_can_never_reach_the_threshold(self):
        # Every rule off: the account specification still caps the payout at
        # one cent above the frozen floor.
        book = Rulebook.from_payload({key: {"enabled": False} for key in RULE_TYPES})
        account = eligible_account(5_000.0)  # balance 30,000, floor 25,100
        decision = book.decide(context(account, requested=1_000_000.0))
        self.assertTrue(decision.approved)
        self.assertEqual(decision.gross_usd, 4_899.99)
        self.assertEqual(decision.binding_cap, "trailing_floor")

    def test_and_the_account_survives_taking_it(self):
        book = Rulebook.from_payload({key: {"enabled": False} for key in RULE_TYPES})
        account = eligible_account(5_000.0)
        decision = book.decide(context(account, requested=1_000_000.0))
        self.assertTrue(account.pay_out(decision.gross_usd, decision.received_usd, AT))
        self.assertTrue(account.alive)
        self.assertEqual(account.balance_usd, 25_100.01)


if __name__ == "__main__":
    unittest.main()
