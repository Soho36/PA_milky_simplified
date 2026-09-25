# Monthly RR pair build: findings

**Daily maximum extracted more cash without changing account mortality in
this experiment.** All 72 paired starts had identical account purchases,
accepted trades, death dates and death trades. Maximum paid more net cash in
70 starts and tied in two; it never paid less. This result is conditional on
the tested $6,800 withdrawal reserve, rulebook and historical paths, not a
general claim that larger payouts cannot increase risk.

| Through July 13, 2026 | Daily minimum | Daily maximum |
|---|---:|---:|
| Monthly starts | 72 | 72 |
| Mean account deaths per start | 23.46 | 23.46 |
| Starts with an empty-book episode | 31 | 31 |
| Empty episodes across starts | 42 | 42 |
| Mean days empty per start | 10.01 | 10.01 |
| Mean accounts alive at end | 15.94 | 15.94 |
| Starts reaching 20 live accounts | 39 | 39 |
| Mean ongoing net cash | $147,053 | $171,354 |

Maximum extracted an average $24,301 more. It did not improve survival;
it changed the timing and amount of cash extraction while the account paths
remained the same. Minimum leaves more profit retained in the accounts.

## Establishment is the vulnerable phase

Counting each start once, 38 of the 42 empty episodes happened before the
book had ever reached five live accounts. The remaining four happened after
a historical peak of exactly five. Twelve episodes occurred when the book
had never held more than one account.

An empty book restarts on the next month boundary because purchases are
externally funded. Empty episodes are therefore interruptions, not permanent
termination of the plan. The latest starts have less time to build inventory.

No book emptied after reaching six accounts in these paths. That observation
does **not** establish a safe six-account threshold: books reaching that size
are selected survivors and face different subsequent market histories.

All 36 starts in 2020–2022 eventually reached 20 and ended with 20. Only three
2023 starts reached 20; none of the 2024–2025 starts did before the endpoint.
Late starts have shorter follow-up; this is not a like-for-like year ranking.

## The first year needs external funding

For the 67 starts with twelve complete months:

| First twelve months | Daily minimum | Daily maximum |
|---|---:|---:|
| Mean deaths | 6.90 | 6.90 |
| Starts with an empty episode | 28 / 67 | 28 / 67 |
| Mean live accounts after twelve months | 5.10 | 5.10 |
| Mean net cash after purchase fees | -$1,303 | -$748 |

The $6,800 reserve is earned through trading. New PAs start with the original
$1,500 drawdown allowance, not an endowed $6,800 buffer. Many young accounts
die before accumulating that reserve or becoming eligible for a payout.
Long-history cash totals conceal this early financing requirement.

## What this supports

For this exact externally funded monthly-purchase plan, daily maximum at the
chosen reserve is the stronger historical cash-extraction policy, with no
observed penalty in deaths or downtime relative to daily minimum. Building
the book remains exposed to startup failures. The test does not establish
that the RR mixture is superior to a homogeneous RR book; that requires
matched constituent controls.

Both policies are subject to firm payout gates. Daily requests do not imply
daily approval. No evaluations, additional replacement purchases, terminal
liquidation or withdrawal-funded purchase restriction are included. Historical
starts overlap and are not independent trials or future probabilities.

All 144 cases passed independent checks covering 5,674 account entry paths,
6,765,432 accepted copies, 6,264 purchase boundaries and 474 checkpoint
ledgers. Three runs reproduced exactly; all 14 targeted tests passed.

- [Every start, policies side by side](START_MONTHS.md)
- [Full methods and yearly tables](monthly_rr_pair_build__REPORT.md)
- [Exact empty episodes](empty_episodes.csv)
- [Paired path and cash comparisons](paired_comparison.json)
- [Independent audit](audit.json)

Reproduce this readout: `venv/Scripts/python.exe scripts/summarize_monthly_rr_pair_build.py`.
