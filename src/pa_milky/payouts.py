"""Running our policy's requests through the firm's rulebook.

Every monthly decision produces one record: an approved payout, or a denial
naming the rule that stopped it. The denial ledger is the point -- it says
which rule costs what without running anything twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .account import Account, money
from .firm import Decision, RequestContext
from .policy import UNBOUNDED_REQUEST_USD


@dataclass(frozen=True, slots=True)
class PayoutEvent:
    at: datetime
    account_id: int
    cohort_month: str
    payout_number: int
    requested_usd: float
    allowed_usd: float
    gross_usd: float
    received_usd: float
    balance_before_usd: float
    balance_after_usd: float
    outstanding_after_usd: float
    binding_cap: str | None


@dataclass(frozen=True, slots=True)
class DenialEvent:
    at: datetime
    account_id: int
    cohort_month: str
    requested_usd: float
    allowed_usd: float
    balance_usd: float
    blocked_by: str
    blockers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PendingPayout:
    """An approved request waiting out the firm's processing delay."""

    due_at: datetime
    requested_at: datetime
    account: Account
    decision: Decision


def build_context(account: Account, at: datetime, requested_usd: float, config) -> RequestContext:
    return RequestContext(
        account=account,
        at=at,
        requested_usd=requested_usd,
        payout_number=account.payout_count + 1,
        starting_balance_usd=config.starting_balance_usd,
        trailing_floor_balance_usd=config.trailing_floor_balance_usd,
    )


def _record_payout(
    account: Account, decision: Decision, at: datetime, *, terminal: bool = False
) -> PayoutEvent:
    before = account.balance_usd
    account.pay_out(decision.gross_usd, decision.received_usd, at, terminal=terminal)
    return PayoutEvent(
        at=at,
        account_id=account.account_id,
        cohort_month=account.cohort_month,
        payout_number=account.payout_count,
        requested_usd=decision.requested_usd,
        allowed_usd=decision.allowed_usd,
        gross_usd=decision.gross_usd,
        received_usd=decision.received_usd,
        balance_before_usd=before,
        balance_after_usd=account.balance_usd,
        outstanding_after_usd=account.entitlement_outstanding_usd,
        binding_cap=decision.binding_cap,
    )


def _record_denial(account: Account, decision: Decision, at: datetime) -> DenialEvent:
    account.requests_blocked += 1
    return DenialEvent(
        at=at,
        account_id=account.account_id,
        cohort_month=account.cohort_month,
        requested_usd=decision.requested_usd,
        allowed_usd=decision.allowed_usd,
        balance_usd=account.balance_usd,
        blocked_by=decision.blocked_by or "unknown",
        blockers=decision.blockers,
    )


def run_monthly_decision(
    accounts: list[Account],
    boundary: datetime,
    config,
    pending: list[PendingPayout],
) -> tuple[list[PayoutEvent], list[DenialEvent]]:
    """Accrue one month for every live account, then ask the firm."""

    policy = config.policy
    rulebook = config.rulebook
    delay_days = rulebook.processing_delay_days
    quantize = policy.quantizer()
    firm_minimum = config.firm_minimum_payout_usd

    payouts: list[PayoutEvent] = []
    denials: list[DenialEvent] = []

    for account in accounts:
        if not account.alive or account.activated_at >= boundary:
            continue
        if policy.amount_rule == "fixed":
            account.accrue(policy.amount_usd, keep_backlog=policy.keeps_backlog)

        requested = policy.requested_usd(account, firm_minimum_usd=firm_minimum)
        decision = rulebook.decide(
            build_context(account, boundary, requested, config), quantize
        )
        if not decision.approved:
            if decision.blocked_by == "no_request":
                account.requests_withheld += 1
            else:
                denials.append(_record_denial(account, decision, boundary))
            continue
        if delay_days > 0:
            # The firm removes the balance at approval, not at request, so a
            # delayed request is held and re-tested when it lands.
            pending.append(
                PendingPayout(
                    due_at=boundary + timedelta(days=delay_days),
                    requested_at=boundary,
                    account=account,
                    decision=decision,
                )
            )
            continue
        payouts.append(_record_payout(account, decision, boundary))

    return payouts, denials


def settle_pending(
    pending: list[PendingPayout], now: datetime, config
) -> tuple[list[PayoutEvent], list[DenialEvent]]:
    """Approve, or deny, requests whose processing delay has run out."""

    rulebook = config.rulebook
    denies_on_shortfall = rulebook.is_on("denial_on_shortfall")
    gate = rulebook.get("minimum_balance")

    payouts: list[PayoutEvent] = []
    denials: list[DenialEvent] = []
    still_waiting: list[PendingPayout] = []

    for item in pending:
        if item.due_at > now:
            still_waiting.append(item)
            continue
        account = item.account
        if not account.alive:
            continue
        ctx = build_context(account, item.due_at, item.decision.requested_usd, config)
        if denies_on_shortfall and gate.enabled and gate.blocks(ctx):
            denials.append(
                DenialEvent(
                    at=item.due_at,
                    account_id=account.account_id,
                    cohort_month=account.cohort_month,
                    requested_usd=item.decision.requested_usd,
                    allowed_usd=item.decision.allowed_usd,
                    balance_usd=account.balance_usd,
                    blocked_by="denial_on_shortfall",
                    blockers=("denial_on_shortfall",),
                )
            )
            account.requests_blocked += 1
            continue
        payouts.append(_record_payout(account, item.decision, item.due_at))

    pending[:] = still_waiting
    return payouts, denials


def run_terminal_withdrawal(
    accounts: list[Account], at: datetime, config
) -> tuple[list[PayoutEvent], list[DenialEvent]]:
    """Close the book when the tape runs out.

    Two readings, and they are not close to each other.

    ``liquidate_profit`` is the idealized benchmark: every dollar of profit
    above the starting balance becomes cash, with no gate, no cap and no split.
    It is a counterfactual about what the equity was *worth*, not a claim that
    it could have been taken.

    ``firm_permitted`` is what the rules actually allow. It is **one** request,
    because the eight-trading-day gate is measured in trading days since the
    last request and the tape has stopped producing them: an account that stops
    trading can never become eligible again.
    """

    mode = config.policy.terminal_withdrawal
    if mode == "none":
        return [], []

    payouts: list[PayoutEvent] = []
    denials: list[DenialEvent] = []

    for account in accounts:
        if not account.alive:
            continue

        if mode == "liquidate_profit":
            gross = money(account.balance_usd - config.starting_balance_usd)
            if gross <= 0:
                continue
            decision = Decision(
                approved=True,
                requested_usd=gross,
                allowed_usd=gross,
                gross_usd=gross,
                received_usd=gross,
                blocked_by=None,
                blockers=(),
                binding_cap=None,
                caps={},
            )
            payouts.append(_record_payout(account, decision, at, terminal=True))
            continue

        decision = config.rulebook.decide(
            build_context(account, at, UNBOUNDED_REQUEST_USD, config), None
        )
        if decision.approved:
            payouts.append(_record_payout(account, decision, at, terminal=True))
        elif decision.blocked_by != "no_request":
            denials.append(_record_denial(account, decision, at))

    return payouts, denials
