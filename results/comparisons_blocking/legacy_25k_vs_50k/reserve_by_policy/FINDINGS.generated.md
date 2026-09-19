# What the broader reserve comparison changes — blocked copying

25K is shown on the left and 50K on the right. Each row shares the same comparison labels. “Bought / alive” means cumulative purchases / ending survivors. Reserve cells retain tie counts; † marks a tie at a tested range boundary. Cash pairs are ongoing / terminal-inclusive, in USD.

**Execution: blocked copying.** Each funded account holds at most one position: accounts still in an earlier trade skip a new signal. Replaying every headline winner confirmed that none of their 2,517 accounts ever held two trades at once. Compare the [non-blocking findings](../../../comparisons/legacy_25k_vs_50k/reserve_by_policy/FINDINGS.md), where every live account copies every signal.

This paired search allows each purchase/withdrawal/cadence family to choose its own reserve, with identical headroom coverage for the two account sizes. Use the [complete policy tables](REPORT.generated.md) for every family; this page explains the headline winners and their turnover.

**These are in-sample results under the inherited payout model.** They do not establish future returns or an optimum under the optional stricter post-payout-six balance interpretation. Account fees differ ($200 / $250), so this is an account-type-and-cost comparison.

## Best complete tested bundles: terminal-inclusive cash

| Budget | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| $1,000 + $0/mo | Monthly; minimum / weekly; reserve $27,000 | $200,400.00 / $200,400.00 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478.15 / $268,478.15 | 56 / 1 |
| $1,000 + $200/mo | Monthly + replacements; maximum / weekly; reserve $25,100 | $665,420.55 / $665,420.55 | 531 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $585,935.35 / $585,935.35 | 265 / 20 |
| $5,000 + $0/mo | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / weekly; reserve $51,100 | $550,450.15 / $550,450.15 | 236 / 20 |
| $5,000 + $200/mo | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $603,595.55 / $603,595.55 | 283 / 20 |

## Where the ongoing-cash winner differs

None: in every product/budget pair, the same tested bundle leads both objectives.

## What supports those cash results?

A 20-live-account cap does not limit cumulative purchases to 20. Low reserves combined with prompt replacement can turn this into repeated withdrawal and replacement, rather than a stable book of mature accounts. Ending with 20 alive does not by itself establish low turnover or robust survival.

A selected reserve equal to the frozen floor means zero voluntary headroom, not permission to ignore the firm's payout gates or withdraw below its floor.

The economic ledger records **booked deficits not funded by the owner**: negative account profit that is excluded from the owner's losses. This is a descriptive ledger quantity, not observed firm losses, cash financing or a valuation of limited liability. The killing excursion is unbooked; see the [economic definitions](../../../../ECONOMIC_EFFECTS.md). Purchase fees below are already deducted from net cash.

| Budget | **25K — Bought / ledger** | **25K — Purchase fees** | **25K — Owner-excluded deficits (ratio)** | **50K — Bought / ledger** | **50K — Purchase fees** | **50K — Owner-excluded deficits (ratio)** |
| --- | --- | --- | --- | --- | --- | --- |
| $1,000 + $0/mo | 68 — [Accounts and payouts](legacy_25k__budget_1000_0__best_ongoing/report.txt) | $13,600.00 | $23,843.65 (11.9%) | 56 — [Accounts and payouts](legacy_50k__budget_1000_0__best_ongoing/report.txt) | $14,000.00 | $21,707.70 (8.1%) |
| $1,000 + $200/mo | 531 — [Accounts and payouts](legacy_25k__budget_1000_200__best_ongoing/report.txt) | $106,200.00 | $252,179.40 (37.9%) | 265 — [Accounts and payouts](legacy_50k__budget_1000_200__best_ongoing/report.txt) | $66,250.00 | $147,963.95 (25.3%) |
| $5,000 + $0/mo | 539 — [Accounts and payouts](legacy_25k__budget_5000_0__best_ongoing/report.txt) | $107,800.00 | $254,351.45 (37.9%) | 236 — [Accounts and payouts](legacy_50k__budget_5000_0__best_ongoing/report.txt) | $59,000.00 | $113,489.20 (20.6%) |
| $5,000 + $200/mo | 539 — [Accounts and payouts](legacy_25k__budget_5000_200__best_ongoing/report.txt) | $107,800.00 | $254,351.45 (37.9%) | 283 — [Accounts and payouts](legacy_50k__budget_5000_200__best_ongoing/report.txt) | $70,750.00 | $141,324.60 (23.4%) |

That ratio is descriptive; it does not establish that profitability depends on the deficit amount. Removing limited liability could change subsequent funding, purchases and trading paths. It is not a re-optimized no-subsidy counterfactual. Large turnover makes the assumed immediate PA availability, fixed seat cost and absence of an evaluation phase especially material.

## Same winners under the stricter later-payout interpretation

Keep every selected operating setting fixed, but enforce the account-specific minimum balance after payout six and later. This can change future funding, cohorts and deaths, not just the final receipt. These are **sensitivity results, not re-optimized strict-rule winners**.

| Budget | **25K — Inherited total** | **25K — Stricter total** | **25K — Change** | **25K — Bought / alive** | **50K — Inherited total** | **50K — Stricter total** | **50K — Change** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $1,000 + $0/mo | $200,400.00 | $200,400.00 | $0.00 | 68 / 3 | $268,478.15 | $258,478.15 | $-10,000.00 | 56 / 1 |
| $1,000 + $200/mo | $665,420.55 | $639,420.75 | $-25,999.80 | 511 / 20 | $585,935.35 | $585,935.35 | $0.00 | 265 / 20 |
| $5,000 + $0/mo | $670,285.60 | $644,285.80 | $-25,999.80 | 519 / 20 | $550,450.15 | $550,450.15 | $0.00 | 236 / 20 |
| $5,000 + $200/mo | $670,285.60 | $644,285.80 | $-25,999.80 | 519 / 20 | $603,595.55 | $603,595.55 | $0.00 | 283 / 20 |

## Fixed daily-minimum policy: best total-scoring reserve

Example budget: $1,000 initial plus $200/month. Each row keeps the withdrawal family and cadence fixed, then selects the reserve within the named purchase policy. The complete report covers all four budgets and both objectives.

| Purchases | **25K — Reserve (ties)** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| Monthly + replacements | $25,100 (7 ties) | $467,700.00 / $467,700.00 | 329 / 20 | $50,100 (8 ties) | $400,500.00 / $400,500.00 | 128 / 20 |
| Monthly | $29,500 (1 tie) | $228,200.00 / $229,700.00 | 74 / 3 | $53,000 (1 tie) | $372,000.00 / $372,000.00 | 54 / 3 |
| Weekly | $28,100 (1 tie) | $367,000.00 / $368,500.00 | 90 / 10 | $53,200 (1 tie) | $399,750.00 / $400,923.65 | 75 / 12 |

## Matched monthly-purchase reference

Daily minimum withdrawals, headroom $6,800: reserve $31,900 for 25K and $56,900 for 50K. This holds the operating settings fixed, in contrast to the separately selected bundles above.

| Budget | 25K total | 50K total | 50K minus 25K |
|---|---:|---:|---:|
| $1,000 + $0/mo | $-1,000.00 | $-1,000.00 | $0.00 |
| $1,000 + $200/mo | $206,700.00 | $297,500.00 | $90,800.00 |
| $5,000 + $0/mo | $75,000.00 | $106,750.00 | $31,750.00 |
| $5,000 + $200/mo | $206,700.00 | $321,500.00 | $114,800.00 |

## How to interpret a selected reserve

The new [best-by-policy file](best_by_policy.csv) records exact ties and explicit tested reserves within 1% of each best positive score. These need not form a continuous band. A boundary winner is conditional on the tested limits; a flat loss across reserves means no useful reserve was found, not that the smallest displayed reserve is a sound choice.

Best-complete-bundle comparisons answer which tested combination made more cash on this tape. They must not be described as a reserve-only improvement or evidence that a larger account always performs better. Before using high-turnover leaders operationally, the unresolved payout interpretation and acquisition assumptions are the next material questions to test.

Regenerate this explanation and the verified winner ledgers with `scripts/explain_legacy_reserve_comparison.py config/studies/legacy_reserve_comparison_blocking.json` after the main study. Existing `FINDINGS.md` remains reader-owned; `FINDINGS.generated.md` is refreshed.
