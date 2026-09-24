"""Study-local variant filtering of the legacy unlimited settlement model.

Reuse the original event loop and trade application, changing only which
accounts see each variant. No shared module globals or source are modified.
This deliberately reproduces the old model: whole-trade MAE/MFE/P&L at exit,
not combined mark-to-market across simultaneous open positions. An account
already killed by an earlier settlement does not book subsequent settlements.
"""
from dataclasses import replace
from types import FunctionType
from pa_milky import simulator


def rebound(function, **bindings):
    clone = FunctionType(function.__code__, {**function.__globals__, **bindings},
                         function.__name__, function.__defaults__, function.__closure__)
    clone.__kwdefaults__ = function.__kwdefaults__
    return clone


def run_overlap_book(trades, config, *, order, trade_rr, **kwargs):
    if any(kwargs.get(k) is not None for k in ('routing', 'router_factory')):
        raise ValueError('Unlimited overlap uses the legacy settlement path, not entry routing')
    order = tuple(order)
    if not order or set(trade_rr.values()) - set(order):
        raise ValueError('Every trade variant needs an allocation')
    fills = []

    def apply_variant(trade, accounts, *, commission, path_order):
        rr = trade_rr[trade.trade_key]
        selected = [a for a in accounts if a.alive and a.activated_at <= trade.entry_at
                    and order[(a.account_id-1) % len(order)] == rr]
        count = simulator._apply_trade(trade, selected, commission=commission, path_order=path_order)
        fills.append(dict(trade_key=trade.trade_key, rr=rr,
                          entry_at=trade.entry_at.isoformat(), exit_at=trade.exit_at.isoformat(),
                          accounts=[a.account_id for a in selected]))
        return count

    advance = rebound(simulator._advance, _apply_trade=apply_variant)
    run = rebound(simulator.run_book, _advance=advance)
    result = run(trades, config, **kwargs)
    return replace(result, routing={'policy': {'mode':'unlimited'},
                   'account_rr': {a.account_id:order[(a.account_id-1) % len(order)] for a in result.accounts},
                   'fill_semantics':'booked settlements; entries overlapping an earlier death may be unbooked'},
                   routing_fills=fills)
