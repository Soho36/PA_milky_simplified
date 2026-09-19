# Hybrid allocation with 20 initial accounts

All arms start with 20 paid accounts ($4,000). No growth, replacements or subsequent contributions. Daily minimum withdrawals, retained balance and terminal request rules match within each case. The main retained balance is $31,900; $30,000 and a fresh 2023 start are separate sensitivity checks. Six hybrid settings were specified before running; these are in-sample comparisons, not validated optima.

For minimum copies m, cap c, free accounts F, and A distinct setups currently occupying accounts:

`reserve = m * max(0, 5 - A - 1)`

`target = min(c, max(m, F - reserve))`

Select up to target free accounts by greatest current drawdown headroom, with account ID breaking ties. Only accepted, still-open setups count toward A. No future duration, P&L or extrema chooses the allocation. When inventory is depleted, attempt the current minimum even if future reserves cannot be maintained; report minimum shortfalls and missed signals. The five-setup assumption is historical, not a future guarantee. Same-time existing exits precede entries; instantaneous trades enter then exit.

Coverage counts all exported signals, including signals after the book dies. Adaptive target coverage is not evidence that a minimum was maintained; the below-minimum column makes that visible. Copy histograms include zeros. Net cash deducts all fees; terminal receipts are shown separately. Signal weights differ, so this is a same-resource comparison, not matched exposure. The unrestricted model is an idealized settlement-time reference; one-position arms retain exported extrema at exit and omit working-order reservations.

## Start 2020; retain $31,900

| Arm | Copies | Signals traded | Below minimum | Deaths | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 7,520 | 2.97% | - | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| blocked_20 | 5,640 | 2.23% | - | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| routed_20_max_headroom | 49,168 | 97.11% | - | 12 | $104,000.00 | $6,891.16 | $110,891.16 |
| routed_20_round_robin | 50,392 | 99.53% | - | 8 | $84,000.00 | $37,938.52 | $121,938.52 |
| hybrid_m1_cap4 | 46,314 | 100.00% | 0 | 11 | $98,500.00 | $4,509.33 | $103,009.33 |
| hybrid_m1_cap8 | 15,228 | 99.66% | 43 | 17 | $25,000.00 | $1,661.44 | $26,661.44 |
| hybrid_m1_cap12 | 3,874 | 3.05% | 12272 | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| hybrid_m2_cap4 | 33,074 | 100.00% | 0 | 10 | $49,000.00 | $5,367.68 | $54,367.68 |
| hybrid_m2_cap8 | 21,500 | 76.79% | 2938 | 18 | $40,000.00 | $0.00 | $40,000.00 |
| hybrid_m2_cap12 | 7,176 | 16.97% | 10510 | 20 | $-4,000.00 | $0.00 | $-4,000.00 |

Copy distribution (`copies: number of signals`):

- hybrid_m1_cap4: `{1: 373, 2: 1284, 3: 631, 4: 10370}`
- hybrid_m1_cap8: `{0: 43, 1: 12224, 2: 18, 4: 4, 8: 369}`
- hybrid_m1_cap12: `{0: 12272, 1: 18, 5: 80, 12: 288}`
- hybrid_m2_cap4: `{2: 8779, 4: 3879}`
- hybrid_m2_cap8: `{0: 2938, 2: 9347, 4: 4, 6: 81, 8: 288}`
- hybrid_m2_cap12: `{0: 10510, 2: 1860, 12: 288}`

## Start 2020; retain $30,000

| Arm | Copies | Signals traded | Below minimum | Deaths | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 7,520 | 2.97% | - | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| blocked_20 | 5,640 | 2.23% | - | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| routed_20_max_headroom | 48,848 | 96.48% | - | 16 | $118,000.00 | $0.00 | $118,000.00 |
| routed_20_round_robin | 50,292 | 99.33% | - | 12 | $108,000.00 | $0.00 | $108,000.00 |
| hybrid_m1_cap4 | 46,120 | 100.00% | 0 | 14 | $112,450.00 | $0.00 | $112,450.00 |
| hybrid_m1_cap8 | 15,211 | 99.53% | 60 | 19 | $29,000.00 | $0.00 | $29,000.00 |
| hybrid_m1_cap12 | 3,874 | 3.05% | 12272 | 20 | $-4,000.00 | $0.00 | $-4,000.00 |
| hybrid_m2_cap4 | 33,074 | 100.00% | 0 | 10 | $58,000.00 | $0.00 | $58,000.00 |
| hybrid_m2_cap8 | 20,602 | 73.24% | 3387 | 20 | $42,000.00 | $0.00 | $42,000.00 |
| hybrid_m2_cap12 | 7,176 | 16.97% | 10510 | 20 | $-4,000.00 | $0.00 | $-4,000.00 |

Copy distribution (`copies: number of signals`):

- hybrid_m1_cap4: `{1: 395, 2: 1348, 3: 631, 4: 10284}`
- hybrid_m1_cap8: `{0: 60, 1: 12207, 2: 18, 4: 4, 8: 369}`
- hybrid_m1_cap12: `{0: 12272, 1: 18, 5: 80, 12: 288}`
- hybrid_m2_cap4: `{2: 8779, 4: 3879}`
- hybrid_m2_cap8: `{0: 3387, 2: 8898, 4: 4, 6: 81, 8: 288}`
- hybrid_m2_cap12: `{0: 10510, 2: 1860, 12: 288}`

## Start 2023; retain $31,900

| Arm | Copies | Signals traded | Below minimum | Deaths | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 138,640 | 100.00% | - | 0 | $406,000.00 | $102,679.00 | $508,679.00 |
| blocked_20 | 101,420 | 73.15% | - | 0 | $356,000.00 | $0.00 | $356,000.00 |
| routed_20_max_headroom | 27,728 | 100.00% | - | 0 | $68,000.00 | $0.00 | $68,000.00 |
| routed_20_round_robin | 27,616 | 99.60% | - | 8 | $44,000.00 | $24,284.96 | $68,284.96 |
| hybrid_m1_cap4 | 27,728 | 100.00% | 0 | 0 | $68,000.00 | $0.00 | $68,000.00 |
| hybrid_m1_cap8 | 53,083 | 100.00% | 0 | 3 | $144,500.00 | $0.00 | $144,500.00 |
| hybrid_m1_cap12 | 68,473 | 100.00% | 0 | 2 | $215,500.00 | $0.00 | $215,500.00 |
| hybrid_m2_cap4 | 27,728 | 100.00% | 0 | 0 | $68,000.00 | $0.00 | $68,000.00 |
| hybrid_m2_cap8 | 50,160 | 100.00% | 0 | 2 | $144,000.00 | $0.00 | $144,000.00 |
| hybrid_m2_cap12 | 64,174 | 100.00% | 0 | 6 | $206,000.00 | $3,000.00 | $209,000.00 |

Copy distribution (`copies: number of signals`):

- hybrid_m1_cap4: `{4: 6932}`
- hybrid_m1_cap8: `{1: 85, 2: 217, 6: 238, 8: 6392}`
- hybrid_m1_cap12: `{1: 302, 3: 238, 5: 1321, 12: 5071}`
- hybrid_m2_cap4: `{4: 6932}`
- hybrid_m2_cap8: `{2: 302, 4: 183, 6: 1376, 8: 5071}`
- hybrid_m2_cap12: `{2: 1861, 6: 62, 10: 14, 12: 4995}`

## Start 2023; retain $30,000

| Arm | Copies | Signals traded | Below minimum | Deaths | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 126,160 | 91.00% | - | 20 | $426,000.00 | $0.00 | $426,000.00 |
| blocked_20 | 92,460 | 66.69% | - | 20 | $366,000.00 | $0.00 | $366,000.00 |
| routed_20_max_headroom | 27,664 | 99.77% | - | 16 | $78,000.00 | $0.00 | $78,000.00 |
| routed_20_round_robin | 27,516 | 99.24% | - | 12 | $70,000.00 | $7,971.36 | $77,971.36 |
| hybrid_m1_cap4 | 27,492 | 100.00% | 0 | 15 | $77,000.00 | $0.00 | $77,000.00 |
| hybrid_m1_cap8 | 52,224 | 100.00% | 0 | 10 | $161,000.00 | $4,300.89 | $165,300.89 |
| hybrid_m1_cap12 | 62,769 | 91.49% | 590 | 20 | $225,000.00 | $0.00 | $225,000.00 |
| hybrid_m2_cap4 | 27,560 | 99.97% | 2 | 16 | $78,000.00 | $0.00 | $78,000.00 |
| hybrid_m2_cap8 | 49,038 | 100.00% | 0 | 8 | $161,000.00 | $7,672.58 | $168,672.58 |
| hybrid_m2_cap12 | 58,980 | 91.60% | 582 | 20 | $219,000.00 | $0.00 | $219,000.00 |

Copy distribution (`copies: number of signals`):

- hybrid_m1_cap4: `{1: 78, 2: 1, 4: 6853}`
- hybrid_m1_cap8: `{1: 166, 2: 217, 6: 331, 7: 106, 8: 6112}`
- hybrid_m1_cap12: `{0: 590, 1: 280, 3: 112, 5: 1321, 12: 4629}`
- hybrid_m2_cap4: `{0: 2, 2: 80, 4: 6850}`
- hybrid_m2_cap8: `{2: 391, 4: 268, 6: 1500, 8: 4773}`
- hybrid_m2_cap12: `{0: 582, 2: 1721, 10: 5, 12: 4624}`

