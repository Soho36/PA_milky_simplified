from datetime import datetime, date
from dataclasses import replace
import unittest
from pa_milky.account import Account
from pa_milky.config import CONFIG_ROOT,load_config
from pa_milky.firm import RequestContext,Rulebook


class TestLegacy50K(unittest.TestCase):
    def setUp(self):
        self.config=load_config(CONFIG_ROOT/'scenarios/legacy_50k_full_rulebook.json')
        self.account=Account(1,'2020-01',datetime(2020,1,1),250,2500,100,True,50000)
        self.account.day_pnl_usd={date(2020,1,i):100 for i in range(1,9)}

    def decision(self,balance,payout=1,request=500,book=None):
        self.account.equity_profit_usd=balance-50000
        return (book or self.config.rulebook).decide(RequestContext(self.account,datetime(2020,2,1),request,payout,50000,50100))

    def test_product_and_minimum_gate(self):
        self.assertEqual(self.config.purchase_fee_usd,250)
        self.assertEqual(self.account.floor_profit_usd,-2500)
        self.assertEqual(self.config.trailing_floor_balance_usd,50100)
        self.assertFalse(self.decision(52599.99).approved)
        self.assertEqual(self.decision(52600).gross_usd,500)

    def test_threshold_freeze_and_touch(self):
        self.account._lift_peak(2599)
        self.assertEqual(self.account.floor_profit_usd,99)
        self.account._lift_peak(2600)
        self.assertEqual(self.account.floor_profit_usd,100)
        self.account._lift_peak(9000)
        self.assertEqual(self.account.floor_profit_usd,100)
        self.assertTrue(self.account._breached(100))
        self.assertFalse(self.account._breached(100.01))

    def test_safety_net_and_first_five_cap(self):
        self.assertEqual(self.decision(53300,request=1200).gross_usd,1200)
        self.assertEqual(self.decision(54000,request=5000).gross_usd,1900)
        self.assertEqual(self.decision(55000,payout=5,request=5000).gross_usd,2000)
        self.assertGreater(self.decision(55000,payout=6,request=5000).gross_usd,2000)

    def test_optional_later_payout_balance_interpretation(self):
        rules=dict(self.config.rulebook.rules)
        gate=rules['minimum_balance']
        rules['minimum_balance']=replace(gate,params={**gate.params,'retain_after_payout_from':6})
        book=Rulebook(rules)
        self.assertEqual(self.decision(55000,6,5000,book).gross_usd,2400)
        self.assertFalse(self.decision(53000,6,500,book).approved)
