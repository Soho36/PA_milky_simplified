"""Paired ongoing/terminal scores from the same trading path."""
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


def annotate_against_benchmark(rows, benchmark):
    """Score candidates against the no-withdrawal path, in place.

    A withdrawal only ever lowers a balance, so the book that never withdraws
    keeps the most accounts alive and books the most trading earnings. A
    candidate booking exactly that much bought its cash without costing a
    trade; anything less has killed accounts, and is charged for the earnings
    it destroyed rather than being flattered by its own smaller path.
    """
    reference = benchmark["booked_net_trading_usd"]
    ceiling = benchmark["path_ceiling_usd"]
    for row in rows:
        if row["booked_net_trading_usd"] > reference:
            raise ValueError(
                "Benchmark is not the survival upper bound: "
                f"{row['policy']} at {row['retained_balance_usd']} booked "
                f"{row['booked_net_trading_usd']} against {reference}")
        row["trading_neutral"] = row["booked_net_trading_usd"] == reference
        row["earnings_forgone_usd"] = money(reference - row["booked_net_trading_usd"])
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
        "economics": economics.to_payload(), "policy_config": p.to_payload(),
    }
