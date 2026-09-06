from dataclasses import replace
from datetime import datetime
import unittest
from tests import test_policy_study
from pa_milky.policy_study import policies
from pa_milky.simulator import run_book, decision_boundaries


class TestCadence(unittest.TestCase):
    def setUp(self):
        fixture=test_policy_study.TestPolicyStudy();fixture.setUp()
        self.config=fixture.config;self.trades=fixture.trades

    def test_daily_checks_do_not_multiply_monthly_entitlement(self):
        p=next(p for p in policies() if p.name=='fixed_750_backlog')
        for cadence in ('calendar_month','weekly','daily'):
            r=run_book(self.trades,replace(self.config,policy=replace(p,cadence=cadence,
                       min_retained_balance_usd=100000,terminal_withdrawal='none')))
            self.assertEqual(len(r.accounts),3)
            self.assertEqual([a.months_accrued for a in r.accounts],[2,1,0])
            self.assertEqual([a.entitlement_accrued_usd for a in r.accounts],[1500,750,0])

    def test_weekly_checks_are_mondays_and_exclude_opening_month(self):
        p=next(p for p in policies() if p.amount_rule=='minimum')
        r=run_book(self.trades,replace(self.config,policy=replace(p,cadence='weekly')))
        self.assertTrue(r.payouts)
        for event in r.payouts:
            self.assertEqual(event.at.weekday(),0)
            self.assertEqual(event.at.hour,0)
            self.assertGreater(event.at.strftime('%Y-%m'),event.cohort_month)

    def test_monthly_boundaries_preserved_in_weekly_schedule(self):
        times=decision_boundaries(datetime(2020,1,2),datetime(2020,3,23),'weekly')
        self.assertIn(datetime(2020,2,1),times)
        self.assertEqual(len(times),len(set(times)))
        self.assertTrue(all(t.day==1 or t.weekday()==0 for t in times))

    def test_future_trades_cannot_change_earlier_daily_payouts(self):
        p=next(p for p in policies() if p.amount_rule=='minimum')
        c=replace(self.config,policy=replace(p,cadence='daily'))
        before=run_book(self.trades,c)
        cutoff=datetime(2020,3,1)
        changed=[replace(t,gross_pnl_usd=-10000,mae_usd=-10000) if t.exit_at>=cutoff else t for t in self.trades]
        after=run_book(changed,c)
        early=lambda r:[e for e in r.payouts if e.at<cutoff]
        self.assertTrue(early(before))
        self.assertEqual(early(before),early(after))
