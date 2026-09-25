# Build an alternating RR 0.50 / 2.50 book from zero

72 starts, one on each month boundary from January 2020 through December 2025. Two daily payout policies; 144 runs. All run through 2026-07-13 21:30:40.

Buy one PA immediately and then on each month boundary if fewer than 20 are alive. Continue monthly purchases after deaths; no intra-month replacement or catch-up batch. Each actual purchase advances 0.50, 2.50, 0.50, 2.50; a skipped month at capacity does not advance the sequence. Equal purchases do not maintain an equal live allocation.

One position at a time per account, one MNQ per trade, $1.05 round-trip commission. Fresh $25,000 PAs with $1,500 trailing drawdown; retain $31,900 before withdrawing ($6,800 above the frozen $25,100 floor). This reserve is earned, not supplied initially. Daily minimum asks for $500 without backlog; daily maximum asks for all permitted excess. Daily checks remain subject to the full historical payout rulebook, with processing delay off. Direct PA purchases cost $200 and are externally funded. No evaluations or funding restriction. Net cash is received payouts minus actual purchase fees, excluding unused owner contributions and retained profit. **No terminal payout or liquidation is counted.**

## Full available history by start

Starts have unequal follow-up. These totals describe overlapping historical replays, not independent observations or estimated probabilities.

| Daily policy | Starts | Mean deaths | Starts with empty book | Empty episodes | Mean empty days | Mean end alive | Reached 20 | Mean net cash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| minimum | 72 | 23.46 | 31 | 42 | 10.01 | 15.94 | 39 | $147,053.47 |
| maximum | 72 | 23.46 | 31 | 42 | 10.01 | 15.94 | 39 | $171,354.28 |

## First twelve months: matched follow-up

Only starts with twelve complete months are included. Later starts are excluded, not counted as surviving a full year.

| Daily policy | Starts | Mean deaths | Starts with empty book | Empty episodes | Mean empty days | Mean end alive | Mean net cash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| minimum | 67 | 6.90 | 28 | 36 | 9.51 | 5.10 | $-1,302.99 |
| maximum | 67 | 6.90 | 28 | 36 | 9.51 | 5.10 | $-747.91 |

## Full-history outcomes by start year

| Start year | Policy | Mean deaths | Starts with empty book / 12 | Empty episodes | Mean empty days | Mean end alive | Reached 20 / 12 |
|---|---|---:|---:|---:|---:|---:|---:|
| 2020 | minimum | 41.42 | 1 | 1 | 1.79 | 20.00 | 12 |
| 2020 | maximum | 41.42 | 1 | 1 | 1.79 | 20.00 | 12 |
| 2021 | minimum | 32.67 | 9 | 9 | 13.91 | 20.00 | 12 |
| 2021 | maximum | 32.67 | 9 | 9 | 13.91 | 20.00 | 12 |
| 2022 | minimum | 26.08 | 6 | 9 | 14.07 | 20.00 | 12 |
| 2022 | maximum | 26.08 | 6 | 9 | 14.07 | 20.00 | 12 |
| 2023 | minimum | 19.58 | 4 | 4 | 1.74 | 17.67 | 3 |
| 2023 | maximum | 19.58 | 4 | 4 | 1.74 | 17.67 | 3 |
| 2024 | minimum | 13.50 | 5 | 7 | 8.96 | 12.00 | 0 |
| 2024 | maximum | 13.50 | 5 | 7 | 8.96 | 12.00 | 0 |
| 2025 | minimum | 7.50 | 6 | 12 | 19.57 | 6.00 | 0 |
| 2025 | maximum | 7.50 | 6 | 12 | 19.57 | 6.00 | 0 |

## Paired comparison and episode definition

Maximum daily produces fewer deaths in 0 starts, the same in 72, and more in 0. Compare policies within the same start date before pooling starts.

An empty-book episode is a positive-duration interval with zero live accounts after the first activation. Startup zero is excluded. A same-timestamp death and purchase are netted; instantaneous zero is not an episode. An episode still open at the data endpoint is marked censored. Death timestamps are trade-exit proxies; intratrade breach times are not available.

Across the replays, 76 of 84 empty episodes occur before the book has ever reached five live accounts; 0 occur after reaching at least ten. These are counts across overlapping runs.

## Evidence and reproduction

See [cases.csv](cases.csv) for every start/policy, [checkpoints.csv](checkpoints.csv) for complete 6/12/24/36-month windows, [empty_episodes.csv](empty_episodes.csv) for exact gaps and historical peak sizes, [accounts.csv](accounts.csv) for deaths and r/r assignments, [purchases.csv](purchases.csv), [payouts.csv](payouts.csv), and [snapshots.csv](snapshots.csv) for monthly capacity. Input coverage, hashes, policies and checks are in [study.json](study.json).

Reproduce: `venv/Scripts/python.exe scripts/study_monthly_rr_pair_build.py --workers 4`. Audit: `venv/Scripts/python.exe scripts/audit_monthly_rr_pair_build.py`. This two-policy experiment evaluates the requested plan; it does not measure diversification relative to homogeneous controls.
