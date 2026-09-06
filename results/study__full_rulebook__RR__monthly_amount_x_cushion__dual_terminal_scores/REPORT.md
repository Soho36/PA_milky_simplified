# Withdrawal amount x cushion

301 candidates, configured full payout rulebook (processing delay off), RR tape. One new account monthly; identical trading path for each candidate's two endpoint scores.

## Extraction ceiling

The hold benchmark makes no withdrawal during trading, so no account dies from one and no candidate outlives it. Its path books $462,022.20 of trading earnings, and emptying that path completely -- nothing left standing in live accounts, no profit split -- would put $472,299.10 in the pocket. Ceiling capture scores combined net cash against that one number, so candidates are read on a fixed yardstick instead of each against the smaller path its own withdrawals left it.

Outliving the benchmark is impossible; out-earning it is not. An account that dies early sits out whatever the benchmark went on to trade, and that stretch can lose money, so a capture above 100% is recorded rather than treated as an error. None of the 300 tested settings out-earn it, so on this tape the reference path is the earnings maximum as well. That is an observed result, not a property of the rulebook.

Trading-neutral means every account took exactly the trades it took under the benchmark. It is decided on a per-account fingerprint of trade counts, booked results and killing trade, never on the earnings total, which two different paths can share. 109 of 300 tested settings qualify. Best capture is 97.50% (minimum_monthly at $30,000), leaving $11,787.35 unextracted -- $6,004.80 to the firm's split and $5,782.55 still standing in live accounts. The benchmark captures 3.01% of its own ceiling: one permitted request per account strands $458,099.10 of its equity.

Both columns are properties of this tape and this monthly acquisition cadence. Capture is an accounting ratio, not a probability of success, and not a comparison against any alternative anyone could actually run.

## Best tested cushion per policy: ongoing cash

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|:-:|---:|
| fixed_750_backlog | $29,800 | $371,497.01 | $0.00 | $371,497.01 | 2 | no | 78.66% |
| fixed_1000_backlog | $29,800 | $370,417.36 | $0.00 | $370,417.36 | 2 | no | 78.43% |
| fixed_1500_backlog | $29,800 | $370,417.36 | $0.00 | $370,417.36 | 2 | no | 78.43% |
| maximum_excess_monthly | $29,800 | $370,417.36 | $0.00 | $370,417.36 | 2 | no | 78.43% |
| fixed_500_backlog | $29,800 | $358,718.90 | $79,443.98 | $438,162.88 | 17 | no | 92.77% |
| legacy_500_blocks | $29,800 | $358,000.00 | $79,443.98 | $437,443.98 | 17 | no | 92.62% |
| minimum_monthly | $28,400 | $283,200.00 | $152,960.79 | $436,160.79 | 18 | no | 92.35% |
| fixed_250_backlog | $30,800 | $185,507.10 | $271,778.91 | $457,286.01 | 22 | yes | 96.82% |

## Best tested cushion per policy: cash including terminal request

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|:-:|---:|
| minimum_monthly | $30,000 | $266,200.00 | $194,311.75 | $460,511.75 | 22 | yes | 97.50% |
| fixed_250_backlog | $30,100 | $185,200.00 | $272,278.91 | $457,478.91 | 22 | yes | 96.86% |
| fixed_500_backlog | $31,600 | $346,082.70 | $110,403.31 | $456,486.01 | 22 | yes | 96.65% |
| fixed_750_backlog | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | yes | 96.65% |
| fixed_1000_backlog | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | yes | 96.65% |
| fixed_1500_backlog | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | yes | 96.65% |
| maximum_excess_monthly | $31,600 | $354,140.38 | $102,345.63 | $456,486.01 | 22 | yes | 96.65% |
| legacy_500_blocks | $31,400 | $345,400.00 | $111,078.91 | $456,478.91 | 22 | yes | 96.65% |

## Hold benchmark

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|:-:|---:|
| hold | none | $-15,800.00 | $30,000.00 | $14,200.00 | 22 | yes | 3.01% |

## Design and interpretation

Fixed targets accrue backlog and permit partial requests after caps; they are not monthly ceilings. The legacy control rounds to whole $500 blocks. Minimum requests $500 monthly without backlog; maximum requests everything permitted above the voluntary cushion. A $250 target can build enough backlog for the $500 minimum.

All net cash deducts the same purchase fees and applicable split. Terminal scoring releases the voluntary cushion and makes one request through the same rulebook; it does not turn paper profit into unrestricted cash. Alive counts are before terminal withdrawal. The two scores are alternative objectives, not independent simulations.

The coarse grid spans $0-$10,000 headroom above the frozen floor, plus no cushion. Each policy's coarse winner for each objective is refined within $500 in $100 steps. This local search can miss other peaks; winning settings are in-sample, not validated operating recommendations. Acquisition cadence, withdrawal cadence, execution assumptions and tape remain fixed.

Reproduce from project root: `venv/Scripts/python.exe scripts/study_withdrawal_amount.py`. See study.json for embedded config, candidate policies, exact grids, input/engine hashes and accounting; candidates.csv for all scores.

## What the experiment says

The ongoing-cash leader is fixed_750_backlog at $29,800, with $371,497.01 and 2 survivors. The closing-cash leader is minimum_monthly at $30,000, with $460,511.75, including $194,311.75 at exit.

The ongoing-cash leader is not trading-neutral: its withdrawals changed which trades were taken, moving booked trading earnings by $-90,300.05 against the benchmark path, and it captures 78.66% of the ceiling. The closing-cash leader is trading-neutral: its withdrawals cost no trade.

The closing leader ties at these tested retained balances: $30,000, $30,100, $30,200, $30,300, $30,400, $30,500, $30,600, $31,100. A tie in closing cash can still hide different cash timing. The first table selects only one representative per family.

Minimum monthly requests are fundamentally different from a $500 backlog entitlement: missed monthly requests do not accumulate into larger future withdrawals. This experiment identifies policy bundles, not a pure causal effect of the nominal target. The local refinement is not exhaustive, and survivor cliffs make exact winning thresholds fragile.

### Nearby tested settings for the two leaders

| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash | Alive | Trading-neutral | Ceiling capture |
|---|---:|---:|---:|---:|---:|:-:|---:|
| fixed_750_backlog | $29,600 | $322,366.76 | $0.00 | $322,366.76 | 2 | no | 68.25% |
| fixed_750_backlog | $29,700 | $319,756.11 | $0.00 | $319,756.11 | 2 | no | 67.70% |
| fixed_750_backlog | $29,800 | $371,497.01 | $0.00 | $371,497.01 | 2 | no | 78.66% |
| fixed_750_backlog | $29,900 | $369,812.86 | $0.00 | $369,812.86 | 2 | no | 78.30% |
| fixed_750_backlog | $30,000 | $367,979.06 | $0.00 | $367,979.06 | 2 | no | 77.91% |
| fixed_750_backlog | $30,100 | $366,554.16 | $1,500.00 | $368,054.16 | 3 | no | 77.93% |
| minimum_monthly | $29,700 | $267,700.00 | $181,320.87 | $449,020.87 | 20 | no | 95.07% |
| minimum_monthly | $29,800 | $266,700.00 | $182,320.87 | $449,020.87 | 20 | no | 95.07% |
| minimum_monthly | $29,900 | $266,200.00 | $188,541.66 | $454,741.66 | 21 | no | 96.28% |
| minimum_monthly | $30,000 | $266,200.00 | $194,311.75 | $460,511.75 | 22 | yes | 97.50% |
| minimum_monthly | $30,100 | $264,700.00 | $195,811.75 | $460,511.75 | 22 | yes | 97.50% |
| minimum_monthly | $30,200 | $262,200.00 | $198,311.75 | $460,511.75 | 22 | yes | 97.50% |
| minimum_monthly | $30,300 | $260,700.00 | $199,811.75 | $460,511.75 | 22 | yes | 97.50% |

## Reproduced leading runs

[Ongoing-cash leader](best_ongoing/report.txt) and [closing-cash leader](best_terminal/report.txt) include account/payout ledgers and embedded config.json files runnable with the normal CLI --config option.
