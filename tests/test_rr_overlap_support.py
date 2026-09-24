"""Overlap must preserve legacy settlements while filtering account variants."""
from dataclasses import replace
from datetime import datetime
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from pa_milky.config import load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.simulator import run_book
from rr_overlap_support import run_overlap_book


def trade(key, entry, exit, pnl, mae=-1):
    return Trade(key, '1-2', 0, int(key), int(key), datetime(2020,1,2,entry),
                 datetime(2020,1,2,exit), mae, max(0,pnl), pnl, 25)


class OverlapTests(unittest.TestCase):
    def setUp(self):
        self.cfg = replace(load_config(ROOT/'config/scenarios/full_rulebook_monthly_500.json'),
                           policy=WithdrawalPolicy(name='hold'), expected_trades=None)

    def test_overlapping_own_signals_all_settle_and_other_variant_is_excluded(self):
        tape = [trade('2',2,3,200), trade('3',2,3,300), trade('1',1,4,100)]
        result = run_overlap_book(tape, self.cfg, order=('0.50','2.50'),
                                  trade_rr={'1':'0.50','2':'0.50','3':'2.50'}, fixed_accounts=2)
        self.assertEqual([a.gross_pnl_usd for a in result.accounts], [300,300])
        self.assertEqual([a.trades_taken for a in result.accounts], [2,1])
        self.assertEqual([f['accounts'] for f in result.routing_fills], [[1],[2],[1]])

    def test_later_settlement_is_not_booked_after_death_even_if_already_open(self):
        tape = [trade('2',2,3,-2000,-2000), trade('1',1,4,5000)]
        result = run_overlap_book(tape, self.cfg, order=('0.50',),
                                  trade_rr={'1':'0.50','2':'0.50'}, fixed_accounts=1)
        legacy = run_book(tape, self.cfg, fixed_accounts=1)
        self.assertEqual(result.accounts, legacy.accounts)
        self.assertEqual(result.copies_filled, 1)
        self.assertEqual(result.routing_fills[-1]['accounts'], [])

    def test_single_variant_matches_unmodified_legacy_loop(self):
        tape = [trade('2',2,3,200), trade('1',1,4,100)]
        result = run_overlap_book(tape, self.cfg, order=('1.00',),
                                  trade_rr={t.trade_key:'1.00' for t in tape}, fixed_accounts=2)
        legacy = run_book(tape, self.cfg, fixed_accounts=2)
        self.assertEqual(result.accounts, legacy.accounts)
        self.assertEqual(result.payouts, legacy.payouts)
        self.assertEqual(result.copies_filled, legacy.copies_filled)


if __name__ == '__main__':
    unittest.main()
