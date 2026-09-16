"""Entry-time allocation of whole trades; no adding to an occupied account.

The tape contains completed trades, not working-order lifetimes. Slots are held
from entry through exit; exits precede new entries at the same timestamp.
"""
from dataclasses import dataclass, asdict
import heapq
import hashlib
import json


def entry_key(trade):
    # Never use exit time or eventual P&L to prioritize simultaneous offers.
    return (trade.entry_at, trade.window_order, trade.source_row, trade.ticket)


def capacity_audit(trades):
    ends = []
    peak = 0
    peak_at = None
    histogram = {}
    for trade in sorted(trades, key=entry_key):
        if trade.exit_at < trade.entry_at:
            raise ValueError("Trade exit precedes entry")
        while ends and ends[0] <= trade.entry_at:
            heapq.heappop(ends)
        heapq.heappush(ends, trade.exit_at)
        count = len(ends)
        histogram[count] = histogram.get(count, 0) + 1
        if count > peak:
            peak, peak_at = count, trade.entry_at
    return {"trades": len(trades), "peak_positions": peak,
            "first_peak_at": peak_at.isoformat() if peak_at else None,
            "occupancy_after_entry_counts": histogram,
            "zero_duration_trades": sum(t.entry_at == t.exit_at for t in trades),
            "interval_convention": "[entry, exit); existing exits first; zero-duration offers enter then immediately exit"}


@dataclass(frozen=True)
class RoutingPolicy:
    mode: str = "routed"
    copies: int = 1
    allocation: str = "max_headroom"

    def __post_init__(self):
        if self.mode not in {"routed", "blocked"}:
            raise ValueError("Unknown routing mode")
        if not isinstance(self.copies, int) or isinstance(self.copies, bool) or self.copies < 1:
            raise ValueError("copies must be a positive integer")
        if self.allocation not in {"max_headroom", "round_robin"}:
            raise ValueError("Unknown allocation")


class TradeRouter:
    def __init__(self, trades, policy, *, demand=None, provision=None):
        capacity_audit(trades)
        self.policy = policy
        self.demand = demand
        self.provision = provision
        self.entries = sorted(enumerate(trades), key=lambda pair: entry_key(pair[1]))
        self.index = 0
        self.busy = set()
        self.assignments = {}
        self.last_account = 0
        self.offered = self.requested = self.filled = 0
        self.fully_filled = self.partial = self.missed = 0
        self.busy_shortfall = self.inventory_shortfall = 0
        self.fills = []
        self.peak_occupied = 0

    @property
    def next_entry(self):
        return self.entries[self.index][1].entry_at if self.index < len(self.entries) else None

    def enter(self, accounts):
        index, trade = self.entries[self.index]
        before = [a for a in accounts if a.alive and a.activated_at <= trade.entry_at]
        free_before = sum(a.account_id not in self.busy for a in before)
        if self.demand is not None and self.provision is not None:
            free_count = sum(a.alive and a.activated_at <= trade.entry_at
                             and a.account_id not in self.busy for a in accounts)
            self.provision(trade.entry_at, max(0, self.demand[index] - free_count))
        eligible = [a for a in accounts if a.alive and a.activated_at <= trade.entry_at]
        free = [a for a in eligible if a.account_id not in self.busy]
        wanted = (self.demand[index] if self.demand is not None else
                  len(eligible) if self.policy.mode == "blocked" else self.policy.copies)
        if self.policy.allocation == "max_headroom":
            free.sort(key=lambda a: (-a.headroom_usd, a.account_id))
        else:
            free.sort(key=lambda a: (a.account_id <= self.last_account, a.account_id))
        selected = free[:wanted]
        if selected:
            self.last_account = selected[-1].account_id
        self.assignments[index] = selected
        self.busy.update(a.account_id for a in selected)
        self.peak_occupied = max(self.peak_occupied, len(self.busy))
        self.offered += 1
        self.requested += wanted
        self.filled += len(selected)
        self.inventory_shortfall += max(0, wanted - len(eligible))
        self.busy_shortfall += min(wanted, len(eligible)) - len(selected)
        self.fully_filled += int(wanted > 0 and len(selected) == wanted)
        self.partial += int(0 < len(selected) < wanted)
        self.missed += int(wanted > 0 and not selected)
        self.fills.append({"trade_key": trade.trade_key,
                           "entry_at": trade.entry_at.isoformat(),
                           "exit_at": trade.exit_at.isoformat(),
                           "requested": wanted, "alive": len(eligible), "free": len(free),
                           "free_before_purchase": free_before,
                           "purchased": len(eligible) - len(before),
                           "accounts": [a.account_id for a in selected]})
        self.index += 1

    def exit(self, index, trade, *, commission, path_order):
        selected = self.assignments.pop(index)
        for account in selected:
            self.busy.remove(account.account_id)
            if account.alive:
                account.apply(trade, commission_usd=commission, path_order=path_order)
        return len(selected)

    def summary(self):
        return {"policy": asdict(self.policy),
                "demand_source": 'per_trade_override' if self.demand is not None else 'policy',
                "signals_offered": self.offered,
                "copies_requested": self.requested, "copies_filled": self.filled,
                "signals_fully_filled": self.fully_filled,
                "signals_partially_filled": self.partial, "signals_missed": self.missed,
                "copies_missed_busy": self.busy_shortfall,
                "copies_missed_inventory": self.inventory_shortfall,
                "peak_occupied_accounts": self.peak_occupied,
                "allocation_sha256": hashlib.sha256(json.dumps(self.fills, sort_keys=True).encode()).hexdigest(),
                "copy_coverage": self.filled / self.requested if self.requested else None}
