# Corrected routing: reuse capacity at matched exposure

The full tape contains 12,658 trades and peaks at **5 simultaneous positions**. The historical mechanical ratio remains **K = 5R**. 24 saved full-period controls reproduced exactly.

Each pair has identical reference trade-copy demand, contract size, commission and withdrawal settings. The pool starts empty. Each entry reuses all available seats and buys only max(0, requested copies minus free seats). Original purchase dates do not trigger routed purchases. Instant paid seats fill only the observed shortfall, including replacements after deaths. All routed cases must fill 100% of requested copies. This is an ex-post counterfactual: the reference survival path determines the replay demand, so it is not a prospective live strategy.

**Resources are not matched.** Routed seats are externally financeable and the reference 20-live-account cap is relaxed. Costs below include every extra seat. Reference demand is inherited; routed procurement is based solely on available capacity. Additional funding is the minimum extra cash required on top of the original contribution schedule when routed receipts can be reinvested. It is separate from purchase costs. Net cash excludes owner contributions.

Same withdrawal rules apply per physical account, so dispersing profits changes eligibility, payout timing and retained balances. Terminal means a firm-permitted final request, not liquidation. Account failures may truncate realized trade P&L even with identical entry-copy demand. MAE/MFE remain per-trade extrema applied at exit; payouts during open trades and intratrade death timing retain that approximation. Working-order reservations are absent from the export. Five is a historical interval result, not a future/live-order capacity guarantee.

2023 starts are fresh-account sensitivity runs through the same final date, not independent validation: these policies were already selected using the wider dataset. No policy has been re-optimized.

## Fresh start in 2020

### Reference funding $1,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 97,993 | 58 / 19 | 41 | $224,400 | $77,887 | $302,287 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 97,993 | 148 / 76 | 97 | $196,400 | $6,463 | $202,863 | $18,000 | $7,400 |
| monthly_one / minimum_daily_31900 | round_robin | 97,993 | 163 / 76 | 109 | $76,900 | $68,086 | $144,986 | $21,000 | $14,300 |
| monthly_one / maximum_weekly_31600 | reference | 97,993 | 58 / 19 | 41 | $232,440 | $66,606 | $299,046 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 97,993 | 148 / 76 | 97 | $213,286 | $51,043 | $264,329 | $18,000 | $6,207 |
| monthly_one / maximum_weekly_31600 | round_robin | 97,993 | 163 / 76 | 109 | $98,777 | $84,036 | $182,812 | $21,000 | $13,909 |
| monthly_one / minimum_calendar_month_30000 | reference | 97,993 | 58 / 19 | 41 | $163,900 | $138,387 | $302,287 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 97,993 | 148 / 76 | 97 | $149,400 | $152,559 | $301,959 | $18,000 | $4,200 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 97,993 | 163 / 76 | 109 | $101,900 | $135,216 | $237,116 | $21,000 | $12,000 |
| weekly_one / minimum_daily_31900 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 1,443 | 15 / 15 | 0 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |
| weekly_one / minimum_daily_31900 | round_robin | 1,443 | 15 / 15 | 5 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |
| weekly_one / maximum_weekly_31600 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 1,443 | 15 / 15 | 0 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 1,443 | 15 / 15 | 5 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |
| weekly_one / minimum_calendar_month_30000 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 1,443 | 15 / 15 | 0 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 1,443 | 15 / 15 | 5 | $-3,000 | $0 | $-3,000 | $2,000 | $2,000 |

### Reference funding $1,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 146,219 | 60 / 20 | 40 | $361,600 | $102,712 | $464,312 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 146,219 | 144 / 80 | 103 | $333,200 | $0 | $333,200 | $16,800 | $5,400 |
| monthly_one / minimum_daily_31900 | round_robin | 146,219 | 180 / 80 | 103 | $147,500 | $106,492 | $253,992 | $24,000 | $14,600 |
| monthly_one / maximum_weekly_31600 | reference | 146,219 | 60 / 20 | 40 | $373,130 | $87,941 | $461,071 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 146,219 | 163 / 80 | 103 | $354,030 | $69,545 | $423,576 | $20,600 | $4,898 |
| monthly_one / maximum_weekly_31600 | round_robin | 146,219 | 180 / 80 | 103 | $181,820 | $139,620 | $321,441 | $24,000 | $14,638 |
| monthly_one / minimum_calendar_month_30000 | reference | 146,219 | 60 / 20 | 40 | $270,000 | $194,312 | $464,312 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 146,219 | 143 / 80 | 63 | $246,900 | $204,832 | $451,732 | $16,600 | $4,200 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 146,219 | 193 / 80 | 133 | $176,400 | $47,438 | $223,838 | $26,600 | $8,300 |
| weekly_one / minimum_daily_31900 | reference | 178,247 | 75 / 20 | 55 | $449,800 | $100,882 | $550,682 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 178,247 | 121 / 100 | 21 | $383,800 | $0 | $383,800 | $9,200 | $11,600 |
| weekly_one / minimum_daily_31900 | round_robin | 178,247 | 183 / 100 | 103 | $202,900 | $211,694 | $414,594 | $21,600 | $26,300 |
| weekly_one / maximum_weekly_31600 | reference | 178,068 | 75 / 20 | 55 | $460,919 | $89,763 | $550,682 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 178,068 | 121 / 100 | 50 | $410,952 | $68,032 | $478,985 | $9,200 | $11,600 |
| weekly_one / maximum_weekly_31600 | round_robin | 178,068 | 202 / 100 | 113 | $162,874 | $148,802 | $311,676 | $25,400 | $20,672 |
| weekly_one / minimum_calendar_month_30000 | reference | 178,247 | 75 / 20 | 55 | $324,500 | $226,182 | $550,682 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 178,247 | 121 / 100 | 21 | $277,800 | $235,645 | $513,445 | $9,200 | $11,600 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 178,247 | 223 / 100 | 163 | $263,400 | $105,397 | $368,797 | $29,600 | $22,500 |

### Reference funding $5,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 145,406 | 59 / 20 | 39 | $361,800 | $102,712 | $464,512 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 145,406 | 143 / 80 | 87 | $331,900 | $0 | $331,900 | $16,800 | $9,400 |
| monthly_one / minimum_daily_31900 | round_robin | 145,406 | 189 / 80 | 129 | $149,700 | $91,156 | $240,856 | $26,000 | $20,000 |
| monthly_one / maximum_weekly_31600 | reference | 145,406 | 59 / 20 | 39 | $373,330 | $87,941 | $461,271 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 145,406 | 143 / 80 | 103 | $354,983 | $74,584 | $429,567 | $16,800 | $7,800 |
| monthly_one / maximum_weekly_31600 | round_robin | 145,406 | 197 / 80 | 137 | $176,870 | $87,082 | $263,952 | $27,600 | $17,879 |
| monthly_one / minimum_calendar_month_30000 | reference | 145,406 | 59 / 20 | 39 | $270,200 | $194,312 | $464,512 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 145,406 | 143 / 80 | 63 | $247,400 | $202,157 | $449,557 | $16,800 | $7,800 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 145,406 | 193 / 80 | 130 | $169,400 | $94,721 | $264,121 | $26,800 | $12,700 |
| weekly_one / minimum_daily_31900 | reference | 187,188 | 75 / 20 | 55 | $443,000 | $101,527 | $544,527 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 187,188 | 131 / 100 | 71 | $379,300 | $0 | $379,300 | $11,200 | $13,200 |
| weekly_one / minimum_daily_31900 | round_robin | 187,188 | 210 / 100 | 124 | $108,500 | $184,906 | $293,406 | $27,000 | $35,500 |
| weekly_one / maximum_weekly_31600 | reference | 187,287 | 76 / 20 | 56 | $453,736 | $90,591 | $544,326 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 187,287 | 120 / 100 | 75 | $409,291 | $75,842 | $485,134 | $8,800 | $14,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 187,287 | 200 / 100 | 120 | $252,499 | $193,674 | $446,173 | $24,800 | $29,552 |
| weekly_one / minimum_calendar_month_30000 | reference | 188,011 | 76 / 20 | 56 | $318,800 | $225,527 | $544,327 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 188,011 | 115 / 100 | 15 | $280,500 | $225,664 | $506,164 | $7,800 | $9,000 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 188,011 | 232 / 100 | 171 | $259,100 | $106,437 | $365,537 | $31,200 | $20,800 |

### Reference funding $5,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 146,219 | 60 / 20 | 40 | $361,600 | $102,712 | $464,312 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 146,219 | 144 / 80 | 103 | $333,200 | $0 | $333,200 | $16,800 | $1,400 |
| monthly_one / minimum_daily_31900 | round_robin | 146,219 | 180 / 80 | 103 | $147,500 | $106,492 | $253,992 | $24,000 | $10,600 |
| monthly_one / maximum_weekly_31600 | reference | 146,219 | 60 / 20 | 40 | $373,130 | $87,941 | $461,071 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 146,219 | 163 / 80 | 103 | $354,030 | $69,545 | $423,576 | $20,600 | $898 |
| monthly_one / maximum_weekly_31600 | round_robin | 146,219 | 180 / 80 | 103 | $181,820 | $139,620 | $321,441 | $24,000 | $10,638 |
| monthly_one / minimum_calendar_month_30000 | reference | 146,219 | 60 / 20 | 40 | $270,000 | $194,312 | $464,312 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 146,219 | 143 / 80 | 63 | $246,900 | $204,832 | $451,732 | $16,600 | $200 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 146,219 | 193 / 80 | 133 | $176,400 | $47,438 | $223,838 | $26,600 | $4,300 |
| weekly_one / minimum_daily_31900 | reference | 208,872 | 83 / 20 | 63 | $490,700 | $98,640 | $589,340 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 208,872 | 110 / 100 | 10 | $434,000 | $0 | $434,000 | $5,400 | $9,400 |
| weekly_one / minimum_daily_31900 | round_robin | 208,872 | 222 / 100 | 134 | $185,100 | $192,260 | $377,360 | $27,800 | $28,100 |
| weekly_one / maximum_weekly_31600 | reference | 208,971 | 84 / 20 | 64 | $501,274 | $87,866 | $589,140 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 208,971 | 120 / 100 | 20 | $468,100 | $84,602 | $552,702 | $7,200 | $9,400 |
| weekly_one / maximum_weekly_31600 | round_robin | 208,971 | 217 / 100 | 137 | $327,738 | $235,571 | $563,310 | $26,600 | $21,033 |
| weekly_one / minimum_calendar_month_30000 | reference | 209,074 | 84 / 20 | 64 | $362,700 | $226,440 | $589,140 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 209,074 | 120 / 100 | 20 | $316,000 | $240,020 | $556,020 | $7,200 | $9,400 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 209,074 | 232 / 100 | 161 | $338,600 | $208,585 | $547,185 | $29,600 | $15,200 |

## Fresh start in 2023

### Reference funding $1,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 43,639 | 33 / 12 | 23 | $87,400 | $41,814 | $129,214 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 43,639 | 87 / 48 | 57 | $77,600 | $1,500 | $79,100 | $10,800 | $3,000 |
| monthly_one / minimum_daily_31900 | round_robin | 43,639 | 76 / 48 | 38 | $300 | $30,915 | $31,215 | $8,600 | $8,800 |
| monthly_one / maximum_weekly_31600 | reference | 43,639 | 33 / 12 | 23 | $91,356 | $34,617 | $125,973 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 43,639 | 87 / 48 | 57 | $90,976 | $40,535 | $131,511 | $10,800 | $3,000 |
| monthly_one / maximum_weekly_31600 | round_robin | 43,639 | 76 / 48 | 38 | $9,988 | $21,000 | $30,988 | $8,600 | $8,251 |
| monthly_one / minimum_calendar_month_30000 | reference | 43,888 | 34 / 12 | 24 | $64,200 | $64,814 | $129,014 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 43,888 | 85 / 48 | 55 | $59,000 | $74,811 | $133,811 | $10,200 | $3,000 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 43,888 | 90 / 48 | 60 | $30,500 | $40,398 | $70,898 | $11,200 | $7,000 |
| weekly_one / minimum_daily_31900 | reference | 95,753 | 36 / 20 | 16 | $233,800 | $85,032 | $318,832 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 95,753 | 160 / 80 | 100 | $216,000 | $8,375 | $224,375 | $24,800 | $5,800 |
| weekly_one / minimum_daily_31900 | round_robin | 95,753 | 134 / 80 | 63 | $27,700 | $73,006 | $100,706 | $19,600 | $19,800 |
| weekly_one / maximum_weekly_31600 | reference | 95,983 | 32 / 20 | 12 | $246,779 | $94,706 | $341,485 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 95,983 | 160 / 80 | 100 | $240,285 | $83,992 | $324,277 | $25,600 | $5,270 |
| weekly_one / maximum_weekly_31600 | round_robin | 95,983 | 139 / 80 | 71 | $50,659 | $52,500 | $103,159 | $21,400 | $19,800 |
| weekly_one / minimum_calendar_month_30000 | reference | 96,599 | 36 / 20 | 16 | $185,300 | $151,492 | $336,792 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 96,599 | 160 / 80 | 100 | $171,500 | $183,542 | $355,042 | $24,800 | $4,900 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 96,599 | 212 / 80 | 152 | $79,600 | $72,848 | $152,448 | $35,200 | $16,800 |

### Reference funding $1,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 117 / 64 | 75 | $137,600 | $1,500 | $139,100 | $14,800 | $4,400 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 144 / 64 | 97 | $68,200 | $61,498 | $129,698 | $20,200 | $10,700 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 117 / 64 | 75 | $151,582 | $48,906 | $200,488 | $14,800 | $4,400 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 144 / 64 | 96 | $85,900 | $78,711 | $164,611 | $20,200 | $9,048 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 117 / 64 | 75 | $102,100 | $117,436 | $219,536 | $14,800 | $4,400 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 154 / 64 | 112 | $93,700 | $59,236 | $152,936 | $22,200 | $6,300 |
| weekly_one / minimum_daily_31900 | reference | 109,195 | 37 / 20 | 17 | $294,600 | $88,876 | $383,476 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 109,195 | 120 / 80 | 80 | $266,000 | $1,500 | $267,500 | $16,600 | $8,400 |
| weekly_one / minimum_daily_31900 | round_robin | 109,195 | 181 / 80 | 121 | $94,300 | $131,188 | $225,488 | $28,800 | $14,800 |
| weekly_one / maximum_weekly_31600 | reference | 109,418 | 34 / 20 | 14 | $307,330 | $94,706 | $402,036 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 109,418 | 120 / 80 | 40 | $296,356 | $85,189 | $381,546 | $17,200 | $8,400 |
| weekly_one / maximum_weekly_31600 | round_robin | 109,418 | 177 / 80 | 115 | $110,859 | $131,935 | $242,794 | $28,600 | $14,800 |
| weekly_one / minimum_calendar_month_30000 | reference | 109,800 | 36 / 20 | 16 | $220,800 | $180,836 | $401,636 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 109,800 | 120 / 80 | 40 | $201,000 | $195,058 | $396,058 | $16,800 | $8,400 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 109,800 | 137 / 80 | 70 | $90,600 | $128,100 | $218,700 | $20,200 | $14,000 |

### Reference funding $5,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 117 / 64 | 75 | $137,600 | $1,500 | $139,100 | $14,800 | $2,200 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 144 / 64 | 97 | $68,200 | $61,498 | $129,698 | $20,200 | $11,900 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 117 / 64 | 75 | $151,582 | $48,906 | $200,488 | $14,800 | $2,200 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 144 / 64 | 96 | $85,900 | $78,711 | $164,611 | $20,200 | $10,448 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 117 / 64 | 75 | $102,100 | $117,436 | $219,536 | $14,800 | $2,000 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 154 / 64 | 112 | $93,700 | $59,236 | $152,936 | $22,200 | $6,900 |
| weekly_one / minimum_daily_31900 | reference | 122,512 | 40 / 20 | 20 | $315,500 | $89,192 | $404,692 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 122,512 | 130 / 95 | 50 | $279,000 | $6,856 | $285,856 | $18,000 | $14,000 |
| weekly_one / minimum_daily_31900 | round_robin | 122,512 | 153 / 95 | 93 | $131,400 | $92,691 | $224,091 | $22,600 | $15,800 |
| weekly_one / maximum_weekly_31600 | reference | 122,735 | 37 / 20 | 17 | $328,546 | $94,706 | $423,252 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 122,735 | 130 / 95 | 50 | $312,006 | $84,019 | $396,024 | $18,600 | $14,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 122,735 | 158 / 95 | 98 | $135,643 | $157,919 | $293,562 | $24,200 | $15,800 |
| weekly_one / minimum_calendar_month_30000 | reference | 123,358 | 40 / 20 | 20 | $231,000 | $191,652 | $422,652 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 123,358 | 115 / 95 | 35 | $211,000 | $203,402 | $414,402 | $15,000 | $14,000 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 123,358 | 129 / 95 | 66 | $121,200 | $98,076 | $219,276 | $17,800 | $15,100 |

### Reference funding $5,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 117 / 64 | 75 | $137,600 | $1,500 | $139,100 | $14,800 | $400 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 144 / 64 | 97 | $68,200 | $61,498 | $129,698 | $20,200 | $6,700 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 117 / 64 | 75 | $151,582 | $48,906 | $200,488 | $14,800 | $400 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 144 / 64 | 96 | $85,900 | $78,711 | $164,611 | $20,200 | $5,048 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 117 / 64 | 75 | $102,100 | $117,436 | $219,536 | $14,800 | $400 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 154 / 64 | 112 | $93,700 | $59,236 | $152,936 | $22,200 | $2,300 |
| weekly_one / minimum_daily_31900 | reference | 130,190 | 36 / 20 | 16 | $359,300 | $106,153 | $465,453 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 130,190 | 120 / 100 | 60 | $308,000 | $0 | $308,000 | $16,800 | $13,400 |
| weekly_one / minimum_daily_31900 | round_robin | 130,190 | 108 / 100 | 34 | $99,400 | $120,732 | $220,132 | $14,400 | $13,400 |
| weekly_one / maximum_weekly_31600 | reference | 130,190 | 36 / 20 | 16 | $370,746 | $94,706 | $465,453 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 130,190 | 120 / 100 | 60 | $342,570 | $87,856 | $430,426 | $16,800 | $13,400 |
| weekly_one / maximum_weekly_31600 | round_robin | 130,190 | 108 / 100 | 34 | $119,013 | $159,751 | $278,764 | $14,400 | $13,400 |
| weekly_one / minimum_calendar_month_30000 | reference | 130,190 | 36 / 20 | 16 | $252,800 | $212,653 | $465,453 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 130,190 | 100 / 100 | 1 | $227,500 | $212,787 | $440,287 | $12,800 | $13,400 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 130,190 | 145 / 100 | 77 | $136,000 | $91,499 | $227,499 | $21,800 | $13,400 |

## Evidence

`study.json` records resolved inputs and engine hashes; `comparison.csv` contains the paired metrics. Each case folder contains demand, per-account ledgers, payouts, purchases and every routed allocation. See the research note for interpretation.
