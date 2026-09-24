# RR 0.50 / RR 2.50: monthly withdrawals and reserve

The mixed book's best tested cash results come from **maximum excess monthly**,
**$1,000 monthly backlog**, and **$1,500 monthly backlog**. All three tie at a
$29,600 retained balance: $4,500 headroom above the frozen $25,100 floor.
They preserve the no-withdrawal account trading paths, including all 27
survivors. This does not mean no accounts died: 79 accounts were purchased
and 52 died on the hold path too.

The run covers January 2, 2020 through July 13, 2026 and tests 265 settings
including hold. Net cash below deducts $15,800 of account fees and applicable
firm split. Terminal cash is one permitted request, not unrestricted equity
liquidation.

| Policy / retained balance | Headroom | Ongoing net cash | Including terminal | Survivors |
|---|---:|---:|---:|---:|
| Three tied leaders / $29,600 | $4,500 | $415,319 | $495,589 | 27 |
| $1,000 backlog / $30,000 | $4,900 | $405,491 | $494,617 | 27 |
| $1,000 backlog / $30,600 | $5,500 | $392,247 | $493,912 | 27 |
| Minimum monthly, its best tested / $29,400 | $4,300 | $234,200 | $235,700 | 27 |

## The boundary matters more than the exact winner

For $1,000 backlog, reducing the retained balance from $29,600 to $29,500
cuts survivors from 27 to 13 and combined cash from $495,589 to $400,890.
The winning threshold sits directly above a historical survival cliff.
It is not evidence that $4,500 headroom is sufficient on new data.

Several higher tested reserves preserve exactly the same trades. At $30,000,
combined cash is only $972 (0.20%) below the peak, although ongoing cash is
$9,828 lower: more extraction is deferred to the final request. At $30,600,
combined cash remains within 0.34% of the peak. These are historical tradeoffs,
not a validated optimum or a test of every intervening balance.

## Minimum monthly leaves substantial money behind

Its best tested setting preserves the hold trading path but leaves $300,185
of profit inside surviving accounts after the terminal request. Only $1,500
is received at that endpoint. Its lower combined cash therefore does not
mean the strategy generated less trading profit. Both this policy and the
leaders booked $527,774 of net trading earnings.

The common hold-path extraction reference is $535,885; the winners capture
92.48%. The remaining $40,296 is $7,549 firm split plus $32,747 retained
profit. This accounting reference is not an executable payout policy.

## What was held fixed

New monthly purchases alternate RR r/r 0.50 and 2.50, starting with 0.50.
Assignments remain fixed for life, so every policy gets the same purchase
schedule and assignments: 40 accounts at 0.50 and 39 at 2.50. The winners
finish with 12 and 15 respectively. This targets equal purchases, not equal
surviving allocations.

As requested, execution is **all eligible signals while flat**. The original
study allowed overlapping positions, so its dollar totals cannot isolate the
effect of changing the r/r allocation. The original uncapped, externally
financed monthly purchases remain: no 20-account cap, evaluation queue,
cash constraint or additional replacements. These results do not settle
the policy choice for a capped operating book.

The eight original policy families and original coarse/refinement grid are
unchanged. Selection is in-sample and local. No assignment-order robustness
claim is made.

## Verification and evidence

All 265 financial identities reconcile. Routing checks cover 25,222,356
accepted copies. Hold and both winning runs reproduce exactly; independent
entry selection checks cover 237 account paths and 334,779 accepted copies.
All 17 targeted tests passed. Both input variants pass reconciliation and
coverage checks. The shared engine and original results were left unchanged.

- [Full tables and methodology](rr_pair_monthly_amount_x_cushion__REPORT.md)
- [Every candidate](candidates.csv)
- [Input hashes, policies and scores](study.json)
- [Independent audit](audit.json)
- [Winner account and payout ledgers](best_ongoing/report.txt)
- [Study design](../../../research/legacy_25k/RR_PAIR_WITHDRAWAL_AMOUNT.md)
