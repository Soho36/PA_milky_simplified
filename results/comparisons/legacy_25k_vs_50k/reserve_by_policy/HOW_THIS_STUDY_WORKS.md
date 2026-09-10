# What this study means in practice

Start with $1,000 or $5,000 in owner cash. In the funded variants, add $200
each month from the second calendar month. Account purchases cost $200 for
25K Legacy or $250 for 50K Legacy. You can have at most 20 live accounts.
Every purchase needs enough available cash; cash received during trading can
fund later purchases. The simulator copies the same trading system and
contract exposure into each live account.

Three purchasing approaches are compared:

- **monthly_one:** attempt one account purchase at the beginning of each month.
  A death opens capacity, but does not trigger an extra purchase between dates.
- **weekly_one:** attempt one account purchase on each Monday.
- **monthly_current_slot_replacements:** maintain the monthly schedule, but
  attempt to replace deaths at the next daily purchase check. If the current
  month's scheduled purchase has not happened, a successful replacement uses
  that month's slot. If it already happened, the replacement does not cancel
  next month's purchase. Multiple deaths can trigger multiple replacements,
  subject to cash and the live-account cap. This is replacement at the next
  modeled daily check, not within the same intraday trade.

For each approach and budget, test daily, weekly and monthly withdrawal checks
from each account's second calendar month. One withdrawal family asks for the
firm minimum ($500); the other asks for all excess that the chosen reserve and
firm rules allow. This study does not search fixed monthly targets with backlog.

An account must have enough balance to make a payout while leaving its reserve.
For example, a $31,900 reserve requires at least $32,400 for a $500 request;
other eligibility rules must also pass. Trading continues after losses take
an account below its reserve. The reserve is not a guarantee against losses.

The same dollar cushion above the frozen drawdown floor translates into
different nominal balances: $6,800 headroom means $31,900 for 25K and $56,900
for 50K. Both account sizes receive the same tested headroom values within
each budget/purchase/withdrawal/cadence combination. Refinements identified
by either product are also tested for the other product.

Two separate questions are scored:

- **Ongoing net cash:** how much was paid to the owner during trading, less
  all account purchase fees?
- **Total net cash:** how much does that become after one final request per
  surviving account, releasing the voluntary reserve but still applying the
  modeled firm rules?

Owner deposits are funding, not profits. Terminal receipts cannot finance
earlier purchases. Accounts means all seats bought throughout the dataset;
Alive means those surviving at the end. The 20-account cap applies to Alive
at any moment, not to cumulative Accounts.

Read the matched differences to compare account sizes with the same reserve
headroom and operating behavior. Read best-by-policy tables to allow each
product to choose its reserve. Read the best-complete-bundle tables to also
allow different withdrawal and purchase behavior. These are different
questions, and their answers need not agree.

"Best tested" is conditional on the specified grid, rules and this historical
tape. Exact ties and near-best tested values are recorded; they are not
confidence intervals. No future-market, start-date or calendar-phase
validation is performed. Higher reserves can delay extraction without
improving survival, so neither the highest reserve nor the most survivors
necessarily produces the most cash.

## Why the earlier 25K daily reference was $31,900

The original **uncapped, monthly-purchase** cadence study produced the following
daily-minimum results. These are historical controls, not results of the new
funded, capped comparison.

| Reserve | Ongoing net cash | Total net cash | Alive |
|---|---:|---:|---:|
| $30,000 | $373,200.00 | $373,200.00 | 2 |
| $31,600 | $355,350.00 | $409,464.98 | 13 |
| $31,700 | $355,350.00 | $409,464.98 | 13 |
| $31,800 | $357,750.00 | $437,748.10 | 18 |
| $31,900 | $357,800.00 | $460,511.75 | 22 |
| $32,000 | $354,850.00 | $460,511.75 | 22 |
| $32,100 | $354,350.00 | $460,511.75 | 22 |

Thus higher values were tested. $31,900 tied for the best total while producing
the most ongoing cash among those tied settings. It was not the only best
total-scoring reserve, nor the reserve producing the most ongoing cash across
all tested settings. That study did not establish what would happen above
$32,100 or throughout the gap between $30,000 and $31,600.

Source: [original cadence evidence](../../../study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/study.json).

Both products use the inherited payout interpretation for comparability.
The optional stricter retained minimum after payout six is not used in this
search. The [shorter findings report](FINDINGS.generated.md) replays the selected
winners under that interpretation as a separate fixed-policy sensitivity;
it does not re-optimize reserves under it.
See the [sources and model limits](../../../../research/legacy_50k/SOURCES.md).

Rerun with `scripts/study_legacy_reserve_comparison.py`. Completed simulations
are checkpointed against a sealed search/configuration/input/engine contract.
The runner refuses to reuse a checkpoint after that contract changes. It
refreshes `REPORT.generated.md`, while existing `REPORT.md` and
`report_breakdown.txt` remain reader-owned. All earlier result folders are
checked for byte-for-byte preservation.
