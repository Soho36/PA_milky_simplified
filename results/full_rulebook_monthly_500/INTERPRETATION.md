# Consistency: timing and amount effects

Full rulebook versus removing consistency, fixed monthly $500 backlog policy,
one account bought per month, RR tape, no terminal withdrawal.

Removing consistency increases net cash by **$4,000**. The cash bridge is:

| Contribution to extra cash | USD |
|---|---:|
| More booked net trading earnings | +1,639.40 |
| Less profit remaining in live accounts | +2,765.55 |
| More positive booked balances removed at account failure | -404.95 |
| Firm split, failed deficits, purchase fees | 0.00 |
| Total | +4,000.00 |
| Reconciliation residual | 0.00 |

The failure term uses last booked balances, not actual liquidation proceeds.
The engine does not book the killing excursion as a realized trade loss.

Separately, matching cumulative owner receipts within each account finds:

- $118,500 of common receipts: $109,000 at the same time and $9,500 earlier
  without consistency.
- Those earlier matched receipts total 424,500 dollar-days of acceleration.
- $4,000 of additional receipts without consistency remain unmatched at the
  endpoint. There are no unmatched baseline receipts.

This supports two observations: part of the receipt stream arrives earlier,
and the rule-free run also extracts more by the endpoint. It does not prove
that particular denied requests later succeeded. The $2,765.55 retained-profit
difference must not be called delayed cash: seven account fates changed.

Removing the safety net has a different bridge: -$18,987.70 of booked trading
earnings, +$6,745.30 from lower remaining profit, and -$257.60 from larger
positive failed balances, summing to -$12,500 cash. These are accounting
contributions, not a unique causal allocation.

The fixed-policy JSON contains all nine rule comparisons and timing summaries.
All cash bridges reconcile to zero cents. See ../../ECONOMIC_EFFECTS.md for
method definitions and limits.
