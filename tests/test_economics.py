"""Exact cash identities and timing examples with known economic outcomes."""
import dataclasses
from datetime import datetime
from types import SimpleNamespace as NS
import unittest

from pa_milky.economics import Economics, receipt_timing


def account(net, gross=0, received=0, alive=True):
    return NS(gross_pnl_usd=net, commission_usd=0, gross_paid_usd=gross,
              received_usd=received, equity_profit_usd=net-gross, alive=alive)


def result(*accounts):
    fees = 200 * len(accounts)
    return NS(accounts=accounts, total_purchase_cost_usd=fees,
              pocket_usd=sum(a.received_usd for a in accounts)-fees)


def receipt(day, amount, key=1):
    return NS(at=datetime(2020, 1, day), received_usd=amount, account_id=key)


class TestEconomics(unittest.TestCase):
    def test_deficit_headline_separates_live_and_failed_accounts(self):
        e = Economics.measure(result(account(-1200, alive=False), account(-300)))
        payload = e.to_payload()
        self.assertEqual(payload['booked_deficits_not_funded_by_owner_usd'], 1500)
        self.assertEqual(payload['dead_account_booked_deficits_usd'], 1200)
        self.assertEqual(payload['live_account_booked_deficits_usd'], 300)
        self.assertEqual(payload['gross_withdrawals_exceeding_booked_earnings_usd'], 0)
        self.assertEqual(e.residual_usd, 0)

    def test_split_is_a_loss_without_a_survival_change(self):
        base = Economics.measure(result(account(2000, 1000, 900)))
        arm = Economics.measure(result(account(2000, 1000, 1000)))
        bridge = arm.bridge_against(base)
        self.assertEqual(bridge['delta_pocket_usd'], 100)
        self.assertEqual(bridge['contributions_usd']['firm_split_usd'], 100)
        self.assertEqual(bridge['residual_usd'], 0)

    def test_failure_residuals_and_negative_trading_reconcile(self):
        e = Economics.measure(result(account(1000, 500, 450, False),
                                     account(-1200, alive=False), account(800)))
        self.assertEqual(e.failed_positive_ledger_usd, 500)
        self.assertEqual(e.failed_negative_ledger_usd, 1200)
        self.assertEqual(e.retained_profit_usd, 800)
        self.assertEqual(e.residual_usd, 0)

    def test_same_amount_later_has_only_timing_difference(self):
        t = receipt_timing([receipt(1, 500)], [receipt(11, 500)])
        self.assertEqual(t['arm_later_usd'], 500)
        self.assertEqual(t['signed_dollar_days'], 5000)
        self.assertEqual(t['mean_signed_days'], 10)
        self.assertEqual(t['unmatched_baseline_usd'], 0)
        self.assertEqual(t['unmatched_arm_usd'], 0)

    def test_partial_receipts_and_unmatched_amounts(self):
        t = receipt_timing([receipt(1, 500)], [receipt(1, 200), receipt(11, 200)])
        self.assertEqual(t['same_time_usd'], 200)
        self.assertEqual(t['arm_later_usd'], 200)
        self.assertEqual(t['unmatched_baseline_usd'], 100)

    def test_never_match_cash_between_accounts(self):
        t = receipt_timing([receipt(1, 500, 1)], [receipt(1, 500, 2)])
        self.assertEqual(t['matched_usd'], 0)
        self.assertIsNone(t['mean_signed_days'])
        self.assertEqual(t['unmatched_arm_usd'], 500)
        self.assertEqual(t['unmatched_baseline_usd'], 500)

    def test_reversing_comparison_reverses_timing(self):
        a, b = [receipt(1, 500)], [receipt(11, 500)]
        self.assertEqual(receipt_timing(b, a)['signed_dollar_days'], -5000)
        self.assertEqual(receipt_timing(b, a)['arm_earlier_usd'], 500)
        self.assertEqual(receipt_timing([], [])['matched_usd'], 0)

    def test_real_tape_terminal_value_not_double_counted(self):
        from pa_milky.config import CONFIG_ROOT, load_config
        from pa_milky.ablation import Arm
        from tests.support import TRADES
        c = load_config(CONFIG_ROOT / 'scenarios/hold_then_liquidate.json')
        a = Arm.measure('hold', None, TRADES, c)
        self.assertEqual(a.stranded_usd, 0)
        self.assertEqual(a.value_usd, a.pocket_usd)
        self.assertEqual(a.economics.residual_usd, 0)

    def test_real_tape_split_counterexample(self):
        from pa_milky.ablation import Arm
        from tests.support import FULL, TRADES
        c = dataclasses.replace(FULL, policy=dataclasses.replace(
            FULL.policy, min_retained_balance_usd=30100))
        a = Arm.measure('base', None, TRADES, c)
        b = Arm.measure('no split', 'profit_split', TRADES,
                        dataclasses.replace(c, rulebook=c.rulebook.without('profit_split')))
        self.assertEqual(b.fates_changed_against(a), 0)
        self.assertEqual(b.value_usd-a.value_usd, 2200)
        self.assertEqual(b.economics.bridge_against(a.economics)['residual_usd'], 0)
