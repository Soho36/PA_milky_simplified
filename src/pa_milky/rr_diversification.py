"""Fixed per-account RR variants on the shared cash/entry/exit event clock.

Exported death times are exit-time proxies. Same-signal and interval-overlap
metrics accompany them so longer exits cannot alone count as diversification.
"""
from collections import Counter
from datetime import datetime, time, timedelta
from functools import partial

from .routing import RoutingPolicy, TradeRouter


def signal_key(trade):
    return (trade.window_id, trade.entry_at)


class RRRouter(TradeRouter):
    def __init__(self, trades, policy, *, weights, trade_rr, **kwargs):
        if policy.mode != 'blocked' or kwargs.get('demand') is not None or kwargs.get('provision') is not None:
            raise ValueError('RR portfolios require blocked copying without demand overrides')
        if not weights or any(not isinstance(n, int) or isinstance(n, bool) or n < 1 for n in weights.values()):
            raise ValueError('RR weights must be positive integers')
        self.weights = dict(weights)
        self.trade_rr = trade_rr
        self.account_rr = {}
        self.accounts = []
        super().__init__(trades, policy, **kwargs)

    def assign(self, accounts):
        self.accounts = accounts
        live = Counter(self.account_rr[a.account_id] for a in accounts
                       if a.alive and a.account_id in self.account_rr)
        for account in accounts:
            if account.account_id not in self.account_rr:
                # Fill the most underrepresented group; assignments never change
                # while an account lives. Deaths therefore create replacement demand
                # for the depleted group instead of gradually erasing that strategy.
                rr = min(self.weights, key=lambda key: live[key] / self.weights[key])
                self.account_rr[account.account_id] = rr
                live[rr] += int(account.alive)

    def enter(self, accounts):
        self.assign(accounts)
        trade = self.entries[self.index][1]
        rr = self.trade_rr[trade.trade_key]
        super().enter([a for a in accounts if self.account_rr[a.account_id] == rr])
        self.fills[-1].update(rr=rr, window=trade.window_id)

    def summary(self):
        self.assign(self.accounts)
        return {**super().summary(), 'weights': self.weights, 'account_rr': self.account_rr}


def run_rr_book(tapes, config, weights, *, acquisition=None, fixed_accounts=None, observer=None):
    from .simulator import run_book
    variants = set(weights)
    if acquisition is not None and acquisition.evaluation is not None:
        variants.add('1.00')
    trades = [t for rr in sorted(variants) for t in tapes[rr]]
    trades.sort(key=lambda t: (t.exit_at, t.entry_at, t.window_order, t.source_row, t.ticket, t.trade_key))
    trade_rr = {t.trade_key: rr for rr in variants for t in tapes[rr]}
    if len(trade_rr) != len(trades):
        raise ValueError('RR tapes must have distinct trade keys')
    return run_book(trades, config, acquisition=acquisition, fixed_accounts=fixed_accounts,
                    observer=observer, routing=RoutingPolicy(mode='blocked'),
                    router_factory=partial(RRRouter, weights=weights, trade_rr=trade_rr),
                    evaluation_tape=tapes['1.00'] if acquisition is not None and acquisition.evaluation is not None else None)


def mortality_metrics(result, trades):
    """Rolling losses of the cohort alive at a day's start; replacements excluded.

    Windows use observed tape trading dates. Half-loss episodes require at least
    five accounts at the window start and use disjoint windows. Interval overlap
    is a conservative possible death cluster, not an assertion of exact timing.
    """
    lookup = {t.trade_key: t for t in trades}
    dates = sorted({t.entry_at.date() for t in trades} | {t.exit_at.date() for t in trades})
    accounts = result.accounts
    deaths = [a for a in accounts if not a.alive]
    by_signal = Counter(signal_key(lookup[a.death_trade_key]) for a in deaths)
    metrics = {'max_same_signal_deaths': max(by_signal.values(), default=0),
               'same_signal_multi_death_events': sum(n > 1 for n in by_signal.values())}
    intervals = [(lookup[a.death_trade_key].entry_at, a.died_at, a.account_id) for a in deaths]
    for days in (1, 5, 20):
        best_count = best_raw = best_possible = 0
        best_fraction = 0.0
        best_at = None
        half_episodes = 0
        next_episode = datetime.min
        for index, day in enumerate(dates):
            start = datetime.combine(day, time())
            end = (datetime.combine(dates[index+days], time()) if index+days < len(dates)
                   else datetime.combine(dates[-1]+timedelta(days=1), time()))
            cohort = [a for a in accounts if a.activated_at <= start and (a.alive or a.died_at >= start)]
            lost = sum(not a.alive and a.died_at < end for a in cohort)
            raw = sum(start <= a.died_at < end for a in deaths)
            possible = sum(entry < end and exit_at >= start for entry, exit_at, _ in intervals)
            best_count = max(best_count, lost)
            best_raw = max(best_raw, raw)
            best_possible = max(best_possible, possible)
            fraction = lost / len(cohort) if cohort else 0
            if fraction > best_fraction:
                best_fraction, best_at = fraction, start.isoformat()
            if len(cohort) >= 5 and fraction >= .5 and start >= next_episode:
                half_episodes += 1
                next_episode = end
        metrics.update({f'worst_{days}d_cohort_deaths': best_count,
                        f'worst_{days}d_fraction': round(best_fraction, 6),
                        f'worst_{days}d_at': best_at,
                        f'half_loss_{days}d_episodes_min5': half_episodes,
                        f'peak_{days}d_replacement_demand': best_raw,
                        f'possible_{days}d_death_cluster': best_possible})
    events = Counter()
    for account in accounts:
        events[account.activated_at] += 1
        if not account.alive:
            events[account.died_at] -= 1
    live = 0
    empty_days = 0.0
    wipes = 0
    previous = result.tape_first_entry
    had_accounts = False
    for at, delta in sorted(events.items()):
        if at > result.tape_last_exit:
            continue
        if live == 0 and had_accounts:
            empty_days += max(0, (at-previous).total_seconds()/86400)
        after = live+delta
        wipes += int(live > 0 and after == 0)
        had_accounts |= after > 0
        live, previous = after, at
    if live == 0 and had_accounts:
        empty_days += max(0, (result.tape_last_exit-previous).total_seconds()/86400)
    metrics.update(book_wipeouts=wipes, days_empty_after_first_activation=round(empty_days, 4),
                   deaths=len(deaths), accounts=len(accounts), alive=result.alive_at_horizon)
    return metrics
