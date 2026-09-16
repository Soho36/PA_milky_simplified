"""Matched-exposure counterfactuals, not a deployable purchase policy.

Freeze a reference run's accepted copies ex post. Replaying that demand changes
its account placement, never adds signals that the reference missed through
account death. Purchase dates are also frozen to prevent funding feedback from
changing the treatment. Additional routed seats are externally financeable.
"""
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

from .account import money
from .economics import Economics
from .routing import RoutingPolicy, capacity_audit
from .simulator import run_book


@dataclass
class ReplayPlan:
    demand: list[int]
    purchases: dict[datetime, int]
    purchase_events: list = field(default_factory=list)
    peak_live: int = 0
    procurement: str = "five_per_purchase"
    max_live_accounts: int | None = None

    def __post_init__(self):
        if self.procurement not in {'five_per_purchase', 'reuse', 'fixed_pool'}:
            raise ValueError('Unknown procurement mode')
        if self.max_live_accounts is not None and (not isinstance(self.max_live_accounts, int)
                                                  or self.max_live_accounts < 1):
            raise ValueError('Live-account cap must be positive')

    def record_purchase(self, at, count, accounts, *, emergency):
        self.purchase_events.append({"at": at.isoformat(), "count": count,
                                     "emergency": emergency})
        self.peak_live = max(self.peak_live, sum(a.alive for a in accounts))


def reference_run(trades, config, acquisition):
    demand = []
    peak_live = 0

    def observe(at, accounts, event, trade):
        nonlocal peak_live
        peak_live = max(peak_live, sum(a.alive for a in accounts))
        if event == "before_trade":
            demand.append(sum(a.alive and a.activated_at <= trade.entry_at for a in accounts))

    result = run_book(trades, config, acquisition=acquisition, observer=observe)
    if len(demand) != len(trades) or sum(demand) != result.copies_filled:
        raise ValueError("Reference demand does not reconcile")
    return result, demand, peak_live


def replay_run(trades, reference, demand, *, allocation, capacity, procurement='reuse'):
    if len(demand) != len(trades) or any(not isinstance(n, int) or n < 0 for n in demand):
        raise ValueError("Invalid reference demand")
    if capacity < capacity_audit(trades)["peak_positions"]:
        raise ValueError("Initial capacity multiplier is below the tape requirement")
    purchases = Counter()
    if procurement == 'five_per_purchase':
        for account in reference.accounts:
            purchases[account.activated_at] += capacity
    elif procurement != 'reuse':
        raise ValueError('Unknown replay procurement')
    # Reuse starts empty and buys precisely the free-slot deficit at entry.
    # A new reference purchase changes demand, not the physical purchase count.
    plan = ReplayPlan(list(demand), dict(purchases), procurement=procurement)
    result = run_book(trades, reference.config, routing=RoutingPolicy(allocation=allocation), replay=plan)
    if result.copies_filled != sum(demand) or result.routing["copy_coverage"] not in (None, 1.0):
        raise ValueError("Matched replay lost exposure")
    if sum(p["count"] for p in plan.purchase_events) != len(result.accounts):
        raise ValueError("Replay purchase ledger does not reconcile")
    return result, plan


def fixed_pool_run(trades, config, *, copies, allocation, initial_seats, max_live_accounts=20):
    if copies < 1 or not isinstance(copies, int):
        raise ValueError('copies must be a positive integer')
    if initial_seats < 1 or initial_seats > max_live_accounts:
        raise ValueError('Initial seats must fit the live-account cap')
    first = min(t.entry_at for t in trades)
    start = datetime(first.year, first.month, 1)
    plan = ReplayPlan([copies] * len(trades), {start: initial_seats},
                      procurement='fixed_pool', max_live_accounts=max_live_accounts)
    result = run_book(trades, config, routing=RoutingPolicy(copies=copies, allocation=allocation),
                      replay=plan)
    return result, plan


def demand_digest(trades, demand):
    material = [(t.trade_key, n) for t, n in zip(trades, demand)]
    return hashlib.sha256(json.dumps(material).encode()).hexdigest()


def measure(result, peak_live):
    economics = Economics.measure(result)
    if economics.residual_usd != 0:
        raise ValueError("Economic ledger failed to reconcile")
    terminal = money(sum(e.received_usd for e in result.terminal_payouts))
    return {"accounts": len(result.accounts), "alive": result.alive_at_horizon,
            "deaths": len(result.dead), "peak_live": peak_live,
            "exceeds_20_live": peak_live > 20,
            "copies": result.copies_filled, "purchase_cost_usd": result.total_purchase_cost_usd,
            "ongoing_net_usd": money(result.pocket_usd - terminal),
            "terminal_received_usd": terminal, "total_net_usd": result.pocket_usd,
            "economics": economics.to_payload(), "routing": result.routing}


def required_topups(result, plan, reference):
    """Extra external funding beyond the reference's owner contribution schedule.

    Allow recycling actual receipts. At a shared timestamp receipts/contributions
    precede purchases, matching the simulator's payout-before-purchase convention.
    """
    contributions = []
    for e in reference.acquisition.cash_events:
        if e["kind"] == "owner_contribution":
            at = e["at"] if isinstance(e["at"], datetime) else datetime.fromisoformat(e["at"])
            contributions.append((at, e['amount_usd']))
    return funding_requirements(result, plan, contributions)


def funding_requirements(result, plan, contributions):
    """Unconstrained funding need, not permission to spend within a budget."""
    events = [(e.at, 0, e.received_usd) for e in result.payouts]
    events += [(at, 0, amount) for at, amount in contributions]
    events += [(datetime.fromisoformat(e["at"]), 1, -e["count"] * result.config.purchase_fee_usd)
               for e in plan.purchase_events]
    cash = topups = 0.0
    for at, priority, amount in sorted(events):
        cash = money(cash + amount)
        if cash < 0:
            topups = money(topups - cash)
            cash = 0.0
    return {"additional_external_funding_usd": topups, "ending_owner_cash_usd": cash}
