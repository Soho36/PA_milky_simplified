from dataclasses import replace
from datetime import datetime, timedelta
from types import SimpleNamespace as NS
import unittest
from pa_milky.acquisition import AcquisitionPolicy,AcquisitionLedger
from pa_milky.simulator import run_book
from pa_milky.loader import Trade
from tests import test_policy_study


class TestAcquisition(unittest.TestCase):
    def test_current_slot_midmonth_death_never_cancels_next_month(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_current_slot_replacements',2000))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,8),0,0,1,200),1)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,1,2,200),1)
        self.assertEqual(ledger.future_slots_used,0)

    def test_current_slot_boundary_deaths_absorb_monthly_purchase(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_current_slot_replacements',2000))
        ledger.fund(datetime(2020,1,1))
        ledger.decide(datetime(2020,1,1),0,0,0,200)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,0,1,200),1)
        self.assertEqual(ledger.replacement_events[-1]['scheduled_bought'],0)
        self.assertTrue(ledger.replacement_events[-1]['consumed_current_month_slot'])
        self.assertEqual(ledger.decide(datetime(2020,3,1),2,1,2,200),1)

    def test_current_slot_multiple_deaths_and_unaffordable_attempt(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_current_slot_replacements',0))
        ledger.fund(datetime(2020,2,1))
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,0,2,200),0)
        self.assertNotIn((2020,2),ledger.filled_month_slots)
        ledger.receive([NS(at=datetime(2020,2,2),received_usd=1000)])
        self.assertEqual(ledger.decide(datetime(2020,2,2),1,0,2,200),2)
        self.assertIn((2020,2),ledger.filled_month_slots)
        self.assertEqual(ledger.future_slots_used,0)
        self.assertEqual(ledger.decide(datetime(2020,3,1),2,2,4,200),1)

    def test_advanced_replacements_consume_future_slots(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_advance_replacements',2000))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,8),0,0,1,200),1)
        self.assertEqual(ledger.future_slots_used,1)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,1,2,200),0)
        self.assertEqual(ledger.future_slots_used,0)
        self.assertEqual(ledger.decide(datetime(2020,3,1),2,1,2,200),1)

    def test_failed_replacement_retries_without_slot_debt(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_advance_replacements',200))
        ledger.fund(datetime(2020,1,1))
        ledger.decide(datetime(2020,1,1),0,0,0,200)
        self.assertEqual(ledger.decide(datetime(2020,1,8),0,0,1,200),0)
        self.assertEqual(ledger.future_slots_used,0)
        ledger.receive([NS(at=datetime(2020,1,9),received_usd=400)])
        self.assertEqual(ledger.decide(datetime(2020,1,9),0,0,1,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,10),0,0,2,200),1)
        self.assertEqual(ledger.future_slots_used,2)
        self.assertEqual(ledger.pending_replacements,0)

    def test_plus_replacement_does_not_cancel_monthly_purchase(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_plus_replacements',2000))
        ledger.fund(datetime(2020,1,1))
        ledger.decide(datetime(2020,1,1),0,0,0,200)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,0,1,200),2)
        self.assertEqual(ledger.future_slots_used,0)


    def test_monthly_two_partial_fill_and_no_catchup(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_two',300))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        ledger.receive([NS(at=datetime(2020,1,2),received_usd=1000)])
        self.assertEqual(ledger.decide(datetime(2020,1,2),0,1,1,200),0)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,19,19,200),1)
        self.assertEqual(ledger.cash_usd,900)

    def test_weekly_one_monday_anchor_and_no_catchup(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('weekly_one',100))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),0)
        self.assertEqual(ledger.decide(datetime(2020,1,6),0,0,0,200),0)
        ledger.receive([NS(at=datetime(2020,1,7),received_usd=1000)])
        self.assertEqual(ledger.decide(datetime(2020,1,7),0,0,0,200),0)
        self.assertEqual(ledger.decide(datetime(2020,1,13),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,20),0,20,20,200),0)
        self.assertEqual(ledger.cash_usd,900)

    def test_cash_blocks_purchases_and_contributions_are_monthly(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_one',100,50))
        ledger.fund(datetime(2020,1,1));ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),0)
        ledger.fund(datetime(2020,2,1));ledger.fund(datetime(2020,3,1))
        self.assertEqual(ledger.decide(datetime(2020,3,1),2,0,0,200),1)
        self.assertEqual(ledger.cash_usd,0)
        self.assertEqual(ledger.contributed_usd,200)
        self.assertEqual(ledger.summary()['cash_identity_residual_usd'],0)

    def test_reinvestment_uses_only_allocated_received_cash_and_respects_cap(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('reinvest',5000,reinvest_fraction=.5,max_live_accounts=2))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,2),0,1,1,200),0)
        ledger.receive([NS(at=datetime(2020,2,1),received_usd=1000)])
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,1,1,200),1)
        self.assertEqual(ledger.decide(datetime(2020,2,2),1,2,2,200),0)
        self.assertEqual(ledger.payout_budget_spent_usd,200)

    def test_restart_replaces_empty_seed_without_spending_payout_allocation(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('reinvest',1000,reinvest_fraction=.5,restart_when_empty=True))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,2),0,0,1,200),1)
        self.assertEqual(ledger.payout_budget_spent_usd,0)
        self.assertEqual(ledger.cash_usd,600)
        self.assertEqual(ledger.decide(datetime(2020,1,3),0,1,2,200),0)

    def test_monthly_funded_control_matches_original_book(self):
        f=test_policy_study.TestPolicyStudy();f.setUp()
        base=run_book(f.trades,f.config)
        funded=run_book(f.trades,f.config,acquisition=AcquisitionPolicy('monthly_one',5000))
        self.assertEqual(base.pocket_usd,funded.pocket_usd)
        self.assertEqual(base.accounts,funded.accounts)
        self.assertEqual(base.payouts,funded.payouts)
        self.assertEqual(funded.acquisition.summary()['net_cash_created_usd'],funded.pocket_usd)
        from pa_milky.report import render_text, summarize
        self.assertIn('ending owner cash',render_text(funded))
        self.assertEqual(summarize(funded)['book']['months_in_dataset'],3)

    def test_replacement_cannot_take_trade_entered_before_purchase(self):
        f=test_policy_study.TestPolicyStudy();f.setUp()
        make=lambda key,entry,exit,pnl,mae:Trade(key,'1-2',1,1,1,entry,exit,mae,0,pnl,0)
        trades=[make('death',datetime(2020,1,2,9),datetime(2020,1,2,10),-2000,-2000),
                make('old_entry',datetime(2020,1,2,11),datetime(2020,1,4,10),100,0),
                make('new_entry',datetime(2020,1,3,10),datetime(2020,1,5,10),100,0)]
        r=run_book(trades,f.config,acquisition=AcquisitionPolicy('replace',1000))
        self.assertEqual(len(r.accounts),2)
        self.assertEqual(r.accounts[1].activated_at,datetime(2020,1,3))
        self.assertEqual(r.accounts[1].trades_taken,1)
        self.assertTrue(all(e['cash_after_usd']>=0 for e in r.acquisition.cash_events))

    def test_no_funding_means_no_accounts_and_no_negative_cash(self):
        f=test_policy_study.TestPolicyStudy();f.setUp()
        r=run_book(f.trades,f.config,acquisition=AcquisitionPolicy('replace',0))
        self.assertEqual(r.accounts,[])
        self.assertEqual(r.pocket_usd,0)

    def test_pass_rate_caps_new_accounts_per_month(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_current_slot_replacements',2000,
                                                   spare_capacity=0,passes_per_month=1))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual(ledger.decide(datetime(2020,1,8),0,0,1,200),0)
        self.assertEqual(ledger.pending_replacements,1)
        self.assertTrue(ledger.decisions[-1]['supply_limited'])
        self.assertFalse(ledger.decisions[-1]['cash_limited'])
        # February's pass settles the debt and consumes February's slot.
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,0,1,200),1)
        self.assertEqual(ledger.spent_usd,400)

    def test_spares_go_live_without_cash_and_count_toward_the_cap(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('monthly_current_slot_replacements',1000,
                                                   max_live_accounts=3,spare_capacity=2,passes_per_month=3))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),1)
        self.assertEqual((ledger.spares,ledger.cash_usd),(2,400))
        # A death is replaced from the shelf; January has no pass left to restock.
        self.assertEqual(ledger.decide(datetime(2020,1,5),0,0,1,200),1)
        self.assertEqual((ledger.spares,ledger.cash_usd),(1,400))
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,1,2,200),1)
        self.assertEqual((ledger.spares,ledger.cash_usd),(1,200))
        # Two live plus one spare fills the cap of three: no further restock.
        self.assertEqual(ledger.decide(datetime(2020,2,2),1,2,3,200),0)
        self.assertEqual(ledger.spares,1)
        self.assertEqual([e['kind'] for e in ledger.cash_events].count('spare_purchase'),2)

    def test_spare_shelf_settings_are_validated(self):
        for kw in ({'passes_per_month':2},{'spare_capacity':1},
                   {'spare_capacity':20,'passes_per_month':1},{'spare_capacity':-1,'passes_per_month':1}):
            with self.assertRaises(ValueError):
                AcquisitionPolicy('monthly_one',1000,**kw)

    def _mass_death_tape(self):
        # Every account alive on the 12th dies together, as copies of one system do.
        make=lambda key,at,pnl,mae:Trade(key,'1-2',1,1,1,at,at+timedelta(hours=1),mae,0,pnl,0)
        return [make(f'{m}-{d}',datetime(2020,m,d,9),-2000 if d==12 else 200,-2000 if d==12 else 0)
                for m in (1,2,3,4) for d in range(2,28)]

    def test_unlimited_pass_rate_reproduces_instant_supply(self):
        f=test_policy_study.TestPolicyStudy();f.setUp()
        trades=self._mass_death_tape()
        for name in ('monthly_one','weekly_one','monthly_current_slot_replacements'):
            base=run_book(trades,f.config,acquisition=AcquisitionPolicy(name,5000))
            shelf=run_book(trades,f.config,acquisition=AcquisitionPolicy(name,5000,spare_capacity=0,
                                                                        passes_per_month=100))
            self.assertEqual((base.pocket_usd,len(base.accounts),base.payouts),
                             (shelf.pocket_usd,len(shelf.accounts),shelf.payouts))
            self.assertEqual(shelf.unused_spares,0)

    def test_limited_supply_and_sunk_spares_reconcile(self):
        from pa_milky.economics import Economics
        f=test_policy_study.TestPolicyStudy();f.setUp()
        trades=self._mass_death_tape()
        base=run_book(trades,f.config,acquisition=AcquisitionPolicy('monthly_current_slot_replacements',5000))
        capped=run_book(trades,f.config,acquisition=AcquisitionPolicy('monthly_current_slot_replacements',5000,
                                                                     spare_capacity=0,passes_per_month=1))
        shelf=run_book(trades,f.config,acquisition=AcquisitionPolicy('monthly_current_slot_replacements',5000,
                                                                    spare_capacity=2,passes_per_month=5))
        self.assertLess(len(capped.accounts),len(base.accounts))
        self.assertGreater(shelf.unused_spares,0)
        for r in (capped,shelf):
            cash=r.acquisition.summary()
            self.assertEqual(cash['net_cash_created_usd'],r.pocket_usd)
            self.assertEqual(cash['purchase_spend_usd'],r.total_purchase_cost_usd)
            self.assertEqual(r.total_purchase_cost_usd,(len(r.accounts)+r.unused_spares)*f.config.purchase_fee_usd)
            self.assertEqual(Economics.measure(r).residual_usd,0)
            self.assertTrue(all(e['cash_after_usd']>=0 for e in r.acquisition.cash_events))

    def test_quarterly_batch_matches_planned_monthly_rate(self):
        ledger=AcquisitionLedger(AcquisitionPolicy('quarterly_three',5000))
        ledger.fund(datetime(2020,1,1))
        self.assertEqual(ledger.decide(datetime(2020,1,1),0,0,0,200),3)
        self.assertEqual(ledger.decide(datetime(2020,2,1),1,3,3,200),0)
        self.assertEqual(ledger.decide(datetime(2020,4,1),3,3,3,200),3)
