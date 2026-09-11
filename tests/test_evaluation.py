from collections import Counter
from datetime import datetime, timedelta
import unittest
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.economics import Economics
from pa_milky.evaluation import EvaluationSpec, Evaluation, Router, add_months, run_episode
from pa_milky.loader import Trade
from pa_milky.simulator import run_book
from tests import test_policy_study

SPEC_25K = EvaluationSpec(1500, 1500, 33, 125, 3)
SPEC_50K = EvaluationSpec(3000, 2500, 40, 125, 5)


def trade(key, entry, exit_, pnl, mae=0.0, mfe=None):
    return Trade(key, '1-2', 1, 1, 1, entry, exit_, mae, max(pnl, 0.0) if mfe is None else mfe, pnl, 0)


def fresh(spec):
    evaluation = Evaluation(1, datetime(2020, 1, 1), months_paid=1)
    evaluation.reset(spec)
    return evaluation


def day(d, hour=9):
    return datetime(2020, 1, d, hour)


class TestEvaluation(unittest.TestCase):
    def settle(self, evaluation, t, spec, order='mae_first', commission=0.0):
        return evaluation.apply(t, spec, commission_per_mnq=commission, path_order=order)

    def test_size_scales_excursions_and_touching_the_floor_fails(self):
        self.assertEqual(self.settle(fresh(SPEC_25K), trade('a', day(2), day(2, 10), 0, mae=-499), SPEC_25K), 'running')
        self.assertEqual(self.settle(fresh(SPEC_25K), trade('a', day(2), day(2, 10), 0, mae=-500), SPEC_25K), 'blown')

    def test_commission_scales_with_size_and_target_passes(self):
        e = fresh(SPEC_25K)
        self.assertEqual(self.settle(e, trade('a', day(2), day(2, 10), 400), SPEC_25K, commission=1.05), 'running')
        self.assertEqual(e.equity_usd, round(3 * (400 - 1.05), 2))
        # 1,196.85 + 3 x (102.10 - 1.05) = 1,500.00 exactly.
        self.assertEqual(self.settle(e, trade('b', day(3), day(3, 10), 102.10), SPEC_25K, commission=1.05), 'passed')
        self.assertEqual(e.passed_at, day(3, 10))

    def test_drawdown_never_freezes(self):
        # A funded 50K would freeze its floor at +100; the evaluation keeps trailing to +200.
        e = fresh(SPEC_50K)
        self.settle(e, trade('a', day(2), day(2, 10), 540), SPEC_50K)
        self.assertEqual((e.equity_usd, e.floor_usd), (2700, 200))
        self.assertEqual(self.settle(e, trade('b', day(3), day(3, 10), 0, mae=-510), SPEC_50K), 'blown')

    def test_favourable_extreme_first_is_the_harsher_order(self):
        t = trade('a', day(2), day(2, 10), 0, mae=-300, mfe=400)
        self.assertEqual(self.settle(fresh(SPEC_25K), t, SPEC_25K, 'mae_first'), 'running')
        self.assertEqual(self.settle(fresh(SPEC_25K), t, SPEC_25K, 'mfe_first'), 'blown')

    def test_router_takes_one_position_at_a_time_in_entry_order(self):
        # Settlement order is B, A, C; A entered first, so B is skipped.
        a = trade('A', day(2, 9), day(2, 11), 0)
        b = trade('B', day(2, 10), datetime(2020, 1, 2, 10, 30), 0)
        c = trade('C', day(2, 11), day(2, 12), 0)
        router = Router([b, a, c])
        self.assertEqual(router.first(day(2, 9)), 1)
        self.assertEqual(router.first(a.exit_at, settled=2), 2)
        self.assertEqual(router.first(datetime(2020, 1, 2, 9, 30)), 0)
        self.assertIsNone(router.first(day(3)))

    def test_monthly_renewal_is_clamped_without_drift(self):
        start = datetime(2020, 1, 31)
        self.assertEqual(add_months(start, 1), datetime(2020, 2, 29))
        self.assertEqual(add_months(start, 2), datetime(2020, 3, 31))
        self.assertEqual(add_months(start, 12), datetime(2021, 1, 31))

    def test_blown_episode_waits_for_renewal_then_passes(self):
        tape = [trade('loss', day(2), day(2, 10), -100, mae=-600),
                trade('skipped', day(20), day(20, 10), 500),
                trade('win', datetime(2020, 2, 3, 9), datetime(2020, 2, 3, 10), 500)]
        passed, months = run_episode(tape, Router(tape), SPEC_25K, datetime(2020, 1, 1),
                                     commission_per_mnq=0.0, path_order='mae_first')
        self.assertEqual((passed, months), (datetime(2020, 2, 3, 10), 2))

    def test_episode_that_never_passes_pays_every_month_of_the_horizon(self):
        tape = [trade('flat', day(2), day(2, 10), 0)]
        passed, months = run_episode(tape, Router(tape), SPEC_25K, datetime(2020, 1, 1),
                                     commission_per_mnq=0.0, path_order='mae_first', horizon_days=180)
        self.assertIsNone(passed)
        self.assertEqual(months, 6)


def make(key, at, pnl, mae=0.0):
    return Trade(key, '1-2', 1, 1, 1, at, at + timedelta(hours=1), mae, max(pnl, 0.0), pnl, 0)


def most_at_once(evaluations):
    ends = [(e.started_at, e.passed_at or e.ended_at or datetime.max) for e in evaluations]
    return max(sum(s <= t < end for s, end in ends) for t, _ in ends)


class TestEvaluationSupply(unittest.TestCase):
    def setUp(self):
        f = test_policy_study.TestPolicyStudy()
        f.setUp()
        self.config = f.config
        # Winners every day; everything alive dies together on the 12th.
        self.tape = [make(f'{m}-{d}', datetime(2020, m, d, 9), -2000 if d == 12 else 200, -2000 if d == 12 else 0)
                     for m in (1, 2, 3, 4) for d in range(2, 28)]

    def run_supply(self, name='monthly_current_slot_replacements', spares=0, at_once=5, cash=1000, tape=None, cap=20):
        policy = AcquisitionPolicy(name, cash, max_live_accounts=cap, spare_capacity=spares,
                                   evaluation=SPEC_25K, evaluations_at_once=at_once)
        return run_book(tape or self.tape, self.config, acquisition=policy)

    def test_costs_reconcile_and_accounts_come_only_from_passes(self):
        r = self.run_supply()
        cash = r.acquisition.summary()
        self.assertGreater(len(r.accounts), 1)
        self.assertEqual(cash['net_cash_created_usd'], r.pocket_usd)
        self.assertEqual(Economics.measure(r).residual_usd, 0)
        self.assertEqual(round(cash['evaluation_fees_usd'] + cash['activation_fees_usd'], 2), cash['purchase_spend_usd'])
        self.assertEqual(cash['activation_fees_usd'], 125 * cash['evaluations_activated'])
        self.assertEqual(len(r.accounts) + r.unused_spares, cash['evaluations_activated'])
        passes = sorted(e.passed_at for e in r.acquisition.evaluations if e.state == 'funded')
        for activated, passed in zip(sorted(a.activated_at for a in r.accounts), passes):
            self.assertGreater(activated, passed)

    def test_one_monthly_order_starts_one_evaluation_a_month(self):
        r = self.run_supply(name='monthly_one')
        starts = Counter(f'{e.started_at:%Y-%m}' for e in r.acquisition.evaluations)
        self.assertTrue(starts and all(n == 1 for n in starts.values()))

    def test_at_once_limit_binds(self):
        r = self.run_supply(spares=5, at_once=2)
        self.assertEqual(most_at_once(r.acquisition.evaluations), 2)

    def test_evaluations_and_spares_hold_seats(self):
        # The ledger raises if live accounts, spares and evaluations ever exceed the cap.
        r = self.run_supply(spares=2, cap=3, cash=5000)
        self.assertLessEqual(most_at_once(r.acquisition.evaluations), 3)
        self.assertGreater(len(r.accounts), 0)

    def test_blown_evaluation_waits_for_renewal(self):
        tape = ([make('loss', datetime(2020, 1, 2, 9), -100, -600)]
                + [make(f'j{d}', datetime(2020, 1, d, 9), 200) for d in range(3, 28)]
                + [make(f'f{d}', datetime(2020, 2, d, 9), 200) for d in range(3, 10)])
        r = self.run_supply(name='monthly_one', tape=tape)
        self.assertEqual(len(r.acquisition.evaluations), 1)
        first = r.acquisition.evaluations[0]
        self.assertEqual((first.resets, first.months_paid), (1, 2))
        self.assertEqual(first.passed_at, datetime(2020, 2, 5, 10))

    def test_evaluation_supply_settings_are_validated(self):
        for kw in ({'evaluation': SPEC_25K, 'evaluations_at_once': 5},
                   {'spare_capacity': 0, 'evaluation': SPEC_25K},
                   {'spare_capacity': 0, 'evaluation': SPEC_25K, 'evaluations_at_once': 5, 'passes_per_month': 2},
                   {'spare_capacity': 0, 'passes_per_month': 1, 'evaluations_at_once': 5}):
            with self.assertRaises(ValueError):
                AcquisitionPolicy('monthly_one', 1000, **kw)


if __name__ == '__main__':
    unittest.main()
