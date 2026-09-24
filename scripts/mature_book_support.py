"""Study-local calendar/owned-inventory adapter; the shared engine is unchanged."""
import ast
import inspect
from collections import Counter
from datetime import datetime, timedelta
from pa_milky.acquisition import AcquisitionLedger
from pa_milky.simulator import run_book


class OwnedInventoryLedger(AcquisitionLedger):
    def decide(self, at, month_index, alive, account_count, fee):
        if not self.seed_bought:
            assert alive == account_count == 0
            self.seed_bought = True
            self.filled_month_slots.add((at.year, at.month))
            self.decisions.append(dict(at=at.isoformat(), wanted=20, bought=20,
                                       alive_before=0, initial_owned_inventory=True,
                                       cash_limited=False, capacity_limited=False, supply_limited=False))
            return 20
        return super().decide(at, month_index, alive, account_count, fee)


def calendar_runner(start, end):
    """Pin the two horizon assignments; keep unsettled trades in the router."""
    tree = ast.parse(inspect.getsource(run_book))
    changed = []
    for node in tree.body[0].body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('first_entry', 'last_exit'):
                node.value = ast.Name(id='STUDY_START' if name == 'first_entry' else 'STUDY_LAST', ctx=ast.Load())
                changed.append(name)
    assert changed == ['first_entry', 'last_exit']
    ast.fix_missing_locations(tree)
    namespace = dict(run_book.__globals__, AcquisitionLedger=OwnedInventoryLedger,
                     STUDY_START=start, STUDY_LAST=end - timedelta(microseconds=1))
    exec(compile(tree, '<mature-study-calendar-adapter>', 'exec'), namespace)
    return namespace['run_book']


def endow(accounts, start, headroom, frozen_profit):
    assert len(accounts) == 20
    for a in accounts:
        assert a.activated_at == start and a.trades_taken == 0 and a.equity_profit_usd == 0
        a.purchase_fee_usd = 0
        a.equity_profit_usd = headroom + frozen_profit
        a.peak_profit_usd = a.equity_profit_usd
        a.floor_profit_usd = frozen_profit
        a.max_equity_profit_usd = a.min_equity_profit_usd = a.equity_profit_usd
        assert a.headroom_usd == headroom


def capacity_metrics(accounts, start, end, stress_end):
    """Event-clock occupancy and first sub-20 recovery; exit-time death proxies."""
    events = Counter()
    for a in accounts:
        events[datetime.fromisoformat(a['activated_at'])] += 1
        if not a['alive']:
            events[datetime.fromisoformat(a['died_at'])] -= 1
    live = 0
    previous = start
    low = 20
    durations = {5: 0.0, 10: 0.0, 20: 0.0}
    empty = 0.0
    wipes = 0
    opened = None
    recoveries = []
    first_loss = None
    for at, delta in sorted(events.items()):
        if at >= end:
            continue
        days = (at - previous).total_seconds() / 86400
        for threshold in durations:
            durations[threshold] += days * (live < threshold)
        empty += days * (live == 0)
        after = live + delta
        assert 0 <= after <= 20
        if at > start and after < 20 and live == 20:
            opened = at
            first_loss = first_loss or at
        if opened is not None and after == 20:
            recoveries.append(dict(loss_at=opened.isoformat(), restored_at=at.isoformat(),
                                   days=(at - opened).total_seconds() / 86400, censored=False))
            opened = None
        wipes += int(live > 0 and after == 0)
        live, previous = after, at
        low = min(low, live)
    days = (end - previous).total_seconds() / 86400
    for threshold in durations:
        durations[threshold] += days * (live < threshold)
    empty += days * (live == 0)
    if opened is not None:
        recoveries.append(dict(loss_at=opened.isoformat(), restored_at='',
                               days=(end - opened).total_seconds() / 86400, censored=True))
    first = recoveries[0] if recoveries else None
    first_stress = first is not None and datetime.fromisoformat(first['loss_at']) < stress_end
    return dict(min_live=low, empty_days=empty, wipeouts=wipes, end_live=live,
                days_below_5=durations[5], days_below_10=durations[10], days_below_20=durations[20],
                had_loss=first is not None, first_loss_in_stress=first_stress,
                first_restored=bool(first and not first['censored']),
                first_recovery_days=first['days'] if first and not first['censored'] else '',
                first_unrecovered_followup_days=first['days'] if first and first['censored'] else '',
                recoveries=recoveries)
