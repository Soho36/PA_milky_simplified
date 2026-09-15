from dataclasses import fields, replace
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest

from pa_milky.reserve_metrics import ReserveObserver
from pa_milky.simulator import run_book
from pa_milky.evaluation import Evaluation
from tests import test_pipeline, test_evaluation


class TestReserveFrontier(unittest.TestCase):
    def test_event_integral_tracks_death_and_excludes_nominal_balance(self):
        start = datetime(2020, 1, 1)
        end = start+timedelta(days=2)
        observer = ReserveObserver(start, end)
        a = SimpleNamespace(alive=True, equity_profit_usd=1000, headroom_usd=900)
        observer(start, [a], 'decision', None)
        a.equity_profit_usd, a.headroom_usd = 2000, 1900
        observer(start+timedelta(hours=12), [a], 'trade', None)
        a.alive = False
        observer(start+timedelta(days=1), [a], 'trade', None)
        observer(end, [a], 'horizon', None)
        row = observer.summary()
        self.assertEqual(row['average_retained_profit_book'], 750)
        self.assertEqual(row['average_retained_profit_per_live_pa'], 1500)
        self.assertEqual(row['average_actual_cushion_per_live_pa'], 1400)
        self.assertEqual(row['live_pa_days'], 1)

    def test_observation_does_not_change_economics_or_terminal_equity(self):
        fixture = test_evaluation.TestEvaluationSupply()
        fixture.setUp()
        p = test_pipeline.TestPipeline().ledger().policy
        plain = run_book(fixture.tape, fixture.config, acquisition=p)
        observer = ReserveObserver(plain.tape_first_entry, plain.tape_last_exit)
        seen = run_book(fixture.tape, fixture.config, acquisition=p, observer=observer)
        self.assertEqual(replace(plain, acquisition=None), replace(seen, acquisition=None))
        for field in fields(plain.acquisition):
            if field.name != 'router':  # Router objects have identity equality.
                self.assertEqual(getattr(plain.acquisition, field.name), getattr(seen.acquisition, field.name))
        self.assertEqual(round(observer.state[1], 2), seen.equity_at_horizon_usd)

    def test_first_check_cash_failure_forfeits_pass_and_never_activates_later(self):
        ledger = test_pipeline.TestPipeline().ledger(activate_on_first_check=True)
        e = Evaluation(1, datetime(2020, 1, 1), state='passed', months_paid=1)
        ledger.active = [e]
        ledger.cash_usd = 0
        ledger.activate(datetime(2020, 1, 2), 0)
        self.assertEqual(e.state, 'cancelled')
        ledger.cash_usd = 5000
        ledger.activate(datetime(2020, 1, 3), 0)
        self.assertEqual(ledger.spares, 0)
        self.assertEqual(ledger.financing_events[-1]['kind'], 'pass_forfeited_cash')

    def test_first_check_capacity_failure_forfeits_but_available_slot_activates(self):
        for alive, expected in [(20, 'cancelled'), (19, 'funded')]:
            ledger = test_pipeline.TestPipeline().ledger(activate_on_first_check=True)
            e = Evaluation(1, datetime(2020, 1, 1), state='passed', months_paid=1)
            ledger.active = [e]
            ledger.activate(datetime(2020, 1, 2), alive)
            self.assertEqual(e.state, expected)


if __name__ == '__main__':
    unittest.main()
