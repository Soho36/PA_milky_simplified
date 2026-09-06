import unittest
from dataclasses import replace
from datetime import datetime
from pa_milky.config import CONFIG_ROOT, load_config
from pa_milky.loader import Trade
from pa_milky.policy import WithdrawalPolicy
from pa_milky.policy_study import (annotate_against_benchmark, measure,
                                   path_ceiling, path_fingerprint, policies)
from pa_milky.simulator import run_book


class TestPolicyStudy(unittest.TestCase):
    def setUp(self):
        self.config = load_config(CONFIG_ROOT/'scenarios/full_rulebook_monthly_500.json')
        self.trades = [Trade(str(i),'1-2',1,i,i,datetime(2020,m,d,9),
                            datetime(2020,m,d,10),0,200,200,0)
                       for i,(m,d) in enumerate([(m,d) for m in (1,2,3) for d in range(2,23)],1)]

    def test_paired_score_equals_independent_no_terminal_run(self):
        for p in (policies()[1], policies()[6], WithdrawalPolicy(name='hold')):
            row = measure(self.trades,self.config,p,26100)
            ongoing = run_book(self.trades,replace(self.config,policy=replace(
                p,min_retained_balance_usd=26100,terminal_withdrawal='none')))
            self.assertEqual(row['ongoing_pocket_usd'],ongoing.pocket_usd)
            self.assertAlmostEqual(row['ongoing_pocket_usd']+row['terminal_received_usd'],
                                   row['combined_pocket_usd'],places=2)
            self.assertEqual(row['alive_before_terminal'],len(ongoing.alive))
            self.assertEqual(row['ongoing_payouts'],len(ongoing.payouts))
            self.assertEqual(row['economics']['residual_usd'],0)
            self.assertGreater(row['terminal_received_usd'],0)

    def test_ceiling_gap_is_exactly_the_split_plus_profit_left_standing(self):
        for p in (policies()[1], policies()[5]):
            row = measure(self.trades, self.config, p, 26100)
            self.assertAlmostEqual(
                row['path_ceiling_usd'] - row['combined_pocket_usd'],
                row['firm_split_usd'] + row['profit_after_terminal_usd'], places=2)
            self.assertEqual(row['unextracted_usd'],
                             round(row['path_ceiling_usd'] - row['combined_pocket_usd'], 2))

    def test_matching_the_benchmark_total_is_not_matching_its_trades(self):
        # Same booked earnings as the benchmark, reached on a different path.
        # Neutrality must read the fingerprint, not the total.
        rows = [{'policy': 'same_path', 'retained_balance_usd': 30000.0,
                 'booked_net_trading_usd': 1000.0, 'combined_pocket_usd': 800.0,
                 'path_fingerprint': 'benchmarkpath'},
                {'policy': 'same_total', 'retained_balance_usd': 29000.0,
                 'booked_net_trading_usd': 1000.0, 'combined_pocket_usd': 900.0,
                 'path_fingerprint': 'someotherpath'}]
        benchmark = {'policy': 'hold', 'retained_balance_usd': None,
                     'booked_net_trading_usd': 1000.0, 'path_ceiling_usd': 1000.0,
                     'combined_pocket_usd': 100.0, 'path_fingerprint': 'benchmarkpath'}
        annotate_against_benchmark(rows + [benchmark], benchmark)
        self.assertEqual([r['trading_neutral'] for r in rows], [True, False])
        self.assertEqual([r['earnings_vs_benchmark_usd'] for r in rows], [0.0, 0.0])
        self.assertEqual([r['ceiling_capture'] for r in rows], [0.8, 0.9])
        self.assertEqual(benchmark['ceiling_capture'], 0.1)
        self.assertTrue(all(r['book_ceiling_usd'] == 1000.0 for r in rows))

    def test_out_earning_the_benchmark_is_recorded_not_rejected(self):
        # Dying early sits out whatever the benchmark went on to trade, and
        # that stretch can lose money. The benchmark bounds survival, not
        # earnings, so this is a result to report rather than an error.
        benchmark = {'policy': 'hold', 'retained_balance_usd': None,
                     'booked_net_trading_usd': 1000.0, 'path_ceiling_usd': 1000.0,
                     'combined_pocket_usd': 100.0, 'path_fingerprint': 'benchmarkpath'}
        row = {'policy': 'dodged_a_losing_stretch', 'retained_balance_usd': 30000.0,
               'booked_net_trading_usd': 1060.0, 'combined_pocket_usd': 1010.0,
               'path_fingerprint': 'diedearlier'}
        annotate_against_benchmark([row], benchmark)
        self.assertFalse(row['trading_neutral'])
        self.assertEqual(row['earnings_vs_benchmark_usd'], 60.0)
        self.assertGreater(row['ceiling_capture'], 1.0)

    def test_fingerprint_separates_paths_that_share_a_total(self):
        class Book:
            def __init__(self, accounts): self.accounts = accounts

        def account(account_id, trades, gross):
            return type('A', (), {'account_id': account_id, 'trades_taken': trades,
                                  'gross_pnl_usd': gross, 'commission_usd': 1.0,
                                  'death_trade_key': None})()
        same = Book([account(1, 10, 400.0), account(2, 10, 600.0)])
        # Identical account count, trade count and total; different per account.
        shuffled = Book([account(1, 10, 600.0), account(2, 10, 400.0)])
        died = Book([account(1, 10, 400.0), account(2, 9, 600.0)])
        self.assertEqual(path_fingerprint(same),
                         path_fingerprint(Book(list(reversed(same.accounts)))))
        self.assertNotEqual(path_fingerprint(same), path_fingerprint(shuffled))
        self.assertNotEqual(path_fingerprint(same), path_fingerprint(died))

    def test_a_cushion_alone_does_not_move_a_book_off_the_benchmark_path(self):
        # This tape never kills an account, so nothing a cushion does can cost
        # a trade. Every setting must fingerprint to the benchmark path: a
        # cushion is a rule about asking, not a rule about trading.
        hold = measure(self.trades, self.config, WithdrawalPolicy(name='hold'), None)
        rows = [measure(self.trades, self.config, policies()[1], level)
                for level in (None, 26100, 30000, 35100)]
        annotate_against_benchmark(rows, hold)
        self.assertTrue(all(r['trading_neutral'] for r in rows))
        self.assertEqual({r['earnings_vs_benchmark_usd'] for r in rows}, {0.0})
        # Same trades, different cash: the scores still have to move.
        self.assertGreater(len({r['combined_pocket_usd'] for r in rows}), 1)

    def test_ceiling_ignores_how_the_split_and_standing_profit_landed(self):
        class Fake:
            booked_net_trading_usd = 500.0
            failed_positive_ledger_usd = 20.0
            failed_negative_ledger_usd = 30.0
            purchase_fees_usd = 40.0
        self.assertEqual(path_ceiling(Fake()), 470.0)

    def test_targets_share_rounding_except_explicit_legacy_control(self):
        choices=policies()
        self.assertEqual(len({p.name for p in choices}),len(choices))
        for p in choices:
            self.assertEqual(p.quantize_to_amount,p.name=='legacy_500_blocks')

    def test_delay_is_rejected_instead_of_counting_unreceived_terminal_cash(self):
        payload=self.config.rulebook.to_payload()
        payload['processing_delay']={'enabled':True,'days':10}
        config=replace(self.config,rulebook=type(self.config.rulebook).from_payload(payload))
        with self.assertRaises(ValueError): measure(self.trades,config,policies()[0],None)
