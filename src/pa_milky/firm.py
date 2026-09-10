"""The firm's payout rulebook.

Every rule Apex applies to a Legacy 25K payout lives here, each independently
switchable. Turning them all off reproduces the ideal world; turning them all
on is the real product. Because each rule is separable, the cost of any one of
them is an ablation run away rather than a rebuild.

The rule text is in the parent project's ``rules/Payout_rules.txt``. Where that
text is ambiguous the reading is a named option, not a silent choice.

A rule can do three things. It can **block** a request outright, it can **cap**
the amount, and -- only the split -- it can change what we *receive* without
changing what leaves the account.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from .account import Account, money

# Blocking rules are consulted in this order, so a denial ledger attributes a
# blocked request to the first rule that stopped it. Every blocker is recorded
# too, because "which rule was first" is an artefact of this ordering and
# "which rules would have blocked" is not.
BLOCK_ORDER = (
    "minimum_balance",
    "trading_days",
    "profitable_days",
    "consistency",
)

SPLIT_MODES = ("cumulative_threshold", "after_n_payouts")

# A payout may never take an account to its trailing threshold. This is the
# account specification, not a firm payout rule, so it is always on and is not
# part of the switchable rulebook. The cent keeps a touch from being a kill.
TOUCH_MARGIN_USD = 0.01


@dataclass(frozen=True, slots=True)
class RequestContext:
    account: Account
    at: datetime
    requested_usd: float
    payout_number: int
    starting_balance_usd: float
    trailing_floor_balance_usd: float

    @property
    def balance_usd(self) -> float:
        return self.account.balance_usd

    @property
    def profit_balance_usd(self) -> float:
        return money(self.account.balance_usd - self.starting_balance_usd)


@dataclass(frozen=True, slots=True)
class Decision:
    approved: bool
    requested_usd: float
    allowed_usd: float
    gross_usd: float
    received_usd: float
    blocked_by: str | None
    blockers: tuple[str, ...]
    binding_cap: str | None
    caps: dict[str, float]


# --------------------------------------------------------------------- rules


@dataclass(frozen=True, slots=True)
class Rule:
    key: str
    enabled: bool
    params: dict

    def applies(self, ctx: RequestContext) -> bool:
        """Whether this rule is live for this particular request number."""

        through = self.params.get("applies_through_payout")
        if through is None:
            return True
        return ctx.payout_number <= int(through)

    def blocks(self, ctx: RequestContext) -> bool:
        return False

    def cap(self, ctx: RequestContext) -> float | None:
        return None


@dataclass(frozen=True, slots=True)
class MinimumBalance(Rule):
    """"Your account must meet the required minimum balance" -- $26,600 at 25K.

    The gate is flat: it does not move with the amount requested.
    """

    def blocks(self, ctx: RequestContext) -> bool:
        return ctx.balance_usd < float(self.params["balance_usd"])


@dataclass(frozen=True, slots=True)
class TradingDays(Rule):
    """"You must have completed at least 8 trading days" since the last request."""

    def blocks(self, ctx: RequestContext) -> bool:
        return ctx.account.trading_days_since_payout < int(self.params["required_days"])


@dataclass(frozen=True, slots=True)
class ProfitableDays(Rule):
    """"At least 5 of those days must show a profit of $50 or more"."""

    def blocks(self, ctx: RequestContext) -> bool:
        profitable = ctx.account.profitable_days_since_payout(
            float(self.params["profit_threshold_usd"])
        )
        return profitable < int(self.params["required_days"])


@dataclass(frozen=True, slots=True)
class Consistency(Rule):
    """The 30% windfall rule.

    No single trading day may be more than 30% of the profit balance at the
    request. The firm's own arithmetic: highest profit day / 0.3 is the minimum
    total profit required. Counters reset at each approved payout, and the rule
    stops applying from the sixth payout.
    """

    def blocks(self, ctx: RequestContext) -> bool:
        best = ctx.account.best_day_since_payout_usd
        if best <= 0:
            return False
        fraction = float(self.params["max_day_fraction"])
        return best > money(fraction * ctx.profit_balance_usd)


@dataclass(frozen=True, slots=True)
class SafetyNet(Rule):
    """The safety net for the first three payouts.

    The net is the drawdown plus $100 -- $26,600 at 25K. A request may encroach
    on it by exactly one minimum payout, so the balance may not fall below
    $26,100. Anything above the minimum must be fully covered above the net:
    for $1,200 the balance must be $26,600 + $700. Both statements are the one
    cap below.
    """

    def cap(self, ctx: RequestContext) -> float | None:
        floor = money(
            float(self.params["net_balance_usd"])
            - float(self.params["encroachment_allowance_usd"])
        )
        return money(ctx.balance_usd - floor)


@dataclass(frozen=True, slots=True)
class MaximumPayout(Rule):
    """"$1,500 (First Five Payouts)"; no maximum from the sixth."""

    def cap(self, ctx: RequestContext) -> float | None:
        return float(self.params["amount_usd"])


@dataclass(frozen=True, slots=True)
class MinimumPayout(Rule):
    """"Minimum Payout: $500 for any account size."

    Checked against the final amount, after every cap, because a request the
    caps have shrunk below the minimum is one the firm will not process.
    """

    @property
    def amount_usd(self) -> float:
        return float(self.params["amount_usd"])


@dataclass(frozen=True, slots=True)
class ProfitSplit(Rule):
    """"100% of the first $25,000 per account, and 90% of the profit after"."""

    def received(self, gross_usd: float, ctx: RequestContext) -> float:
        mode = self.params.get("mode", "cumulative_threshold")
        rate = float(self.params["reduced_rate"])
        if mode == "after_n_payouts":
            # The competing reading in the same document: 90% until five
            # payouts are complete, 100% from the sixth.
            through = int(self.params["full_rate_from_payout"])
            return money(gross_usd if ctx.payout_number >= through else gross_usd * rate)
        threshold = float(self.params["full_rate_threshold_usd"])
        already = ctx.account.gross_paid_usd
        at_full = max(0.0, min(gross_usd, threshold - already))
        at_reduced = gross_usd - at_full
        return money(at_full + at_reduced * rate)


@dataclass(frozen=True, slots=True)
class ProcessingDelay(Rule):
    """Calendar days between an approved request and cash in hand."""

    @property
    def days(self) -> int:
        return int(self.params["days"])


@dataclass(frozen=True, slots=True)
class DenialOnShortfall(Rule):
    """"If your account balance falls below the minimum ... it will be denied."

    Only reachable when a processing delay opens a gap between request and
    approval; with same-instant settlement there is nothing to fall below.
    """


RULE_TYPES: dict[str, type[Rule]] = {
    "minimum_balance": MinimumBalance,
    "trading_days": TradingDays,
    "profitable_days": ProfitableDays,
    "consistency": Consistency,
    "safety_net": SafetyNet,
    "maximum_payout": MaximumPayout,
    "minimum_payout": MinimumPayout,
    "profit_split": ProfitSplit,
    "processing_delay": ProcessingDelay,
    "denial_on_shortfall": DenialOnShortfall,
}


# ------------------------------------------------------------------ rulebook


@dataclass(frozen=True, slots=True)
class Rulebook:
    rules: dict[str, Rule] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict) -> "Rulebook":
        rules: dict[str, Rule] = {}
        for key, spec in payload.items():
            if key not in RULE_TYPES:
                raise ValueError(f"Unknown firm rule: {key!r}")
            spec = dict(spec)
            enabled = bool(spec.pop("enabled", False))
            rules[key] = RULE_TYPES[key](key=key, enabled=enabled, params=spec)
        missing = set(RULE_TYPES) - set(rules)
        if missing:
            raise ValueError(f"Firm rulebook is missing rules: {sorted(missing)}")
        return cls(rules=rules)

    def to_payload(self) -> dict:
        return {
            key: {"enabled": rule.enabled, **rule.params}
            for key, rule in sorted(self.rules.items())
        }

    def get(self, key: str) -> Rule:
        return self.rules[key]

    def is_on(self, key: str) -> bool:
        return self.rules[key].enabled

    @property
    def active_keys(self) -> tuple[str, ...]:
        return tuple(sorted(key for key, rule in self.rules.items() if rule.enabled))

    def without(self, key: str) -> "Rulebook":
        """The same rulebook with one rule switched off -- an ablation arm."""

        if key not in self.rules:
            raise ValueError(f"Unknown firm rule: {key!r}")
        rules = dict(self.rules)
        rule = rules[key]
        rules[key] = type(rule)(key=rule.key, enabled=False, params=rule.params)
        return Rulebook(rules=rules)

    @property
    def processing_delay_days(self) -> int:
        rule = self.rules["processing_delay"]
        return rule.days if rule.enabled else 0

    # --------------------------------------------------------------- decision

    def decide(
        self, ctx: RequestContext, quantize: Callable[[float], float] | None = None
    ) -> Decision:
        """Run one payout request through every switched-on rule."""

        if ctx.requested_usd <= 0:
            return Decision(
                approved=False,
                requested_usd=ctx.requested_usd,
                allowed_usd=0.0,
                gross_usd=0.0,
                received_usd=0.0,
                blocked_by="no_request",
                blockers=("no_request",),
                binding_cap=None,
                caps={},
            )

        blockers = tuple(
            key
            for key in BLOCK_ORDER
            if self.rules[key].enabled
            and self.rules[key].applies(ctx)
            and self.rules[key].blocks(ctx)
        )
        if blockers:
            return Decision(
                approved=False,
                requested_usd=ctx.requested_usd,
                allowed_usd=0.0,
                gross_usd=0.0,
                received_usd=0.0,
                blocked_by=blockers[0],
                blockers=blockers,
                binding_cap=None,
                caps={},
            )

        # The trailing threshold always caps a payout; it is the account, not a
        # switchable rule. Once the safety net expires it becomes the only cap.
        caps = {
            "trailing_floor": money(
                ctx.balance_usd - ctx.trailing_floor_balance_usd - TOUCH_MARGIN_USD
            )
        }
        minimum = self.rules['minimum_balance']
        post_from = minimum.params.get('retain_after_payout_from')
        if minimum.enabled and post_from is not None and ctx.payout_number >= int(post_from):
            caps['post_payout_minimum_balance'] = money(ctx.balance_usd-float(minimum.params['balance_usd']))
        for key in ("safety_net", "maximum_payout"):
            rule = self.rules[key]
            if rule.enabled and rule.applies(ctx):
                value = rule.cap(ctx)
                if value is not None:
                    caps[key] = money(value)

        binding_cap = min(caps, key=lambda key: caps[key])
        allowed = money(min(ctx.requested_usd, caps[binding_cap]))
        if caps[binding_cap] >= ctx.requested_usd:
            binding_cap = None

        amount = money(quantize(allowed)) if quantize else allowed
        minimum = self.rules["minimum_payout"]
        if minimum.enabled and amount < minimum.amount_usd:
            return Decision(
                approved=False,
                requested_usd=ctx.requested_usd,
                allowed_usd=allowed,
                gross_usd=0.0,
                received_usd=0.0,
                blocked_by="minimum_payout",
                blockers=("minimum_payout",),
                binding_cap=binding_cap,
                caps=caps,
            )
        if amount <= 0:
            return Decision(
                approved=False,
                requested_usd=ctx.requested_usd,
                allowed_usd=allowed,
                gross_usd=0.0,
                received_usd=0.0,
                blocked_by=binding_cap or "capped_to_zero",
                blockers=(binding_cap or "capped_to_zero",),
                binding_cap=binding_cap,
                caps=caps,
            )

        split = self.rules["profit_split"]
        received = split.received(amount, ctx) if split.enabled else amount
        return Decision(
            approved=True,
            requested_usd=ctx.requested_usd,
            allowed_usd=allowed,
            gross_usd=amount,
            received_usd=received,
            blocked_by=None,
            blockers=(),
            binding_cap=binding_cap,
            caps=caps,
        )
