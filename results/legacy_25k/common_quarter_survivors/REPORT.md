# Survivors of the three shared failure quarters

Full ordinary grid: 602 settings, RR and GG r/r 0.50–3.50 in 0.01 steps. Each test starts fresh at quarter start with $1,500 fixed headroom, one MNQ and $1.05 commission. No withdrawals or replacements.

| Quarter | RR surviving r/r bands | Count / 301 | GG surviving r/r bands | Count / 301 |
|---|---|---:|---|---:|
| Q2 2022 | None | 0 | None | 0 |
| Q3 2024 | 0.59–0.61, 0.77–1.21 | 48 | None | 0 |
| Q2 2025 | None | 0 | None | 0 |

**Settings surviving all three: none.**

## Context for every setting surviving at least one target

All 26 fresh-start quarters are recalculated for survivors and three reference settings. “Common failures remaining” is the intersection with RR 0.50, RR 2.50 and GG 1.25; it is not a simulated allocation or replacement policy.

| Arm | Target quarters survived / 3 | Minimum headroom in survived target(s) | Failed quarters / 26 | Common failures remaining |
|---|---:|---:|---:|---:|
| RR:0.50 | 0 | — | 5 | 3 |
| RR:0.59 | 1 | $4.55 | 4 | 2 |
| RR:0.60 | 1 | $4.55 | 4 | 2 |
| RR:0.61 | 1 | $8.05 | 4 | 2 |
| RR:0.77 | 1 | $37.70 | 7 | 2 |
| RR:0.78 | 1 | $155.80 | 7 | 2 |
| RR:0.79 | 1 | $155.80 | 7 | 2 |
| RR:0.80 | 1 | $155.80 | 6 | 2 |
| RR:0.81 | 1 | $209.80 | 6 | 2 |
| RR:0.82 | 1 | $266.30 | 5 | 2 |
| RR:0.83 | 1 | $198.40 | 5 | 2 |
| RR:0.84 | 1 | $211.40 | 5 | 2 |
| RR:0.85 | 1 | $211.40 | 5 | 2 |
| RR:0.86 | 1 | $211.40 | 6 | 2 |
| RR:0.87 | 1 | $209.40 | 6 | 2 |
| RR:0.88 | 1 | $209.40 | 6 | 2 |
| RR:0.89 | 1 | $295.40 | 6 | 2 |
| RR:0.90 | 1 | $448.55 | 6 | 2 |
| RR:0.91 | 1 | $275.05 | 6 | 2 |
| RR:0.92 | 1 | $145.05 | 7 | 2 |
| RR:0.93 | 1 | $249.60 | 7 | 2 |
| RR:0.94 | 1 | $249.60 | 6 | 2 |
| RR:0.95 | 1 | $249.60 | 7 | 2 |
| RR:0.96 | 1 | $416.10 | 7 | 2 |
| RR:0.97 | 1 | $445.15 | 7 | 2 |
| RR:0.98 | 1 | $440.65 | 7 | 2 |
| RR:0.99 | 1 | $397.15 | 7 | 2 |
| RR:1.00 | 1 | $415.65 | 7 | 2 |
| RR:1.01 | 1 | $498.70 | 7 | 2 |
| RR:1.02 | 1 | $498.70 | 8 | 2 |
| RR:1.03 | 1 | $498.70 | 8 | 2 |
| RR:1.04 | 1 | $420.70 | 8 | 2 |
| RR:1.05 | 1 | $396.20 | 8 | 2 |
| RR:1.06 | 1 | $396.20 | 8 | 2 |
| RR:1.07 | 1 | $362.25 | 8 | 2 |
| RR:1.08 | 1 | $362.25 | 8 | 2 |
| RR:1.09 | 1 | $376.75 | 8 | 2 |
| RR:1.10 | 1 | $584.60 | 8 | 2 |
| RR:1.11 | 1 | $491.10 | 8 | 2 |
| RR:1.12 | 1 | $491.10 | 8 | 2 |
| RR:1.13 | 1 | $274.15 | 7 | 2 |
| RR:1.14 | 1 | $165.65 | 7 | 2 |
| RR:1.15 | 1 | $119.70 | 7 | 2 |
| RR:1.16 | 1 | $110.80 | 7 | 2 |
| RR:1.17 | 1 | $25.30 | 7 | 2 |
| RR:1.18 | 1 | $25.30 | 6 | 2 |
| RR:1.19 | 1 | $57.30 | 7 | 2 |
| RR:1.20 | 1 | $57.30 | 7 | 2 |
| RR:1.21 | 1 | $64.30 | 7 | 2 |
| RR:2.50 | 0 | — | 6 | 3 |
| GG:1.25 | 0 | — | 5 | 3 |

## Interpretation and checks

These quarters were selected because the earlier candidates failed in them. A finely selected survivor is therefore a historical finding, not independent evidence that it will protect a future portfolio. Inspect neighboring settings and other failed quarters.

Survival means no MAE/net-close breach during the quarter; positive ending P&L does not erase an earlier failure. Minimum headroom is relative to the fixed starting floor, not peak-to-trough drawdown. Analytical P&L continues after a failure solely for diagnostics.

Target cases with a position unclosed at the horizon: 0. Those positions and their full MAE are censored as in the prior studies. Breach times based on MAE remain intervals.

All 78 coarse target results reproduce exactly. 2979 cases passed independent router and Decimal marker checks. Every tape passed loader reconciliation and coverage; source hashes were unchanged during loading.

RR1000 is excluded from this grid because it is a separate all-hours tape with different entry availability. Existing studies and their manifests are unchanged.

[Design](../../../research/legacy_25k/COMMON_QUARTER_SURVIVORS.md) · [All target paths](target_quarters.csv) · [All setting summaries](setting_summary.csv) · [Context quarters](context_quarters.csv) · [Manifest](manifest.json)
