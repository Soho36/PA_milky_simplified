# GG-to-GG diversification only

This study selects GG r/r settings independently. It contains no RR-to-GG ranking, four-group selection or decision about splitting capital between strategies.

**GG has some reciprocal historical failure separation, but this screen does not establish a pair superior to its strongest individual GG controls.** GG 0.50/1.00 ties for the lowest primary episode-overlap ratio with GG 0.50/3.25 and GG 0.50/3.50. The first pair loses both components in five quarters, while the latter two do so in six. GG 1.25 alone also fails in five quarters, with fewer individual losses and higher average P&L. Different objective choices therefore select different settings.

All 78 distinct pairs from 13 r/r settings (0.50–3.50 by 0.25), plus 13 homogeneous GG controls. Equal-weight paths, one MNQ per account, $1.05 commission, fresh synchronized starts with $1,500 fixed headroom, no operating policies. Primary: 26 quarters, January 2020–June 2026. Monthly/six-month resets and $6,800 are saved as sensitivities. Episode boundaries and their trading-date calendar use GG exclusively.

24 of 78 pairs have unique failed quarters on both sides. The minimum both-failed quarter count among pairs is 5/26. Read each constituent control before crediting a mixture with protection.

| GG r/r settings | Lower fails | Higher fails | Both fail | Lower-only / higher-only | Mean fraction lost | Mean quarter P&L | Mean quarter realized DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1.00 alone | 6 | 6 | 6/26 | 0 / 0 | 23.1% | $1,148 | $2,122 |
| 1.25 alone | 5 | 5 | 5/26 | 0 / 0 | 19.2% | $1,297 | $2,154 |
| 1.50 alone | 5 | 5 | 5/26 | 0 / 0 | 19.2% | $1,282 | $2,182 |
| 0.50 / 1.00 | 9 | 6 | 5/26 | 4 / 1 | 28.8% | $888 | $2,085 |
| 0.50 / 1.25 | 9 | 5 | 5/26 | 4 / 0 | 26.9% | $963 | $2,099 |
| 0.50 / 1.75 | 9 | 7 | 6/26 | 3 / 1 | 30.8% | $868 | $2,142 |
| 0.50 / 3.25 | 9 | 7 | 6/26 | 3 / 1 | 30.8% | $917 | $2,261 |
| 0.50 / 3.50 | 9 | 7 | 6/26 | 3 / 1 | 30.8% | $1,043 | $2,204 |
| 1.25 / 1.50 | 5 | 5 | 5/26 | 0 / 0 | 19.2% | $1,289 | $2,142 |
| 0.75 / 1.00 | 9 | 6 | 6/26 | 3 / 0 | 28.8% | $1,026 | $2,081 |
| 0.75 / 1.25 | 9 | 5 | 5/26 | 4 / 0 | 26.9% | $1,100 | $2,082 |
| 0.75 / 1.50 | 9 | 5 | 5/26 | 4 / 0 | 26.9% | $1,093 | $2,084 |

"Both fail" means by quarter end, not necessarily on the same date. Homogeneous rows show duplicated identical accounts; the same count in both columns is not two separate observations. P&L/DD are normalized, not sums over account counts.

## GG-only episode sensitivity

Cells are shared / lower-only / higher-only episodes. Episodes pool GG first-breach intervals, with 5/20/40-observed-date gaps and transitive merging. These are dated strategy-loss episodes, not identified economic regimes.

| GG pair | Window months | Gap 5 | Gap 20 | Gap 40 |
|---|---:|---|---|---|
| 0.50 / 1.00 | 1 | 14 / 2 / 1 | 9 / 2 / 1 | 8 / 1 / 1 |
| 0.50 / 1.00 | 3 | 5 / 4 / 1 | 5 / 3 / 1 | 5 / 3 / 1 |
| 0.50 / 1.00 | 6 | 3 / 4 / 2 | 4 / 3 / 1 | 4 / 3 / 1 |
| 0.50 / 1.25 | 1 | 13 / 3 / 2 | 9 / 2 / 1 | 8 / 1 / 1 |
| 0.50 / 1.25 | 3 | 5 / 4 / 0 | 5 / 3 / 0 | 5 / 3 / 0 |
| 0.50 / 1.25 | 6 | 3 / 4 / 1 | 4 / 3 / 0 | 4 / 3 / 0 |
| 0.50 / 1.75 | 1 | 13 / 3 / 4 | 8 / 3 / 3 | 7 / 2 / 3 |
| 0.50 / 1.75 | 3 | 6 / 3 / 1 | 6 / 2 / 1 | 6 / 2 / 1 |
| 0.50 / 1.75 | 6 | 4 / 3 / 2 | 5 / 2 / 1 | 5 / 2 / 1 |
| 1.25 / 1.50 | 1 | 14 / 1 / 1 | 9 / 1 / 1 | 8 / 1 / 1 |
| 1.25 / 1.50 | 3 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 |
| 1.25 / 1.50 | 6 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |

The same history informed the earlier studies; this is exploratory, not unseen validation. Curve smoothing and reciprocal failure protection are different outcomes. Do not label two GG bands diversified merely because their r/r numbers differ. Unclosed boundary trades and their full MAE remain censored.

Source hashes are checked. Existing GG single curves and first markers reproduce exactly. Pair P&L and drawdown bounds are checked, and episode counts are reconstructed from membership sets. Checks: {"episode_pair_checks": 1404, "pair_curve_checks": 2028, "prior_marker_matches": 676, "prior_single_curve_matches": 338}.

Reproduce: `.\venv\Scripts\python.exe scripts/study_gg_pairs.py`.
