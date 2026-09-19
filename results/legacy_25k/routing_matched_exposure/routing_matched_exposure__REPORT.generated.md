# Matched-exposure account routing

The full tape contains 12,658 trades and peaks at **5 simultaneous positions**. The historical mechanical ratio remains **K = 5R**. 24 saved full-period controls reproduced exactly.

Each pair has identical reference trade-copy demand, contract size, commission and withdrawal settings. Original purchase dates are frozen; each reference purchase provisions five routed seats. Instant paid seats would fill any shortage after deaths. All routed cases must fill 100% of requested copies. This is an ex-post counterfactual: the reference survival path determines the replay demand, so it is not a prospective live strategy.

**Resources are not matched.** Routed seats are externally financeable and the reference 20-live-account cap is relaxed. Costs below include every extra seat. The underlying purchase schedule is inherited, but physical account purchases differ. Additional funding is the minimum extra cash required on top of the original contribution schedule when routed receipts can be reinvested. It is separate from purchase costs. Net cash excludes owner contributions.

Same withdrawal rules apply per physical account, so dispersing profits changes eligibility, payout timing and retained balances. Terminal means a firm-permitted final request, not liquidation. Account failures may truncate realized trade P&L even with identical entry-copy demand. MAE/MFE remain per-trade extrema applied at exit; payouts during open trades and intratrade death timing retain that approximation. Working-order reservations are absent from the export. Five is a historical interval result, not a future/live-order capacity guarantee.

2023 starts are fresh-account sensitivity runs through the same final date, not independent validation: these policies were already selected using the wider dataset. No policy has been re-optimized.

## Fresh start in 2020

### Reference funding $1,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 97,993 | 58 / 19 | 41 | $224,400 | $77,887 | $302,287 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 97,993 | 290 / 290 | 0 | $152,500 | $4,500 | $157,000 | $46,400 | $26,500 |
| monthly_one / minimum_daily_31900 | round_robin | 97,993 | 290 / 146 | 164 | $-51,500 | $87,183 | $35,683 | $46,400 | $52,000 |
| monthly_one / maximum_weekly_31600 | reference | 97,993 | 58 / 19 | 41 | $232,440 | $66,606 | $299,046 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 97,993 | 290 / 290 | 0 | $174,021 | $57,202 | $231,223 | $46,400 | $26,028 |
| monthly_one / maximum_weekly_31600 | round_robin | 97,993 | 290 / 146 | 164 | $-50,473 | $90,183 | $39,710 | $46,400 | $50,077 |
| monthly_one / minimum_calendar_month_30000 | reference | 97,993 | 58 / 19 | 41 | $163,900 | $138,387 | $302,287 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 97,993 | 290 / 290 | 0 | $110,500 | $144,575 | $255,075 | $46,400 | $23,500 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 97,993 | 290 / 146 | 164 | $-32,500 | $97,617 | $65,117 | $46,400 | $37,000 |
| weekly_one / minimum_daily_31900 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |
| weekly_one / minimum_daily_31900 | round_robin | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |
| weekly_one / maximum_weekly_31600 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |
| weekly_one / minimum_calendar_month_30000 | reference | 1,443 | 5 / 5 | 5 | $-1,000 | $0 | $-1,000 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 1,443 | 25 / 25 | 0 | $-5,000 | $0 | $-5,000 | $4,000 | $4,000 |

### Reference funding $1,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 146,219 | 60 / 20 | 40 | $361,600 | $102,712 | $464,312 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 146,219 | 300 / 300 | 0 | $273,000 | $0 | $273,000 | $48,000 | $35,900 |
| monthly_one / minimum_daily_31900 | round_robin | 146,219 | 300 / 220 | 172 | $-42,500 | $151,685 | $109,185 | $48,000 | $47,200 |
| monthly_one / maximum_weekly_31600 | reference | 146,219 | 60 / 20 | 40 | $373,130 | $87,941 | $461,071 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 146,219 | 300 / 300 | 0 | $297,589 | $70,481 | $368,070 | $48,000 | $33,989 |
| monthly_one / maximum_weekly_31600 | round_robin | 146,219 | 300 / 220 | 172 | $-36,700 | $142,779 | $106,079 | $48,000 | $47,200 |
| monthly_one / minimum_calendar_month_30000 | reference | 146,219 | 60 / 20 | 40 | $270,000 | $194,312 | $464,312 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 146,219 | 300 / 300 | 0 | $196,500 | $197,763 | $394,263 | $48,000 | $30,400 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 146,219 | 300 / 220 | 172 | $500 | $167,663 | $168,163 | $48,000 | $46,700 |
| weekly_one / minimum_daily_31900 | reference | 178,247 | 75 / 20 | 55 | $449,800 | $100,882 | $550,682 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 178,247 | 375 / 375 | 0 | $317,000 | $518 | $317,518 | $60,000 | $66,600 |
| weekly_one / minimum_daily_31900 | round_robin | 178,247 | 375 / 255 | 251 | $-23,500 | $141,492 | $117,992 | $60,000 | $66,600 |
| weekly_one / maximum_weekly_31600 | reference | 178,068 | 75 / 20 | 55 | $460,919 | $89,763 | $550,682 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 178,068 | 375 / 375 | 0 | $357,276 | $102,109 | $459,385 | $60,000 | $66,600 |
| weekly_one / maximum_weekly_31600 | round_robin | 178,068 | 375 / 287 | 227 | $-10,782 | $173,130 | $162,348 | $60,000 | $66,600 |
| weekly_one / minimum_calendar_month_30000 | reference | 178,247 | 75 / 20 | 55 | $324,500 | $226,182 | $550,682 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 178,247 | 375 / 375 | 0 | $217,000 | $224,155 | $441,155 | $60,000 | $66,600 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 178,247 | 375 / 255 | 251 | $48,000 | $162,403 | $210,403 | $60,000 | $66,600 |

### Reference funding $5,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 145,406 | 59 / 20 | 39 | $361,800 | $102,712 | $464,512 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 145,406 | 295 / 295 | 0 | $278,500 | $0 | $278,500 | $47,200 | $39,500 |
| monthly_one / minimum_daily_31900 | round_robin | 145,406 | 295 / 185 | 160 | $-42,000 | $146,261 | $104,261 | $47,200 | $54,000 |
| monthly_one / maximum_weekly_31600 | reference | 145,406 | 59 / 20 | 39 | $373,330 | $87,941 | $461,271 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 145,406 | 295 / 295 | 0 | $301,019 | $56,965 | $357,984 | $47,200 | $37,789 |
| monthly_one / maximum_weekly_31600 | round_robin | 145,406 | 295 / 185 | 160 | $-37,707 | $147,761 | $110,054 | $47,200 | $54,000 |
| monthly_one / minimum_calendar_month_30000 | reference | 145,406 | 59 / 20 | 39 | $270,200 | $194,312 | $464,512 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 145,406 | 295 / 295 | 0 | $200,500 | $203,488 | $403,988 | $47,200 | $33,000 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 145,406 | 295 / 185 | 160 | $-8,500 | $169,542 | $161,042 | $47,200 | $52,000 |
| weekly_one / minimum_daily_31900 | reference | 187,188 | 75 / 20 | 55 | $443,000 | $101,527 | $544,527 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 187,188 | 375 / 375 | 0 | $330,500 | $1,087 | $331,587 | $60,000 | $70,000 |
| weekly_one / minimum_daily_31900 | round_robin | 187,188 | 375 / 264 | 220 | $-62,000 | $166,867 | $104,867 | $60,000 | $70,000 |
| weekly_one / maximum_weekly_31600 | reference | 187,287 | 76 / 20 | 56 | $453,736 | $90,591 | $544,326 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 187,287 | 380 / 380 | 0 | $361,977 | $75,493 | $437,470 | $60,800 | $71,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 187,287 | 380 / 265 | 257 | $31,519 | $176,752 | $208,271 | $60,800 | $71,000 |
| weekly_one / minimum_calendar_month_30000 | reference | 188,011 | 76 / 20 | 56 | $318,800 | $225,527 | $544,327 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 188,011 | 380 / 380 | 0 | $223,000 | $228,828 | $451,828 | $60,800 | $63,500 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 188,011 | 380 / 266 | 226 | $20,000 | $124,475 | $144,475 | $60,800 | $71,000 |

### Reference funding $5,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 146,219 | 60 / 20 | 40 | $361,600 | $102,712 | $464,312 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 146,219 | 300 / 300 | 0 | $273,000 | $0 | $273,000 | $48,000 | $31,900 |
| monthly_one / minimum_daily_31900 | round_robin | 146,219 | 300 / 220 | 172 | $-42,500 | $151,685 | $109,185 | $48,000 | $43,200 |
| monthly_one / maximum_weekly_31600 | reference | 146,219 | 60 / 20 | 40 | $373,130 | $87,941 | $461,071 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 146,219 | 300 / 300 | 0 | $297,589 | $70,481 | $368,070 | $48,000 | $29,989 |
| monthly_one / maximum_weekly_31600 | round_robin | 146,219 | 300 / 220 | 172 | $-36,700 | $142,779 | $106,079 | $48,000 | $43,200 |
| monthly_one / minimum_calendar_month_30000 | reference | 146,219 | 60 / 20 | 40 | $270,000 | $194,312 | $464,312 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 146,219 | 300 / 300 | 0 | $196,500 | $197,763 | $394,263 | $48,000 | $26,400 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 146,219 | 300 / 220 | 172 | $500 | $167,663 | $168,163 | $48,000 | $42,700 |
| weekly_one / minimum_daily_31900 | reference | 208,872 | 83 / 20 | 63 | $490,700 | $98,640 | $589,340 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 208,872 | 415 / 415 | 0 | $339,000 | $583 | $339,583 | $66,400 | $70,800 |
| weekly_one / minimum_daily_31900 | round_robin | 208,872 | 415 / 239 | 245 | $-58,000 | $190,345 | $132,345 | $66,400 | $70,800 |
| weekly_one / maximum_weekly_31600 | reference | 208,971 | 84 / 20 | 64 | $501,274 | $87,866 | $589,140 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 208,971 | 420 / 420 | 0 | $378,651 | $84,624 | $463,274 | $67,200 | $71,800 |
| weekly_one / maximum_weekly_31600 | round_robin | 208,971 | 420 / 297 | 259 | $-22,072 | $185,104 | $163,033 | $67,200 | $71,800 |
| weekly_one / minimum_calendar_month_30000 | reference | 209,074 | 84 / 20 | 64 | $362,700 | $226,440 | $589,140 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 209,074 | 420 / 420 | 0 | $240,000 | $234,799 | $474,799 | $67,200 | $71,300 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 209,074 | 420 / 266 | 277 | $112,000 | $261,347 | $373,347 | $67,200 | $70,800 |

## Fresh start in 2023

### Reference funding $1,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 43,639 | 33 / 12 | 23 | $87,400 | $41,814 | $129,214 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 43,639 | 165 / 165 | 0 | $58,000 | $1,500 | $59,500 | $26,400 | $6,500 |
| monthly_one / minimum_daily_31900 | round_robin | 43,639 | 165 / 95 | 100 | $-32,500 | $46,697 | $14,197 | $26,400 | $32,000 |
| monthly_one / maximum_weekly_31600 | reference | 43,639 | 33 / 12 | 23 | $91,356 | $34,617 | $125,973 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 43,639 | 165 / 165 | 0 | $67,134 | $23,590 | $90,723 | $26,400 | $6,179 |
| monthly_one / maximum_weekly_31600 | round_robin | 43,639 | 165 / 95 | 100 | $-31,108 | $43,697 | $12,589 | $26,400 | $32,000 |
| monthly_one / minimum_calendar_month_30000 | reference | 43,888 | 34 / 12 | 24 | $64,200 | $64,814 | $129,014 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 43,888 | 170 / 170 | 0 | $39,500 | $73,522 | $113,022 | $27,200 | $6,000 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 43,888 | 170 / 78 | 100 | $-9,000 | $50,867 | $41,867 | $27,200 | $15,500 |
| weekly_one / minimum_daily_31900 | reference | 95,753 | 36 / 20 | 16 | $233,800 | $85,032 | $318,832 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 95,753 | 180 / 180 | 0 | $192,000 | $20,487 | $212,487 | $28,800 | $17,000 |
| weekly_one / minimum_daily_31900 | round_robin | 95,753 | 182 / 146 | 114 | $3,600 | $85,056 | $88,656 | $29,200 | $31,400 |
| weekly_one / maximum_weekly_31600 | reference | 95,983 | 32 / 20 | 12 | $246,779 | $94,706 | $341,485 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 95,983 | 160 / 160 | 0 | $222,437 | $64,770 | $287,207 | $25,600 | $15,000 |
| weekly_one / maximum_weekly_31600 | round_robin | 95,983 | 193 / 146 | 133 | $46,015 | $52,411 | $98,426 | $32,200 | $31,400 |
| weekly_one / minimum_calendar_month_30000 | reference | 96,599 | 36 / 20 | 16 | $185,300 | $151,492 | $336,792 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 96,599 | 180 / 180 | 0 | $157,000 | $178,177 | $335,177 | $28,800 | $22,500 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 96,599 | 182 / 167 | 104 | $10,100 | $77,675 | $87,775 | $29,200 | $34,400 |

### Reference funding $1,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 215 / 215 | 0 | $105,000 | $1,500 | $106,500 | $34,400 | $13,100 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $33,600 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 215 / 215 | 0 | $121,524 | $45,081 | $166,605 | $34,400 | $12,779 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $33,600 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 215 / 215 | 0 | $78,500 | $110,166 | $188,666 | $34,400 | $11,800 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 215 / 120 | 138 | $-34,500 | $69,073 | $34,573 | $34,400 | $28,900 |
| weekly_one / minimum_daily_31900 | reference | 109,195 | 37 / 20 | 17 | $294,600 | $88,876 | $383,476 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 109,195 | 185 / 185 | 0 | $233,000 | $13,599 | $246,599 | $29,600 | $25,600 |
| weekly_one / minimum_daily_31900 | round_robin | 109,195 | 185 / 142 | 105 | $10,000 | $78,794 | $88,794 | $29,600 | $29,200 |
| weekly_one / maximum_weekly_31600 | reference | 109,418 | 34 / 20 | 14 | $307,330 | $94,706 | $402,036 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 109,418 | 170 / 170 | 0 | $265,805 | $68,591 | $334,396 | $27,200 | $25,074 |
| weekly_one / maximum_weekly_31600 | round_robin | 109,418 | 170 / 142 | 94 | $58,755 | $84,164 | $142,918 | $27,200 | $29,200 |
| weekly_one / minimum_calendar_month_30000 | reference | 109,800 | 36 / 20 | 16 | $220,800 | $180,836 | $401,636 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 109,800 | 180 / 180 | 0 | $179,000 | $187,902 | $366,902 | $28,800 | $24,800 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 109,800 | 180 / 153 | 85 | $27,500 | $147,056 | $174,556 | $28,800 | $31,200 |

### Reference funding $5,000 initially + $0/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 215 / 215 | 0 | $105,000 | $1,500 | $106,500 | $34,400 | $12,500 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $38,000 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 215 / 215 | 0 | $121,524 | $45,081 | $166,605 | $34,400 | $12,179 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $38,000 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 215 / 215 | 0 | $78,500 | $110,166 | $188,666 | $34,400 | $11,000 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 215 / 120 | 138 | $-34,500 | $69,073 | $34,573 | $34,400 | $32,500 |
| weekly_one / minimum_daily_31900 | reference | 122,512 | 40 / 20 | 20 | $315,500 | $89,192 | $404,692 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 122,512 | 200 / 200 | 0 | $259,000 | $8,343 | $267,343 | $32,000 | $30,500 |
| weekly_one / minimum_daily_31900 | round_robin | 122,512 | 200 / 144 | 106 | $18,500 | $146,556 | $165,056 | $32,000 | $32,000 |
| weekly_one / maximum_weekly_31600 | reference | 122,735 | 37 / 20 | 17 | $328,546 | $94,706 | $423,252 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 122,735 | 185 / 185 | 0 | $287,977 | $60,821 | $348,798 | $29,600 | $29,839 |
| weekly_one / maximum_weekly_31600 | round_robin | 122,735 | 185 / 144 | 104 | $63,419 | $152,525 | $215,944 | $29,600 | $32,000 |
| weekly_one / minimum_calendar_month_30000 | reference | 123,358 | 40 / 20 | 20 | $231,000 | $191,652 | $422,652 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 123,358 | 200 / 200 | 0 | $186,500 | $198,416 | $384,916 | $32,000 | $28,500 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 123,358 | 200 / 157 | 118 | $45,500 | $98,299 | $143,799 | $32,000 | $34,000 |

### Reference funding $5,000 initially + $200/month

| Purchases / withdrawal | Allocation | Copies | Accounts / peak live | Deaths | Ongoing net | Terminal receipt | Total net | Extra seat cost | Extra funding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| monthly_one / minimum_daily_31900 | reference | 66,129 | 43 / 16 | 29 | $151,400 | $62,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_daily_31900 | max_headroom | 66,129 | 215 / 215 | 0 | $105,000 | $1,500 | $106,500 | $34,400 | $9,100 |
| monthly_one / minimum_daily_31900 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $29,600 |
| monthly_one / maximum_weekly_31600 | reference | 66,129 | 43 / 16 | 29 | $157,480 | $53,582 | $211,061 | $0 | $0 |
| monthly_one / maximum_weekly_31600 | max_headroom | 66,129 | 215 / 215 | 0 | $121,524 | $45,081 | $166,605 | $34,400 | $8,779 |
| monthly_one / maximum_weekly_31600 | round_robin | 66,129 | 215 / 120 | 138 | $-43,000 | $76,573 | $33,573 | $34,400 | $29,600 |
| monthly_one / minimum_calendar_month_30000 | reference | 66,129 | 43 / 16 | 29 | $110,400 | $103,902 | $214,302 | $0 | $0 |
| monthly_one / minimum_calendar_month_30000 | max_headroom | 66,129 | 215 / 215 | 0 | $78,500 | $110,166 | $188,666 | $34,400 | $7,800 |
| monthly_one / minimum_calendar_month_30000 | round_robin | 66,129 | 215 / 120 | 138 | $-34,500 | $69,073 | $34,573 | $34,400 | $24,900 |
| weekly_one / minimum_daily_31900 | reference | 130,190 | 36 / 20 | 16 | $359,300 | $106,153 | $465,453 | $0 | $0 |
| weekly_one / minimum_daily_31900 | max_headroom | 130,190 | 180 / 180 | 0 | $284,000 | $0 | $284,000 | $28,800 | $28,800 |
| weekly_one / minimum_daily_31900 | round_robin | 130,190 | 180 / 173 | 91 | $61,500 | $82,693 | $144,193 | $28,800 | $28,800 |
| weekly_one / maximum_weekly_31600 | reference | 130,190 | 36 / 20 | 16 | $370,746 | $94,706 | $465,453 | $0 | $0 |
| weekly_one / maximum_weekly_31600 | max_headroom | 130,190 | 180 / 180 | 0 | $318,473 | $95,676 | $414,149 | $28,800 | $28,800 |
| weekly_one / maximum_weekly_31600 | round_robin | 130,190 | 180 / 173 | 91 | $95,007 | $69,097 | $164,104 | $28,800 | $28,800 |
| weekly_one / minimum_calendar_month_30000 | reference | 130,190 | 36 / 20 | 16 | $252,800 | $212,653 | $465,453 | $0 | $0 |
| weekly_one / minimum_calendar_month_30000 | max_headroom | 130,190 | 180 / 180 | 0 | $204,500 | $206,737 | $411,237 | $28,800 | $28,800 |
| weekly_one / minimum_calendar_month_30000 | round_robin | 130,190 | 180 / 173 | 97 | $103,000 | $71,414 | $174,414 | $28,800 | $28,800 |

## Evidence

`study.json` records resolved inputs and engine hashes; `comparison.csv` contains the paired metrics. Each case folder contains demand, per-account ledgers, payouts, purchases and every routed allocation. See the research note for interpretation.
