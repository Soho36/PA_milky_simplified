# RR 0.50 / RR 2.50 with overlap: monthly withdrawal amount x cushion

262 candidates including hold. Same eight payout families, coarse grid and local refinement as the original study. Full historical payout rulebook, processing delay off, one MNQ per trade, $200 purchase fee.

**Allocation:** new monthly purchases alternate 0.50, 2.50, starting with 0.50. Each account keeps its variant for life. The 50/50 target applies to purchases, not surviving accounts; deaths can skew the live allocation. The schedule is fixed across policies so withdrawals cannot change future variant assignments.

**Execution:** each account takes every eligible signal from its assigned variant, allowing unlimited overlapping positions. This reproduces the original whole-trade MAE/MFE/P&L settlement at exit, without aggregate open-position mark-to-market. A death stops subsequent settlements, including trades already open. The same uncapped, externally financed monthly purchases are retained: no 20-seat cap, evaluation queue, funding budget or additional replacements. This is a policy sweep, not the fully built 20-seat experiment.

## Extraction ceiling

The hold benchmark makes no withdrawal during trading, so no account dies from one and no candidate outlives it. Its path books $470,886.50 of trading earnings, and emptying that path completely -- nothing left standing in live accounts, no profit split -- would put $481,308.75 in the pocket. Ceiling capture scores combined net cash against that one number, so candidates are read on a fixed yardstick instead of each against the smaller path its own withdrawals left it.

Outliving the benchmark is impossible; out-earning it is not. An account that dies early sits out whatever the benchmark went on to trade, and that stretch can lose money, so a capture above 100% is recorded rather than treated as an error. None of the 261 tested settings out-earn it, so on this tape the reference path is the earnings maximum as well. That is an observed result, not a property of the rulebook.

Trading-neutral means every account took exactly the trades it took under the benchmark. It is decided on a per-account fingerprint of exact booked trade keys, assignment and killing trade, never on the earnings total, which two different paths can share. 150 of 261 tested settings qualify. Best capture is 92.16% (fixed_1500_backlog at $31,200), leaving $37,726.97 unextracted -- $10,607.22 to the firm's split and $27,119.75 still standing in live accounts. The benchmark captures 2.64% of its own ceiling: one permitted request per account strands $468,608.75 of its equity.

Both columns are properties of this tape and this monthly acquisition cadence. Capture is an accounting ratio, not a probability of success, and not a comparison against any alternative anyone could actually run.

The neutrality check here hashes every accepted trade key per account, including assignment and killing trade. The ceiling is a fixed no-withdrawal reference, not an achievable payout policy.

## Best tested cushion per policy: ongoing cash

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1500_backlog | $31,200 | $367,282.17 | $76,299.61 | $443,581.78 | 79 | 21 | yes | 92.16% |
| maximum_excess_monthly | $31,200 | $367,282.17 | $76,299.61 | $443,581.78 | 79 | 21 | yes | 92.16% |
| fixed_1000_backlog | $31,200 | $361,832.75 | $74,935.72 | $436,768.47 | 79 | 21 | yes | 90.75% |
| fixed_750_backlog | $31,200 | $341,933.38 | $58,815.88 | $400,749.26 | 79 | 21 | yes | 83.26% |
| legacy_500_blocks | $30,800 | $281,550.00 | $46,134.90 | $327,684.90 | 79 | 21 | yes | 68.08% |
| fixed_500_backlog | $31,200 | $279,864.96 | $53,927.64 | $333,792.60 | 79 | 21 | yes | 69.35% |
| minimum_monthly | $28,800 | $221,950.00 | $0.00 | $221,950.00 | 79 | 20 | no | 46.11% |
| fixed_250_backlog | $29,200 | $172,694.55 | $171,285.77 | $343,980.32 | 79 | 21 | yes | 71.47% |

## Best tested cushion per policy: including terminal request

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1500_backlog | $31,200 | $367,282.17 | $76,299.61 | $443,581.78 | 79 | 21 | yes | 92.16% |
| maximum_excess_monthly | $31,200 | $367,282.17 | $76,299.61 | $443,581.78 | 79 | 21 | yes | 92.16% |
| fixed_1000_backlog | $31,200 | $361,832.75 | $74,935.72 | $436,768.47 | 79 | 21 | yes | 90.75% |
| fixed_750_backlog | $35,200 | $287,245.52 | $115,034.90 | $402,280.42 | 79 | 21 | yes | 83.58% |
| fixed_250_backlog | $32,300 | $168,498.00 | $216,110.44 | $384,608.44 | 79 | 21 | yes | 79.91% |
| fixed_500_backlog | $31,200 | $279,864.96 | $53,927.64 | $333,792.60 | 79 | 21 | yes | 69.35% |
| legacy_500_blocks | $31,200 | $278,550.00 | $54,924.79 | $333,474.79 | 79 | 21 | yes | 69.28% |
| minimum_monthly | $28,800 | $221,950.00 | $0.00 | $221,950.00 | 79 | 20 | no | 46.11% |

## Hold reference

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| hold | none | $-15,800.00 | $28,500.00 | $12,700.00 | 79 | 21 | yes | 2.64% |

Retained balance = $25,100 frozen floor + headroom. Initial accounts still start at $25,000 with $1,500 trailing drawdown; a retained-balance setting is a withdrawal threshold, not starting capital. Minimum monthly asks $500 without backlog. Fixed targets accrue backlog; legacy rounds to $500 blocks. Maximum asks all permitted excess. Net cash deducts purchase fees and firm split. Terminal cash is one permitted request per surviving account, not liquidation.

## What the experiment says

The ongoing-cash leader is fixed_1500_backlog at $31,200, with $367,282.17 and 21 survivors. The closing-cash leader is fixed_1500_backlog at $31,200, with $443,581.78, including $76,299.61 at exit.

The ongoing-cash leader is trading-neutral: its withdrawals cost no trade. The closing-cash leader is trading-neutral: its withdrawals cost no trade.

The closing leader ties at these tested retained balances: $31,200. A tie in closing cash can still hide different cash timing. The first table selects only one representative per family.

Minimum monthly requests are fundamentally different from a $500 backlog entitlement: missed monthly requests do not accumulate into larger future withdrawals. This experiment identifies policy bundles, not a pure causal effect of the nominal target. The local refinement is not exhaustive, and survivor cliffs make exact winning thresholds fragile.

### Nearby tested settings for the two leaders

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1500_backlog | $31,100 | $329,241.03 | $70,714.69 | $399,955.72 | 79 | 20 | no | 83.10% |
| fixed_1500_backlog | $31,200 | $367,282.17 | $76,299.61 | $443,581.78 | 79 | 21 | yes | 92.16% |
| fixed_1500_backlog | $31,300 | $364,477.12 | $72,549.87 | $437,026.99 | 79 | 21 | yes | 90.80% |
| fixed_1500_backlog | $31,400 | $362,892.67 | $73,909.87 | $436,802.54 | 79 | 21 | yes | 90.75% |
| fixed_1500_backlog | $31,500 | $361,191.07 | $75,269.87 | $436,460.94 | 79 | 21 | yes | 90.68% |

## Validation and reproduction

All 262 economic ledgers reconcile. Audited 31,382,198 accepted copies for variant membership, activation, booked settlement counts and killing trades. Both winning runs were reproduced with account and payout ledgers. The loader checks trade/stats reconciliation and per-window coverage; hashes and actual spans for both variants are in study.json.

Reproduce: `venv/Scripts/python.exe scripts/study_rr_pair_overlap_withdrawal_amount.py --workers 4`. Use this runner: the normal single-tape CLI does not encode the mixed allocation. See candidates.csv, study.json, best_ongoing/ and best_terminal/. Thresholds are in-sample, the refinement is local, and the allocation order is fixed rather than permutation-tested.
