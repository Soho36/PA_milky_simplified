"""Ledger reconciliation and descriptive receipt timing, not causal dollar tracing."""
from collections import defaultdict
from dataclasses import asdict, dataclass
from .account import money


@dataclass(frozen=True)
class Economics:
    booked_net_trading_usd: float
    firm_split_usd: float
    retained_profit_usd: float
    failed_positive_ledger_usd: float
    failed_negative_ledger_usd: float
    purchase_fees_usd: float
    pocket_usd: float
    residual_usd: float

    @classmethod
    def measure(cls, result):
        accounts = result.accounts
        net = money(sum(a.gross_pnl_usd - a.commission_usd for a in accounts))
        split = money(sum(a.gross_paid_usd - a.received_usd for a in accounts))
        retained = money(sum(a.equity_profit_usd for a in accounts if a.alive))
        positive = money(sum(max(0, a.equity_profit_usd) for a in accounts if not a.alive))
        negative = money(sum(max(0, -a.equity_profit_usd) for a in accounts if not a.alive))
        fees = result.total_purchase_cost_usd
        predicted = money(net - split - retained - positive + negative - fees)
        return cls(net, split, retained, positive, negative, fees,
                   result.pocket_usd, money(result.pocket_usd - predicted))

    def to_payload(self):
        return asdict(self)

    def bridge_against(self, baseline):
        # Contributions sum to the observed pocket difference, arm minus baseline.
        signs = {"booked_net_trading_usd": 1, "firm_split_usd": -1,
                 "retained_profit_usd": -1, "failed_positive_ledger_usd": -1,
                 "failed_negative_ledger_usd": 1, "purchase_fees_usd": -1}
        contributions = {k: money(sign * (getattr(self, k) - getattr(baseline, k)))
                         for k, sign in signs.items()}
        delta = money(self.pocket_usd - baseline.pocket_usd)
        return {"contributions_usd": contributions, "delta_pocket_usd": delta,
                "residual_usd": money(delta - sum(contributions.values()))}


def receipt_timing(baseline_events, arm_events):
    """Match cumulative owner-receipt dollars FIFO within each account.

    Positive days mean the arm received the matched dollars later. This is a
    distribution comparison, not proof that a particular denied ask was paid.
    Unmatched dollars are unresolved amount differences, never assumed delayed.
    """
    def group(events):
        out = defaultdict(list)
        for e in sorted(events, key=lambda e: (e.at, e.account_id)):
            cents = round(e.received_usd * 100)
            if cents > 0:
                out[e.account_id].append([e.at, cents])
        return out
    base, arm = group(baseline_events), group(arm_events)
    matched = later = earlier = same = 0
    dollar_days = later_days = earlier_days = 0.0
    unmatched_base = unmatched_arm = 0
    for key in base.keys() | arm.keys():
        left, right = base[key], arm[key]
        i = j = 0
        while i < len(left) and j < len(right):
            cents = min(left[i][1], right[j][1])
            days = (right[j][0] - left[i][0]).total_seconds() / 86400
            matched += cents
            dollar_days += cents / 100 * days
            if days > 0:
                later += cents
                later_days += cents / 100 * days
            elif days < 0:
                earlier += cents
                earlier_days -= cents / 100 * days
            else:
                same += cents
            left[i][1] -= cents
            right[j][1] -= cents
            if not left[i][1]: i += 1
            if not right[j][1]: j += 1
        unmatched_base += sum(v for _, v in left[i:])
        unmatched_arm += sum(v for _, v in right[j:])
    return {"method": "per_account_cumulative_receipts_fifo",
            "matched_usd": matched / 100, "arm_later_usd": later / 100,
            "arm_earlier_usd": earlier / 100, "same_time_usd": same / 100,
            "signed_dollar_days": round(dollar_days, 2),
            "later_dollar_days": round(later_days, 2),
            "earlier_dollar_days": round(earlier_days, 2),
            "mean_signed_days": round(dollar_days / (matched / 100), 4) if matched else None,
            "unmatched_baseline_usd": unmatched_base / 100,
            "unmatched_arm_usd": unmatched_arm / 100}
