from datetime import datetime,timedelta
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from rr_curve_support import select_trades,daily_path,curve_metrics,first_markers,failure_metrics
from study_rr_curves import router_selection
from pa_milky.loader import Trade


def trade(i,at,duration,pnl,mae=0):
    return Trade(str(i),'1-2',1,i,i,at,at+timedelta(hours=duration),mae,max(0,pnl),pnl,100)


class CurveTests(unittest.TestCase):
    def test_horizon_censoring_does_not_free_a_busy_slot(self):
        at=datetime(2020,1,1)
        tape=[trade(1,at,48,500),trade(2,at+timedelta(hours=1),1,1000)]
        end=at+timedelta(days=1)
        chosen=select_trades(tape,at,end)
        self.assertEqual([t.trade_key for t in chosen],['1'])
        self.assertEqual(router_selection(tape,at,end),['1'])
        self.assertEqual(daily_path(chosen,['2020-01-01'],end,0),[0])
        self.assertTrue(all(x is None for x in first_markers(chosen,100,end,0).values()))

    def test_same_time_exit_and_zero_duration_match_router(self):
        at=datetime(2020,1,1)
        tape=[trade(1,at,1,10),trade(2,at+timedelta(hours=1),0,20),
              trade(3,at+timedelta(hours=1),1,30)]
        chosen=select_trades(tape,at,at+timedelta(days=1))
        self.assertEqual([t.trade_key for t in chosen],['1','2','3'])
        self.assertEqual(router_selection(tape,at,at+timedelta(days=1)),['1','2','3'])

    def test_intratrade_breach_is_marked_without_truncating_curve(self):
        at=datetime(2020,1,1); end=at+timedelta(days=3)
        chosen=[trade(1,at,1,100,mae=-2000),trade(2,at+timedelta(days=1),1,200)]
        markers=first_markers(chosen,1500,end,0)
        self.assertIsNone(markers['closed_floor'])
        self.assertEqual(markers['excursion_floor']['trade_key'],'1')
        self.assertEqual(markers['excursion_floor']['interval_start'],at.isoformat())
        self.assertEqual(daily_path(chosen,['2020-01-01','2020-01-02'],end,0),[100,300])

    def test_fixed_floor_differs_from_peak_drawdown(self):
        at=datetime(2020,1,1)
        chosen=[trade(1,at,1,5000),trade(2,at+timedelta(days=1),1,-2000,mae=-2000)]
        m=first_markers(chosen,1500,at+timedelta(days=3),0)
        self.assertIsNone(m['excursion_floor']); self.assertIsNotNone(m['closed_peak_dd'])

    def test_recovery_and_unrecovered_episode(self):
        m,e=curve_metrics([100,40,120,70],['2020-01-01','2020-01-02','2020-01-03','2020-01-04'],'2020-01-01')
        self.assertEqual(m['max_drawdown'],60)
        self.assertEqual(m['longest_underwater_trading_dates'],2)
        self.assertEqual(m['recovered_episodes'],1)
        self.assertTrue(m['unrecovered_at_end'])

    def test_duplicate_rr_marker_weights_do_not_diversify(self):
        m={'window':'1-2','entry':'2020-01-01T01:00:00','exit':'2020-01-02T01:00:00',
           'interval_start':'2020-01-01T01:00:00'}
        result=failure_metrics(['1.00','1.00'],{'1.00':m},['2020-01-01','2020-01-02'])
        self.assertEqual(result['fraction_breached'],1)
        self.assertEqual(result['max_same_signal_fraction'],1)
        self.assertEqual(result['possible_1d_fraction'],1)


if __name__=='__main__':unittest.main()
