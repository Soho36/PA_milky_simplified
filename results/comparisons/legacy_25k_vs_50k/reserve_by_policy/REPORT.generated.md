# Legacy 25K versus 50K: best tested reserves by operating policy

[Excel workbook — summary, budget comparisons and data](../Legacy_25K_vs_50K.xlsx)

25K is shown on the left and 50K on the right. Each row shares the same comparison labels. “Bought / alive” means cumulative purchases / ending survivors. Reserve cells retain tie counts; † marks a tie at a tested range boundary. Cash pairs are ongoing / terminal-inclusive, in USD.

5,196 simulations; 144 product/budget/policy families; 72 prior matched controls reproduced. Each paired family tests exactly the same floor-headroom values for both products.

## How to read this comparison

These are in-sample best tested settings, not global optima or expected future earnings. A reserve is the balance left after a withdrawal, not a trading stop. Daily minimum means request $500 when eligible and enough balance remains; maximum means request all excess permitted by the reserve and firm rules. Checks start in the account's second calendar month.

Same RR tape and exposure, four owner budgets, 20 live accounts, user-specified seat fees $200 (25K) / $250 (50K). The matched comparison therefore includes cost as well as account mechanics. Ongoing = receipts during trading minus all purchase fees; total adds one permitted endpoint request releasing the voluntary reserve. Owner contributions are excluded from both net scores.

**Rule interpretation:** both products retain the inherited payout model. The optional post-payout-six retained minimum is not enabled or re-optimized here. See [source audit and limitations](../../../../research/legacy_50k/SOURCES.md).

**Coverage:** minimum and maximum withdrawal families, daily/weekly/monthly checks; monthly-one, weekly-one and monthly purchases with current-month-slot replacements. Fixed-amount backlog policies, quarterly schedules, batch purchases and calendar-phase variation are outside this focused comparison.

Common coarse headrooms above the frozen floor: [0, 1000, 2000, 3000, 4000, 4900, 5000, 6000, 6500, 6800, 7000, 8000, 9000, 10000, 12500, 15000]. Within every budget/purchase/withdrawal/cadence family, refine +/-$500 in $100 steps around each product's coarse winner for each objective; apply the UNION of those values to BOTH products. This is a broad coarse search plus local refinement, not a continuous or exhaustive $100 grid. Secondary objective, then lower reserve, breaks display ties. All primary-score ties remain in the data.

The frozen floors are $25,100 and $50,100: headroom $6,800 means reserves $31,900 and $56,900. The old 25K cadence study tested $31,600–$32,100 plus the $30,000 minimum-policy control; its $31,900 result was conditional on that grid.

## Files

- [All paired settings](all_settings.csv) and [matched 50K-minus-25K differences](matched_deltas.csv).
- [Best reserves by family and objective](best_by_policy.csv), including exact ties, tested bounds and the explicit list of tested reserves within 1% of the best positive score. Those lists need not be continuous bands and are not confidence intervals.
- [Research contract and evidence](study.json). [Operating notes](HOW_THIS_STUDY_WORKS.md).

## $1,000 initial; $0/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly; minimum / daily; reserve $29,100 | $266,650.00 / $266,650.00 | 61 / 2 | Monthly + replacements; maximum / daily; reserve $53,600 | $507,356.85 / $507,356.85 | 122 / 20 |
| total | Monthly; minimum / monthly; reserve $28,400 | $194,300.00 / $308,604.52 | 61 / 14 | Monthly + replacements; minimum / monthly; reserve $53,200 | $332,000.00 / $530,385.53 | 38 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $233,488.82 | 58 / 2 | $54,800 (1 tie) | $324,863.02 | 41 / 3 |
| maximum / monthly | total | $31,600 (1 tie) | $298,261.47 | 58 / 17 | $56,600 (1 tie) | $410,770.78 | 37 / 20 |
| maximum / daily | ongoing | $30,200 (1 tie) | $238,983.64 | 58 / 2 | $55,200 (1 tie) | $333,043.24 | 41 / 3 |
| maximum / daily | total | $32,300 (1 tie) | $298,093.58 | 57 / 17 | $58,300 (1 tie) | $418,322.27 | 35 / 20 |
| maximum / weekly | ongoing | $30,000 (1 tie) | $234,388.79 | 58 / 2 | $55,100 (1 tie) | $327,426.54 | 41 / 3 |
| maximum / weekly | total | $31,600 (1 tie) | $299,046.10 | 58 / 17 | $58,300 (1 tie) | $418,572.25 | 34 / 20 |
| minimum / monthly | ongoing | $28,400 (2 ties) | $194,300.00 | 61 / 14 | $53,400 (2 ties) | $262,250.00 | 41 / 20 |
| minimum / monthly | total | $28,400 (3 ties) | $308,604.52 | 61 / 14 | $53,400 (3 ties) | $427,272.41 | 41 / 20 |
| minimum / daily | ongoing | $29,100 (1 tie) | $266,650.00 | 61 / 2 | $54,100 (1 tie) | $368,100.00 | 43 / 3 |
| minimum / daily | total | $33,300 (2 ties) | $302,687.21 | 56 / 17 | $58,400 (2 ties) | $418,572.26 | 34 / 20 |
| minimum / weekly | ongoing | $28,800 (1 tie) | $258,150.00 | 60 / 2 | $53,800 (1 tie) | $351,650.00 | 42 / 3 |
| minimum / weekly | total | $32,300 (7 ties) | $302,687.21 | 56 / 17 | $57,300 (9 ties) | $418,322.26 | 35 / 20 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| maximum / monthly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| maximum / daily | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| maximum / daily | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| maximum / weekly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| maximum / weekly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / monthly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / monthly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / daily | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / daily | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / weekly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |
| minimum / weekly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 4 / 0 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,100 (40 ties) † | $-1,000.00 | 5 / 0 | $52,600 (1 tie) | $483,267.10 | 124 / 20 |
| maximum / monthly | total | $25,100 (40 ties) † | $-1,000.00 | 5 / 0 | $52,600 (1 tie) | $483,267.10 | 124 / 20 |
| maximum / daily | ongoing | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $53,600 (1 tie) | $507,356.85 | 122 / 20 |
| maximum / daily | total | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $53,600 (1 tie) | $507,356.85 | 122 / 20 |
| maximum / weekly | ongoing | $25,100 (38 ties) † | $-1,000.00 | 5 / 0 | $53,800 (1 tie) | $489,877.80 | 99 / 20 |
| maximum / weekly | total | $25,100 (38 ties) † | $-1,000.00 | 5 / 0 | $56,600 (1 tie) | $491,378.26 | 36 / 20 |
| minimum / monthly | ongoing | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $52,700 (1 tie) | $339,500.00 | 40 / 20 |
| minimum / monthly | total | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $53,200 (2 ties) | $530,385.53 | 38 / 20 |
| minimum / daily | ongoing | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $53,400 (1 tie) | $466,500.00 | 82 / 20 |
| minimum / daily | total | $25,100 (31 ties) † | $-1,000.00 | 5 / 0 | $53,400 (1 tie) | $466,500.00 | 82 / 20 |
| minimum / weekly | ongoing | $25,100 (40 ties) † | $-1,000.00 | 5 / 0 | $53,300 (2 ties) | $459,200.00 | 60 / 20 |
| minimum / weekly | total | $25,100 (40 ties) † | $-1,000.00 | 5 / 0 | $54,100 (1 tie) | $475,000.00 | 58 / 20 |

## $1,000 initial; $200/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $749,859.45 / $749,859.45 | 611 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $714,514.60 / $714,514.60 | 368 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $749,859.45 / $749,859.45 | 611 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $714,514.60 / $714,514.60 | 368 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $373,417.36 | 64 / 2 | $54,800 (1 tie) | $414,973.75 | 54 / 3 |
| maximum / monthly | total | $31,600 (1 tie) | $460,286.01 | 60 / 20 | $57,600 (11 ties) | $507,238.48 | 49 / 20 |
| maximum / daily | ongoing | $30,800 (1 tie) | $368,769.22 | 64 / 2 | $55,800 (1 tie) | $410,926.60 | 54 / 3 |
| maximum / daily | total | $32,600 (1 tie) | $459,618.13 | 60 / 20 | $57,600 (11 ties) | $507,238.49 | 49 / 20 |
| maximum / weekly | ongoing | $30,000 (1 tie) | $375,549.86 | 64 / 2 | $55,100 (1 tie) | $419,345.90 | 54 / 3 |
| maximum / weekly | total | $31,600 (1 tie) | $461,070.58 | 60 / 20 | $58,900 (2 ties) | $507,238.44 | 49 / 20 |
| minimum / monthly | ongoing | $28,400 (2 ties) | $285,200.00 | 69 / 18 | $52,900 (2 ties) | $317,750.00 | 53 / 20 |
| minimum / monthly | total | $30,000 (7 ties) | $464,311.75 | 60 / 20 | $57,600 (11 ties) | $507,238.48 | 49 / 20 |
| minimum / daily | ongoing | $29,200 (1 tie) | $387,000.00 | 69 / 2 | $53,700 (1 tie) | $439,600.00 | 57 / 3 |
| minimum / daily | total | $31,900 (15 ties) | $464,311.75 | 60 / 20 | $57,300 (14 ties) | $507,238.48 | 49 / 20 |
| minimum / weekly | ongoing | $28,600 (1 tie) | $374,650.00 | 69 / 2 | $53,600 (1 tie) | $428,950.00 | 56 / 3 |
| minimum / weekly | total | $31,200 (13 ties) | $464,311.75 | 60 / 20 | $56,900 (8 ties) | $507,238.48 | 49 / 20 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $460,486.42 | 91 / 8 | $54,800 (1 tie) | $472,865.20 | 72 / 9 |
| maximum / monthly | total | $32,600 (1 tie) | $552,685.57 | 69 / 20 | $57,200 (1 tie) | $563,498.69 | 51 / 20 |
| maximum / daily | ongoing | $30,800 (1 tie) | $455,592.01 | 94 / 8 | $55,800 (1 tie) | $467,570.79 | 74 / 9 |
| maximum / daily | total | $33,600 (1 tie) | $553,085.57 | 67 / 20 | $57,800 (4 ties) | $563,248.69 | 52 / 20 |
| maximum / weekly | ongoing | $30,100 (1 tie) | $466,344.32 | 95 / 8 | $55,100 (1 tie) | $479,549.21 | 75 / 10 |
| maximum / weekly | total | $32,200 (1 tie) | $551,281.78 | 72 / 20 | $57,200 (1 tie) | $563,248.60 | 52 / 20 |
| minimum / monthly | ongoing | $27,200 (1 tie) | $358,800.00 | 91 / 20 | $52,200 (1 tie) | $361,750.00 | 71 / 20 |
| minimum / monthly | total | $31,000 (9 ties) | $550,881.87 | 74 / 20 | $56,000 (5 ties) | $562,998.68 | 53 / 20 |
| minimum / daily | ongoing | $29,100 (1 tie) | $484,750.00 | 98 / 8 | $54,100 (1 tie) | $493,300.00 | 78 / 10 |
| minimum / daily | total | $32,800 (4 ties) | $551,281.87 | 72 / 20 | $56,900 (2 ties) | $562,498.68 | 55 / 20 |
| minimum / weekly | ongoing | $28,900 (1 tie) | $461,850.00 | 97 / 8 | $53,900 (1 tie) | $474,250.00 | 77 / 10 |
| minimum / weekly | total | $32,200 (3 ties) | $551,281.87 | 72 / 20 | $55,800 (8 ties) | $562,248.68 | 56 / 20 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,500 (1 tie) | $613,545.95 | 401 / 20 | $52,600 (1 tie) | $566,749.25 | 164 / 20 |
| maximum / monthly | total | $25,500 (1 tie) | $613,545.95 | 401 / 20 | $56,100 (1 tie) | $584,473.63 | 49 / 20 |
| maximum / daily | ongoing | $26,200 (1 tie) | $720,480.70 | 564 / 20 | $50,700 (1 tie) | $714,514.60 | 368 / 20 |
| maximum / daily | total | $26,200 (1 tie) | $720,480.70 | 564 / 20 | $50,700 (1 tie) | $714,514.60 | 368 / 20 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $749,859.45 | 611 / 20 | $51,900 (1 tie) | $675,727.30 | 243 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $749,859.45 | 611 / 20 | $51,900 (1 tie) | $675,727.30 | 243 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $422,950.00 | 135 / 20 | $50,100 (8 ties) † | $424,000.00 | 68 / 20 |
| minimum / monthly | total | $25,100 (7 ties) † | $589,359.07 | 135 / 20 | $53,000 (2 ties) | $606,322.70 | 55 / 20 |
| minimum / daily | ongoing | $26,800 (1 tie) | $605,900.00 | 253 / 20 | $52,500 (1 tie) | $599,250.00 | 129 / 20 |
| minimum / daily | total | $26,800 (1 tie) | $605,900.00 | 253 / 20 | $52,500 (1 tie) | $599,250.00 | 129 / 20 |
| minimum / weekly | ongoing | $25,100 (7 ties) † | $589,000.00 | 270 / 20 | $50,100 (8 ties) † | $564,000.00 | 140 / 20 |
| minimum / weekly | total | $25,100 (7 ties) † | $589,000.00 | 270 / 20 | $55,600 (2 ties) | $588,623.29 | 49 / 20 |

## $5,000 initial; $0/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $810,670.40 / $810,670.40 | 674 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $723,141.60 / $723,141.60 | 371 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $810,670.40 / $810,670.40 | 674 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $723,141.60 / $723,141.60 | 371 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $373,617.36 | 63 / 2 | $54,800 (1 tie) | $365,192.41 | 55 / 3 |
| maximum / monthly | total | $31,600 (1 tie) | $460,486.01 | 59 / 20 | $56,100 (1 tie) | $458,152.98 | 51 / 20 |
| maximum / daily | ongoing | $30,800 (1 tie) | $368,969.22 | 63 / 2 | $55,800 (1 tie) | $360,608.43 | 55 / 3 |
| maximum / daily | total | $32,600 (1 tie) | $460,018.13 | 58 / 20 | $58,300 (4 ties) | $458,652.98 | 49 / 20 |
| maximum / weekly | ongoing | $30,000 (1 tie) | $375,749.86 | 63 / 2 | $55,100 (1 tie) | $368,668.94 | 55 / 3 |
| maximum / weekly | total | $31,600 (1 tie) | $461,270.58 | 59 / 20 | $58,300 (1 tie) | $458,902.92 | 48 / 20 |
| minimum / monthly | ongoing | $28,400 (2 ties) | $285,200.00 | 69 / 18 | $52,900 (2 ties) | $318,000.00 | 52 / 20 |
| minimum / monthly | total | $30,000 (7 ties) | $464,511.75 | 59 / 20 | $52,900 (5 ties) | $500,170.67 | 52 / 20 |
| minimum / daily | ongoing | $29,200 (1 tie) | $387,000.00 | 69 / 2 | $53,700 (1 tie) | $437,350.00 | 54 / 3 |
| minimum / daily | total | $33,300 (2 ties) | $464,911.75 | 57 / 20 | $58,400 (3 ties) | $458,902.97 | 48 / 20 |
| minimum / weekly | ongoing | $28,600 (1 tie) | $374,650.00 | 69 / 2 | $53,600 (1 tie) | $415,700.00 | 54 / 3 |
| minimum / weekly | total | $32,300 (7 ties) | $464,911.75 | 57 / 20 | $57,300 (9 ties) | $458,652.97 | 49 / 20 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $452,905.13 | 94 / 8 | $54,800 (1 tie) | $463,472.23 | 76 / 9 |
| maximum / monthly | total | $33,600 (1 tie) | $546,326.54 | 66 / 20 | $58,600 (1 tie) | $556,802.21 | 48 / 20 |
| maximum / daily | ongoing | $30,400 (1 tie) | $452,350.09 | 97 / 8 | $55,000 (1 tie) | $466,309.11 | 84 / 10 |
| maximum / daily | total | $34,500 (1 tie) | $546,726.56 | 64 / 20 | $59,600 (1 tie) | $560,747.66 | 47 / 20 |
| maximum / weekly | ongoing | $30,000 (1 tie) | $461,537.84 | 96 / 8 | $55,100 (1 tie) | $470,441.04 | 78 / 10 |
| maximum / weekly | total | $34,100 (1 tie) | $546,526.46 | 65 / 20 | $58,600 (2 ties) | $556,052.13 | 51 / 20 |
| minimum / monthly | ongoing | $28,100 (1 tie) | $388,200.00 | 86 / 20 | $53,100 (1 tie) | $392,150.00 | 63 / 20 |
| minimum / monthly | total | $28,100 (2 ties) | $581,596.36 | 86 / 20 | $53,600 (1 tie) | $589,809.03 | 56 / 20 |
| minimum / daily | ongoing | $28,800 (1 tie) | $489,650.00 | 114 / 8 | $53,900 (1 tie) | $497,100.00 | 88 / 10 |
| minimum / daily | total | $33,500 (2 ties) | $545,526.53 | 70 / 20 | $58,500 (2 ties) | $555,802.20 | 52 / 20 |
| minimum / weekly | ongoing | $28,700 (1 tie) | $464,350.00 | 109 / 8 | $53,600 (1 tie) | $481,250.00 | 89 / 10 |
| minimum / weekly | total | $32,900 (3 ties) | $545,326.53 | 71 / 20 | $57,900 (3 ties) | $555,552.20 | 53 / 20 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $26,800 (1 tie) | $678,255.90 | 357 / 20 | $52,300 (1 tie) | $586,061.40 | 189 / 20 |
| maximum / monthly | total | $26,800 (1 tie) | $678,255.90 | 357 / 20 | $52,300 (1 tie) | $586,061.40 | 189 / 20 |
| maximum / daily | ongoing | $26,200 (1 tie) | $794,134.10 | 605 / 20 | $50,700 (1 tie) | $723,141.60 | 371 / 20 |
| maximum / daily | total | $26,200 (1 tie) | $794,134.10 | 605 / 20 | $50,700 (1 tie) | $723,141.60 | 371 / 20 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $810,670.40 | 674 / 20 | $51,900 (1 tie) | $679,116.75 | 248 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $810,670.40 | 674 / 20 | $51,900 (1 tie) | $679,116.75 | 248 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $479,000.00 | 155 / 20 | $50,100 (8 ties) † | $427,000.00 | 64 / 20 |
| minimum / monthly | total | $25,100 (7 ties) † | $646,827.80 | 155 / 20 | $53,000 (2 ties) | $599,587.90 | 61 / 20 |
| minimum / daily | ongoing | $26,800 (1 tie) | $679,000.00 | 265 / 20 | $52,500 (1 tie) | $609,250.00 | 129 / 20 |
| minimum / daily | total | $26,800 (1 tie) | $679,000.00 | 265 / 20 | $52,500 (1 tie) | $609,250.00 | 129 / 20 |
| minimum / weekly | ongoing | $25,100 (7 ties) † | $662,600.00 | 297 / 20 | $50,100 (8 ties) † | $572,250.00 | 143 / 20 |
| minimum / weekly | total | $25,100 (7 ties) † | $662,600.00 | 297 / 20 | $50,100 (8 ties) † | $572,250.00 | 143 / 20 |

## $5,000 initial; $200/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $810,670.40 / $810,670.40 | 674 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $734,753.85 / $734,753.85 | 370 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $810,670.40 / $810,670.40 | 674 / 20 | Monthly + replacements; maximum / daily; reserve $50,700 | $734,753.85 / $734,753.85 | 370 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $373,417.36 | 64 / 2 | $54,800 (1 tie) | $427,285.55 | 55 / 3 |
| maximum / monthly | total | $31,600 (1 tie) | $460,286.01 | 60 / 20 | $56,100 (1 tie) | $518,827.05 | 51 / 20 |
| maximum / daily | ongoing | $30,800 (1 tie) | $368,769.22 | 64 / 2 | $55,800 (1 tie) | $423,259.38 | 55 / 3 |
| maximum / daily | total | $32,200 (1 tie) | $460,018.16 | 60 / 20 | $56,900 (4 ties) | $518,827.09 | 51 / 20 |
| maximum / weekly | ongoing | $30,000 (1 tie) | $375,549.86 | 64 / 2 | $55,100 (1 tie) | $431,640.30 | 55 / 3 |
| maximum / weekly | total | $31,600 (1 tie) | $461,070.58 | 60 / 20 | $62,100 (12 ties) † | $518,827.04 | 51 / 20 |
| minimum / monthly | ongoing | $28,400 (2 ties) | $285,200.00 | 69 / 18 | $53,400 (2 ties) | $321,000.00 | 52 / 20 |
| minimum / monthly | total | $30,000 (7 ties) | $464,311.75 | 60 / 20 | $54,800 (17 ties) † | $518,827.04 | 51 / 20 |
| minimum / daily | ongoing | $29,200 (1 tie) | $387,000.00 | 69 / 2 | $54,100 (1 tie) | $442,800.00 | 56 / 3 |
| minimum / daily | total | $31,900 (9 ties) | $464,311.75 | 60 / 20 | $57,000 (12 ties) † | $518,827.04 | 51 / 20 |
| minimum / weekly | ongoing | $28,600 (1 tie) | $374,650.00 | 69 / 2 | $53,600 (1 tie) | $428,950.00 | 56 / 3 |
| minimum / weekly | total | $31,200 (10 ties) | $464,311.75 | 60 / 20 | $56,000 (17 ties) † | $518,827.04 | 51 / 20 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $29,800 (1 tie) | $500,637.63 | 101 / 8 | $54,800 (1 tie) | $511,619.46 | 78 / 9 |
| maximum / monthly | total | $33,600 (1 tie) | $590,540.14 | 77 / 20 | $58,600 (1 tie) | $600,371.08 | 57 / 20 |
| maximum / daily | ongoing | $30,800 (1 tie) | $496,427.16 | 101 / 8 | $55,800 (1 tie) | $506,908.99 | 78 / 9 |
| maximum / daily | total | $34,200 (5 ties) | $590,140.16 | 79 / 20 | $59,200 (5 ties) | $599,871.10 | 59 / 20 |
| maximum / weekly | ongoing | $30,100 (1 tie) | $507,025.97 | 102 / 8 | $55,100 (1 tie) | $518,733.91 | 79 / 10 |
| maximum / weekly | total | $34,000 (2 ties) | $589,940.01 | 80 / 20 | $58,800 (4 ties) | $599,620.96 | 60 / 20 |
| minimum / monthly | ongoing | $28,100 (1 tie) | $440,700.00 | 76 / 20 | $52,600 (1 tie) | $453,700.00 | 67 / 20 |
| minimum / monthly | total | $28,100 (2 ties) | $630,562.86 | 76 / 20 | $52,600 (2 ties) | $633,632.94 | 67 / 20 |
| minimum / daily | ongoing | $29,000 (1 tie) | $534,200.00 | 109 / 8 | $54,000 (1 tie) | $536,450.00 | 86 / 10 |
| minimum / daily | total | $34,200 (3 ties) | $590,140.13 | 79 / 20 | $58,700 (3 ties) | $599,621.07 | 60 / 20 |
| minimum / weekly | ongoing | $28,800 (1 tie) | $516,300.00 | 110 / 8 | $53,900 (1 tie) | $512,950.00 | 87 / 10 |
| minimum / weekly | total | $33,200 (5 ties) | $589,940.13 | 80 / 20 | $58,200 (3 ties) | $599,621.07 | 60 / 20 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $26,800 (1 tie) | $686,630.15 | 361 / 20 | $52,200 (1 tie) | $623,893.55 | 189 / 20 |
| maximum / monthly | total | $26,800 (1 tie) | $686,630.15 | 361 / 20 | $52,200 (1 tie) | $623,893.55 | 189 / 20 |
| maximum / daily | ongoing | $26,200 (1 tie) | $794,134.10 | 605 / 20 | $50,700 (1 tie) | $734,753.85 | 370 / 20 |
| maximum / daily | total | $26,200 (1 tie) | $794,134.10 | 605 / 20 | $50,700 (1 tie) | $734,753.85 | 370 / 20 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $810,670.40 | 674 / 20 | $51,900 (1 tie) | $681,721.90 | 250 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $810,670.40 | 674 / 20 | $51,900 (1 tie) | $681,721.90 | 250 / 20 |
| minimum / monthly | ongoing | $26,700 (1 tie) | $483,500.00 | 100 / 20 | $50,100 (13 ties) † | $475,500.00 | 52 / 20 |
| minimum / monthly | total | $27,900 (2 ties) | $651,204.67 | 73 / 20 | $52,700 (2 ties) | $645,449.62 | 47 / 20 |
| minimum / daily | ongoing | $26,800 (1 tie) | $679,000.00 | 265 / 20 | $52,500 (2 ties) | $613,250.00 | 129 / 20 |
| minimum / daily | total | $26,800 (1 tie) | $679,000.00 | 265 / 20 | $52,500 (2 ties) | $613,250.00 | 129 / 20 |
| minimum / weekly | ongoing | $25,100 (7 ties) † | $663,800.00 | 296 / 20 | $53,100 (1 tie) | $590,500.00 | 81 / 20 |
| minimum / weekly | total | $25,100 (7 ties) † | $663,800.00 | 296 / 20 | $57,100 (6 ties) | $612,663.28 | 58 / 20 |

## Limits on interpreting a winner

A boundary tie warns that some equally best setting touches the tested limits; it can also mean all reserves produce the same failure path. A unique interior winner still does not prove a global optimum: untested intervals and other trade histories remain. Reserves selected on the same tape are subject to selection bias. Near-best results describe parameter sensitivity on this tape, not robustness to future markets. Selecting reserves separately measures adaptation; use matched rows for a fixed-policy account comparison. A higher ongoing score can come with fewer survivors and a lower total.
