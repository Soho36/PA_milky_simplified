"""Summaries and renderings of a brick-1 book run."""

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
    alive, dead = result.alive, result.dead
    alive_profit = [a.equity_profit_usd for a in alive]
    lifetimes = [(a.died_at - a.activated_at).days for a in dead if a.died_at is not None]
    cost = result.total_purchase_cost_usd
    paper_profit = money(sum(alive_profit))

    return {
        "schema_version": "pa_milky_simplified.result.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "brick": 1,
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
            "withdrawn_usd": 0.0,
            "owner_cash_position_usd": money(-cost),
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


def _fmt(value: float | None, width: int = 12) -> str:
    return "-".rjust(width) if value is None else f"{value:,.2f}".rjust(width)


def render_text(result: BookResult) -> str:
    s = summarize(result)
    run, tape, book, cash = s["run"], s["tape"], s["book"], s["cash"]
    alive_equity = s["alive_equity"]
    alive_stats = alive_equity["profit_above_start"]
    dead_life = s["dead_accounts"]["lifetime_days"]
    dead_trades = s["dead_accounts"]["trades_before_death"]

    lines: list[str] = []
    add = lines.append

    add("=" * 78)
    add("  BRICK 1 - IDEAL-WORLD LEGACY 25K PA BOOK")
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
    add("")

    add("  THE BOOK")
    add(f"    months in dataset / accounts opened .. {book['accounts_opened']}")
    add(
        f"    alive at end of dataset .............. {book['accounts_alive_at_end']}"
        f"  ({book['survival_rate'] * 100:.1f}%)"
    )
    add(f"    blown on the trailing drawdown ....... {book['accounts_dead']}")
    add("")

    add("  CASH")
    add(
        f"    spent buying accounts ................ ${cash['spent_on_accounts_usd']:,.2f}"
        f"  ({book['accounts_opened']} x ${run['purchase_fee_usd']:,.0f})"
    )
    add(f"    withdrawn (no payout rules in brick 1)  ${cash['withdrawn_usd']:,.2f}")
    add(f"    owner cash position .................. ${cash['owner_cash_position_usd']:,.2f}")
    add("")

    add("  EQUITY IN SURVIVING ACCOUNTS")
    add(f"    combined balance ..................... ${alive_equity['total_balance_usd']:,.2f}")
    add(f"    combined profit above start .......... ${alive_equity['total_paper_profit_usd']:,.2f}")
    add(
        f"    that profit minus all account fees ... "
        f"${alive_equity['paper_profit_minus_cost_usd']:,.2f}"
    )
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
    add("    cohort     trades  status  died          lifetime      balance      headroom")
    add("    " + "-" * 72)
    for account in result.accounts:
        status = "ALIVE" if account.alive else "dead "
        died = account.died_at.strftime("%Y-%m-%d") if account.died_at else "-"
        life = f"{(account.died_at - account.activated_at).days}d" if account.died_at else "-"
        balance = f"{account.balance_usd:,.2f}" if account.alive else "-"
        headroom = f"{account.headroom_usd:,.2f}" if account.alive else "-"
        add(
            f"    {account.cohort_month}  {account.trades_taken:6,}  {status}  "
            f"{died:<12}  {life:>8}  {balance:>12}  {headroom:>12}"
        )
    add("=" * 78)
    return "\n".join(lines)


def write_outputs(result: BookResult, out_dir: str | Path) -> dict[str, Path]:
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    summary_path = directory / "summary.json"
    accounts_path = directory / "accounts.csv"
    report_path = directory / "report.txt"

    summary_path.write_text(json.dumps(summarize(result), indent=2), encoding="utf-8")
    rows = account_rows(result)
    with accounts_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report_path.write_text(render_text(result), encoding="utf-8")
    return {"summary": summary_path, "accounts": accounts_path, "report": report_path}
