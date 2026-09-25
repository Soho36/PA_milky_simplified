"""Boundary metrics and actual-purchase alternation for the capped monthly plan."""
from dataclasses import replace
from datetime import datetime
from functools import partial
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from monthly_pair_support import book_metrics,add_months
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.config import load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from study_rr_pair_withdrawal_amount import AlternatingRouter


class MonthlyPairTests(unittest.TestCase):
    def test_gap_and_terminal_censoring_exclude_initial_zero(self):
        rows=[dict(activated_at='2020-01-01',died_at='2020-01-10'),
              dict(activated_at='2020-02-01',died_at='2020-02-10')]
        m,e=book_metrics(rows,datetime(2020,1,1),datetime(2020,3,1))
        self.assertEqual(m['empty_episodes'],2)
        self.assertEqual(m['empty_days'],42)
        self.assertFalse(e[0]['censored']);self.assertTrue(e[1]['censored'])
        self.assertEqual(m['deaths'],2)

    def test_checkpoint_excludes_events_on_boundary_and_nets_simultaneous_restart(self):
        rows=[dict(activated_at='2020-01-01',died_at='2020-02-01'),
              dict(activated_at='2020-02-01',died_at='')]
        m,_=book_metrics(rows,datetime(2020,1,1),datetime(2020,2,1))
        self.assertEqual((m['purchased'],m['deaths'],m['end_alive']),(1,0,1))
        m,_=book_metrics(rows,datetime(2020,1,1),datetime(2020,3,1))
        self.assertEqual((m['empty_episodes'],m['empty_days']),(0,0))

    def test_cap_pauses_purchases_but_not_per_purchase_rr_sequence(self):
        start=datetime(2020,1,1);trades=[];variants={}
        def add(at,pnl,rr):
            k=str(len(trades)+1)
            trades.append(Trade(k,'1-2',0,len(trades),len(trades),at,at,
                                min(0,pnl),max(0,pnl),pnl,1))
            variants[k]=rr
        for i in range(24):
            at=add_months(start,i).replace(day=2)
            for rr in ('0.50','2.50'):add(at,2,rr)
        add(datetime(2021,10,15),-2000,'0.50')
        trades.sort(key=lambda t:(t.exit_at,t.entry_at,t.source_row))
        cfg=replace(load_config(ROOT/'config/scenarios/full_rulebook_monthly_500.json'),
                    policy=WithdrawalPolicy(),expected_trades=None)
        result=run_book(trades,cfg,acquisition=AcquisitionPolicy('monthly_one',200,200,max_live_accounts=20),
                        routing=RoutingPolicy(mode='blocked'),router_factory=partial(AlternatingRouter,
                        weights={'0.50':1,'2.50':1},trade_rr=variants))
        self.assertEqual(len(result.accounts),22)
        self.assertEqual(result.accounts[20].activated_at,datetime(2021,11,1))
        self.assertEqual(result.routing['account_rr'][21],'0.50')
        self.assertEqual(result.routing['account_rr'][22],'2.50')
        self.assertFalse(any(a.activated_at.month in (9,10) and a.activated_at.year==2021 for a in result.accounts))


if __name__=='__main__':unittest.main()
