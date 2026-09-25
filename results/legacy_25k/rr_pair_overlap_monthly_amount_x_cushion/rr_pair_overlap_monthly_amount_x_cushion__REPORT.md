# RR 1.00 vs RR 0.50 / 2.50: overlapping-position withdrawal study

**Comparison layout:** RR 1.00 is on the left; the RR 0.50 / 2.50 pair is on the right. Both use overlapping positions and uncapped monthly purchases. Tables use the saved [original RR1 study](../../study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores__REPORT.md) and [pair scores](study.json). The original tested 301 candidates; the pair tested 262, because local refinement follows different winners. Ceiling capture is relative to each book's own hold path, not a shared dollar ceiling.

Unless explicitly compared in a table, the narrative below describes the **pair**.

262 candidates including hold. Same eight payout families, coarse grid and local refinement as the original study. Full historical payout rulebook, processing delay off, one MNQ per trade, $200 purchase fee.

**Allocation:** new monthly purchases alternate 0.50, 2.50, starting with 0.50. Each account keeps its variant for life. The 50/50 target applies to purchases, not surviving accounts; deaths can skew the live allocation. The schedule is fixed across policies so withdrawals cannot change future variant assignments.

**Execution:** each account takes every eligible signal from its assigned variant, allowing unlimited overlapping positions. This reproduces the original whole-trade MAE/MFE/P&L settlement at exit, without aggregate open-position mark-to-market. A death stops subsequent settlements, including trades already open. The same uncapped, externally financed monthly purchases are retained: no 20-seat cap, evaluation queue, funding budget or additional replacements. This is a policy sweep, not the fully built 20-seat experiment.

## Pair extraction ceiling

The hold benchmark makes no withdrawal during trading, so no account dies from one and no candidate outlives it. Its path books $470,886.50 of trading earnings, and emptying that path completely -- nothing left standing in live accounts, no profit split -- would put $481,308.75 in the pocket. Ceiling capture scores combined net cash against that one number, so candidates are read on a fixed yardstick instead of each against the smaller path its own withdrawals left it.

Outliving the benchmark is impossible; out-earning it is not. An account that dies early sits out whatever the benchmark went on to trade, and that stretch can lose money, so a capture above 100% is recorded rather than treated as an error. None of the 261 tested settings out-earn it, so on this tape the reference path is the earnings maximum as well. That is an observed result, not a property of the rulebook.

Trading-neutral means every account took exactly the trades it took under the benchmark. It is decided on a per-account fingerprint of exact booked trade keys, assignment and killing trade, never on the earnings total, which two different paths can share. 150 of 261 tested settings qualify. Best capture is 92.16% (fixed_1500_backlog at $31,200), leaving $37,726.97 unextracted -- $10,607.22 to the firm's split and $27,119.75 still standing in live accounts. The benchmark captures 2.64% of its own ceiling: one permitted request per account strands $468,608.75 of its equity.

Both columns are properties of this tape and this monthly acquisition cadence. Capture is an accounting ratio, not a probability of success, and not a comparison against any alternative anyone could actually run.

The neutrality check here hashes every accepted trade key per account, including assignment and killing trade. The ceiling is a fixed no-withdrawal reference, not an achievable payout policy.

## Best tested cushion per policy: ongoing cash

Each side selects its own best tested reserve for this objective; the reserves can differ. Both books purchase 79 accounts. Policy order is identical in both sections.

| Policy / setting | Measurement | RR 1.00 (left) | RR 0.50 / 2.50 pair (right) |
|---|---|---:|---:|
| **fixed_250_backlog** | Retained balance | $30,800 | $29,200 |
| | Ongoing net cash | $185,507.10 | $172,694.55 |
| | Terminal receipt | $271,778.91 | $171,285.77 |
| | Combined net cash | $457,286.01 | $343,980.32 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.82% | 71.47% |
| **fixed_500_backlog** | Retained balance | $29,800 | $31,200 |
| | Ongoing net cash | $358,718.90 | $279,864.96 |
| | Terminal receipt | $79,443.98 | $53,927.64 |
| | Combined net cash | $438,162.88 | $333,792.60 |
| | Alive | 17 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 92.77% | 69.35% |
| **fixed_750_backlog** | Retained balance | $29,800 | $31,200 |
| | Ongoing net cash | $371,497.01 | $341,933.38 |
| | Terminal receipt | $0.00 | $58,815.88 |
| | Combined net cash | $371,497.01 | $400,749.26 |
| | Alive | 2 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 78.66% | 83.26% |
| **fixed_1000_backlog** | Retained balance | $29,800 | $31,200 |
| | Ongoing net cash | $370,417.36 | $361,832.75 |
| | Terminal receipt | $0.00 | $74,935.72 |
| | Combined net cash | $370,417.36 | $436,768.47 |
| | Alive | 2 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 78.43% | 90.75% |
| **fixed_1500_backlog** | Retained balance | $29,800 | $31,200 |
| | Ongoing net cash | $370,417.36 | $367,282.17 |
| | Terminal receipt | $0.00 | $76,299.61 |
| | Combined net cash | $370,417.36 | $443,581.78 |
| | Alive | 2 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 78.43% | 92.16% |
| **minimum_monthly** | Retained balance | $28,400 | $28,800 |
| | Ongoing net cash | $283,200.00 | $221,950.00 |
| | Terminal receipt | $152,960.79 | $0.00 |
| | Combined net cash | $436,160.79 | $221,950.00 |
| | Alive | 18 | 20 |
| | Trading-neutral | no | no |
| | Own hold-ceiling capture | 92.35% | 46.11% |
| **maximum_excess_monthly** | Retained balance | $29,800 | $31,200 |
| | Ongoing net cash | $370,417.36 | $367,282.17 |
| | Terminal receipt | $0.00 | $76,299.61 |
| | Combined net cash | $370,417.36 | $443,581.78 |
| | Alive | 2 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 78.43% | 92.16% |
| **legacy_500_blocks** | Retained balance | $29,800 | $30,800 |
| | Ongoing net cash | $358,000.00 | $281,550.00 |
| | Terminal receipt | $79,443.98 | $46,134.90 |
| | Combined net cash | $437,443.98 | $327,684.90 |
| | Alive | 17 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 92.62% | 68.08% |

## Best tested cushion per policy: including terminal request

Each side selects its own best tested reserve for this objective; the reserves can differ. Both books purchase 79 accounts. Policy order is identical in both sections.

| Policy / setting | Measurement | RR 1.00 (left) | RR 0.50 / 2.50 pair (right) |
|---|---|---:|---:|
| **fixed_250_backlog** | Retained balance | $30,100 | $32,300 |
| | Ongoing net cash | $185,200.00 | $168,498.00 |
| | Terminal receipt | $272,278.91 | $216,110.44 |
| | Combined net cash | $457,478.91 | $384,608.44 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.86% | 79.91% |
| **fixed_500_backlog** | Retained balance | $31,600 | $31,200 |
| | Ongoing net cash | $346,082.70 | $279,864.96 |
| | Terminal receipt | $110,403.31 | $53,927.64 |
| | Combined net cash | $456,486.01 | $333,792.60 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 69.35% |
| **fixed_750_backlog** | Retained balance | $31,600 | $35,200 |
| | Ongoing net cash | $354,140.38 | $287,245.52 |
| | Terminal receipt | $102,345.63 | $115,034.90 |
| | Combined net cash | $456,486.01 | $402,280.42 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 83.58% |
| **fixed_1000_backlog** | Retained balance | $31,600 | $31,200 |
| | Ongoing net cash | $354,140.38 | $361,832.75 |
| | Terminal receipt | $102,345.63 | $74,935.72 |
| | Combined net cash | $456,486.01 | $436,768.47 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 90.75% |
| **fixed_1500_backlog** | Retained balance | $31,600 | $31,200 |
| | Ongoing net cash | $354,140.38 | $367,282.17 |
| | Terminal receipt | $102,345.63 | $76,299.61 |
| | Combined net cash | $456,486.01 | $443,581.78 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 92.16% |
| **minimum_monthly** | Retained balance | $30,000 | $28,800 |
| | Ongoing net cash | $266,200.00 | $221,950.00 |
| | Terminal receipt | $194,311.75 | $0.00 |
| | Combined net cash | $460,511.75 | $221,950.00 |
| | Alive | 22 | 20 |
| | Trading-neutral | yes | no |
| | Own hold-ceiling capture | 97.50% | 46.11% |
| **maximum_excess_monthly** | Retained balance | $31,600 | $31,200 |
| | Ongoing net cash | $354,140.38 | $367,282.17 |
| | Terminal receipt | $102,345.63 | $76,299.61 |
| | Combined net cash | $456,486.01 | $443,581.78 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 92.16% |
| **legacy_500_blocks** | Retained balance | $31,400 | $31,200 |
| | Ongoing net cash | $345,400.00 | $278,550.00 |
| | Terminal receipt | $111,078.91 | $54,924.79 |
| | Combined net cash | $456,478.91 | $333,474.79 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 96.65% | 69.28% |

## Hold reference

| Policy / setting | Measurement | RR 1.00 (left) | RR 0.50 / 2.50 pair (right) |
|---|---|---:|---:|
| **hold** | Retained balance | none | none |
| | Ongoing net cash | $-15,800.00 | $-15,800.00 |
| | Terminal receipt | $30,000.00 | $28,500.00 |
| | Combined net cash | $14,200.00 | $12,700.00 |
| | Alive | 22 | 21 |
| | Trading-neutral | yes | yes |
| | Own hold-ceiling capture | 3.01% | 2.64% |

Retained balance = $25,100 frozen floor + headroom. Initial accounts still start at $25,000 with $1,500 trailing drawdown; a retained-balance setting is a withdrawal threshold, not starting capital. Minimum monthly asks $500 without backlog. Fixed targets accrue backlog; legacy rounds to $500 blocks. Maximum asks all permitted excess. Net cash deducts purchase fees and firm split. Terminal cash is one permitted request per surviving account, not liquidation.

## What the pair experiment says

**Interpretation for choosing an operating policy:** the mixture may change which accounts fail together, but this comparison has not established a general advantage in profitability, cash extraction or reserve requirements. The two cash-optimal books preserve their own hold paths; the pair books slightly more net trading earnings, while RR1 extracts more total cash after the terminal request. Trading earnings and accessible cash are different outcomes.

The comparison also cannot isolate the benefit of mixing from the merits of the constituents themselves. Homogeneous RR 0.50 and RR 2.50 controls under the same operating setup are needed for that. Account equity is separate: a surviving component cannot transfer its headroom to rescue a failing account, so diversification does not automatically reduce the reserve needed in each account.

For withdrawal-policy selection, give more weight to **ongoing cash, preservation of trading capacity, and performance across a reserve range** than to one winning total-cash figure that includes a large endpoint payout. Terminal receipts depend on eligibility at the chosen endpoint. Exact winning reserves are in-sample thresholds, not established safe minimums. The uncapped monthly-purchase results do not by themselves settle the policy choice for a capped, growing live book.

The ongoing-cash leader is fixed_1500_backlog at $31,200, with $367,282.17 and 21 survivors. The closing-cash leader is fixed_1500_backlog at $31,200, with $443,581.78, including $76,299.61 at exit.

The ongoing-cash leader is trading-neutral: its withdrawals cost no trade. The closing-cash leader is trading-neutral: its withdrawals cost no trade.

The closing leader ties at these tested retained balances: $31,200. A tie in closing cash can still hide different cash timing. The first table selects only one representative per family.

Minimum monthly requests are fundamentally different from a $500 backlog entitlement: missed monthly requests do not accumulate into larger future withdrawals. This experiment identifies policy bundles, not a pure causal effect of the nominal target. The local refinement is not exhaustive, and survivor cliffs make exact winning thresholds fragile.

### Nearby tested settings for the two leaders

The pair has the same leader for both objectives. Here both sides use **the same policy and retained balance**, rather than their independently selected winners. Missing historical settings are marked “not tested”; no scores are interpolated.

| Policy / setting | Measurement | RR 1.00 (left) | RR 0.50 / 2.50 pair (right) |
|---|---|---:|---:|
| **fixed_1500_backlog / $31,100** | Ongoing net cash | $362,770.74 | $329,241.03 |
| | Terminal receipt | $83,098.20 | $70,714.69 |
| | Combined net cash | $445,868.94 | $399,955.72 |
| | Alive | 20 | 20 |
| | Trading-neutral | no | no |
| | Own hold-ceiling capture | 94.40% | 83.10% |
| **fixed_1500_backlog / $31,200** | Ongoing net cash | $360,834.78 | $367,282.17 |
| | Terminal receipt | $84,734.15 | $76,299.61 |
| | Combined net cash | $445,568.93 | $443,581.78 |
| | Alive | 20 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 94.34% | 92.16% |
| **fixed_1500_backlog / $31,300** | Ongoing net cash | $358,894.78 | $364,477.12 |
| | Terminal receipt | $86,374.15 | $72,549.87 |
| | Combined net cash | $445,268.93 | $437,026.99 |
| | Alive | 20 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 94.28% | 90.80% |
| **fixed_1500_backlog / $31,400** | Ongoing net cash | $356,954.78 | $362,892.67 |
| | Terminal receipt | $88,014.15 | $73,909.87 |
| | Combined net cash | $444,968.93 | $436,802.54 |
| | Alive | 20 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 94.21% | 90.75% |
| **fixed_1500_backlog / $31,500** | Ongoing net cash | $355,014.78 | $361,191.07 |
| | Terminal receipt | $89,654.15 | $75,269.87 |
| | Combined net cash | $444,668.93 | $436,460.94 |
| | Alive | 20 | 21 |
| | Trading-neutral | no | yes |
| | Own hold-ceiling capture | 94.15% | 90.68% |

## Validation and reproduction

All 262 economic ledgers reconcile. Audited 31,382,198 accepted copies for variant membership, activation, booked settlement counts and killing trades. Both winning runs were reproduced with account and payout ledgers. The loader checks trade/stats reconciliation and per-window coverage; hashes and actual spans for both variants are in study.json.

Reproduce: `venv/Scripts/python.exe scripts/study_rr_pair_overlap_withdrawal_amount.py --workers 4`. Use this runner: the normal single-tape CLI does not encode the mixed allocation. See candidates.csv, study.json, best_ongoing/ and best_terminal/. Thresholds are in-sample, the refinement is local, and the allocation order is fixed rather than permutation-tested.
