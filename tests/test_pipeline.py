from dataclasses import replace
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest

from pa_milky.acquisition import AcquisitionPolicy, AcquisitionLedger
from pa_milky.evaluation import Evaluation
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.simulator import run_book
from tests.test_evaluation import SPEC_25K
from tests import test_evaluation


class TestPipeline(unittest.TestCase):
    def ledger(self, **kw):
        p=AcquisitionPolicy('monthly_current_slot_replacements',5000,spare_capacity=0,
            evaluation=SPEC_25K,evaluations_at_once=5,persistent_demand=True,**kw)
        ledger=AcquisitionLedger(p)
        ledger.attach_tape([],commission_per_mnq=0,path_order='mae_first')
        ledger.fund(datetime(2020,1,1))
        return ledger

    def test_missed_order_survives_and_deploys_off_schedule(self):
        l=self.ledger()
        self.assertEqual(l.decide(datetime(2020,1,1),0,0,0,200),0)
        l.decide(datetime(2020,1,2),0,0,0,200)
        self.assertEqual(l.shortfall,1)
        l.active[0].state='passed'
        self.assertEqual(l.decide(datetime(2020,1,3),0,0,0,200),1)
        self.assertEqual(l.pending_month_orders,[])

    def test_needed_evaluation_renews_instead_of_cancelling(self):
        l=self.ledger()
        l.decide(datetime(2020,1,1),0,0,0,200)
        e=l.active[0]
        e.state='blown'
        l.decide(datetime(2020,2,1),1,0,0,200)
        self.assertEqual((e.state,e.months_paid,e.resets),('running',2,1))
        self.assertEqual(l.pending_month_orders,[(2020,1),(2020,2)])

    def test_replacement_consumes_current_order_not_older_backlog(self):
        l=self.ledger()
        l.pending_month_orders=[(2020,1)]
        l.spares=1
        count=l.decide_persistent(datetime(2020,2,1),0,1,200)
        self.assertEqual(count,1)
        self.assertEqual(l.pending_month_orders,[(2020,1)])
        self.assertEqual(l.pending_replacements,0)

    def test_full_book_does_not_accumulate_growth_orders(self):
        l=self.ledger()
        l.decide_persistent(datetime(2020,1,1),20,20,200)
        self.assertEqual(l.pending_month_orders,[])

    def test_stagger_is_global_across_batches_and_renewals(self):
        l=self.ledger(evaluation_start_interval_days=7)
        l.policy=replace(l.policy,spare_capacity=5)
        for d in range(45): l.decide(datetime(2020,1,1)+timedelta(days=d),d//31,0,0,200)
        starts=[e.started_at for e in l.evaluations]
        self.assertGreater(len(starts),1)
        self.assertTrue(all((b-a).days>=7 for a,b in zip(starts,starts[1:])))

    def test_unreserved_evaluations_wait_for_funded_capacity(self):
        l=self.ledger(evaluations_reserve_seats=False)
        e=Evaluation(1,datetime(2020,1,1),state='passed',months_paid=1)
        l.active=[e]
        l.activate(datetime(2020,1,2),20)
        self.assertEqual((e.state,l.spares),('passed',0))
        l.activate(datetime(2020,1,3),19)
        self.assertEqual((e.state,l.spares),('funded',1))

    def test_unaffordable_activation_is_cash_not_missing_pass(self):
        l=self.ledger()
        l.cash_usd=0
        l.active=[Evaluation(1,datetime(2020,1,1),state='passed',months_paid=1)]
        l.activate(datetime(2020,1,2),0)
        flags=l.limits(datetime(2020,1,2),0,200,1,0)
        self.assertTrue(flags['cash_limited'])
        self.assertFalse(flags['supply_limited'])
        self.assertEqual(l.financing_events[0]['kind'],'activation_blocked')

    def test_metrics_include_unresolved_deaths_and_cap_holds(self):
        fixture=test_evaluation.TestEvaluationSupply()
        fixture.setUp()
        p=replace(self.ledger().policy,spare_capacity=2,evaluation_start_interval_days=1)
        r=run_book(fixture.tape,fixture.config,acquisition=p)
        metrics=measure_pipeline(r)
        waits=replacement_records(r)
        self.assertEqual(metrics['deaths'],len(r.accounts)-r.alive_at_horizon)
        self.assertEqual(metrics['deaths'],metrics['replacements_filled']+metrics['replacements_unfilled'])
        self.assertEqual(metrics['unfilled_account_days'],round(sum(w['wait_days'] for w in waits),2))
        self.assertTrue(all(d['alive']+d['spares']+d['in_flight']<=20 for d in r.acquisition.pipeline_daily))

    def test_pipeline_options_require_compatible_policy(self):
        for kw in ({'evaluation_start_interval_days':-1},{'evaluation_start_interval_days':1.5}):
            with self.assertRaises(ValueError): self.ledger(**kw)
        with self.assertRaises(ValueError):
            AcquisitionPolicy('monthly_one',5000,persistent_demand=True)

    def test_fifo_waits_include_final_day_death_and_censoring(self):
        r=SimpleNamespace(
            accounts=[SimpleNamespace(account_id=1,died_at=datetime(2020,1,1,12)),
                      SimpleNamespace(account_id=2,died_at=datetime(2020,1,2,12)),
                      SimpleNamespace(account_id=3,died_at=datetime(2020,1,5))],
            tape_last_exit=datetime(2020,1,5),
            acquisition=SimpleNamespace(replacement_events=[{'at':'2020-01-03T00:00:00','replacements':1}]))
        records=replacement_records(r)
        self.assertEqual([w['wait_days'] for w in records],[1.5,2.5,0])
        self.assertEqual([w['censored'] for w in records],[False,True,True])
        self.assertFalse(any(w['next_check'] for w in records))

    def test_next_check_service_allows_normal_midnight_delay(self):
        r=SimpleNamespace(accounts=[SimpleNamespace(account_id=1,died_at=datetime(2020,1,1,12))],
            tape_last_exit=datetime(2020,1,3),
            acquisition=SimpleNamespace(replacement_events=[{'at':'2020-01-02T00:00:00','replacements':1}]))
        self.assertTrue(replacement_records(r)[0]['next_check'])


if __name__=='__main__': unittest.main()
