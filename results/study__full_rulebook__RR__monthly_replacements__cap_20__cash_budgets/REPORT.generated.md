# Monthly growth with earlier replacements

48 candidates; 24 monthly/weekly controls reproduce the existing purchase study exactly.

The main question is whether earlier replacement improves monthly buying under the same funding, live cap and withdrawal settings. The weekly control also changes initial growth and cohort dates. None of these comparisons is proof that replacement delay alone caused a cash difference.

## Policy definitions

Monthly-one and weekly-one retain their existing schedules. **Current-slot replacements** replaces deaths at the next midnight check. If the current month has no successful scheduled purchase yet, the first successful replacement fills the current month slot. If the scheduled purchase already happened, replacements do not affect next month. **Plus replacements** retains monthly purchases and buys additional replacements. Both retry pending replacements daily when unaffordable; failures create no slot debt. Multiple deaths can trigger multiple replacements, limited by cash and capacity. A replacement account that dies creates a new replacement obligation.

At the first-day monthly boundary, deaths are processed before purchases. A successful replacement fills the current slot, so no extra scheduled purchase is made that day. Multiple deaths may still receive multiple replacements. After a completed monthly purchase, later replacements never cancel future purchases. A skipped unaffordable monthly attempt expires as before, but a later successful replacement can fill that otherwise unused slot. Failed replacement attempts consume no slot. There are no purchases after terminal receipts. The former future-slot rule is retained only in archives/studies/monthly_replacements_future_slots.

## Matched withdrawal comparisons

### $1,000 initial; $0/month; daily_minimum_retain_31900

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | daily_minimum_retain_31900 | 58 | 17 | $11,600 | $224,400.00 | $302,287.21 | $303,287.21 |
| weekly_one | daily_minimum_retain_31900 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_current_slot_replacements | daily_minimum_retain_31900 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_plus_replacements | daily_minimum_retain_31900 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 7.6305 | never | 2385.896 | 70.995 | 2 | 0 |
| weekly_one | 0.1108 | never | 2385.896 | None | 5 | 0 |
| monthly_current_slot_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |
| monthly_plus_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |

### $1,000 initial; $0/month; weekly_excess_retain_31600

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | weekly_excess_retain_31600 | 58 | 17 | $11,600 | $232,440.45 | $299,046.10 | $300,046.10 |
| weekly_one | weekly_excess_retain_31600 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_current_slot_replacements | weekly_excess_retain_31600 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_plus_replacements | weekly_excess_retain_31600 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 7.6305 | never | 2385.896 | 70.995 | 2 | 0 |
| weekly_one | 0.1108 | never | 2385.896 | None | 5 | 0 |
| monthly_current_slot_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |
| monthly_plus_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |

### $1,000 initial; $0/month; monthly_minimum_retain_30000

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | monthly_minimum_retain_30000 | 58 | 17 | $11,600 | $163,900.00 | $302,287.21 | $303,287.21 |
| weekly_one | monthly_minimum_retain_30000 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_current_slot_replacements | monthly_minimum_retain_30000 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |
| monthly_plus_replacements | monthly_minimum_retain_30000 | 5 | 0 | $1,000 | $-1,000.00 | $-1,000.00 | $0.00 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 7.6305 | never | 2385.896 | 70.995 | 2 | 0 |
| weekly_one | 0.1108 | never | 2385.896 | None | 5 | 0 |
| monthly_current_slot_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |
| monthly_plus_replacements | 0.0566 | never | 2385.896 | 0.1204 | 3 | 0 |

### $1,000 initial; $200/month; daily_minimum_retain_31900

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | daily_minimum_retain_31900 | 60 | 20 | $12,000 | $361,600.00 | $464,311.75 | $480,911.75 |
| weekly_one | daily_minimum_retain_31900 | 75 | 20 | $15,000 | $449,800.00 | $550,681.87 | $567,281.87 |
| monthly_current_slot_replacements | daily_minimum_retain_31900 | 69 | 20 | $13,800 | $458,800.00 | $559,996.24 | $576,596.24 |
| monthly_plus_replacements | daily_minimum_retain_31900 | 67 | 20 | $13,400 | $466,200.00 | $567,276.77 | $583,876.77 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 13.9341 | 2022-09-26T00:00:00 | 1096.9 | 56.6667 | 0 | 0 |
| monthly_current_slot_replacements | 13.5156 | 2023-04-01T00:00:00 | 1187.28 | 31.3908 | 0 | 0 |
| monthly_plus_replacements | 13.631 | 2023-03-01T00:00:00 | 1155.0 | 32.6993 | 0 | 0 |

### $1,000 initial; $200/month; weekly_excess_retain_31600

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | weekly_excess_retain_31600 | 60 | 20 | $12,000 | $373,130.03 | $461,070.58 | $477,670.58 |
| weekly_one | weekly_excess_retain_31600 | 75 | 20 | $15,000 | $460,918.96 | $550,681.79 | $567,281.79 |
| monthly_current_slot_replacements | weekly_excess_retain_31600 | 69 | 20 | $13,800 | $471,237.28 | $559,996.16 | $576,596.16 |
| monthly_plus_replacements | weekly_excess_retain_31600 | 67 | 20 | $13,400 | $478,991.92 | $567,276.69 | $583,876.69 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 13.918 | 2022-09-26T00:00:00 | 1096.9 | 54.5619 | 0 | 0 |
| monthly_current_slot_replacements | 13.5156 | 2023-04-01T00:00:00 | 1187.28 | 31.3908 | 0 | 0 |
| monthly_plus_replacements | 13.631 | 2023-03-01T00:00:00 | 1155.0 | 32.6993 | 0 | 0 |

### $1,000 initial; $200/month; monthly_minimum_retain_30000

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | monthly_minimum_retain_30000 | 60 | 20 | $12,000 | $270,000.00 | $464,311.75 | $480,911.75 |
| weekly_one | monthly_minimum_retain_30000 | 75 | 20 | $15,000 | $324,500.00 | $550,681.87 | $567,281.87 |
| monthly_current_slot_replacements | monthly_minimum_retain_30000 | 69 | 20 | $13,800 | $332,200.00 | $559,996.24 | $576,596.24 |
| monthly_plus_replacements | monthly_minimum_retain_30000 | 67 | 20 | $13,400 | $338,100.00 | $567,276.77 | $583,876.77 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 13.9341 | 2022-09-26T00:00:00 | 1096.9 | 56.6667 | 0 | 0 |
| monthly_current_slot_replacements | 13.5156 | 2023-04-01T00:00:00 | 1187.28 | 31.3908 | 0 | 0 |
| monthly_plus_replacements | 13.631 | 2023-03-01T00:00:00 | 1155.0 | 32.6993 | 0 | 0 |

### $5,000 initial; $0/month; daily_minimum_retain_31900

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | daily_minimum_retain_31900 | 59 | 20 | $11,800 | $361,800.00 | $464,511.75 | $469,511.75 |
| weekly_one | daily_minimum_retain_31900 | 75 | 20 | $15,000 | $443,000.00 | $544,526.53 | $549,526.53 |
| monthly_current_slot_replacements | daily_minimum_retain_31900 | 94 | 20 | $18,800 | $476,400.00 | $577,343.23 | $582,343.23 |
| monthly_plus_replacements | daily_minimum_retain_31900 | 94 | 20 | $18,800 | $476,400.00 | $577,343.23 | $582,343.23 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.3647 | 2024-12-01T00:00:00 | 1796.0 | 61.7399 | 0 | 0 |
| weekly_one | 14.652 | 2022-10-10T00:00:00 | 1124.9 | 104.9418 | 0 | 0 |
| monthly_current_slot_replacements | 14.8393 | 2022-12-01T00:00:00 | 1065.556 | 38.9577 | 0 | 0 |
| monthly_plus_replacements | 14.8393 | 2022-12-01T00:00:00 | 1065.556 | 38.9577 | 0 | 0 |

### $5,000 initial; $0/month; weekly_excess_retain_31600

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | weekly_excess_retain_31600 | 59 | 20 | $11,800 | $373,330.03 | $461,270.58 | $466,270.58 |
| weekly_one | weekly_excess_retain_31600 | 76 | 20 | $15,200 | $453,735.95 | $544,326.46 | $549,326.46 |
| monthly_current_slot_replacements | weekly_excess_retain_31600 | 103 | 20 | $20,600 | $493,402.42 | $579,992.77 | $584,992.77 |
| monthly_plus_replacements | weekly_excess_retain_31600 | 101 | 20 | $20,200 | $497,520.26 | $583,768.08 | $588,768.08 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.3647 | 2024-12-01T00:00:00 | 1796.0 | 61.7399 | 0 | 0 |
| weekly_one | 14.6586 | 2022-10-10T00:00:00 | 1124.9 | 102.7862 | 0 | 0 |
| monthly_current_slot_replacements | 14.9004 | 2022-11-01T00:00:00 | 1036.156 | 34.4461 | 0 | 0 |
| monthly_plus_replacements | 14.9523 | 2022-10-01T00:00:00 | 1005.156 | 35.2866 | 0 | 0 |

### $5,000 initial; $0/month; monthly_minimum_retain_30000

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | monthly_minimum_retain_30000 | 59 | 20 | $11,800 | $270,200.00 | $464,511.75 | $469,511.75 |
| weekly_one | monthly_minimum_retain_30000 | 76 | 20 | $15,200 | $318,800.00 | $544,326.53 | $549,326.53 |
| monthly_current_slot_replacements | monthly_minimum_retain_30000 | 78 | 20 | $15,600 | $351,900.00 | $583,579.14 | $588,579.14 |
| monthly_plus_replacements | monthly_minimum_retain_30000 | 76 | 20 | $15,200 | $355,800.00 | $587,354.45 | $592,354.45 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.3647 | 2024-12-01T00:00:00 | 1796.0 | 61.7399 | 0 | 0 |
| weekly_one | 14.7138 | 2022-10-10T00:00:00 | 1124.9 | 102.6848 | 0 | 0 |
| monthly_current_slot_replacements | 15.0019 | 2022-11-01T00:00:00 | 1036.156 | 45.1215 | 0 | 0 |
| monthly_plus_replacements | 15.0538 | 2022-10-01T00:00:00 | 1005.156 | 46.7185 | 0 | 0 |

### $5,000 initial; $200/month; daily_minimum_retain_31900

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | daily_minimum_retain_31900 | 60 | 20 | $12,000 | $361,600.00 | $464,311.75 | $484,911.75 |
| weekly_one | daily_minimum_retain_31900 | 83 | 20 | $16,600 | $490,700.00 | $589,340.13 | $609,940.13 |
| monthly_current_slot_replacements | daily_minimum_retain_31900 | 91 | 20 | $18,200 | $503,600.00 | $603,593.42 | $624,193.42 |
| monthly_plus_replacements | daily_minimum_retain_31900 | 89 | 20 | $17,800 | $507,500.00 | $607,368.73 | $627,968.73 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 16.3776 | 2020-08-03T00:00:00 | 940.888 | 102.2657 | 0 | 0 |
| monthly_current_slot_replacements | 15.8229 | 2022-09-01T00:00:00 | 974.812 | 27.2404 | 0 | 0 |
| monthly_plus_replacements | 15.8493 | 2022-08-01T00:00:00 | 943.0 | 28.0182 | 0 | 0 |

### $5,000 initial; $200/month; weekly_excess_retain_31600

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | weekly_excess_retain_31600 | 60 | 20 | $12,000 | $373,130.03 | $461,070.58 | $481,670.58 |
| weekly_one | weekly_excess_retain_31600 | 84 | 20 | $16,800 | $501,273.61 | $589,140.00 | $609,740.00 |
| monthly_current_slot_replacements | weekly_excess_retain_31600 | 99 | 20 | $19,800 | $516,088.02 | $601,993.31 | $622,593.31 |
| monthly_plus_replacements | weekly_excess_retain_31600 | 97 | 20 | $19,400 | $520,205.86 | $605,768.62 | $626,368.62 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 16.3842 | 2020-08-03T00:00:00 | 940.888 | 100.4214 | 0 | 0 |
| monthly_current_slot_replacements | 15.8134 | 2022-09-01T00:00:00 | 974.812 | 24.7684 | 0 | 0 |
| monthly_plus_replacements | 15.8398 | 2022-08-01T00:00:00 | 943.0 | 25.4012 | 0 | 0 |

### $5,000 initial; $200/month; monthly_minimum_retain_30000

| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |
|---|---|---:|---:|---:|---:|---:|---:|
| monthly_one | monthly_minimum_retain_30000 | 60 | 20 | $12,000 | $270,000.00 | $464,311.75 | $484,911.75 |
| weekly_one | monthly_minimum_retain_30000 | 84 | 20 | $16,800 | $362,700.00 | $589,140.13 | $609,740.13 |
| monthly_current_slot_replacements | monthly_minimum_retain_30000 | 86 | 20 | $17,200 | $380,300.00 | $608,177.50 | $628,777.50 |
| monthly_plus_replacements | monthly_minimum_retain_30000 | 88 | 20 | $17,600 | $382,400.00 | $610,954.96 | $631,554.96 |

| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |
|---|---:|---|---:|---:|---:|---:|
| monthly_one | 11.4272 | 2024-12-01T00:00:00 | 1796.0 | 61.0719 | 0 | 0 |
| weekly_one | 16.392 | 2020-08-03T00:00:00 | 940.888 | 100.1312 | 0 | 0 |
| monthly_current_slot_replacements | 15.9113 | 2022-09-01T00:00:00 | 974.812 | 26.1095 | 0 | 0 |
| monthly_plus_replacements | 16.0646 | 2022-06-01T00:00:00 | 883.62 | 26.6551 | 0 | 0 |

## Reading the diagnostics

Average live accounts and days below cap integrate account births/deaths in event time from the common opening calendar-month boundary to tape end. They include ramp-up. Death-to-purchase waits pair each purchase with the oldest unmatched prior death (FIFO). For scheduled controls this is a descriptive vacancy measure, not a claim the purchase was caused by that death. Unmatched deaths are censored at the endpoint; their aggregate unresolved wait is in CSV, so a short matched mean alone cannot establish prompt replacement. Same-timestamp deaths are processed before purchases.

All results use the existing Legacy 25K rules, no processing delay, and one permitted terminal request. Net cash excludes contributions and deducts fees. These variants change replacement timing or expand buying; neither guarantees the same total purchases or cohort exposure as monthly-one. Historical in-sample results only.
