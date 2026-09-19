# Legacy 25K versus 50K: best tested reserves by operating policy — blocked copying

25K is shown on the left and 50K on the right. Each row shares the same comparison labels. “Bought / alive” means cumulative purchases / ending survivors. Reserve cells retain tie counts; † marks a tie at a tested range boundary. Cash pairs are ongoing / terminal-inclusive, in USD.

4,178 simulations; 144 product/budget/policy families; 206 blocked-optimization settings reproduced, including per-trade account assignments. Each paired family tests exactly the same floor-headroom values for both products.

**Execution: blocked copying.** Each funded account holds at most one position. A signal is copied by every live account that is flat at its entry; an account still in an earlier trade skips it. Everything else matches the [non-blocking comparison](../../../comparisons/legacy_25k_vs_50k/reserve_by_policy/REPORT.md), where every live account copies every signal: same tape, grid, budgets, fees and rules.

## How to read this comparison

These are in-sample best tested settings, not global optima or expected future earnings. A reserve is the balance left after a withdrawal, not a trading stop. Daily minimum means request $500 when eligible and enough balance remains; maximum means request all excess permitted by the reserve and firm rules. Checks start in the account's second calendar month.

Same RR tape and exposure, four owner budgets, 20 live accounts, user-specified seat fees $200 (25K) / $250 (50K). The matched comparison therefore includes cost as well as account mechanics. Ongoing = receipts during trading minus all purchase fees; total adds one permitted endpoint request releasing the voluntary reserve. Owner contributions are excluded from both net scores.

**Rule interpretation:** both products retain the inherited payout model. The optional post-payout-six retained minimum is not enabled or re-optimized here. See [source audit and limitations](../../../../research/legacy_50k/SOURCES.md).

**Coverage:** minimum and maximum withdrawal families, daily/weekly/monthly checks; monthly-one, weekly-one and monthly purchases with current-month-slot replacements. Fixed-amount backlog policies, quarterly schedules, batch purchases and calendar-phase variation are outside this focused comparison.

Common coarse headrooms above the frozen floor: [0, 1000, 2000, 3000, 4000, 4900, 5000, 6000, 6500, 6800, 7000, 8000, 9000, 10000, 12500, 15000]. Within every budget/purchase/withdrawal/cadence family, refine +/-$500 in $100 steps around each product's coarse winner for each objective; apply the UNION of those values to BOTH products. This is a broad coarse search plus local refinement, not a continuous or exhaustive $100 grid. Secondary objective, then lower reserve, breaks display ties. All primary-score ties remain in the data.

The frozen floors are $25,100 and $50,100: headroom $6,800 means reserves $31,900 and $56,900. The blocked-optimization cross-check covers monthly and monthly-plus-replacement purchases; weekly purchases are excluded because that study buys its seed account on the first day rather than the first Monday.

## Files

- [All paired settings](all_settings.csv) and [matched 50K-minus-25K differences](matched_deltas.csv).
- [Best reserves by family and objective](best_by_policy.csv), including exact ties, tested bounds and the explicit list of tested reserves within 1% of the best positive score. Those lists need not be continuous bands and are not confidence intervals.
- [Research contract and evidence](study.json). [Operating notes](HOW_THIS_STUDY_WORKS.md).

## $1,000 initial; $0/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly; minimum / weekly; reserve $27,000 | $200,400.00 / $200,400.00 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478.15 / $268,478.15 | 56 / 1 |
| total | Monthly; minimum / weekly; reserve $27,000 | $200,400.00 / $200,400.00 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478.15 / $268,478.15 | 56 / 1 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $26,200 (1 tie) | $93,052.10 | 75 / 3 | $50,100 (17 ties) † | $-857.45 | 6 / 0 |
| maximum / monthly | total | $26,200 (1 tie) | $94,552.10 | 75 / 3 | $50,100 (17 ties) † | $-857.45 | 6 / 0 |
| maximum / daily | ongoing | $27,600 (1 tie) | $148,363.85 | 64 / 2 | $52,600 (1 tie) | $248,723.55 | 49 / 1 |
| maximum / daily | total | $27,600 (1 tie) | $149,863.85 | 64 / 2 | $52,600 (1 tie) | $248,723.55 | 49 / 1 |
| maximum / weekly | ongoing | $27,100 (1 tie) | $151,160.90 | 72 / 1 | $52,100 (1 tie) | $268,478.15 | 56 / 1 |
| maximum / weekly | total | $27,100 (1 tie) | $151,160.90 | 72 / 1 | $52,100 (1 tie) | $268,478.15 | 56 / 1 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $104,700.00 | 74 / 10 | $50,100 (21 ties) † | $-1,000.00 | 6 / 0 |
| minimum / monthly | total | $25,100 (7 ties) † | $157,312.63 | 74 / 10 | $50,100 (21 ties) † | $-1,000.00 | 6 / 0 |
| minimum / daily | ongoing | $27,100 (1 tie) | $135,900.00 | 68 / 3 | $50,100 (31 ties) † | $-1,000.00 | 12 / 0 |
| minimum / daily | total | $27,100 (1 tie) | $135,900.00 | 68 / 3 | $50,100 (31 ties) † | $-1,000.00 | 12 / 0 |
| minimum / weekly | ongoing | $27,000 (1 tie) | $200,400.00 | 68 / 3 | $50,100 (31 ties) † | $-1,000.00 | 12 / 0 |
| minimum / weekly | total | $27,000 (1 tie) | $200,400.00 | 68 / 3 | $50,100 (31 ties) † | $-1,000.00 | 12 / 0 |

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
| maximum / monthly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-857.45 | 6 / 0 |
| maximum / monthly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-857.45 | 6 / 0 |
| maximum / daily | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-978.20 | 11 / 0 |
| maximum / daily | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-978.20 | 11 / 0 |
| maximum / weekly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-975.35 | 14 / 0 |
| maximum / weekly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (8 ties) † | $-975.35 | 14 / 0 |
| minimum / monthly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 6 / 0 |
| minimum / monthly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 6 / 0 |
| minimum / daily | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 10 / 0 |
| minimum / daily | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 10 / 0 |
| minimum / weekly | ongoing | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 10 / 0 |
| minimum / weekly | total | $25,100 (21 ties) † | $-1,000.00 | 5 / 0 | $50,100 (21 ties) † | $-1,000.00 | 10 / 0 |

## $1,000 initial; $200/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $665,420.55 / $665,420.55 | 531 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $585,935.35 / $585,935.35 | 265 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $665,420.55 / $665,420.55 | 531 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $585,935.35 / $585,935.35 | 265 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $28,700 (1 tie) | $234,927.30 | 74 / 3 | $53,700 (1 tie) | $348,417.80 | 50 / 3 |
| maximum / monthly | total | $31,000 (3 ties) | $315,242.87 | 74 / 19 | $56,000 (6 ties) | $437,229.68 | 46 / 20 |
| maximum / daily | ongoing | $29,500 (1 tie) | $229,009.60 | 74 / 3 | $54,100 (1 tie) | $344,116.90 | 51 / 3 |
| maximum / daily | total | $31,300 (1 tie) | $316,062.42 | 74 / 19 | $56,200 (7 ties) | $437,229.68 | 46 / 20 |
| maximum / weekly | ongoing | $29,100 (1 tie) | $236,917.35 | 74 / 3 | $53,900 (1 tie) | $351,097.05 | 51 / 3 |
| maximum / weekly | total | $31,300 (1 tie) | $316,062.42 | 74 / 19 | $56,300 (5 ties) | $437,229.68 | 46 / 20 |
| minimum / monthly | ongoing | $28,600 (1 tie) | $172,700.00 | 74 / 19 | $50,100 (8 ties) † | $279,000.00 | 50 / 20 |
| minimum / monthly | total | $28,600 (3 ties) | $316,742.87 | 74 / 19 | $50,100 (8 ties) † | $448,929.83 | 50 / 20 |
| minimum / daily | ongoing | $29,500 (1 tie) | $228,200.00 | 74 / 3 | $53,000 (1 tie) | $372,000.00 | 54 / 3 |
| minimum / daily | total | $29,500 (1 tie) | $229,700.00 | 74 / 3 | $53,000 (1 tie) | $372,000.00 | 54 / 3 |
| minimum / weekly | ongoing | $29,100 (1 tie) | $222,700.00 | 74 / 4 | $50,100 (8 ties) † | $381,500.00 | 54 / 3 |
| minimum / weekly | total | $29,100 (1 tie) | $224,200.00 | 74 / 4 | $50,100 (8 ties) † | $381,500.00 | 54 / 3 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $28,700 (1 tie) | $334,150.65 | 90 / 10 | $53,600 (1 tie) | $374,107.55 | 61 / 12 |
| maximum / monthly | total | $31,000 (2 ties) | $388,853.70 | 75 / 20 | $56,300 (1 tie) | $452,933.30 | 44 / 20 |
| maximum / daily | ongoing | $29,100 (1 tie) | $334,593.60 | 89 / 10 | $54,300 (1 tie) | $363,281.45 | 61 / 12 |
| maximum / daily | total | $31,300 (1 tie) | $394,811.15 | 74 / 20 | $56,700 (2 ties) | $451,517.90 | 44 / 20 |
| maximum / weekly | ongoing | $28,900 (1 tie) | $347,348.50 | 88 / 10 | $53,900 (1 tie) | $387,817.30 | 61 / 12 |
| maximum / weekly | total | $31,300 (1 tie) | $394,811.15 | 74 / 20 | $56,600 (3 ties) | $451,517.90 | 44 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $283,200.00 | 139 / 20 | $50,100 (13 ties) † | $307,250.00 | 59 / 20 |
| minimum / monthly | total | $27,500 (2 ties) | $439,014.00 | 73 / 20 | $50,100 (13 ties) † | $478,955.54 | 59 / 20 |
| minimum / daily | ongoing | $28,100 (1 tie) | $367,000.00 | 90 / 10 | $53,200 (1 tie) | $399,750.00 | 75 / 12 |
| minimum / daily | total | $28,100 (1 tie) | $368,500.00 | 90 / 10 | $53,200 (1 tie) | $400,923.65 | 75 / 12 |
| minimum / weekly | ongoing | $27,000 (1 tie) | $368,000.00 | 115 / 10 | $50,100 (13 ties) † | $425,000.00 | 88 / 12 |
| minimum / weekly | total | $27,000 (1 tie) | $368,000.00 | 115 / 10 | $50,100 (13 ties) † | $425,000.00 | 88 / 12 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,800 (1 tie) | $510,942.90 | 285 / 20 | $51,000 (1 tie) | $441,756.55 | 154 / 20 |
| maximum / monthly | total | $25,800 (1 tie) | $540,942.90 | 285 / 20 | $51,000 (1 tie) | $441,756.55 | 154 / 20 |
| maximum / daily | ongoing | $25,100 (1 tie) † | $624,674.85 | 569 / 20 | $50,100 (6 ties) † | $585,935.35 | 265 / 20 |
| maximum / daily | total | $25,100 (1 tie) † | $624,674.85 | 569 / 20 | $50,100 (6 ties) † | $585,935.35 | 265 / 20 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $665,420.55 | 531 / 20 | $51,100 (1 tie) | $551,666.75 | 234 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $665,420.55 | 531 / 20 | $51,100 (1 tie) | $551,666.75 | 234 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $356,000.00 | 185 / 20 | $50,100 (8 ties) † | $283,250.00 | 67 / 20 |
| minimum / monthly | total | $25,100 (7 ties) † | $509,740.80 | 185 / 20 | $50,100 (8 ties) † | $454,430.68 | 67 / 20 |
| minimum / daily | ongoing | $25,100 (7 ties) † | $467,700.00 | 329 / 20 | $50,100 (8 ties) † | $400,500.00 | 128 / 20 |
| minimum / daily | total | $25,100 (7 ties) † | $467,700.00 | 329 / 20 | $50,100 (8 ties) † | $400,500.00 | 128 / 20 |
| minimum / weekly | ongoing | $25,100 (7 ties) † | $462,900.00 | 248 / 20 | $50,100 (8 ties) † | $411,250.00 | 123 / 20 |
| minimum / weekly | total | $25,100 (7 ties) † | $462,900.00 | 248 / 20 | $50,100 (8 ties) † | $411,250.00 | 123 / 20 |

## $5,000 initial; $0/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / weekly; reserve $51,100 | $550,450.15 / $550,450.15 | 236 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / weekly; reserve $51,100 | $550,450.15 / $550,450.15 | 236 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $28,700 (1 tie) | $174,867.10 | 68 / 3 | $53,700 (1 tie) | $308,714.20 | 43 / 3 |
| maximum / monthly | total | $28,700 (1 tie) | $176,367.10 | 68 / 3 | $53,700 (1 tie) | $310,714.20 | 43 / 3 |
| maximum / daily | ongoing | $29,500 (1 tie) | $133,952.60 | 65 / 3 | $54,500 (1 tie) | $276,404.55 | 43 / 3 |
| maximum / daily | total | $31,600 (1 tie) | $173,754.30 | 58 / 13 | $54,500 (1 tie) | $279,667.85 | 43 / 3 |
| maximum / weekly | ongoing | $29,100 (1 tie) | $158,684.00 | 67 / 3 | $54,100 (1 tie) | $298,911.00 | 43 / 3 |
| maximum / weekly | total | $31,300 (1 tie) | $194,929.04 | 59 / 14 | $54,100 (1 tie) | $301,091.75 | 43 / 3 |
| minimum / monthly | ongoing | $26,700 (1 tie) | $173,700.00 | 79 / 16 | $50,100 (13 ties) † | $280,000.00 | 46 / 20 |
| minimum / monthly | total | $26,900 (1 tie) | $285,658.59 | 79 / 17 | $50,100 (13 ties) † | $449,929.83 | 46 / 20 |
| minimum / daily | ongoing | $28,000 (1 tie) | $218,200.00 | 79 / 4 | $53,000 (1 tie) | $373,000.00 | 50 / 3 |
| minimum / daily | total | $28,000 (1 tie) | $218,200.00 | 79 / 4 | $53,000 (1 tie) | $373,000.00 | 50 / 3 |
| minimum / weekly | ongoing | $27,600 (1 tie) | $217,700.00 | 79 / 4 | $50,100 (13 ties) † | $381,500.00 | 54 / 3 |
| minimum / weekly | total | $27,600 (1 tie) | $217,700.00 | 79 / 4 | $50,100 (13 ties) † | $381,500.00 | 54 / 3 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $26,800 (1 tie) | $306,267.50 | 176 / 10 | $51,200 (1 tie) | $340,067.10 | 115 / 12 |
| maximum / monthly | total | $31,000 (1 tie) | $318,928.35 | 67 / 20 | $56,100 (1 tie) | $395,487.40 | 39 / 20 |
| maximum / daily | ongoing | $29,100 (1 tie) | $264,300.95 | 93 / 10 | $51,500 (1 tie) | $371,052.40 | 138 / 5 |
| maximum / daily | total | $31,300 (1 tie) | $333,184.50 | 68 / 20 | $56,200 (1 tie) | $402,304.85 | 39 / 20 |
| maximum / weekly | ongoing | $27,100 (1 tie) | $333,157.60 | 197 / 6 | $52,100 (1 tie) | $395,060.75 | 118 / 5 |
| maximum / weekly | total | $27,100 (1 tie) | $334,331.25 | 197 / 6 | $56,300 (1 tie) | $399,822.60 | 39 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $294,700.00 | 164 / 20 | $53,700 (2 ties) | $237,250.00 | 43 / 20 |
| minimum / monthly | total | $25,100 (7 ties) † | $440,740.45 | 164 / 20 | $54,200 (1 tie) | $421,592.05 | 41 / 20 |
| minimum / daily | ongoing | $26,800 (1 tie) | $296,300.00 | 211 / 10 | $50,100 (13 ties) † | $345,250.00 | 115 / 12 |
| minimum / daily | total | $26,800 (1 tie) | $296,300.00 | 211 / 10 | $50,100 (13 ties) † | $345,250.00 | 115 / 12 |
| minimum / weekly | ongoing | $26,900 (1 tie) | $419,700.00 | 159 / 10 | $50,100 (13 ties) † | $454,500.00 | 92 / 12 |
| minimum / weekly | total | $26,900 (1 tie) | $419,700.00 | 159 / 10 | $50,100 (13 ties) † | $454,500.00 | 92 / 12 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,800 (1 tie) | $514,001.70 | 288 / 20 | $50,100 (17 ties) † | $-4,857.45 | 22 / 0 |
| maximum / monthly | total | $25,800 (1 tie) | $544,001.70 | 288 / 20 | $50,100 (17 ties) † | $-4,857.45 | 22 / 0 |
| maximum / daily | ongoing | $25,100 (1 tie) † | $629,288.00 | 575 / 20 | $50,100 (8 ties) † | $-4,981.40 | 65 / 0 |
| maximum / daily | total | $25,100 (1 tie) † | $629,288.00 | 575 / 20 | $50,100 (8 ties) † | $-4,981.40 | 65 / 0 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $670,285.60 | 539 / 20 | $51,100 (1 tie) | $550,450.15 | 236 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $670,285.60 | 539 / 20 | $51,100 (1 tie) | $550,450.15 | 236 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $379,600.00 | 167 / 20 | $50,100 (21 ties) † | $-5,000.00 | 22 / 0 |
| minimum / monthly | total | $25,100 (7 ties) † | $533,340.80 | 167 / 20 | $50,100 (21 ties) † | $-5,000.00 | 22 / 0 |
| minimum / daily | ongoing | $25,100 (7 ties) † | $471,000.00 | 335 / 20 | $50,100 (21 ties) † | $-5,000.00 | 58 / 0 |
| minimum / daily | total | $25,100 (7 ties) † | $471,000.00 | 335 / 20 | $50,100 (21 ties) † | $-5,000.00 | 58 / 0 |
| minimum / weekly | ongoing | $25,100 (7 ties) † | $466,700.00 | 254 / 20 | $50,100 (21 ties) † | $-5,000.00 | 56 / 0 |
| minimum / weekly | total | $25,100 (7 ties) † | $466,700.00 | 254 / 20 | $50,100 (21 ties) † | $-5,000.00 | 56 / 0 |

## $5,000 initial; $200/month

### Best complete tested bundles

| Objective | **25K — Policy and reserve** | **25K — Ongoing / total** | **25K — Bought / alive** | **50K — Policy and reserve** | **50K — Ongoing / total** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- |
| ongoing | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $603,595.55 / $603,595.55 | 283 / 20 |
| total | Monthly + replacements; maximum / weekly; reserve $25,100 | $670,285.60 / $670,285.60 | 539 / 20 | Monthly + replacements; maximum / daily; reserve $50,100 | $603,595.55 / $603,595.55 | 283 / 20 |

### monthly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $28,700 (1 tie) | $234,927.30 | 74 / 3 | $53,700 (1 tie) | $359,211.10 | 52 / 3 |
| maximum / monthly | total | $31,000 (3 ties) | $315,242.87 | 74 / 19 | $56,000 (14 ties) † | $456,799.27 | 48 / 20 |
| maximum / daily | ongoing | $29,500 (1 tie) | $229,009.60 | 74 / 3 | $54,100 (1 tie) | $350,760.95 | 53 / 3 |
| maximum / daily | total | $31,300 (1 tie) | $316,062.42 | 74 / 19 | $56,200 (15 ties) † | $456,799.27 | 48 / 20 |
| maximum / weekly | ongoing | $29,100 (1 tie) | $236,917.35 | 74 / 3 | $54,100 (1 tie) | $359,677.00 | 52 / 3 |
| maximum / weekly | total | $31,300 (1 tie) | $316,062.42 | 74 / 19 | $56,300 (14 ties) † | $456,799.27 | 48 / 20 |
| minimum / monthly | ongoing | $28,600 (1 tie) | $172,700.00 | 74 / 19 | $50,100 (8 ties) † | $279,000.00 | 50 / 20 |
| minimum / monthly | total | $28,600 (3 ties) | $316,742.87 | 74 / 19 | $53,600 (22 ties) † | $456,799.27 | 48 / 20 |
| minimum / daily | ongoing | $29,500 (1 tie) | $228,200.00 | 74 / 3 | $53,000 (1 tie) | $372,000.00 | 54 / 3 |
| minimum / daily | total | $29,500 (1 tie) | $229,700.00 | 74 / 3 | $53,000 (1 tie) | $372,000.00 | 54 / 3 |
| minimum / weekly | ongoing | $29,100 (1 tie) | $222,700.00 | 74 / 4 | $50,100 (8 ties) † | $381,500.00 | 54 / 3 |
| minimum / weekly | total | $29,100 (1 tie) | $224,200.00 | 74 / 4 | $50,100 (8 ties) † | $381,500.00 | 54 / 3 |

### weekly_one: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $28,700 (1 tie) | $340,958.70 | 114 / 10 | $53,700 (1 tie) | $382,451.60 | 81 / 12 |
| maximum / monthly | total | $31,000 (2 ties) | $421,134.00 | 94 / 20 | $56,100 (1 tie) | $469,771.40 | 58 / 20 |
| maximum / daily | ongoing | $29,100 (1 tie) | $346,362.90 | 113 / 10 | $54,100 (1 tie) | $388,221.60 | 85 / 12 |
| maximum / daily | total | $31,200 (1 tie) | $434,525.55 | 90 / 20 | $56,300 (1 tie) | $468,518.50 | 58 / 20 |
| maximum / weekly | ongoing | $27,100 (1 tie) | $337,336.30 | 196 / 6 | $52,100 (1 tie) | $395,060.75 | 118 / 5 |
| maximum / weekly | total | $31,300 (1 tie) | $428,256.50 | 91 / 20 | $56,300 (2 ties) | $467,454.75 | 58 / 20 |
| minimum / monthly | ongoing | $26,700 (1 tie) | $317,000.00 | 135 / 20 | $50,100 (13 ties) † | $328,500.00 | 70 / 20 |
| minimum / monthly | total | $26,800 (1 tie) | $482,045.22 | 130 / 20 | $50,100 (13 ties) † | $501,090.23 | 70 / 20 |
| minimum / daily | ongoing | $28,000 (1 tie) | $392,000.00 | 140 / 10 | $53,000 (1 tie) | $430,750.00 | 89 / 12 |
| minimum / daily | total | $28,000 (1 tie) | $392,000.00 | 140 / 10 | $53,000 (1 tie) | $430,750.00 | 89 / 12 |
| minimum / weekly | ongoing | $26,900 (1 tie) | $423,600.00 | 157 / 10 | $50,100 (13 ties) † | $454,500.00 | 92 / 12 |
| minimum / weekly | total | $26,900 (1 tie) | $423,600.00 | 157 / 10 | $50,100 (13 ties) † | $454,500.00 | 92 / 12 |

### monthly_current_slot_replacements: best reserve within each withdrawal policy

| Withdraw / checks | Objective | **25K — Reserve (ties)** | **25K — Score** | **25K — Bought / alive** | **50K — Reserve (ties)** | **50K — Score** | **50K — Bought / alive** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| maximum / monthly | ongoing | $25,800 (1 tie) | $514,001.70 | 288 / 20 | $50,100 (1 tie) † | $535,926.15 | 204 / 20 |
| maximum / monthly | total | $25,800 (1 tie) | $544,001.70 | 288 / 20 | $50,100 (1 tie) † | $535,926.15 | 204 / 20 |
| maximum / daily | ongoing | $25,100 (1 tie) † | $629,288.00 | 575 / 20 | $50,100 (6 ties) † | $603,595.55 | 283 / 20 |
| maximum / daily | total | $25,100 (1 tie) † | $629,288.00 | 575 / 20 | $50,100 (6 ties) † | $603,595.55 | 283 / 20 |
| maximum / weekly | ongoing | $25,100 (1 tie) † | $670,285.60 | 539 / 20 | $51,100 (1 tie) | $573,130.15 | 245 / 20 |
| maximum / weekly | total | $25,100 (1 tie) † | $670,285.60 | 539 / 20 | $51,100 (1 tie) | $573,130.15 | 245 / 20 |
| minimum / monthly | ongoing | $25,100 (7 ties) † | $379,600.00 | 167 / 20 | $50,100 (8 ties) † | $364,750.00 | 81 / 20 |
| minimum / monthly | total | $25,100 (7 ties) † | $533,340.80 | 167 / 20 | $50,100 (8 ties) † | $534,132.28 | 81 / 20 |
| minimum / daily | ongoing | $27,600 (1 tie) | $483,700.00 | 214 / 20 | $52,900 (1 tie) | $495,250.00 | 121 / 20 |
| minimum / daily | total | $27,600 (1 tie) | $483,700.00 | 214 / 20 | $52,900 (1 tie) | $495,250.00 | 121 / 20 |
| minimum / weekly | ongoing | $26,800 (1 tie) | $506,600.00 | 222 / 20 | $50,100 (13 ties) † | $514,500.00 | 142 / 20 |
| minimum / weekly | total | $26,800 (1 tie) | $506,600.00 | 222 / 20 | $50,100 (13 ties) † | $514,500.00 | 142 / 20 |

## Limits on interpreting a winner

A boundary tie warns that some equally best setting touches the tested limits; it can also mean all reserves produce the same failure path. A unique interior winner still does not prove a global optimum: untested intervals and other trade histories remain. Reserves selected on the same tape are subject to selection bias. Near-best results describe parameter sensitivity on this tape, not robustness to future markets. Selecting reserves separately measures adaptation; use matched rows for a fixed-policy account comparison. A higher ongoing score can come with fewer survivors and a lower total.
