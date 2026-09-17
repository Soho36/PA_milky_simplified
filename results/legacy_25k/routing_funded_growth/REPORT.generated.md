# Routing versus copying under funded monthly growth

Each case starts with five paid accounts, identical initial cash/monthly contributions, a 20-live-account cap, one additional account at the start of each subsequent month, and daily checks for funded death replacements. Replacements do not consume monthly growth slots. Both obey available owner cash; receipts can fund purchases. No extra external funding or entry-time rescue purchases are allowed. Unaffordable scheduled growth is skipped; unfilled replacements remain pending. The initial five replace the first ordinary monthly purchase.

Daily minimum withdrawal checks, retained balance, rulebook, contract size and commission are identical within a case. Purchases and account balances can diverge because trading outcomes and receipt timing differ. The two retained-balance settings are separate fixed-policy comparisons, not an optimization.

| Arm | Execution |
|---|---|
| unlimited_reference | Existing model: every eligible account takes every trade, including overlap. An idealized benchmark. |
| blocked_copy | Every live account tries each signal but accepts only when flat. No spreading copies to recover missed signals. |
| adaptive_max_headroom | One shared pool; R=floor(live accounts/5); choose free accounts with most headroom. |
| adaptive_round_robin | Same dynamic R and budget; rotate through free accounts. |

R is recomputed before each entry from live inventory, including busy accounts. R rises at 10, 15 and 20 seats and falls after deaths. Below five it is zero; those zero-target signals are reported separately. R affects new entries only. This study matches resources and operating rules, **not trade exposure**: at 20 accounts the unlimited model targets 20 copies, while full-coverage routing targets four.

Coverage of requested copies excludes R=0 offers. Signal participation counts exported signals receiving at least one copy and therefore exposes pauses. Copy counts and planned contract-hours describe exposure; they do not normalize away payout thresholds or account failure. Extrema remain applied at exit, and unlimited concurrent floating P&L is not aggregated. Funded seats remain instantly available at daily purchase checks; evaluation lead times and working-order reservations are absent. The 2023 starts are sensitivity checks, not independent policy selection.

All net figures subtract all account fees and exclude owner contributions. Total includes a firm-permitted terminal request.

## Fresh start in 2020

### $1,000 initially + $0/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 5 / 0 | 1,880 | 3.0% | 12,282 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $30,000 | blocked_copy | 5 / 0 | 1,410 | 2.2% | 12,283 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $30,000 | adaptive_max_headroom | 5 / 4 | 2,222 | 17.6% | 10,436 | $-1,000.00 | $1,500.00 | $500.00 | $1,500.00 |
| $30,000 | adaptive_round_robin | 5 / 4 | 381 | 3.0% | 12,277 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $31,900 | unlimited_reference | 5 / 0 | 1,880 | 3.0% | 12,282 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $31,900 | blocked_copy | 5 / 0 | 1,410 | 2.2% | 12,283 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $31,900 | adaptive_max_headroom | 5 / 4 | 2,222 | 17.6% | 10,436 | $-1,000.00 | $1,500.00 | $500.00 | $1,500.00 |
| $31,900 | adaptive_round_robin | 5 / 4 | 381 | 3.0% | 12,277 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |

### $1,000 initially + $200/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 107 / 20 | 175,255 | 99.4% | 79 | $495,850.00 | $30,000.00 | $525,850.00 | $542,450.00 |
| $30,000 | blocked_copy | 87 / 20 | 103,911 | 73.1% | 82 | $334,100.00 | $0.00 | $334,100.00 | $350,700.00 |
| $30,000 | adaptive_max_headroom | 38 / 20 | 45,912 | 100.0% | 0 | $108,400.00 | $0.00 | $108,400.00 | $125,000.00 |
| $30,000 | adaptive_round_robin | 48 / 20 | 41,650 | 100.0% | 0 | $67,400.00 | $29,952.17 | $97,352.17 | $113,952.17 |
| $31,900 | unlimited_reference | 67 / 20 | 175,352 | 99.4% | 79 | $466,200.00 | $101,076.77 | $567,276.77 | $583,876.77 |
| $31,900 | blocked_copy | 67 / 20 | 97,351 | 73.1% | 80 | $268,600.00 | $0.00 | $268,600.00 | $285,200.00 |
| $31,900 | adaptive_max_headroom | 28 / 20 | 45,921 | 100.0% | 0 | $94,400.00 | $5,306.52 | $99,706.52 | $116,306.52 |
| $31,900 | adaptive_round_robin | 57 / 20 | 41,186 | 100.0% | 0 | $51,100.00 | $26,379.05 | $77,479.05 | $94,079.05 |

### $5,000 initially + $0/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 118 / 20 | 184,015 | 100.0% | 4 | $517,700.00 | $30,000.00 | $547,700.00 | $552,700.00 |
| $30,000 | blocked_copy | 82 / 20 | 128,706 | 73.5% | 4 | $372,100.00 | $0.00 | $372,100.00 | $377,100.00 |
| $30,000 | adaptive_max_headroom | 31 / 20 | 45,799 | 100.0% | 0 | $104,300.00 | $0.00 | $104,300.00 | $109,300.00 |
| $30,000 | adaptive_round_robin | 64 / 20 | 39,630 | 100.0% | 0 | $52,200.00 | $32,385.19 | $84,585.19 | $89,585.19 |
| $31,900 | unlimited_reference | 73 / 20 | 175,608 | 100.0% | 4 | $468,500.00 | $101,481.07 | $569,981.07 | $574,981.07 |
| $31,900 | blocked_copy | 47 / 20 | 120,441 | 73.5% | 2 | $335,100.00 | $0.00 | $335,100.00 | $340,100.00 |
| $31,900 | adaptive_max_headroom | 28 / 20 | 43,639 | 100.0% | 0 | $90,900.00 | $0.00 | $90,900.00 | $95,900.00 |
| $31,900 | adaptive_round_robin | 55 / 20 | 30,820 | 100.0% | 0 | $8,500.00 | $26,025.27 | $34,525.27 | $39,525.27 |

### $5,000 initially + $200/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 108 / 20 | 219,898 | 100.0% | 4 | $582,150.00 | $30,000.00 | $612,150.00 | $632,750.00 |
| $30,000 | blocked_copy | 108 / 20 | 146,367 | 73.5% | 4 | $387,400.00 | $0.00 | $387,400.00 | $408,000.00 |
| $30,000 | adaptive_max_headroom | 38 / 20 | 45,912 | 100.0% | 0 | $108,400.00 | $0.00 | $108,400.00 | $129,000.00 |
| $30,000 | adaptive_round_robin | 56 / 20 | 45,850 | 100.0% | 0 | $66,800.00 | $31,692.26 | $98,492.26 | $119,092.26 |
| $31,900 | unlimited_reference | 76 / 20 | 206,943 | 100.0% | 4 | $524,300.00 | $99,514.56 | $623,814.56 | $644,414.56 |
| $31,900 | blocked_copy | 77 / 20 | 143,152 | 73.5% | 2 | $359,100.00 | $0.00 | $359,100.00 | $379,700.00 |
| $31,900 | adaptive_max_headroom | 28 / 20 | 45,921 | 100.0% | 0 | $94,400.00 | $5,306.52 | $99,706.52 | $120,306.52 |
| $31,900 | adaptive_round_robin | 54 / 20 | 45,854 | 100.0% | 0 | $29,200.00 | $45,571.97 | $74,771.97 | $95,371.97 |

## Fresh start in 2023

### $1,000 initially + $0/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 66 / 20 | 99,583 | 100.0% | 0 | $299,300.00 | $30,000.00 | $329,300.00 | $330,300.00 |
| $30,000 | blocked_copy | 48 / 20 | 63,666 | 73.2% | 0 | $216,400.00 | $0.00 | $216,400.00 | $217,400.00 |
| $30,000 | adaptive_max_headroom | 32 / 20 | 16,536 | 100.0% | 0 | $39,100.00 | $0.00 | $39,100.00 | $40,100.00 |
| $30,000 | adaptive_round_robin | 5 / 4 | 331 | 4.8% | 6,601 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |
| $31,900 | unlimited_reference | 51 / 20 | 84,983 | 100.0% | 0 | $175,800.00 | $62,469.33 | $238,269.33 | $239,269.33 |
| $31,900 | blocked_copy | 42 / 20 | 56,627 | 73.2% | 0 | $139,600.00 | $7,500.00 | $147,100.00 | $148,100.00 |
| $31,900 | adaptive_max_headroom | 36 / 20 | 14,531 | 100.0% | 0 | $23,300.00 | $3,000.00 | $26,300.00 | $27,300.00 |
| $31,900 | adaptive_round_robin | 5 / 4 | 331 | 4.8% | 6,601 | $-1,000.00 | $0.00 | $-1,000.00 | $0.00 |

### $1,000 initially + $200/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 73 / 20 | 115,390 | 100.0% | 0 | $363,900.00 | $30,000.00 | $393,900.00 | $403,300.00 |
| $30,000 | blocked_copy | 53 / 20 | 82,085 | 73.2% | 2 | $304,900.00 | $0.00 | $304,900.00 | $314,300.00 |
| $30,000 | adaptive_max_headroom | 31 / 20 | 22,902 | 100.0% | 0 | $68,300.00 | $0.00 | $68,300.00 | $77,700.00 |
| $30,000 | adaptive_round_robin | 38 / 20 | 21,888 | 100.0% | 0 | $13,400.00 | $26,894.92 | $40,294.92 | $49,694.92 |
| $31,900 | unlimited_reference | 36 / 20 | 106,782 | 100.0% | 0 | $285,300.00 | $88,299.48 | $373,599.48 | $382,999.48 |
| $31,900 | blocked_copy | 31 / 20 | 78,411 | 73.2% | 0 | $248,300.00 | $0.00 | $248,300.00 | $257,700.00 |
| $31,900 | adaptive_max_headroom | 24 / 20 | 22,909 | 100.0% | 0 | $57,700.00 | $6,889.94 | $64,589.94 | $73,989.94 |
| $31,900 | adaptive_round_robin | 38 / 20 | 21,888 | 100.0% | 0 | $-1,600.00 | $15,000.00 | $13,400.00 | $22,800.00 |

### $5,000 initially + $0/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 74 / 20 | 119,305 | 100.0% | 0 | $375,700.00 | $30,000.00 | $405,700.00 | $410,700.00 |
| $30,000 | blocked_copy | 49 / 20 | 86,927 | 73.2% | 2 | $336,700.00 | $0.00 | $336,700.00 | $341,700.00 |
| $30,000 | adaptive_max_headroom | 31 / 20 | 22,902 | 100.0% | 0 | $68,300.00 | $0.00 | $68,300.00 | $73,300.00 |
| $30,000 | adaptive_round_robin | 46 / 20 | 22,805 | 100.0% | 0 | $24,800.00 | $36,841.58 | $61,641.58 | $66,641.58 |
| $31,900 | unlimited_reference | 40 / 20 | 113,805 | 100.0% | 0 | $313,500.00 | $92,419.77 | $405,919.77 | $410,919.77 |
| $31,900 | blocked_copy | 28 / 20 | 86,006 | 73.2% | 0 | $303,400.00 | $0.00 | $303,400.00 | $308,400.00 |
| $31,900 | adaptive_max_headroom | 24 / 20 | 22,909 | 100.0% | 0 | $57,700.00 | $6,889.94 | $64,589.94 | $69,589.94 |
| $31,900 | adaptive_round_robin | 39 / 20 | 22,014 | 100.0% | 0 | $8,700.00 | $19,294.17 | $27,994.17 | $32,994.17 |

### $5,000 initially + $200/month

| Reserve | Arm | Bought / alive | Trade copies | Signals traded | Zero-target signals | Ongoing net | Terminal receipt | Total net | Ending owner cash |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $30,000 | unlimited_reference | 74 / 20 | 119,305 | 100.0% | 0 | $375,700.00 | $30,000.00 | $405,700.00 | $419,100.00 |
| $30,000 | blocked_copy | 49 / 20 | 86,927 | 73.2% | 2 | $336,700.00 | $0.00 | $336,700.00 | $350,100.00 |
| $30,000 | adaptive_max_headroom | 31 / 20 | 22,902 | 100.0% | 0 | $68,300.00 | $0.00 | $68,300.00 | $81,700.00 |
| $30,000 | adaptive_round_robin | 35 / 20 | 22,886 | 100.0% | 0 | $24,000.00 | $14,069.87 | $38,069.87 | $51,469.87 |
| $31,900 | unlimited_reference | 35 / 20 | 119,409 | 100.0% | 0 | $349,000.00 | $97,910.76 | $446,910.76 | $460,310.76 |
| $31,900 | blocked_copy | 29 / 20 | 86,953 | 73.2% | 0 | $308,700.00 | $0.00 | $308,700.00 | $322,100.00 |
| $31,900 | adaptive_max_headroom | 24 / 20 | 22,909 | 100.0% | 0 | $57,700.00 | $6,889.94 | $64,589.94 | $77,989.94 |
| $31,900 | adaptive_round_robin | 35 / 20 | 22,886 | 100.0% | 0 | $5,000.00 | $18,031.14 | $23,031.14 | $36,431.14 |

