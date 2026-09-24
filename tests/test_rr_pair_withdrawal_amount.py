"""Regression checks for fixed assignment and per-variant while-flat copying."""
from dataclasses import replace
from datetime import datetime
from functools import partial
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from pa_milky.config import load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.routing import RoutingPolicy
from pa_milky.simulator import run_book
from study_rr_pair_withdrawal_amount import AlternatingRouter


class PairAmountTests(unittest.TestCase):
    def test_deaths_do_not_change_next_purchase_assignment(self):
        router = AlternatingRouter([], RoutingPolicy(mode='blocked'),
                                   weights={'0.50':1, '2.50':1}, trade_rr={})
        accounts = [SimpleNamespace(account_id=i, alive=True) for i in range(1,5)]
        router.assign(accounts)
        accounts[1].alive = accounts[3].alive = False
        accounts.append(SimpleNamespace(account_id=5, alive=True))
        router.assign(accounts)
        self.assertEqual(router.account_rr, {1:'0.50',2:'2.50',3:'0.50',4:'2.50',5:'0.50'})

    def test_each_variant_has_its_own_occupancy_and_same_time_exit_precedes_entry(self):
        def trade(key, entry, exit, pnl):
            return Trade(key, '1-2', 0, int(key), int(key),
                         datetime(2020,1,2,entry), datetime(2020,1,2,exit),
                         -1, max(0,pnl), pnl, 25)
        trades = [trade('1',1,3,100), trade('2',1,2,200),
                  trade('3',2,3,300), trade('4',2,3,400), trade('5',3,4,500)]
        trades.sort(key=lambda t:(t.exit_at,t.entry_at,t.source_row))
        variants = {'1':'0.50','2':'2.50','3':'0.50','4':'2.50','5':'0.50'}
        cfg = replace(load_config(ROOT/'config/scenarios/full_rulebook_monthly_500.json'),
                      policy=WithdrawalPolicy(name='hold'), expected_trades=None)
        result = run_book(trades, cfg, fixed_accounts=2, routing=RoutingPolicy(mode='blocked'),
                          router_factory=partial(AlternatingRouter, weights={'0.50':1,'2.50':1},
                                                 trade_rr=variants))
        fills = {f['trade_key']:f['accounts'] for f in result.routing_fills}
        self.assertEqual(fills, {'1':[1], '2':[2], '3':[], '4':[2], '5':[1]})
        self.assertEqual([a.trades_taken for a in result.accounts], [2,2])
        self.assertEqual([a.gross_pnl_usd for a in result.accounts], [600,600])


if __name__ == '__main__':
    unittest.main()
