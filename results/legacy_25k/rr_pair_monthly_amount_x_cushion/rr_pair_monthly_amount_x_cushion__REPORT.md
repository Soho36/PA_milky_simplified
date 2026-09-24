# RR 0.50 / RR 2.50: monthly withdrawal amount x cushion

265 candidates including hold. Same eight payout families, coarse grid and local refinement as the original study. Full historical payout rulebook, processing delay off, one MNQ per account, $200 purchase fee.

**Allocation:** new monthly purchases alternate 0.50, 2.50, starting with 0.50. Each account keeps its variant for life. The 50/50 target applies to purchases, not surviving accounts; deaths can skew the live allocation. The schedule is fixed across policies so withdrawals cannot change future variant assignments.

**Execution difference:** each account accepts every eligible signal from its variant while flat. The referenced original study allowed overlapping positions; its dollar totals are not a matched control. The same uncapped, externally financed monthly purchases are retained: no 20-seat cap, evaluation queue, funding budget or additional replacements. This is a policy sweep, not the fully built 20-seat experiment.

## Extraction ceiling

The hold benchmark makes no withdrawal during trading, so no account dies from one and no candidate outlives it. Its path books $527,774.40 of trading earnings, and emptying that path completely -- nothing left standing in live accounts, no profit split -- would put $535,885.10 in the pocket. Ceiling capture scores combined net cash against that one number, so candidates are read on a fixed yardstick instead of each against the smaller path its own withdrawals left it.

Outliving the benchmark is impossible; out-earning it is not. An account that dies early sits out whatever the benchmark went on to trade, and that stretch can lose money, so a capture above 100% is recorded rather than treated as an error. None of the 264 tested settings out-earn it, so on this tape the reference path is the earnings maximum as well. That is an observed result, not a property of the rulebook.

Trading-neutral means every account took exactly the trades it took under the benchmark. It is decided on a per-account fingerprint of trade counts, booked results and killing trade, never on the earnings total, which two different paths can share. 156 of 264 tested settings qualify. Best capture is 92.48% (fixed_1000_backlog at $29,600), leaving $40,295.75 unextracted -- $7,548.61 to the firm's split and $32,747.14 still standing in live accounts. The benchmark captures 4.05% of its own ceiling: one permitted request per account strands $514,185.10 of its equity.

Both columns are properties of this tape and this monthly acquisition cadence. Capture is an accounting ratio, not a probability of success, and not a comparison against any alternative anyone could actually run.

The neutrality check here hashes every accepted trade key per account, including assignment and killing trade. The ceiling is a fixed no-withdrawal reference, not an achievable payout policy.

## Best tested cushion per policy: ongoing cash

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1000_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_1500_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| maximum_excess_monthly | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_750_backlog | $29,600 | $411,777.98 | $62,222.10 | $474,000.08 | 79 | 27 | yes | 88.45% |
| fixed_500_backlog | $29,600 | $362,727.48 | $40,018.87 | $402,746.35 | 79 | 27 | yes | 75.16% |
| legacy_500_blocks | $29,400 | $362,100.00 | $40,163.72 | $402,263.72 | 79 | 27 | yes | 75.07% |
| minimum_monthly | $29,400 | $234,200.00 | $1,500.00 | $235,700.00 | 79 | 27 | yes | 43.98% |
| fixed_250_backlog | $29,900 | $191,922.35 | $140,578.97 | $332,501.32 | 79 | 27 | yes | 62.05% |

## Best tested cushion per policy: including terminal request

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1000_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_1500_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| maximum_excess_monthly | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_750_backlog | $31,300 | $373,354.14 | $112,886.81 | $486,240.95 | 79 | 27 | yes | 90.74% |
| fixed_500_backlog | $30,400 | $353,425.48 | $58,866.08 | $412,291.56 | 79 | 27 | yes | 76.94% |
| legacy_500_blocks | $30,400 | $350,550.00 | $60,601.28 | $411,151.28 | 79 | 27 | yes | 76.72% |
| fixed_250_backlog | $29,400 | $189,876.70 | $208,497.14 | $398,373.84 | 79 | 26 | no | 74.34% |
| minimum_monthly | $29,400 | $234,200.00 | $1,500.00 | $235,700.00 | 79 | 27 | yes | 43.98% |

## Hold reference

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| hold | none | $-15,800.00 | $37,500.00 | $21,700.00 | 79 | 27 | yes | 4.05% |

Retained balance = $25,100 frozen floor + headroom. Initial accounts still start at $25,000 with $1,500 trailing drawdown; a retained-balance setting is a withdrawal threshold, not starting capital. Minimum monthly asks $500 without backlog. Fixed targets accrue backlog; legacy rounds to $500 blocks. Maximum asks all permitted excess. Net cash deducts purchase fees and firm split. Terminal cash is one permitted request per surviving account, not liquidation.

## What the experiment says

The ongoing-cash leader is fixed_1000_backlog at $29,600, with $415,319.38 and 27 survivors. The closing-cash leader is fixed_1000_backlog at $29,600, with $495,589.35, including $80,269.97 at exit.

The ongoing-cash leader is trading-neutral: its withdrawals cost no trade. The closing-cash leader is trading-neutral: its withdrawals cost no trade.

The closing leader ties at these tested retained balances: $29,600. A tie in closing cash can still hide different cash timing. The first table selects only one representative per family.

Minimum monthly requests are fundamentally different from a $500 backlog entitlement: missed monthly requests do not accumulate into larger future withdrawals. This experiment identifies policy bundles, not a pure causal effect of the nominal target. The local refinement is not exhaustive, and survivor cliffs make exact winning thresholds fragile.

### Nearby tested settings for the two leaders

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Accounts | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|---:|:-:|---:|
| fixed_1000_backlog | $29,300 | $325,535.30 | $26,784.98 | $352,320.28 | 79 | 13 | no | 65.75% |
| fixed_1000_backlog | $29,400 | $374,955.32 | $27,484.98 | $402,440.30 | 79 | 13 | no | 75.10% |
| fixed_1000_backlog | $29,500 | $372,705.32 | $28,184.98 | $400,890.30 | 79 | 13 | no | 74.81% |
| fixed_1000_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_1000_backlog | $29,700 | $413,038.70 | $82,105.65 | $495,144.35 | 79 | 27 | yes | 92.40% |
| fixed_1000_backlog | $29,800 | $409,771.30 | $85,445.65 | $495,216.95 | 79 | 27 | yes | 92.41% |
| fixed_1000_backlog | $29,900 | $407,631.30 | $87,285.65 | $494,916.95 | 79 | 27 | yes | 92.36% |
| fixed_1000_backlog | $29,300 | $325,535.30 | $26,784.98 | $352,320.28 | 79 | 13 | no | 65.75% |
| fixed_1000_backlog | $29,400 | $374,955.32 | $27,484.98 | $402,440.30 | 79 | 13 | no | 75.10% |
| fixed_1000_backlog | $29,500 | $372,705.32 | $28,184.98 | $400,890.30 | 79 | 13 | no | 74.81% |
| fixed_1000_backlog | $29,600 | $415,319.38 | $80,269.97 | $495,589.35 | 79 | 27 | yes | 92.48% |
| fixed_1000_backlog | $29,700 | $413,038.70 | $82,105.65 | $495,144.35 | 79 | 27 | yes | 92.40% |
| fixed_1000_backlog | $29,800 | $409,771.30 | $85,445.65 | $495,216.95 | 79 | 27 | yes | 92.41% |
| fixed_1000_backlog | $29,900 | $407,631.30 | $87,285.65 | $494,916.95 | 79 | 27 | yes | 92.36% |

## Validation and reproduction

All 265 economic ledgers reconcile. Audited 25,222,356 accepted copies for variant membership, activation, non-overlap, counts and killing trades. Both winning runs were reproduced with account and payout ledgers. The loader checks trade/stats reconciliation and per-window coverage; hashes and actual spans for both variants are in study.json.

Reproduce: `venv/Scripts/python.exe scripts/study_rr_pair_withdrawal_amount.py --workers 4`. Use this runner: the normal single-tape CLI does not encode the mixed allocation. See candidates.csv, study.json, best_ongoing/ and best_terminal/. Thresholds are in-sample, the refinement is local, and the allocation order is fixed rather than permutation-tested.
