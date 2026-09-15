"""Observe retained profit at simulator event times without changing decisions.

The integral uses settled equity between events, not an invented intratrade
mark-to-market path. Nominal account balances are never treated as capital.
"""
class ReserveObserver:
    def __init__(self, first, last, *, trace=False):
        self.first, self.last = first, last
        self.at = first
        self.state = (0, 0.0, 0.0, 0.0)
        self.integrals = [0.0] * 4
        self.trace = trace
        self.trade_trace = []
        self.before = {}

    def __call__(self, at, accounts, event, trade):
        if event == 'before_trade':
            if self.trace and '2026-03-01' <= at.isoformat() < '2026-04-01':
                self.before = {a.account_id: (a.equity_profit_usd, a.floor_profit_usd)
                               for a in accounts if a.alive and a.activated_at <= trade.entry_at}
            return
        clipped = min(self.last, max(self.first, at))
        if clipped < self.at:
            raise ValueError('Observer events are out of order')
        days = (clipped-self.at).total_seconds()/86400
        for i, value in enumerate(self.state):
            self.integrals[i] += days*value
        self.at = clipped
        live = [a for a in accounts if a.alive]
        self.state = (len(live), sum(a.equity_profit_usd for a in live),
                      sum(max(0, a.equity_profit_usd) for a in live),
                      sum(a.headroom_usd for a in live))
        if event == 'trade' and self.before:
            for a in accounts:
                if a.account_id not in self.before:
                    continue
                equity, floor = self.before[a.account_id]
                self.trade_trace.append({
                    'at': at.isoformat(), 'account_id': a.account_id, 'trade_key': trade.trade_key,
                    'entry_at': trade.entry_at.isoformat(), 'equity_before': equity,
                    'floor_before': floor, 'mae': trade.mae_usd, 'mfe': trade.mfe_usd,
                    'gross_pnl': trade.gross_pnl_usd,
                    'adverse_equity': round(equity+min(0, trade.mae_usd), 2),
                    'equity_after': a.equity_profit_usd, 'floor_after': a.floor_profit_usd,
                    'alive_after': a.alive, 'death_equity': a.death_equity_usd if not a.alive else None})
            self.before = {}

    def summary(self):
        days = (self.last-self.first).total_seconds()/86400
        live_days, equity_days, positive_days, cushion_days = self.integrals
        return {
            'observed_days': round(days, 4),
            'live_pa_days': round(live_days, 4),
            'average_live_pas_event_weighted': round(live_days/days, 4),
            'vacant_capacity_days_including_startup': round(20*days-live_days, 2),
            'average_retained_profit_book': round(equity_days/days, 2),
            'average_positive_retained_profit_book': round(positive_days/days, 2),
            'average_retained_profit_per_live_pa': round(equity_days/live_days, 2) if live_days else None,
            'average_actual_cushion_book': round(cushion_days/days, 2),
            'average_actual_cushion_per_live_pa': round(cushion_days/live_days, 2) if live_days else None}
