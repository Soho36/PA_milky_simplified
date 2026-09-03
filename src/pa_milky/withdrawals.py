"""Taking cash out of a Performance Account.

Brick 2 introduces the first prop-firm rule of the study: the safety-net gate.
An account may only pay out once its balance shows the starting balance plus
the $1,500 safety net plus the $100 being asked for -- $26,600. Everything else
about the withdrawal is still ideal: any amount, any time, no request count, no
consistency rule, no processing delay, no profit split.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .account import Account, money
from .config import WithdrawalRules


@dataclass(frozen=True, slots=True)
class WithdrawalEvent:
    at: datetime
    account_id: int
    cohort_month: str
    amount_usd: float
    balance_before_usd: float
    balance_after_usd: float
    outstanding_after_usd: float


def allowed_amount(account: Account, rules: WithdrawalRules) -> float:
    """How much of the outstanding entitlement this account may pay right now.

    Two gates, in order. The eligibility gate asks whether a request may be
    made at all; the safety net then caps what the request may take, so a
    backlog can never be paid out of the protected balance.
    """

    if not account.alive or account.entitlement_outstanding_usd <= 0:
        return 0.0
    if account.balance_usd < rules.eligibility_balance_usd:
        return 0.0

    payable = account.entitlement_outstanding_usd
    if rules.safety_net_balance_usd is not None:
        payable = min(payable, money(account.balance_usd - rules.safety_net_balance_usd))
    if payable <= 0:
        return 0.0

    if rules.shortfall == "partial":
        return money(payable)
    # "skip" and "accrue_backlog" are both all-or-nothing at the decision; they
    # differ only in whether an unpaid month stays owed, which accrue() decides.
    if payable < rules.amount_usd:
        return 0.0
    # Pay whole months only, so the pocket stays a clean multiple of the amount.
    whole_months = int(payable // rules.amount_usd)
    return money(whole_months * rules.amount_usd)


def run_monthly_decision(
    accounts: list[Account], boundary: datetime, rules: WithdrawalRules
) -> list[WithdrawalEvent]:
    """Accrue one month for every live account, then pay what is allowed."""

    events: list[WithdrawalEvent] = []
    for account in accounts:
        if not account.alive or account.activated_at >= boundary:
            continue
        account.accrue(rules.amount_usd, keep_backlog=rules.shortfall != "skip")
        amount = allowed_amount(account, rules)
        if amount <= 0:
            continue
        before = account.balance_usd
        account.withdraw(amount, boundary)
        events.append(
            WithdrawalEvent(
                at=boundary,
                account_id=account.account_id,
                cohort_month=account.cohort_month,
                amount_usd=amount,
                balance_before_usd=before,
                balance_after_usd=account.balance_usd,
                outstanding_after_usd=account.entitlement_outstanding_usd,
            )
        )
    return events
