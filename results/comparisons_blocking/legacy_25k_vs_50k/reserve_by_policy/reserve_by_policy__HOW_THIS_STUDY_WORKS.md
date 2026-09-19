# What this study means in practice — blocked copying

This is the blocked-copying twin of the
[non-blocking reserve comparison](../../../comparisons/legacy_25k_vs_50k/reserve_by_policy/reserve_by_policy__HOW_THIS_STUDY_WORKS.md).
The grid, budgets, fees, rules and trading tape are identical. Only the
execution rule differs.

## Blocked copying

Each funded account holds at most one position (one MNQ). When a signal
arrives, every live account that is flat copies it. An account still in an
earlier trade skips the new signal and never adds to its position. Exits are
processed before entries at the same timestamp, so an account that closes a
trade can take the next signal that enters at that moment.

In the non-blocking comparison every live account copies every signal, even
while already in a position, so one account can hold several overlapping
trades. Blocking removes those extra positions. It changes each account's
equity path, when it becomes eligible for payouts and when it fails. Cash,
survival and the best reserve can therefore all move, in either direction.

Accounts bought on the same day take identical trades until one of them
fails, just as in the non-blocking study. Blocking does not by itself stagger
a book; accounts drift apart only when they were activated at different times.

## The operating choices

Start with $1,000 or $5,000 in owner cash. In the funded variants, add $200
each month from the second calendar month. Account purchases cost $200 for
25K Legacy or $250 for 50K Legacy. You can have at most 20 live accounts.
Every purchase needs enough available cash; cash received during trading can
fund later purchases.

Three purchasing approaches are compared:

- **monthly_one:** attempt one account purchase at the beginning of each month.
  A death opens capacity, but does not trigger an extra purchase between dates.
- **weekly_one:** attempt one account purchase on each Monday.
- **monthly_current_slot_replacements:** maintain the monthly schedule, but
  attempt to replace deaths at the next daily purchase check. If the current
  month's scheduled purchase has not happened, a successful replacement uses
  that month's slot. If it already happened, the replacement does not cancel
  next month's purchase. Multiple deaths can trigger multiple replacements,
  subject to cash and the live-account cap.

For each approach and budget, test daily, weekly and monthly withdrawal checks
from each account's second calendar month. One withdrawal family asks for the
firm minimum ($500); the other asks for all excess that the chosen reserve and
firm rules allow. This study does not search fixed monthly targets with backlog.

An account must have enough balance to make a payout while leaving its reserve.
For example, a $31,900 reserve requires at least $32,400 for a $500 request;
other eligibility rules must also pass. The reserve is not a guarantee against
losses. The same dollar cushion above the frozen drawdown floor means $31,900
for 25K and $56,900 for 50K at $6,800 headroom. Both account sizes receive the
same tested headroom values, including refinements found by either product.

Two separate questions are scored:

- **Ongoing net cash:** how much was paid to the owner during trading, less
  all account purchase fees?
- **Total net cash:** how much does that become after one final request per
  surviving account, releasing the voluntary reserve but still applying the
  modeled firm rules?

Owner deposits are funding, not profits. Accounts means all seats bought
throughout the dataset; Alive means those surviving at the end. The
20-account cap applies to Alive at any moment, not to cumulative Accounts.
Funded accounts are available immediately when affordable; there is no
evaluation phase in this study.

## Checks specific to this run

- Settings shared with the 25K
  [blocked-copying optimization](../../../legacy_25k/blocked_optimization/blocked_optimization__REPORT.generated.md)
  (one starting account, monthly or monthly-plus-replacement purchases) must
  reproduce exactly, including every per-trade account assignment. Weekly
  purchases are excluded there because that study buys its first account on
  the first day rather than the first Monday.
- Every headline winner is replayed, and its trade assignments are checked
  independently: no account may hold two overlapping trades. The results are
  in `winner_analysis.json`.
- The non-blocking comparison and every other result file are hashed before
  the run and verified unchanged afterwards (`preservation_check.json`).

"Best tested" is conditional on the specified grid, rules and this historical
tape. Exact ties and near-best tested values are recorded; they are not
confidence intervals.

Rerun with
`scripts/study_legacy_reserve_comparison.py config/studies/legacy_reserve_comparison_blocking.json`,
then `scripts/explain_legacy_reserve_comparison.py` and
`scripts/format_legacy_comparison_reports.py` with the same argument and this
folder respectively. Completed simulations are checkpointed against a sealed
search/configuration/input/engine contract.
