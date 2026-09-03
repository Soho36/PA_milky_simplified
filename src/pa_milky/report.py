"""Summaries and renderings of a book run."""

from __future__ import annotations

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


def summarize(result: BookResult) -> dict:
    config = result.config
    rules = config.withdrawals
    alive, dead = result.alive, result.dead
    alive_profit = [a.equity_profit_usd for a in alive]
    lifetimes = [(a.died_at - a.activated_at).days for a in dead if a.died_at is not None]
    cost = result.total_purchase_cost_usd
    paper_profit = money(sum(alive_profit))
    withdrawn = result.total_withdrawn_usd
    payers = [a for a in result.accounts if a.withdrawal_count > 0]

    summary = {
        "schema_version": "pa_milky_simplified.result.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brick": config.brick,
        "brick_name": config.brick_name,
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
            "owner_cash_position_usd": money(withdrawn - cost),
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
    }

    if rules.enabled:
        events = result.withdrawals
        summary["withdrawals"] = {
            "policy": rules.policy,
            "amount_usd": rules.amount_usd,
            "eligibility_balance_usd": rules.eligibility_balance_usd,
            "safety_net_balance_usd": rules.safety_net_balance_usd,
            "shortfall": rules.shortfall,
            "events": len(events),
            "first_withdrawal": events[0].at.isoformat(sep=" ") if events else None,
            "last_withdrawal": events[-1].at.isoformat(sep=" ") if events else None,
            "accounts_that_ever_paid": len(payers),
            "accounts_that_never_paid": len(result.accounts) - len(payers),
            "per_paying_account_usd": _stats([a.withdrawn_usd for a in payers]),
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
                "withdrawn_usd": account.withdrawn_usd,
                "withdrawal_count": account.withdrawal_count,
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


def withdrawal_rows(result: BookResult) -> list[dict]:
    return [
        {
            "at": event.at.isoformat(sep=" "),
            "account_id": event.account_id,
            "cohort_month": event.cohort_month,
            "amount_usd": event.amount_usd,
            "balance_before_usd": event.balance_before_usd,
            "balance_after_usd": event.balance_after_usd,
            "outstanding_after_usd": event.outstanding_after_usd,
        }
        for event in result.withdrawals
    ]


def _fmt(value: float | None, width: int = 12) -> str:
    return "-".rjust(width) if value is None else f"{value:,.2f}".rjust(width)


def render_text(result: BookResult) -> str:
    s = summarize(result)
    run, tape, book, cash = s["run"], s["tape"], s["book"], s["cash"]
    alive_equity = s["alive_equity"]
    alive_stats = alive_equity["profit_above_start"]
    dead_life = s["dead_accounts"]["lifetime_days"]
    dead_trades = s["dead_accounts"]["trades_before_death"]
    withdrawals = s.get("withdrawals")

    lines: list[str] = []
    add = lines.append

    add("=" * 78)
    add(f"  BRICK {s['brick']} - {s['brick_name'].replace('_', ' ').upper()}")
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
        net = withdrawals["safety_net_balance_usd"]
        add(
            f"  withdrawals ${withdrawals['amount_usd']:,.0f}/month per account"
            f"  |  gate ${withdrawals['eligibility_balance_usd']:,.0f}"
            f"  |  safety net {'none' if net is None else f'${net:,.0f}'}"
            f"  |  {withdrawals['shortfall']}"
        )
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
    add(
        f"    withdrawn from accounts .............. ${cash['withdrawn_usd']:,.2f}"
        + (f"  ({withdrawals['events']:,} withdrawals)" if withdrawals else "")
    )
    add(
        f"    spent buying accounts ................ ${-cash['spent_on_accounts_usd']:,.2f}"
        f"  ({book['accounts_opened']} x ${run['purchase_fee_usd']:,.0f})"
    )
    add(f"    ---------------------------------------{'-' * 14}")
    add(f"    IN OUR POCKET ........................ ${cash['owner_cash_position_usd']:,.2f}")
    add("")

    if withdrawals:
        per = withdrawals["per_paying_account_usd"]
        add("  WITHDRAWAL DETAIL")
        add(
            f"    accounts that ever paid .............. {withdrawals['accounts_that_ever_paid']}"
            f" of {book['accounts_opened']}"
            f"   (never paid: {withdrawals['accounts_that_never_paid']})"
        )
        add(f"    first / last ......................... {withdrawals['first_withdrawal']}"
            f"  ->  {withdrawals['last_withdrawal']}")
        add(f"    per paying account: mean {_fmt(per['mean'])}  median {_fmt(per['median'])}")
        add(f"                        min  {_fmt(per['min'])}  max    {_fmt(per['max'])}")
        add(f"    entitlement accrued .................. "
            f"${withdrawals['entitlement_accrued_usd']:,.2f}")
        add(f"    still owed by live accounts .......... "
            f"${withdrawals['outstanding_on_live_accounts_usd']:,.2f}")
        add(f"    written off when accounts died ....... "
            f"${withdrawals['outstanding_lost_to_deaths_usd']:,.2f}")
        add("")

    add("  EQUITY IN SURVIVING ACCOUNTS")
    add(f"    combined balance ..................... ${alive_equity['total_balance_usd']:,.2f}")
    add(f"    combined profit above start .......... ${alive_equity['total_paper_profit_usd']:,.2f}")
    add(f"    per account: mean {_fmt(alive_stats['mean'])}  median {_fmt(alive_stats['median'])}")
    add(f"                 min  {_fmt(alive_stats['min'])}  max    {_fmt(alive_stats['max'])}")
    add("")

    add("  BLOWN ACCOUNTS")
    add(
        f"    lifetime days: median {_fmt(dead_life['median'])}"
        f"  min {_fmt(dead_life['min'])}  max {_fmt(dead_life['max'])}"
    )
    add(
        f"    trades taken:  median {_fmt(dead_trades['median'])}"
        f"  min {_fmt(dead_trades['min'])}  max {_fmt(dead_trades['max'])}"
    )
    add("")

    add("  PER-ACCOUNT LEDGER")
    add("    cohort     trades  status  died          lifetime"
        "     withdrawn      balance      headroom")
    add("    " + "-" * 87)
    for account in result.accounts:
        status = "ALIVE" if account.alive else "dead "
        died = account.died_at.strftime("%Y-%m-%d") if account.died_at else "-"
        life = f"{(account.died_at - account.activated_at).days}d" if account.died_at else "-"
        balance = f"{account.balance_usd:,.2f}" if account.alive else "-"
        headroom = f"{account.headroom_usd:,.2f}" if account.alive else "-"
        drawn = f"{account.withdrawn_usd:,.2f}" if account.withdrawn_usd else "-"
        add(
            f"    {account.cohort_month}  {account.trades_taken:6,}  {status}  "
            f"{died:<12}  {life:>8}  {drawn:>12}  {balance:>12}  {headroom:>12}"
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

    accounts_path = directory / "accounts.csv"
    rows = account_rows(result)
    with accounts_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    written["accounts"] = accounts_path

    events = withdrawal_rows(result)
    if events:
        events_path = directory / "withdrawals.csv"
        with events_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(events[0]))
            writer.writeheader()
            writer.writerows(events)
        written["withdrawals"] = events_path

    report_path = directory / "report.txt"
    report_path.write_text(render_text(result), encoding="utf-8")
    written["report"] = report_path
    return written
