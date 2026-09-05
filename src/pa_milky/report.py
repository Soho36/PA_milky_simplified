"""Summaries and renderings of a book run."""

from __future__ import annotations

import collections
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import median

from .account import money
from .simulator import BookResult


def _stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"count": 0, "total": 0.0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(values),
        "total": money(sum(values)),
        "mean": money(sum(values) / len(values)),
        "median": money(median(values)),
        "min": money(min(values)),
        "max": money(max(values)),
    }


def _policy_label(policy) -> str:
    if not policy.enabled:
        return "none"
    return "fixed_monthly" if policy.amount_rule == "fixed" else f"monthly_{policy.amount_rule}"


def _gate_balance(rulebook) -> float:
    rule = rulebook.get("minimum_balance")
    return float(rule.params["balance_usd"]) if rule.enabled else 0.0


def _net_floor_balance(rulebook) -> float | None:
    rule = rulebook.get("safety_net")
    if not rule.enabled:
        return None
    return money(
        float(rule.params["net_balance_usd"])
        - float(rule.params["encroachment_allowance_usd"])
    )


def summarize(result: BookResult) -> dict:
    config = result.config
    policy, rulebook = config.policy, config.rulebook
    alive, dead = result.alive, result.dead
    alive_profit = [a.equity_profit_usd for a in alive]
    lifetimes = [(a.died_at - a.activated_at).days for a in dead if a.died_at is not None]
    cost = result.total_purchase_cost_usd
    paper_profit = money(sum(alive_profit))
    withdrawn = result.total_withdrawn_usd
    received = result.total_received_usd
    payers = [a for a in result.accounts if a.payout_count > 0]

    summary = {
        "schema_version": "pa_milky_simplified.result.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brick": config.brick,
        "brick_name": config.brick_name,
        "scenario": config.scenario,
        "run": {
            "strategy": config.strategy,
            "risk_reward": config.risk_reward,
            "contracts_per_copy": config.contracts_per_copy,
            "commission_usd_per_copy": config.commission_per_copy_usd,
            "path_order": config.path_order,
            "concurrency": config.concurrency,
            "trailing_drawdown_usd": config.trailing_drawdown_usd,
            "frozen_floor_profit_usd": config.frozen_floor_profit_usd,
            "purchase_fee_usd": config.purchase_fee_usd,
        },
        "tape": {
            "trades_loaded": result.trades_loaded,
            "first_entry": result.tape_first_entry.isoformat(sep=" "),
            "last_exit": result.tape_last_exit.isoformat(sep=" "),
            "copies_filled": result.copies_filled,
        },
        "book": {
            "months_in_dataset": len(result.accounts),
            "accounts_opened": len(result.accounts),
            "accounts_alive_at_end": len(alive),
            "accounts_dead": len(dead),
            "survival_rate": (
                round(len(alive) / len(result.accounts), 4) if result.accounts else 0.0
            ),
        },
        "cash": {
            "spent_on_accounts_usd": cost,
            "withdrawn_usd": withdrawn,
            "owner_cash_position_usd": money(received - cost),
        },
        "alive_equity": {
            "profit_above_start": _stats(alive_profit),
            "total_balance_usd": money(sum(a.balance_usd for a in alive)),
            "total_paper_profit_usd": paper_profit,
            "paper_profit_minus_cost_usd": money(paper_profit - cost),
        },
        "dead_accounts": {
            "count": len(dead),
            "lifetime_days": _stats([float(v) for v in lifetimes]),
            "trades_before_death": _stats([float(a.trades_taken) for a in dead]),
        },
        "trades_per_account": _stats([float(a.trades_taken) for a in result.accounts]),
        "firm_rules": {
            "active": list(rulebook.active_keys),
            "rulebook": rulebook.to_payload(),
        },
    }

    # Cash lost to the firm's split, and the split-free gross, kept separate so
    # the two are never confused for one another.
    summary["cash"]["received_usd"] = received
    summary["cash"]["lost_to_split_usd"] = money(withdrawn - received)

    if policy.liquidates:
        terminal_gross = money(sum(e.gross_usd for e in result.terminal_payouts))
        terminal_received = money(sum(e.received_usd for e in result.terminal_payouts))
        summary["terminal"] = {
            "mode": policy.terminal_withdrawal,
            "at": result.tape_last_exit.isoformat(sep=" "),
            "accounts_alive_at_horizon": result.alive_at_horizon,
            "equity_at_horizon_usd": result.equity_at_horizon_usd,
            "accounts_paid": len(result.terminal_payouts),
            "gross_usd": terminal_gross,
            "received_usd": terminal_received,
            "extracted_fraction_of_equity": (
                round(terminal_gross / result.equity_at_horizon_usd, 4)
                if result.equity_at_horizon_usd
                else 0.0
            ),
            "stranded_usd": money(result.equity_at_horizon_usd - terminal_gross),
        }

    if policy.enabled or policy.liquidates:
        summary["withdrawals"] = {
            "policy": _policy_label(policy),
            "amount_usd": policy.amount_usd,
            "eligibility_balance_usd": _gate_balance(rulebook),
            "safety_net_balance_usd": _net_floor_balance(rulebook),
            "shortfall": policy.shortfall,
            "events": len(result.payouts),
            "first_withdrawal": (
                result.payouts[0].at.isoformat(sep=" ") if result.payouts else None
            ),
            "last_withdrawal": (
                result.payouts[-1].at.isoformat(sep=" ") if result.payouts else None
            ),
            "accounts_that_ever_paid": len(payers),
            "accounts_that_never_paid": len(result.accounts) - len(payers),
            "per_paying_account_usd": _stats([a.gross_paid_usd for a in payers]),
            "entitlement_accrued_usd": money(
                sum(a.entitlement_accrued_usd for a in result.accounts)
            ),
            "outstanding_on_live_accounts_usd": money(
                sum(a.entitlement_outstanding_usd for a in alive)
            ),
            "outstanding_lost_to_deaths_usd": money(
                sum(a.entitlement_outstanding_usd for a in dead)
            ),
        }
        blocked_first = collections.Counter(e.blocked_by for e in result.denials)
        blocked_any: collections.Counter = collections.Counter()
        for event in result.denials:
            blocked_any.update(set(event.blockers))
        binding = collections.Counter(
            e.binding_cap for e in result.payouts if e.binding_cap
        )
        summary["denials"] = {
            "requests_denied": len(result.denials),
            "requests_approved": len(result.payouts),
            "requests_withheld_by_policy": sum(
                a.requests_withheld for a in result.accounts
            ),
            "requests_unpaid_at_horizon": result.requests_unpaid_at_horizon,
            "blocked_by_first": dict(blocked_first.most_common()),
            "blocked_by_any": dict(blocked_any.most_common()),
            "binding_cap_on_approved": dict(binding.most_common()),
        }
    return summary


def account_rows(result: BookResult) -> list[dict]:
    rows = []
    for account in result.accounts:
        rows.append(
            {
                "account_id": account.account_id,
                "cohort_month": account.cohort_month,
                "activated_at": account.activated_at.isoformat(sep=" "),
                "alive": account.alive,
                "died_at": account.died_at.isoformat(sep=" ") if account.died_at else "",
                "death_reason": account.death_reason or "",
                "death_equity_usd": (
                    account.death_equity_usd if account.death_equity_usd is not None else ""
                ),
                "death_trade_key": account.death_trade_key or "",
                "lifetime_days": (
                    (account.died_at - account.activated_at).days if account.died_at else ""
                ),
                "trades_taken": account.trades_taken,
                "wins": account.wins,
                "losses": account.losses,
                "gross_pnl_usd": account.gross_pnl_usd,
                "commission_usd": account.commission_usd,
                "payout_count": account.payout_count,
                "requests_blocked": account.requests_blocked,
                "requests_withheld": account.requests_withheld,
                "withdrawn_usd": account.gross_paid_usd,
                "received_usd": account.received_usd,
                "months_accrued": account.months_accrued,
                "entitlement_accrued_usd": account.entitlement_accrued_usd,
                "entitlement_outstanding_usd": account.entitlement_outstanding_usd,
                "first_withdrawal_at": (
                    account.first_withdrawal_at.isoformat(sep=" ")
                    if account.first_withdrawal_at
                    else ""
                ),
                "equity_profit_usd": account.equity_profit_usd,
                "balance_usd": account.balance_usd if account.alive else "",
                "max_equity_profit_usd": account.max_equity_profit_usd,
                "min_equity_profit_usd": account.min_equity_profit_usd,
                "peak_profit_usd": account.peak_profit_usd,
                "floor_profit_usd": account.floor_profit_usd,
                "headroom_usd": account.headroom_usd if account.alive else "",
            }
        )
    return rows


def payout_rows(result: BookResult) -> list[dict]:
    return [
        {
            "at": e.at.isoformat(sep=" "),
            "account_id": e.account_id,
            "cohort_month": e.cohort_month,
            "payout_number": e.payout_number,
            "requested_usd": e.requested_usd,
            "allowed_usd": e.allowed_usd,
            "gross_usd": e.gross_usd,
            "received_usd": e.received_usd,
            "balance_before_usd": e.balance_before_usd,
            "balance_after_usd": e.balance_after_usd,
            "outstanding_after_usd": e.outstanding_after_usd,
            "binding_cap": e.binding_cap or "",
        }
        for e in result.payouts
    ]


def denial_rows(result: BookResult) -> list[dict]:
    return [
        {
            "at": e.at.isoformat(sep=" "),
            "account_id": e.account_id,
            "cohort_month": e.cohort_month,
            "requested_usd": e.requested_usd,
            "allowed_usd": e.allowed_usd,
            "balance_usd": e.balance_usd,
            "blocked_by": e.blocked_by,
            "blockers": "|".join(e.blockers),
        }
        for e in result.denials
    ]


def _fmt(value: float | None, width: int = 12) -> str:
    return "-".rjust(width) if value is None else f"{value:,.2f}".rjust(width)


def render_text(result: BookResult) -> str:
    s = summarize(result)
    run, tape, book, cash = s["run"], s["tape"], s["book"], s["cash"]
    alive_equity = s["alive_equity"]
    alive_stats = alive_equity["profit_above_start"]
    dead_life = s["dead_accounts"]["lifetime_days"]
    withdrawals = s.get("withdrawals")
    denials = s.get("denials")
    rulebook = result.config.rulebook

    lines: list[str] = []
    add = lines.append

    title = s["scenario"].replace("_", " ").upper()
    add("=" * 78)
    add(f"  {title}")
    add("=" * 78)
    add(
        f"  strategy {run['strategy']} @ RR {run['risk_reward']}"
        f"  |  {run['contracts_per_copy']} MNQ/copy"
        f"  |  commission ${run['commission_usd_per_copy']:.2f} round turn"
        f"  |  path {run['path_order']}"
    )
    add(
        f"  tape {tape['first_entry']} -> {tape['last_exit']}"
        f"  |  {tape['trades_loaded']:,} trades -> {tape['copies_filled']:,} copies filled"
    )
    if withdrawals:
        add(
            f"  policy: ${withdrawals['amount_usd']:,.0f}/month per account"
            f"  ({withdrawals['policy']}, {withdrawals['shortfall']})"
        )
    add("")

    add("  FIRM RULES")
    for key, spec in sorted(rulebook.to_payload().items()):
        mark = "ON " if spec["enabled"] else "off"
        params = ", ".join(
            f"{k}={v}" for k, v in spec.items() if k != "enabled" and v is not None
        )
        add(f"    [{mark}] {key:<20} {params}")
    add("")

    add("  THE BOOK")
    add(f"    months in dataset / accounts opened .. {book['accounts_opened']}")
    add(
        f"    alive at end of dataset .............. {book['accounts_alive_at_end']}"
        f"  ({book['survival_rate'] * 100:.1f}%)"
    )
    add(f"    blown on the trailing drawdown ....... {book['accounts_dead']}")
    add("")

    add("  CASH IN OUR POCKET")
    add(f"    gross out of the accounts ............ ${cash['withdrawn_usd']:,.2f}"
        + (f"  ({withdrawals['events']:,} payouts)" if withdrawals else ""))
    add(f"    lost to the firm's split ............. ${-cash['lost_to_split_usd'] or 0.0:,.2f}")
    add(f"    spent buying accounts ................ ${-cash['spent_on_accounts_usd']:,.2f}"
        f"  ({book['accounts_opened']} x ${run['purchase_fee_usd']:,.0f})")
    add(f"    ---------------------------------------{'-' * 14}")
    add(f"    IN OUR POCKET ........................ ${cash['owner_cash_position_usd']:,.2f}")
    add("")

    if denials:
        add("  WHICH RULE STOPPED US")
        add(f"    requests approved .................... {denials['requests_approved']:,}")
        add(f"    requests denied ...................... {denials['requests_denied']:,}")
        if denials["requests_withheld_by_policy"]:
            add(
                "    withheld by our own cushion .......... "
                f"{denials['requests_withheld_by_policy']:,}  (we never asked)"
            )
        if denials["blocked_by_any"]:
            add("    denied by rule (a request may trip several):")
            for key, count in denials["blocked_by_any"].items():
                first = denials["blocked_by_first"].get(key, 0)
                add(f"      {key:<22} {count:>6,}   (first blocker {first:,})")
        if denials["binding_cap_on_approved"]:
            add("    on approved payouts, the amount was capped by:")
            for key, count in denials["binding_cap_on_approved"].items():
                add(f"      {key:<22} {count:>6,}")
        add("")

    terminal = s.get("terminal")
    if terminal:
        add("  CLOSING THE BOOK")
        add(f"    mode ................................. {terminal['mode']}")
        add(f"    accounts alive at the horizon ........ {terminal['accounts_alive_at_horizon']}")
        add(f"    equity standing in them .............. "
            f"${terminal['equity_at_horizon_usd']:,.2f}")
        add(f"    accounts that could take anything .... {terminal['accounts_paid']}")
        add(f"    extracted ............................ ${terminal['gross_usd']:,.2f}"
            f"   ({terminal['extracted_fraction_of_equity'] * 100:.1f}% of it)")
        add(f"    stranded in the accounts ............. ${terminal['stranded_usd']:,.2f}")
        add("")

    if withdrawals:
        per = withdrawals["per_paying_account_usd"]
        add("  PAYOUT DETAIL")
        add(f"    accounts that ever paid .............. {withdrawals['accounts_that_ever_paid']}"
            f" of {book['accounts_opened']}"
            f"   (never paid: {withdrawals['accounts_that_never_paid']})")
        add(f"    first / last ......................... {withdrawals['first_withdrawal']}"
            f"  ->  {withdrawals['last_withdrawal']}")
        add(f"    per paying account: mean {_fmt(per['mean'])}  median {_fmt(per['median'])}")
        add(f"                        min  {_fmt(per['min'])}  max    {_fmt(per['max'])}")
        add("")

    add("  EQUITY LEFT IN SURVIVING ACCOUNTS")
    add(f"    combined balance ..................... ${alive_equity['total_balance_usd']:,.2f}")
    add(f"    combined profit above start .......... ${alive_equity['total_paper_profit_usd']:,.2f}")
    add(f"    per account: mean {_fmt(alive_stats['mean'])}  median {_fmt(alive_stats['median'])}")
    add(f"                 min  {_fmt(alive_stats['min'])}  max    {_fmt(alive_stats['max'])}")
    add("")

    add("  BLOWN ACCOUNTS")
    add(f"    lifetime days: median {_fmt(dead_life['median'])}"
        f"  min {_fmt(dead_life['min'])}  max {_fmt(dead_life['max'])}")
    causes = collections.Counter(a.death_reason for a in result.dead)
    for reason, count in causes.most_common():
        add(f"    {reason:<26} {count:>4}")
    add("")

    add("  PER-ACCOUNT LEDGER")
    add("    cohort     trades  status  died          lifetime"
        "      payouts    received      balance")
    add("    " + "-" * 87)
    for account in result.accounts:
        status = "ALIVE" if account.alive else "dead "
        died = account.died_at.strftime("%Y-%m-%d") if account.died_at else "-"
        life = f"{(account.died_at - account.activated_at).days}d" if account.died_at else "-"
        balance = f"{account.balance_usd:,.2f}" if account.alive else "-"
        got = f"{account.received_usd:,.2f}" if account.received_usd else "-"
        count = f"{account.payout_count}" if account.payout_count else "-"
        add(
            f"    {account.cohort_month}  {account.trades_taken:6,}  {status}  "
            f"{died:<12}  {life:>8}  {count:>12}  {got:>10}  {balance:>12}"
        )
    add("=" * 78)
    return "\n".join(lines)


def write_outputs(result: BookResult, out_dir: str | Path) -> dict[str, Path]:
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    summary_path = directory / "summary.json"
    summary_path.write_text(json.dumps(summarize(result), indent=2), encoding="utf-8")
    written["summary"] = summary_path

    def _csv(name: str, rows: list[dict]) -> None:
        if not rows:
            return
        path = directory / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        written[name.removesuffix(".csv")] = path

    _csv("accounts.csv", account_rows(result))
    _csv("withdrawals.csv", payout_rows(result))
    _csv("denials.csv", denial_rows(result))

    report_path = directory / "report.txt"
    report_path.write_text(render_text(result), encoding="utf-8")
    written["report"] = report_path
    return written
