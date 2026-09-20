from dataclasses import replace
from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.evaluation import EvaluationSpec
from pa_milky.provenance import inputs_accepted
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import run_rr_book, mortality_metrics
from pa_milky.simulator import run_book
from .support import IDEAL, make_trade


def trade(rr, entry, exit_at, pnl=10, *, row=1, mae=0):
    return replace(make_trade(entry, exit_at, pnl, row=row, mae=mae),
                   trade_key=f'RR{rr}:test:{row}')


class RRPortfolioTests(unittest.TestCase):
    def test_different_exits_change_later_eligibility(self):
        at = datetime(2020, 1, 2, 9)
        short = [trade('0.50', at, at+timedelta(hours=1)),
                 trade('0.50', at+timedelta(hours=2), at+timedelta(hours=3), row=2)]
        long = [trade('2.00', at, at+timedelta(hours=4)),
                trade('2.00', at+timedelta(hours=2), at+timedelta(hours=5), row=2)]
        result = run_rr_book({'0.50': short, '2.00': long}, IDEAL, {'0.50': 1, '2.00': 1}, fixed_accounts=2)
        self.assertEqual([a.trades_taken for a in result.accounts], [2, 1])
        self.assertEqual(result.copies_filled, 3)
        self.assertEqual(result.routing['account_rr'], {1: '0.50', 2: '2.00'})

    def test_homogeneous_replay_equals_original_blocked_engine(self):
        at = datetime(2020, 1, 2, 9)
        tape = [trade('1.00', at, at+timedelta(hours=2), -50, mae=-50),
                trade('1.00', at+timedelta(hours=1), at+timedelta(hours=3), row=2)]
        control = run_book(tape, IDEAL, fixed_accounts=4, routing=RoutingPolicy(mode='blocked'))
        mixed = run_rr_book({'1.00': tape}, IDEAL, {'1.00': 1}, fixed_accounts=4)
        self.assertEqual(control.accounts, mixed.accounts)
        self.assertEqual(control.payouts, mixed.payouts)
        self.assertEqual(control.copies_filled, mixed.copies_filled)

    def test_deaths_keep_their_common_signal_despite_different_exit_times(self):
        at = datetime(2020, 1, 2, 9)
        tapes = {rr: [trade(rr, at, at+timedelta(days=days), -2000, mae=-2000)]
                 for rr, days in [('0.50', 0), ('2.00', 2)]}
        result = run_rr_book(tapes, IDEAL, {'0.50': 1, '2.00': 1}, fixed_accounts=2)
        metrics = mortality_metrics(result, sum(tapes.values(), []))
        self.assertEqual(metrics['max_same_signal_deaths'], 2)
        self.assertEqual(metrics['worst_1d_cohort_deaths'], 1)
        self.assertEqual(metrics['possible_1d_death_cluster'], 2)
        self.assertEqual(metrics['book_wipeouts'], 1)

    def test_replacement_restores_the_depleted_rr_group(self):
        at = datetime(2020, 1, 2, 9)
        tapes = {
            '0.50': [trade('0.50', at, at+timedelta(hours=1), -2000, mae=-2000),
                     trade('0.50', at+timedelta(days=2), at+timedelta(days=2,hours=1), row=2)],
            '2.00': [trade('2.00', at, at+timedelta(hours=1)),
                     trade('2.00', at+timedelta(days=2), at+timedelta(days=2,hours=1), row=2)]}
        policy = AcquisitionPolicy('replace', 1000, max_live_accounts=2, replacement_target=2)
        result = run_rr_book(tapes, IDEAL, {'0.50':1,'2.00':1}, acquisition=policy)
        self.assertEqual(result.routing['account_rr'], {1:'0.50',2:'2.00',3:'0.50'})
        self.assertEqual(result.acquisition.summary()['cash_identity_residual_usd'], 0)

    def test_evaluations_ignore_other_rr_events(self):
        at = datetime(2020, 1, 2, 9)
        reference = [trade('1.00', at+timedelta(days=i), at+timedelta(days=i,hours=1), 100, row=i+1)
                     for i in range(20)]
        distracting = [trade('2.00', at+timedelta(days=i,minutes=1), at+timedelta(days=i,minutes=2),
                              -10000, mae=-10000, row=i+1) for i in range(20)]
        spec = EvaluationSpec(profit_target_usd=1500,trailing_drawdown_usd=1500,
                              monthly_fee_usd=33,activation_fee_usd=125,contracts=3)
        acq = AcquisitionPolicy('monthly_current_slot_replacements',1000,200,
                                spare_capacity=2,evaluation=spec,evaluations_at_once=2)
        # Extra RR events have no assigned PA group; the evaluation tape must
        # remain unchanged even with those earlier catastrophic exits present.
        normal = run_book(reference, IDEAL, acquisition=acq, routing=RoutingPolicy(mode='blocked'))
        union = sorted(reference+distracting, key=lambda t:(t.exit_at,t.entry_at,t.window_order,t.source_row,t.ticket))
        from functools import partial
        from pa_milky.rr_diversification import RRRouter
        alternate = run_book(union, IDEAL, acquisition=acq, routing=RoutingPolicy(mode='blocked'),
            evaluation_tape=reference, router_factory=partial(RRRouter, weights={'1.00':1},
                trade_rr={t.trade_key:('1.00' if t in reference else '2.00') for t in union}))
        self.assertEqual(normal.acquisition.summary(), alternate.acquisition.summary())
        self.assertEqual(normal.accounts, alternate.accounts)


class InputTransitionTests(unittest.TestCase):
    def test_only_explicit_equivalent_transitions_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'results').mkdir()
            (root/'results/INPUT_CHANGES.json').write_text(json.dumps({'transitions':[
                {'old_combined_sha256':'old','new_combined_sha256':'new','simulation_equivalent':True},
                {'old_combined_sha256':'new','new_combined_sha256':'different','simulation_equivalent':False}]}))
            with patch('pa_milky.provenance.PROJECT_ROOT', root):
                self.assertTrue(inputs_accepted({'combined_sha256':'old'},{'combined_sha256':'new'}))
                self.assertFalse(inputs_accepted({'combined_sha256':'old'},{'combined_sha256':'different'}))


if __name__ == '__main__':
    unittest.main()
