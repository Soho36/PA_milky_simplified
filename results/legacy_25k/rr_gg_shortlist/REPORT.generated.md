# Fixed RR/GG shortlist

## Isolation: all 26 quarters, equal allocations

| Portfolio | Full loss / 26 | Mean accounts failed | Mean quarter P&L | Mean quarter DD | Worst quarter DD |
|---|---:|---:|---:|---:|---:|
| RR:0.50 | 5 | 19.23% | $868 | $1,537 | $3,094 |
| RR:1.00 | 7 | 26.92% | $1,044 | $1,790 | $6,379 |
| RR:2.50 | 6 | 23.08% | $1,494 | $2,006 | $5,140 |
| GG:1.25 | 5 | 19.23% | $1,297 | $2,154 | $5,417 |
| rr_pair | 3 | 21.15% | $1,181 | $1,660 | $4,036 |
| cross_pair | 3 | 19.23% | $1,082 | $1,565 | $4,175 |
| rr_triple | 2 | 23.08% | $1,135 | $1,670 | $4,817 |
| cross_triple | 2 | 21.79% | $1,070 | $1,554 | $4,909 |

All settings use one MNQ, $1,500 fixed initial headroom and $1.05 commission. Fractions and curves are normalized to equal total allocation. Analytical P&L continues after failure and is not cash earned by surviving accounts. DD is realized daily maximum drawdown, not exact intratrade portfolio equity. Every arm has a worst-quarter failed fraction of 100%.

## Operating: all assignment orders

| Portfolio | Continuous cases / cases | Starts continuous in every order / 6 | Mean wipeouts | Mean empty days | Mean deaths | Mean net cash |
|---|---:|---:|---:|---:|---:|---:|
| RR:0.50 | 3/6 | 3 | 0.500 | 21.29 | 36.5 | $122,092 |
| RR:1.00 | 1/6 | 1 | 1.333 | 16.92 | 31.0 | $196,779 |
| RR:2.50 | 3/6 | 3 | 2.000 | 14.79 | 33.5 | $243,290 |
| GG:1.25 | 3/6 | 3 | 1.667 | 26.32 | 43.3 | $147,734 |
| rr_pair | 8/12 | 3 | 0.417 | 6.94 | 34.9 | $201,332 |
| cross_pair | 8/12 | 3 | 0.583 | 14.36 | 38.2 | $162,052 |
| rr_triple | 23/36 | 3 | 0.694 | 7.17 | 32.4 | $206,283 |
| cross_triple | 24/36 | 3 | 0.556 | 11.90 | 36.7 | $178,061 |

Starts are equally weighted; each start averages all of that portfolio's assignment orders. Cases/start horizons overlap and are not independent trials. Continuity requires activation and no subsequent empty-book event. Cash is receipts less acquisition costs, excluding retained equity; funding contributions are not trading profits.

Operating uses the inherited daily-minimum/$6,800-reserve policy, shared cap 20, RR1 evaluation supply and replacement rules, over 2020–2025 starts through July 13, 2026. PAs begin with their original trailing floor; the reserve is not starting headroom. Integer group sizes and actual occupancy vary during deployment. This differs deliberately from the fixed-floor isolation.

[Design](../../../research/legacy_25k/RR_GG_SHORTLIST.md) · [Isolation quarters](isolation_quarters.csv) · [Isolation summary](isolation_summary.csv) · [Operating cases](operating_comparison.csv) · [Per-start order ranges](operating_by_start.csv) · [Operating summary](operating_summary.csv) · [Audit](audit.json)
