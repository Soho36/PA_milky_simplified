"""Evaluation procurement and blocked PA execution share a causal timeline."""
from datetime import datetime
from dataclasses import replace
import unittest

from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import CONFIG_ROOT, load_config
from pa_milky.economics import Economics
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from tests.test_evaluation import SPEC_25K, trade


class BlockedPipelineTests(unittest.TestCase):
    def test_pass_activation_blocking_death_and_delayed_replacement(self):
        def at(day, hour=0):
            return datetime(2020, 1, day, hour)

        # Exports are settlement-ordered: the overlapping short trade exits first.
        tape = [trade('first_pass', at(2,9), at(2,10), 510),
                trade('busy_skip', at(3,10), at(3,11), 100),
                trade('long', at(3,9), at(3,12), 100),
                trade('reuse_on_exit', at(3,12), at(3,13), 100),
                trade('pa_death', at(4,9), at(4,10), -2000, mae=-2000),
                trade('second_pass', at(6,9), at(6,10), 510),
                trade('replacement_pa', at(7,9), at(7,10), 100)]
        config = load_config(CONFIG_ROOT/'scenarios/full_rulebook_monthly_500.json')
        config = replace(config, expected_trades=len(tape))
        acq = AcquisitionPolicy('monthly_current_slot_replacements', 1000,
            max_live_accounts=20, spare_capacity=0, evaluation=SPEC_25K,
            evaluations_at_once=5, persistent_demand=True)
        result = run_book(tape, config, acquisition=acq, routing=RoutingPolicy(mode='blocked'))
        fills = {f['trade_key']:f['accounts'] for f in result.routing_fills}
        self.assertEqual(fills, {'first_pass':[], 'busy_skip':[], 'long':[1],
            'reuse_on_exit':[1], 'pa_death':[1], 'second_pass':[], 'replacement_pa':[2]})
        self.assertEqual([a.activated_at for a in result.accounts], [at(3),at(7)])
        self.assertEqual(result.accounts[0].died_at, at(4,10))
        self.assertEqual(result.acquisition.replacement_events[-1]['at'], at(7).isoformat())
        self.assertEqual(result.total_purchase_cost_usd, 2*(33+125))
        self.assertEqual(Economics.measure(result).residual_usd, 0)
        self.assertTrue(all(d['alive']+d['spares']+d['in_flight']<=20
                            for d in result.acquisition.pipeline_daily))


if __name__=='__main__':
    unittest.main()
