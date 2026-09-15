"""Passive, event-weighted balance dispersion for reserve comparisons."""
from math import sqrt
from .reserve_metrics import ReserveObserver


def group_state(accounts):
    """Population spread; do not count empty/singleton groups as synchronized."""
    if len(accounts) < 2:
        return (0, 0, 0, 0, 0)
    values = [a.equity_profit_usd for a in accounts]
    mean = sum(values)/len(values)
    distinct = len(set(values))
    return (1, sqrt(sum((v-mean)**2 for v in values)/len(values)),
            max(values)-min(values), distinct, int(distinct == 1))


class DispersionObserver(ReserveObserver):
    def __init__(self, first, last, *, trace=False):
        super().__init__(first, last, trace=trace)
        self.groups = {'live': (0,)*5, 'frozen': (0,)*5}
        self.areas = {key: [0.0]*5 for key in self.groups}
        self.prior_alive = 0
        self.empty_transitions = 0
        self.large_book_wipes = 0
        self.snapshots = []

    def __call__(self, at, accounts, event, trade):
        if event == 'before_trade':
            if at.isoformat() == '2026-03-30T06:00:00':
                live = [a for a in accounts if a.alive]
                self.snapshots.append({'at': at.isoformat(), 'alive': len(live),
                    'distinct_balances': len({a.equity_profit_usd for a in live}),
                    'min_profit': min((a.equity_profit_usd for a in live), default=None),
                    'max_profit': max((a.equity_profit_usd for a in live), default=None),
                    'accounts': [{'id': a.account_id, 'profit': a.equity_profit_usd,
                                  'cushion': a.headroom_usd} for a in live]})
            super().__call__(at, accounts, event, trade)
            return
        clipped = min(self.last, max(self.first, at))
        days = (clipped-self.at).total_seconds()/86400
        if days < 0:
            raise ValueError('Dispersion events out of order')
        for key, state in self.groups.items():
            for i, value in enumerate(state):
                self.areas[key][i] += days*value
        super().__call__(at, accounts, event, trade)
        live = [a for a in accounts if a.alive]
        if self.prior_alive and not live:
            self.empty_transitions += 1
            self.large_book_wipes += int(self.prior_alive >= 5)
        self.prior_alive = len(live)
        self.groups['live'] = group_state(live)
        self.groups['frozen'] = group_state([a for a in live
            if a.floor_profit_usd == a.frozen_floor_profit_usd])

    def summary(self):
        result = super().summary()
        for key, area in self.areas.items():
            days = area[0]
            result[key+'_multiple_account_days'] = round(days, 4)
            for i, metric in enumerate(('mean_balance_std_usd', 'mean_balance_range_usd',
                                        'mean_distinct_balances', 'identical_balance_fraction'), 1):
                result[key+'_'+metric] = round(area[i]/days, 4) if days else None
        snapshot = self.snapshots[-1] if self.snapshots else {}
        result.update(book_empty_transitions=self.empty_transitions,
            book_wipes_from_at_least_five_live=self.large_book_wipes,
            march30_pretrade_alive=snapshot.get('alive'),
            march30_pretrade_distinct=snapshot.get('distinct_balances'),
            march30_pretrade_profit_min=snapshot.get('min_profit'),
            march30_pretrade_profit_max=snapshot.get('max_profit'))
        return result
