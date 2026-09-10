# Legacy 25K versus 50K: best tested reserves by operating policy

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

| Objective | Product | Purchases | Withdraw / checks | Reserve | Accounts | Alive | Ongoing | Total |
|---|---|---|---|---:|---:|---:|---:|---:|
| ongoing | legacy_25k | monthly_one | minimum / daily | $29,100 | 61 | 2 | $266,650.00 | $266,650.00 |
| ongoing | legacy_50k | monthly_current_slot_replacements | maximum / daily | $53,600 | 122 | 20 | $507,356.85 | $507,356.85 |
| total | legacy_25k | monthly_one | minimum / calendar_month | $28,400 | 61 | 14 | $194,300.00 | $308,604.52 |
| total | legacy_50k | monthly_current_slot_replacements | minimum / calendar_month | $53,200 | 38 | 20 | $332,000.00 | $530,385.53 |

### monthly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $233,488.82 | 58 | 2 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $31,600 | $298,261.47 | 58 | 17 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,200 | $238,983.64 | 58 | 2 | 1 | no |
| legacy_25k | maximum / daily | total | $32,300 | $298,093.58 | 57 | 17 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,000 | $234,388.79 | 58 | 2 | 1 | no |
| legacy_25k | maximum / weekly | total | $31,600 | $299,046.10 | 58 | 17 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,400 | $194,300.00 | 61 | 14 | 2 | no |
| legacy_25k | minimum / calendar_month | total | $28,400 | $308,604.52 | 61 | 14 | 3 | no |
| legacy_25k | minimum / daily | ongoing | $29,100 | $266,650.00 | 61 | 2 | 1 | no |
| legacy_25k | minimum / daily | total | $33,300 | $302,687.21 | 56 | 17 | 2 | no |
| legacy_25k | minimum / weekly | ongoing | $28,800 | $258,150.00 | 60 | 2 | 1 | no |
| legacy_25k | minimum / weekly | total | $32,300 | $302,687.21 | 56 | 17 | 7 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $324,863.02 | 41 | 3 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $56,600 | $410,770.78 | 37 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,200 | $333,043.24 | 41 | 3 | 1 | no |
| legacy_50k | maximum / daily | total | $58,300 | $418,322.27 | 35 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $327,426.54 | 41 | 3 | 1 | no |
| legacy_50k | maximum / weekly | total | $58,300 | $418,572.25 | 34 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $53,400 | $262,250.00 | 41 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | total | $53,400 | $427,272.41 | 41 | 20 | 3 | no |
| legacy_50k | minimum / daily | ongoing | $54,100 | $368,100.00 | 43 | 3 | 1 | no |
| legacy_50k | minimum / daily | total | $58,400 | $418,572.26 | 34 | 20 | 2 | no |
| legacy_50k | minimum / weekly | ongoing | $53,800 | $351,650.00 | 42 | 3 | 1 | no |
| legacy_50k | minimum / weekly | total | $57,300 | $418,322.26 | 35 | 20 | 9 | no |

### weekly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | maximum / calendar_month | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | maximum / daily | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | maximum / daily | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | maximum / weekly | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | maximum / weekly | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / calendar_month | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / calendar_month | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / daily | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / daily | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / weekly | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_25k | minimum / weekly | total | $25,100 | $-1,000.00 | 5 | 0 | 21 | yes |
| legacy_50k | maximum / calendar_month | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | maximum / calendar_month | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | maximum / daily | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | maximum / daily | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | maximum / weekly | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | maximum / weekly | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / calendar_month | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / calendar_month | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / daily | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / daily | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / weekly | ongoing | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |
| legacy_50k | minimum / weekly | total | $50,100 | $-1,000.00 | 4 | 0 | 21 | yes |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 40 | yes |
| legacy_25k | maximum / calendar_month | total | $25,100 | $-1,000.00 | 5 | 0 | 40 | yes |
| legacy_25k | maximum / daily | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | maximum / daily | total | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | maximum / weekly | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 38 | yes |
| legacy_25k | maximum / weekly | total | $25,100 | $-1,000.00 | 5 | 0 | 38 | yes |
| legacy_25k | minimum / calendar_month | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | minimum / calendar_month | total | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | minimum / daily | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | minimum / daily | total | $25,100 | $-1,000.00 | 5 | 0 | 31 | yes |
| legacy_25k | minimum / weekly | ongoing | $25,100 | $-1,000.00 | 5 | 0 | 40 | yes |
| legacy_25k | minimum / weekly | total | $25,100 | $-1,000.00 | 5 | 0 | 40 | yes |
| legacy_50k | maximum / calendar_month | ongoing | $52,600 | $483,267.10 | 124 | 20 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $52,600 | $483,267.10 | 124 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $53,600 | $507,356.85 | 122 | 20 | 1 | no |
| legacy_50k | maximum / daily | total | $53,600 | $507,356.85 | 122 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $53,800 | $489,877.80 | 99 | 20 | 1 | no |
| legacy_50k | maximum / weekly | total | $56,600 | $491,378.26 | 36 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $52,700 | $339,500.00 | 40 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | total | $53,200 | $530,385.53 | 38 | 20 | 2 | no |
| legacy_50k | minimum / daily | ongoing | $53,400 | $466,500.00 | 82 | 20 | 1 | no |
| legacy_50k | minimum / daily | total | $53,400 | $466,500.00 | 82 | 20 | 1 | no |
| legacy_50k | minimum / weekly | ongoing | $53,300 | $459,200.00 | 60 | 20 | 2 | no |
| legacy_50k | minimum / weekly | total | $54,100 | $475,000.00 | 58 | 20 | 1 | no |

## $1,000 initial; $200/month

### Best complete tested bundles

| Objective | Product | Purchases | Withdraw / checks | Reserve | Accounts | Alive | Ongoing | Total |
|---|---|---|---|---:|---:|---:|---:|---:|
| ongoing | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 611 | 20 | $749,859.45 | $749,859.45 |
| ongoing | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 368 | 20 | $714,514.60 | $714,514.60 |
| total | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 611 | 20 | $749,859.45 | $749,859.45 |
| total | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 368 | 20 | $714,514.60 | $714,514.60 |

### monthly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $373,417.36 | 64 | 2 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $31,600 | $460,286.01 | 60 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,800 | $368,769.22 | 64 | 2 | 1 | no |
| legacy_25k | maximum / daily | total | $32,600 | $459,618.13 | 60 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,000 | $375,549.86 | 64 | 2 | 1 | no |
| legacy_25k | maximum / weekly | total | $31,600 | $461,070.58 | 60 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,400 | $285,200.00 | 69 | 18 | 2 | no |
| legacy_25k | minimum / calendar_month | total | $30,000 | $464,311.75 | 60 | 20 | 7 | no |
| legacy_25k | minimum / daily | ongoing | $29,200 | $387,000.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / daily | total | $31,900 | $464,311.75 | 60 | 20 | 15 | no |
| legacy_25k | minimum / weekly | ongoing | $28,600 | $374,650.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / weekly | total | $31,200 | $464,311.75 | 60 | 20 | 13 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $414,973.75 | 54 | 3 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $57,600 | $507,238.48 | 49 | 20 | 11 | no |
| legacy_50k | maximum / daily | ongoing | $55,800 | $410,926.60 | 54 | 3 | 1 | no |
| legacy_50k | maximum / daily | total | $57,600 | $507,238.49 | 49 | 20 | 11 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $419,345.90 | 54 | 3 | 1 | no |
| legacy_50k | maximum / weekly | total | $58,900 | $507,238.44 | 49 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | ongoing | $52,900 | $317,750.00 | 53 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | total | $57,600 | $507,238.48 | 49 | 20 | 11 | no |
| legacy_50k | minimum / daily | ongoing | $53,700 | $439,600.00 | 57 | 3 | 1 | no |
| legacy_50k | minimum / daily | total | $57,300 | $507,238.48 | 49 | 20 | 14 | no |
| legacy_50k | minimum / weekly | ongoing | $53,600 | $428,950.00 | 56 | 3 | 1 | no |
| legacy_50k | minimum / weekly | total | $56,900 | $507,238.48 | 49 | 20 | 8 | no |

### weekly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $460,486.42 | 91 | 8 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $32,600 | $552,685.57 | 69 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,800 | $455,592.01 | 94 | 8 | 1 | no |
| legacy_25k | maximum / daily | total | $33,600 | $553,085.57 | 67 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,100 | $466,344.32 | 95 | 8 | 1 | no |
| legacy_25k | maximum / weekly | total | $32,200 | $551,281.78 | 72 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $27,200 | $358,800.00 | 91 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | total | $31,000 | $550,881.87 | 74 | 20 | 9 | no |
| legacy_25k | minimum / daily | ongoing | $29,100 | $484,750.00 | 98 | 8 | 1 | no |
| legacy_25k | minimum / daily | total | $32,800 | $551,281.87 | 72 | 20 | 4 | no |
| legacy_25k | minimum / weekly | ongoing | $28,900 | $461,850.00 | 97 | 8 | 1 | no |
| legacy_25k | minimum / weekly | total | $32,200 | $551,281.87 | 72 | 20 | 3 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $472,865.20 | 72 | 9 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $57,200 | $563,498.69 | 51 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,800 | $467,570.79 | 74 | 9 | 1 | no |
| legacy_50k | maximum / daily | total | $57,800 | $563,248.69 | 52 | 20 | 4 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $479,549.21 | 75 | 10 | 1 | no |
| legacy_50k | maximum / weekly | total | $57,200 | $563,248.60 | 52 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $52,200 | $361,750.00 | 71 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | total | $56,000 | $562,998.68 | 53 | 20 | 5 | no |
| legacy_50k | minimum / daily | ongoing | $54,100 | $493,300.00 | 78 | 10 | 1 | no |
| legacy_50k | minimum / daily | total | $56,900 | $562,498.68 | 55 | 20 | 2 | no |
| legacy_50k | minimum / weekly | ongoing | $53,900 | $474,250.00 | 77 | 10 | 1 | no |
| legacy_50k | minimum / weekly | total | $55,800 | $562,248.68 | 56 | 20 | 8 | no |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $25,500 | $613,545.95 | 401 | 20 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $25,500 | $613,545.95 | 401 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $26,200 | $720,480.70 | 564 | 20 | 1 | no |
| legacy_25k | maximum / daily | total | $26,200 | $720,480.70 | 564 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $25,100 | $749,859.45 | 611 | 20 | 1 | yes |
| legacy_25k | maximum / weekly | total | $25,100 | $749,859.45 | 611 | 20 | 1 | yes |
| legacy_25k | minimum / calendar_month | ongoing | $25,100 | $422,950.00 | 135 | 20 | 7 | yes |
| legacy_25k | minimum / calendar_month | total | $25,100 | $589,359.07 | 135 | 20 | 7 | yes |
| legacy_25k | minimum / daily | ongoing | $26,800 | $605,900.00 | 253 | 20 | 1 | no |
| legacy_25k | minimum / daily | total | $26,800 | $605,900.00 | 253 | 20 | 1 | no |
| legacy_25k | minimum / weekly | ongoing | $25,100 | $589,000.00 | 270 | 20 | 7 | yes |
| legacy_25k | minimum / weekly | total | $25,100 | $589,000.00 | 270 | 20 | 7 | yes |
| legacy_50k | maximum / calendar_month | ongoing | $52,600 | $566,749.25 | 164 | 20 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $56,100 | $584,473.63 | 49 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $50,700 | $714,514.60 | 368 | 20 | 1 | no |
| legacy_50k | maximum / daily | total | $50,700 | $714,514.60 | 368 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $51,900 | $675,727.30 | 243 | 20 | 1 | no |
| legacy_50k | maximum / weekly | total | $51,900 | $675,727.30 | 243 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $50,100 | $424,000.00 | 68 | 20 | 8 | yes |
| legacy_50k | minimum / calendar_month | total | $53,000 | $606,322.70 | 55 | 20 | 2 | no |
| legacy_50k | minimum / daily | ongoing | $52,500 | $599,250.00 | 129 | 20 | 1 | no |
| legacy_50k | minimum / daily | total | $52,500 | $599,250.00 | 129 | 20 | 1 | no |
| legacy_50k | minimum / weekly | ongoing | $50,100 | $564,000.00 | 140 | 20 | 8 | yes |
| legacy_50k | minimum / weekly | total | $55,600 | $588,623.29 | 49 | 20 | 2 | no |

## $5,000 initial; $0/month

### Best complete tested bundles

| Objective | Product | Purchases | Withdraw / checks | Reserve | Accounts | Alive | Ongoing | Total |
|---|---|---|---|---:|---:|---:|---:|---:|
| ongoing | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 674 | 20 | $810,670.40 | $810,670.40 |
| ongoing | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 371 | 20 | $723,141.60 | $723,141.60 |
| total | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 674 | 20 | $810,670.40 | $810,670.40 |
| total | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 371 | 20 | $723,141.60 | $723,141.60 |

### monthly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $373,617.36 | 63 | 2 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $31,600 | $460,486.01 | 59 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,800 | $368,969.22 | 63 | 2 | 1 | no |
| legacy_25k | maximum / daily | total | $32,600 | $460,018.13 | 58 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,000 | $375,749.86 | 63 | 2 | 1 | no |
| legacy_25k | maximum / weekly | total | $31,600 | $461,270.58 | 59 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,400 | $285,200.00 | 69 | 18 | 2 | no |
| legacy_25k | minimum / calendar_month | total | $30,000 | $464,511.75 | 59 | 20 | 7 | no |
| legacy_25k | minimum / daily | ongoing | $29,200 | $387,000.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / daily | total | $33,300 | $464,911.75 | 57 | 20 | 2 | no |
| legacy_25k | minimum / weekly | ongoing | $28,600 | $374,650.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / weekly | total | $32,300 | $464,911.75 | 57 | 20 | 7 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $365,192.41 | 55 | 3 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $56,100 | $458,152.98 | 51 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,800 | $360,608.43 | 55 | 3 | 1 | no |
| legacy_50k | maximum / daily | total | $58,300 | $458,652.98 | 49 | 20 | 4 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $368,668.94 | 55 | 3 | 1 | no |
| legacy_50k | maximum / weekly | total | $58,300 | $458,902.92 | 48 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $52,900 | $318,000.00 | 52 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | total | $52,900 | $500,170.67 | 52 | 20 | 5 | no |
| legacy_50k | minimum / daily | ongoing | $53,700 | $437,350.00 | 54 | 3 | 1 | no |
| legacy_50k | minimum / daily | total | $58,400 | $458,902.97 | 48 | 20 | 3 | no |
| legacy_50k | minimum / weekly | ongoing | $53,600 | $415,700.00 | 54 | 3 | 1 | no |
| legacy_50k | minimum / weekly | total | $57,300 | $458,652.97 | 49 | 20 | 9 | no |

### weekly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $452,905.13 | 94 | 8 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $33,600 | $546,326.54 | 66 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,400 | $452,350.09 | 97 | 8 | 1 | no |
| legacy_25k | maximum / daily | total | $34,500 | $546,726.56 | 64 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,000 | $461,537.84 | 96 | 8 | 1 | no |
| legacy_25k | maximum / weekly | total | $34,100 | $546,526.46 | 65 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,100 | $388,200.00 | 86 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | total | $28,100 | $581,596.36 | 86 | 20 | 2 | no |
| legacy_25k | minimum / daily | ongoing | $28,800 | $489,650.00 | 114 | 8 | 1 | no |
| legacy_25k | minimum / daily | total | $33,500 | $545,526.53 | 70 | 20 | 2 | no |
| legacy_25k | minimum / weekly | ongoing | $28,700 | $464,350.00 | 109 | 8 | 1 | no |
| legacy_25k | minimum / weekly | total | $32,900 | $545,326.53 | 71 | 20 | 3 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $463,472.23 | 76 | 9 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $58,600 | $556,802.21 | 48 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,000 | $466,309.11 | 84 | 10 | 1 | no |
| legacy_50k | maximum / daily | total | $59,600 | $560,747.66 | 47 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $470,441.04 | 78 | 10 | 1 | no |
| legacy_50k | maximum / weekly | total | $58,600 | $556,052.13 | 51 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | ongoing | $53,100 | $392,150.00 | 63 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | total | $53,600 | $589,809.03 | 56 | 20 | 1 | no |
| legacy_50k | minimum / daily | ongoing | $53,900 | $497,100.00 | 88 | 10 | 1 | no |
| legacy_50k | minimum / daily | total | $58,500 | $555,802.20 | 52 | 20 | 2 | no |
| legacy_50k | minimum / weekly | ongoing | $53,600 | $481,250.00 | 89 | 10 | 1 | no |
| legacy_50k | minimum / weekly | total | $57,900 | $555,552.20 | 53 | 20 | 3 | no |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $26,800 | $678,255.90 | 357 | 20 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $26,800 | $678,255.90 | 357 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $26,200 | $794,134.10 | 605 | 20 | 1 | no |
| legacy_25k | maximum / daily | total | $26,200 | $794,134.10 | 605 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $25,100 | $810,670.40 | 674 | 20 | 1 | yes |
| legacy_25k | maximum / weekly | total | $25,100 | $810,670.40 | 674 | 20 | 1 | yes |
| legacy_25k | minimum / calendar_month | ongoing | $25,100 | $479,000.00 | 155 | 20 | 7 | yes |
| legacy_25k | minimum / calendar_month | total | $25,100 | $646,827.80 | 155 | 20 | 7 | yes |
| legacy_25k | minimum / daily | ongoing | $26,800 | $679,000.00 | 265 | 20 | 1 | no |
| legacy_25k | minimum / daily | total | $26,800 | $679,000.00 | 265 | 20 | 1 | no |
| legacy_25k | minimum / weekly | ongoing | $25,100 | $662,600.00 | 297 | 20 | 7 | yes |
| legacy_25k | minimum / weekly | total | $25,100 | $662,600.00 | 297 | 20 | 7 | yes |
| legacy_50k | maximum / calendar_month | ongoing | $52,300 | $586,061.40 | 189 | 20 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $52,300 | $586,061.40 | 189 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $50,700 | $723,141.60 | 371 | 20 | 1 | no |
| legacy_50k | maximum / daily | total | $50,700 | $723,141.60 | 371 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $51,900 | $679,116.75 | 248 | 20 | 1 | no |
| legacy_50k | maximum / weekly | total | $51,900 | $679,116.75 | 248 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $50,100 | $427,000.00 | 64 | 20 | 8 | yes |
| legacy_50k | minimum / calendar_month | total | $53,000 | $599,587.90 | 61 | 20 | 2 | no |
| legacy_50k | minimum / daily | ongoing | $52,500 | $609,250.00 | 129 | 20 | 1 | no |
| legacy_50k | minimum / daily | total | $52,500 | $609,250.00 | 129 | 20 | 1 | no |
| legacy_50k | minimum / weekly | ongoing | $50,100 | $572,250.00 | 143 | 20 | 8 | yes |
| legacy_50k | minimum / weekly | total | $50,100 | $572,250.00 | 143 | 20 | 8 | yes |

## $5,000 initial; $200/month

### Best complete tested bundles

| Objective | Product | Purchases | Withdraw / checks | Reserve | Accounts | Alive | Ongoing | Total |
|---|---|---|---|---:|---:|---:|---:|---:|
| ongoing | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 674 | 20 | $810,670.40 | $810,670.40 |
| ongoing | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 370 | 20 | $734,753.85 | $734,753.85 |
| total | legacy_25k | monthly_current_slot_replacements | maximum / weekly | $25,100 | 674 | 20 | $810,670.40 | $810,670.40 |
| total | legacy_50k | monthly_current_slot_replacements | maximum / daily | $50,700 | 370 | 20 | $734,753.85 | $734,753.85 |

### monthly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $373,417.36 | 64 | 2 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $31,600 | $460,286.01 | 60 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,800 | $368,769.22 | 64 | 2 | 1 | no |
| legacy_25k | maximum / daily | total | $32,200 | $460,018.16 | 60 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $30,000 | $375,549.86 | 64 | 2 | 1 | no |
| legacy_25k | maximum / weekly | total | $31,600 | $461,070.58 | 60 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,400 | $285,200.00 | 69 | 18 | 2 | no |
| legacy_25k | minimum / calendar_month | total | $30,000 | $464,311.75 | 60 | 20 | 7 | no |
| legacy_25k | minimum / daily | ongoing | $29,200 | $387,000.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / daily | total | $31,900 | $464,311.75 | 60 | 20 | 9 | no |
| legacy_25k | minimum / weekly | ongoing | $28,600 | $374,650.00 | 69 | 2 | 1 | no |
| legacy_25k | minimum / weekly | total | $31,200 | $464,311.75 | 60 | 20 | 10 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $427,285.55 | 55 | 3 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $56,100 | $518,827.05 | 51 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,800 | $423,259.38 | 55 | 3 | 1 | no |
| legacy_50k | maximum / daily | total | $56,900 | $518,827.09 | 51 | 20 | 4 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $431,640.30 | 55 | 3 | 1 | no |
| legacy_50k | maximum / weekly | total | $62,100 | $518,827.04 | 51 | 20 | 12 | yes |
| legacy_50k | minimum / calendar_month | ongoing | $53,400 | $321,000.00 | 52 | 20 | 2 | no |
| legacy_50k | minimum / calendar_month | total | $54,800 | $518,827.04 | 51 | 20 | 17 | yes |
| legacy_50k | minimum / daily | ongoing | $54,100 | $442,800.00 | 56 | 3 | 1 | no |
| legacy_50k | minimum / daily | total | $57,000 | $518,827.04 | 51 | 20 | 12 | yes |
| legacy_50k | minimum / weekly | ongoing | $53,600 | $428,950.00 | 56 | 3 | 1 | no |
| legacy_50k | minimum / weekly | total | $56,000 | $518,827.04 | 51 | 20 | 17 | yes |

### weekly_one: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $29,800 | $500,637.63 | 101 | 8 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $33,600 | $590,540.14 | 77 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $30,800 | $496,427.16 | 101 | 8 | 1 | no |
| legacy_25k | maximum / daily | total | $34,200 | $590,140.16 | 79 | 20 | 5 | no |
| legacy_25k | maximum / weekly | ongoing | $30,100 | $507,025.97 | 102 | 8 | 1 | no |
| legacy_25k | maximum / weekly | total | $34,000 | $589,940.01 | 80 | 20 | 2 | no |
| legacy_25k | minimum / calendar_month | ongoing | $28,100 | $440,700.00 | 76 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | total | $28,100 | $630,562.86 | 76 | 20 | 2 | no |
| legacy_25k | minimum / daily | ongoing | $29,000 | $534,200.00 | 109 | 8 | 1 | no |
| legacy_25k | minimum / daily | total | $34,200 | $590,140.13 | 79 | 20 | 3 | no |
| legacy_25k | minimum / weekly | ongoing | $28,800 | $516,300.00 | 110 | 8 | 1 | no |
| legacy_25k | minimum / weekly | total | $33,200 | $589,940.13 | 80 | 20 | 5 | no |
| legacy_50k | maximum / calendar_month | ongoing | $54,800 | $511,619.46 | 78 | 9 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $58,600 | $600,371.08 | 57 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $55,800 | $506,908.99 | 78 | 9 | 1 | no |
| legacy_50k | maximum / daily | total | $59,200 | $599,871.10 | 59 | 20 | 5 | no |
| legacy_50k | maximum / weekly | ongoing | $55,100 | $518,733.91 | 79 | 10 | 1 | no |
| legacy_50k | maximum / weekly | total | $58,800 | $599,620.96 | 60 | 20 | 4 | no |
| legacy_50k | minimum / calendar_month | ongoing | $52,600 | $453,700.00 | 67 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | total | $52,600 | $633,632.94 | 67 | 20 | 2 | no |
| legacy_50k | minimum / daily | ongoing | $54,000 | $536,450.00 | 86 | 10 | 1 | no |
| legacy_50k | minimum / daily | total | $58,700 | $599,621.07 | 60 | 20 | 3 | no |
| legacy_50k | minimum / weekly | ongoing | $53,900 | $512,950.00 | 87 | 10 | 1 | no |
| legacy_50k | minimum / weekly | total | $58,200 | $599,621.07 | 60 | 20 | 3 | no |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Product | Withdraw / checks | Objective | Best reserve | Score | Accounts | Alive | Equally best reserves | Boundary tie? |
|---|---|---|---:|---:|---:|---:|---:|---|
| legacy_25k | maximum / calendar_month | ongoing | $26,800 | $686,630.15 | 361 | 20 | 1 | no |
| legacy_25k | maximum / calendar_month | total | $26,800 | $686,630.15 | 361 | 20 | 1 | no |
| legacy_25k | maximum / daily | ongoing | $26,200 | $794,134.10 | 605 | 20 | 1 | no |
| legacy_25k | maximum / daily | total | $26,200 | $794,134.10 | 605 | 20 | 1 | no |
| legacy_25k | maximum / weekly | ongoing | $25,100 | $810,670.40 | 674 | 20 | 1 | yes |
| legacy_25k | maximum / weekly | total | $25,100 | $810,670.40 | 674 | 20 | 1 | yes |
| legacy_25k | minimum / calendar_month | ongoing | $26,700 | $483,500.00 | 100 | 20 | 1 | no |
| legacy_25k | minimum / calendar_month | total | $27,900 | $651,204.67 | 73 | 20 | 2 | no |
| legacy_25k | minimum / daily | ongoing | $26,800 | $679,000.00 | 265 | 20 | 1 | no |
| legacy_25k | minimum / daily | total | $26,800 | $679,000.00 | 265 | 20 | 1 | no |
| legacy_25k | minimum / weekly | ongoing | $25,100 | $663,800.00 | 296 | 20 | 7 | yes |
| legacy_25k | minimum / weekly | total | $25,100 | $663,800.00 | 296 | 20 | 7 | yes |
| legacy_50k | maximum / calendar_month | ongoing | $52,200 | $623,893.55 | 189 | 20 | 1 | no |
| legacy_50k | maximum / calendar_month | total | $52,200 | $623,893.55 | 189 | 20 | 1 | no |
| legacy_50k | maximum / daily | ongoing | $50,700 | $734,753.85 | 370 | 20 | 1 | no |
| legacy_50k | maximum / daily | total | $50,700 | $734,753.85 | 370 | 20 | 1 | no |
| legacy_50k | maximum / weekly | ongoing | $51,900 | $681,721.90 | 250 | 20 | 1 | no |
| legacy_50k | maximum / weekly | total | $51,900 | $681,721.90 | 250 | 20 | 1 | no |
| legacy_50k | minimum / calendar_month | ongoing | $50,100 | $475,500.00 | 52 | 20 | 13 | yes |
| legacy_50k | minimum / calendar_month | total | $52,700 | $645,449.62 | 47 | 20 | 2 | no |
| legacy_50k | minimum / daily | ongoing | $52,500 | $613,250.00 | 129 | 20 | 2 | no |
| legacy_50k | minimum / daily | total | $52,500 | $613,250.00 | 129 | 20 | 2 | no |
| legacy_50k | minimum / weekly | ongoing | $53,100 | $590,500.00 | 81 | 20 | 1 | no |
| legacy_50k | minimum / weekly | total | $57,100 | $612,663.28 | 58 | 20 | 6 | no |

## Limits on interpreting a winner

A boundary tie warns that some equally best setting touches the tested limits; it can also mean all reserves produce the same failure path. A unique interior winner still does not prove a global optimum: untested intervals and other trade histories remain. Reserves selected on the same tape are subject to selection bias. Near-best results describe parameter sensitivity on this tape, not robustness to future markets. Selecting reserves separately measures adaptation; use matched rows for a fixed-policy account comparison. A higher ongoing score can come with fewer survivors and a lower total.
