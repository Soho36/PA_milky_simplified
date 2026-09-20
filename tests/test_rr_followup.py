"""Behavioral tests for study-local assignment and heterogeneous reserves."""
from dataclasses import replace
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from rr_followup_support import Sleeves, SleeveRouter, LadderPolicy
from pa_milky.account import Account
from pa_milky.config import PROJECT_ROOT, load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book


def account(i, profit=0):
    return Account(i,'2020-01',datetime(2020,1,1),200,1500,100,True,equity_profit_usd=profit)


class FollowupTests(unittest.TestCase):
    def test_each_reserve_limits_its_own_request(self):
        seats=[account(1,8100),account(2,8100)]
        assignment=Sleeves([dict(rr='1.00',reserve=5300),dict(rr='1.00',reserve=8300)])
        assignment.assign(seats)
        maximum=LadderPolicy(sleeves=assignment,floor_balance=25100,cadence='daily',amount_rule='maximum')
        minimum=LadderPolicy(sleeves=assignment,floor_balance=25100,cadence='daily',amount_rule='minimum')
        self.assertEqual([maximum.requested_usd(a,firm_minimum_usd=500) for a in seats],[2700,0])
        self.assertEqual([minimum.requested_usd(a,firm_minimum_usd=500) for a in seats],[500,0])
        seats[0].equity_profit_usd=5700
        self.assertEqual(minimum.requested_usd(seats[0],firm_minimum_usd=500),300)

    def test_replacements_refill_missing_reserve_and_preserve_survivors(self):
        assignment=Sleeves([dict(rr='1.00',reserve=5300),dict(rr='1.00',reserve=8300)])
        seats=[account(i) for i in range(1,5)]
        assignment.assign(seats)
        self.assertEqual(assignment.assigned,{1:0,2:1,3:0,4:1})
        seats[0].alive=False; seats[2].alive=False
        seats.extend([account(5),account(6)])
        assignment.assign(seats)
        self.assertEqual(assignment.assigned,{1:0,2:1,3:0,4:1,5:0,6:0})

    def test_twenty_labels_do_not_make_identical_rr_losses_independent(self):
        config=load_config(PROJECT_ROOT/'config/scenarios/ideal_world.json')
        at=datetime(2020,1,2,9)
        trade=Trade('rr1:1','10-11',10,1,1,at,at+timedelta(hours=1),-2000,0,-2000,0)
        assignment=Sleeves([dict(rr='1.00',reserve=5300+i*100) for i in range(20)])
        result=run_book([trade],config,fixed_accounts=20,routing=RoutingPolicy(mode='blocked'),
            router_factory=partial(SleeveRouter,sleeves=assignment,weights={'1.00':20},trade_rr={trade.trade_key:'1.00'}))
        self.assertEqual(len(result.dead),20)
        self.assertEqual(len(set(assignment.assigned.values())),20)
        self.assertEqual(result.copies_filled,20)

    def test_uniform_ladder_exactly_replays_standard_withdrawal_policy(self):
        config=load_config(PROJECT_ROOT/'config/scenarios/no_rules_monthly_500.json')
        at=datetime(2020,1,2,9)
        trades=[Trade(f'rr1:{i}','10-11',10,i,i,at+timedelta(days=i*31),
            at+timedelta(days=i*31,hours=1),0,12000,12000,0) for i in range(3)]
        policy=WithdrawalPolicy(cadence='daily',amount_rule='maximum',min_retained_balance_usd=31900)
        control=run_book(trades,replace(config,policy=policy),fixed_accounts=4,routing=RoutingPolicy(mode='blocked'))
        assignment=Sleeves([dict(rr='1.00',reserve=6800) for _ in range(4)])
        ladder=LadderPolicy(sleeves=assignment,floor_balance=25100,cadence='daily',amount_rule='maximum')
        def observe(at,accounts,event,trade):
            if event=='decision': assignment.assign(accounts)
        result=run_book(trades,replace(config,policy=ladder),fixed_accounts=4,observer=observe,
            routing=RoutingPolicy(mode='blocked'),router_factory=partial(SleeveRouter,sleeves=assignment,
                weights={'1.00':4},trade_rr={t.trade_key:'1.00' for t in trades}))
        self.assertGreater(len(result.payouts),0)
        self.assertEqual(result.accounts,control.accounts)
        self.assertEqual(result.payouts,control.payouts)
        self.assertEqual(result.pocket_usd,control.pocket_usd)


if __name__=='__main__':
    unittest.main()
