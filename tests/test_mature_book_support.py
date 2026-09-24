"""Boundary and seed-inventory regressions for the study-local adapter."""
from dataclasses import replace
from datetime import datetime
from functools import partial
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from pa_milky.config import load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import RRRouter
from pa_milky.acquisition import AcquisitionPolicy
from mature_book_support import calendar_runner,endow,OwnedInventoryLedger


class MatureSupportTests(unittest.TestCase):
    def test_unclosed_trade_remains_busy_and_its_future_loss_is_censored(self):
        start=datetime(2020,1,1); end=datetime(2020,4,1)
        def trade(key,entry,exit,pnl,mae):
            return Trade(key,'1-2',1,int(key),int(key),datetime.fromisoformat(entry),
                         datetime.fromisoformat(exit),mae,max(0,pnl),pnl,25)
        trades=[trade('1','2020-01-02T01:00:00','2020-01-02T02:00:00',50,-10),
                trade('2','2020-03-31T01:00:00','2020-04-02T02:00:00',-2000,-2000),
                trade('3','2020-03-31T02:00:00','2020-03-31T03:00:00',-2000,-2000)]
        trades.sort(key=lambda t:t.exit_at)
        cfg=replace(load_config(ROOT/'config/scenarios/full_rulebook_monthly_500.json'),
                    policy=WithdrawalPolicy(),purchase_fee_usd=0,expected_trades=None,expected_windows=None)
        def seed(at,accounts,event,t):
            if event=='decision' and at==start:endow(accounts,start,1500,100)
        result=calendar_runner(start,end)(trades,cfg,fixed_accounts=20,observer=seed,
                  routing=RoutingPolicy(mode='blocked'),router_factory=partial(
                      RRRouter,weights={'1.00':20},trade_rr={t.trade_key:'1.00' for t in trades}))
        self.assertEqual(result.alive_at_horizon,20)
        self.assertEqual(result.copies_filled,20)
        self.assertTrue(all(a.trades_taken==1 and a.equity_profit_usd==1648.95 for a in result.accounts))
        fills={f['trade_key']:f['accounts'] for f in result.routing_fills}
        self.assertEqual(len(fills['2']),20)
        self.assertEqual(fills['3'],[])

    def test_owned_seeds_do_not_consume_replacement_cash(self):
        ledger=OwnedInventoryLedger(AcquisitionPolicy('monthly_current_slot_replacements',5000))
        at=datetime(2020,1,1);ledger.fund(at)
        self.assertEqual(ledger.decide(at,0,0,0,200),20)
        self.assertEqual(ledger.cash_usd,5000)
        self.assertEqual(ledger.spent_usd,0)
        self.assertEqual(ledger.decide(datetime(2020,1,2),0,19,20,200),1)
        self.assertEqual(ledger.spent_usd,200)
        self.assertEqual(ledger.summary()['cash_identity_residual_usd'],0)

    def test_weighted_router_replenishes_small_component(self):
        router=RRRouter([],RoutingPolicy(mode='blocked'),weights={'0.50':9,'2.50':9,'1.00':2},trade_rr={})
        accounts=[SimpleNamespace(account_id=i,alive=True) for i in range(1,21)]
        router.assign(accounts)
        self.assertEqual(list(router.account_rr.values()).count('1.00'),2)
        for a in accounts:
            if router.account_rr[a.account_id]=='1.00':a.alive=False
        accounts.extend(SimpleNamespace(account_id=i,alive=True) for i in (21,22))
        router.assign(accounts)
        self.assertEqual([router.account_rr[i] for i in (21,22)],['1.00','1.00'])


if __name__=='__main__':unittest.main()
