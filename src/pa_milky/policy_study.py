"""Paired ongoing/terminal scores from the same trading path."""
import hashlib
from dataclasses import replace
from .account import money
from .policy import WithdrawalPolicy
from .simulator import run_book
from .economics import Economics


def policies():
    choices = [WithdrawalPolicy(name=f"fixed_{amount}_backlog", cadence="calendar_month",
        amount_rule="fixed", amount_usd=amount, shortfall="accrue_backlog",
        quantize_to_amount=False) for amount in (250, 500, 750, 1000, 1500)]
    choices += [WithdrawalPolicy(name="minimum_monthly", cadence="calendar_month",
                    amount_rule="minimum", quantize_to_amount=False),
                WithdrawalPolicy(name="maximum_excess_monthly", cadence="calendar_month",
                    amount_rule="maximum", quantize_to_amount=False),
                WithdrawalPolicy(name="legacy_500_blocks", cadence="calendar_month",
                    amount_usd=500, shortfall="accrue_backlog", quantize_to_amount=True)]
    return choices


def path_ceiling(economics):
    """Most cash this trading path could ever put in the pocket.

    The pocket identity with nothing left standing in live accounts and no
    profit split taken. Purchase fees and the dead-account ledgers stay in:
    they are settled before any withdrawal is chosen, so no policy can undo
    them. A target rather than a hard bound, and not a reachable policy: a
    book whose live accounts stand below their start balance carries negative
    retained profit and can score above its own ceiling.
    """
    return money(economics.booked_net_trading_usd
                 - economics.failed_positive_ledger_usd
                 + economics.failed_negative_ledger_usd
                 - economics.purchase_fees_usd)


def path_fingerprint(result):
    """Identify the trades a book actually took, not what they summed to.

    Equal booked earnings are not equal trading: two different sets of fills
    can total the same dollar, and an account that dies early can even out-earn
    one that trades on into a losing stretch. Per account this pins the count
    and the booked result of what it traded and the trade it died on, so a path
    that differs anywhere shows up even when the totals coincide.
    """
    material = [(a.account_id, a.trades_taken, money(a.gross_pnl_usd),
                 money(a.commission_usd), a.death_trade_key)
                for a in sorted(result.accounts, key=lambda a: a.account_id)]
    return hashlib.sha256(repr(material).encode()).hexdigest()[:16]


def annotate_against_benchmark(rows, benchmark):
    """Score candidates against the no-withdrawal reference path, in place.

    A withdrawal only ever lowers a balance, so no candidate outlives the book
    that never withdraws. Living longer is not the same as earning more, though
    -- the extra trades can lose -- so the benchmark is a common yardstick, not
    a proven maximum. Capture above 100% is therefore possible and is recorded
    rather than rejected: it means a candidate's earlier deaths sat out a
    net-losing stretch the benchmark traded through. Neutrality is decided on
    the path fingerprint, never on the earnings total, so a candidate counts as
    neutral only when every account took exactly the trades it took under the
    benchmark.
    """
    reference = benchmark["booked_net_trading_usd"]
    ceiling = benchmark["path_ceiling_usd"]
    for row in rows:
        row["trading_neutral"] = row["path_fingerprint"] == benchmark["path_fingerprint"]
        row["earnings_vs_benchmark_usd"] = money(row["booked_net_trading_usd"] - reference)
        row["book_ceiling_usd"] = ceiling
        row["ceiling_capture"] = (round(row["combined_pocket_usd"] / ceiling, 6)
                                  if ceiling > 0 else None)
    return rows


def measure(trades, config, policy, cushion):
    if config.rulebook.processing_delay_days:
        raise ValueError("Paired study requires zero processing delay")
    p = replace(policy, min_retained_balance_usd=cushion, terminal_withdrawal="firm_permitted")
    result = run_book(trades, replace(config, policy=p))
    terminal = money(sum(e.received_usd for e in result.terminal_payouts))
    economics = Economics.measure(result)
    if economics.residual_usd != 0:
        raise ValueError("Economic ledger failed to reconcile")
    ceiling = path_ceiling(economics)
    return {
        "policy": p.name, "retained_balance_usd": cushion,
        "headroom_usd": None if cushion is None else money(cushion-config.trailing_floor_balance_usd),
        "ongoing_pocket_usd": money(result.pocket_usd-terminal),
        "terminal_received_usd": terminal, "combined_pocket_usd": result.pocket_usd,
        "alive_before_terminal": result.alive_at_horizon,
        "ongoing_payouts": len(result.payouts)-len(result.terminal_payouts),
        "terminal_payouts": len(result.terminal_payouts),
        "profit_before_terminal_usd": result.equity_at_horizon_usd,
        "profit_after_terminal_usd": economics.retained_profit_usd,
        "booked_net_trading_usd": economics.booked_net_trading_usd,
        "firm_split_usd": economics.firm_split_usd,
        "path_ceiling_usd": ceiling,
        "unextracted_usd": money(ceiling - result.pocket_usd),
        "path_fingerprint": path_fingerprint(result),
        "economics": economics.to_payload(), "policy_config": p.to_payload(),
    }
