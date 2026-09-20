# RR composition, group count and reserve ladders: complete comparisons

730 historical runs. 130 prior controls reproduced; 42,311,067 trade copies checked. Core engine unchanged.

No arm or reserve value was changed after results were observed. Primary daily minimum / $6,800 mean target and March daily maximum / $5,700 mean target have different frozen evaluation-supply policies. Cash excludes terminal withdrawals and owner contributions.

## Frozen arms

| Arm | RR groups | RR range | Reserve offsets |
|---|---:|---|---|
| rr_1.00 | 1 | 1.00–1.00 | $0 to $0 (1 targets) |
| wide4 | 4 | 0.50–3.50 | $0 to $0 (1 targets) |
| center4 | 4 | 1.25–2.75 | $0 to $0 (1 targets) |
| edge4 | 4 | 0.50–3.50 | $0 to $0 (1 targets) |
| without050 | 4 | 0.75–3.50 | $0 to $0 (1 targets) |
| extremes2 | 2 | 0.50–3.50 | $0 to $0 (1 targets) |
| grid5 | 5 | 0.50–3.50 | $0 to $0 (1 targets) |
| grid10 | 10 | 0.50–3.50 | $0 to $0 (1 targets) |
| grid20 | 20 | 0.50–3.50 | $0 to $0 (1 targets) |
| ladder4 | 1 | 1.00–1.00 | $-1,500 to $1,500 (4 targets) |
| ladder20 | 1 | 1.00–1.00 | $-1,500 to $1,500 (20 targets) |
| uniform_low | 1 | 1.00–1.00 | $-1,500 to $-1,500 (1 targets) |
| uniform_high | 1 | 1.00–1.00 | $1,500 to $1,500 (1 targets) |
| grid20_reverse | 20 | 0.50–3.50 | $0 to $0 (1 targets) |
| ladder20_reverse | 1 | 1.00–1.00 | $-1,500 to $1,500 (20 targets) |

center4 has half the wide4 range; edge4 keeps endpoints, count and mean fixed. without050 is a single-constituent ablation that also changes mean/range. Group-count contrasts necessarily change constituents. Reverse arms change assignment order only.

## Primary operating: continuity across starts

Vectors are 2020 / 2021 / 2022 / 2023 / 2024 / 2025; histories overlap and are not independent samples.

| Arm | Wipeouts by start | Max same-signal deaths by start | Possible 20-day cluster by start |
|---|---|---|---|
| rr_1.00 | 2 / 2 / 2 / 1 / 0 / 1 | 7 / 5 / 5 / 5 / 2 / 2 | 13 / 8 / 6 / 6 / 7 / 8 |
| wide4 | 0 / 0 / 0 / 0 / 0 / 0 | 3 / 4 / 3 / 4 / 2 / 1 | 7 / 10 / 7 / 6 / 3 / 3 |
| center4 | 2 / 0 / 1 / 0 / 0 / 0 | 5 / 6 / 2 / 1 / 2 / 1 | 8 / 8 / 6 / 5 / 5 / 2 |
| edge4 | 0 / 0 / 0 / 1 / 0 / 0 | 4 / 4 / 2 / 2 / 3 / 1 | 11 / 11 / 7 / 7 / 8 / 4 |
| without050 | 2 / 0 / 1 / 0 / 0 / 0 | 4 / 4 / 3 / 4 / 2 / 1 | 9 / 8 / 8 / 6 / 3 / 4 |
| extremes2 | 0 / 0 / 0 / 1 / 0 / 0 | 7 / 6 / 5 / 3 / 2 / 1 | 12 / 11 / 9 / 6 / 6 / 2 |
| grid5 | 0 / 0 / 0 / 1 / 0 / 0 | 3 / 3 / 2 / 2 / 2 / 1 | 8 / 8 / 5 / 5 / 5 / 5 |
| grid10 | 0 / 1 / 0 / 1 / 0 / 0 | 3 / 4 / 1 / 2 / 1 / 1 | 6 / 7 / 5 / 6 / 5 / 4 |
| grid20 | 0 / 1 / 0 / 1 / 0 / 0 | 4 / 3 / 2 / 2 / 2 / 2 | 6 / 6 / 6 / 6 / 3 / 7 |
| ladder4 | 2 / 2 / 2 / 1 / 0 / 1 | 7 / 5 / 5 / 5 / 2 / 2 | 13 / 8 / 7 / 9 / 9 / 8 |
| ladder20 | 2 / 2 / 2 / 1 / 0 / 1 | 7 / 5 / 5 / 5 / 2 / 2 | 13 / 8 / 7 / 10 / 12 / 8 |
| uniform_low | 3 / 3 / 3 / 1 / 0 / 1 | 8 / 10 / 10 / 7 / 4 / 2 | 20 / 20 / 20 / 18 / 15 / 8 |
| uniform_high | 2 / 2 / 2 / 1 / 0 / 1 | 7 / 5 / 5 / 5 / 2 / 2 | 13 / 8 / 6 / 6 / 7 / 8 |
| grid20_reverse | 2 / 2 / 2 / 1 / 0 / 0 | 3 / 4 / 2 / 2 / 2 / 1 | 7 / 6 / 5 / 6 / 5 / 3 |
| ladder20_reverse | 2 / 2 / 2 / 1 / 0 / 1 | 7 / 5 / 5 / 5 / 2 / 2 | 13 / 8 / 6 / 6 / 7 / 8 |

Wipeout counts include small startup books. `wipeout_events.csv` records the live count before the final loss, the preceding 20-calendar-day peak, the lifetime peak reached before each episode, and the time until reopening. A one-seat final loss can follow an earlier cluster, so the last-seat count alone is insufficient.

### Empty duration and startup context, primary operating

| Arm | Total empty days across six overlapping starts | Wipeouts before ever reaching five PAs | Other wipeouts |
|---|---:|---:|---:|
| rr_1.00 | 101.52 | 4 | 4 |
| wide4 | 0.00 | 0 | 0 |
| center4 | 56.06 | 3 | 0 |
| edge4 | 47.23 | 0 | 1 |
| without050 | 20.18 | 3 | 0 |
| extremes2 | 48.09 | 0 | 1 |
| grid5 | 8.17 | 0 | 1 |
| grid10 | 65.24 | 1 | 1 |
| grid20 | 73.53 | 1 | 1 |
| ladder4 | 101.52 | 4 | 4 |
| ladder20 | 101.52 | 4 | 4 |
| uniform_low | 123.00 | 4 | 7 |
| uniform_high | 101.52 | 4 | 4 |
| grid20_reverse | 75.84 | 4 | 3 |
| ladder20_reverse | 101.52 | 4 | 4 |

## Primary operating: 2021–2025 paired comparisons

Counts below are descriptive comparisons with RR1 across five overlapping starts. Cash ranges contain paired cash differences, not independent expected returns.

| Arm | Starts with no wipeout | Lower / equal / higher 20-day cluster | Cash difference range |
|---|---:|---|---:|
| rr_1.00 | 1/5 | 0 / 5 / 0 | $0 to $0 |
| wide4 | 5/5 | 2 / 1 / 2 | $-18,268 to $23,014 |
| center4 | 4/5 | 3 / 2 / 0 | $4,896 to $32,717 |
| edge4 | 4/5 | 1 / 0 / 4 | $-46,153 to $8,646 |
| without050 | 4/5 | 2 / 2 / 1 | $4,267 to $19,573 |
| extremes2 | 4/5 | 2 / 1 / 2 | $-75,605 to $13,370 |
| grid5 | 4/5 | 4 / 1 / 0 | $-26,313 to $28,837 |
| grid10 | 3/5 | 4 / 1 / 0 | $3,514 to $57,007 |
| grid20 | 3/5 | 3 / 2 / 0 | $2,132 to $40,618 |
| ladder4 | 1/5 | 0 / 2 / 3 | $-7,120 to $526 |
| ladder20 | 1/5 | 0 / 2 / 3 | $-7,962 to $3,526 |
| uniform_low | 1/5 | 0 / 1 / 4 | $2,000 to $10,123 |
| uniform_high | 1/5 | 0 / 5 / 0 | $-30,000 to $0 |
| grid20_reverse | 2/5 | 4 / 1 / 0 | $18,304 to $33,821 |
| ladder20_reverse | 1/5 | 0 / 5 / 0 | $-8,500 to $0 |

## Group count: 2023 isolation and operating

A one-account RR group can lose only one copier, but several groups can lose on the same signal. A full copier-group loss means all actual copiers of that signal in that group died; it does not mean all nominal seats were present or exposed.

| Phase | Arm | Mean occupied groups on live days | Within-group peak | Portfolio signal peak | Most groups losing on one signal | Full copier-group loss events / group loss events | Possible 20-day cluster |
|---|---|---:|---:|---:|---:|---:|---:|
| isolation | rr_1.00 | 1.00 | 0 | 0 | 0 | 0 / 0 | 0 |
| isolation | extremes2 | 1.05 | 10 | 10 | 1 | 1 / 1 | 10 |
| isolation | wide4 | 3.05 | 5 | 5 | 1 | 1 / 1 | 5 |
| isolation | grid5 | 4.05 | 4 | 4 | 1 | 1 / 1 | 4 |
| isolation | grid10 | 9.05 | 2 | 2 | 1 | 1 / 1 | 2 |
| isolation | grid20 | 18.28 | 1 | 1 | 1 | 2 / 2 | 1 |
| isolation | grid20_reverse | 18.28 | 1 | 1 | 1 | 2 / 2 | 1 |
| isolation | ladder4 | 3.83 | 5 | 5 | 1 | 2 / 2 | 10 |
| isolation | ladder20 | 19.42 | 1 | 3 | 3 | 7 / 7 | 7 |
| operating | rr_1.00 | 1.00 | 5 | 5 | 1 | 1 / 14 | 6 |
| operating | extremes2 | 1.96 | 3 | 3 | 2 | 2 / 24 | 6 |
| operating | wide4 | 3.70 | 2 | 4 | 4 | 3 / 26 | 6 |
| operating | grid5 | 4.58 | 2 | 2 | 2 | 5 / 25 | 5 |
| operating | grid10 | 8.47 | 1 | 2 | 2 | 8 / 15 | 6 |
| operating | grid20 | 12.94 | 1 | 2 | 2 | 21 / 21 | 6 |
| operating | grid20_reverse | 12.92 | 1 | 2 | 2 | 24 / 24 | 6 |
| operating | ladder4 | 3.83 | 3 | 5 | 4 | 4 / 24 | 9 |
| operating | ladder20 | 12.91 | 1 | 5 | 5 | 28 / 28 | 10 |

## Reserve control: actual capital and dispersion, 2023 operating

Daily averages condition on days with at least one live PA. Positive account equity is profit retained inside live PAs, not withdrawable cash. Effective headroom groups = N² / sum(equal-headroom group size²). It is descriptive, not independent risk capacity.

| Arm | Wipeouts | Empty days | Deaths | Mean live PAs | Mean effective headroom groups | Mean retained positive equity | Net operating cash |
|---|---:|---:|---:|---:|---:|---:|---:|
| rr_1.00 | 1 | 42.22 | 19 | 13.30 | 6.72 | $70,027 | $176,775 |
| uniform_low | 1 | 42.22 | 36 | 12.13 | 6.23 | $54,524 | $186,898 |
| uniform_high | 1 | 42.22 | 19 | 13.30 | 6.72 | $80,630 | $151,275 |
| ladder4 | 1 | 42.22 | 27 | 12.99 | 10.97 | $67,584 | $173,188 |
| ladder20 | 1 | 42.22 | 28 | 12.91 | 8.05 | $64,422 | $175,122 |
| ladder20_reverse | 1 | 42.22 | 19 | 13.30 | 7.98 | $73,800 | $172,775 |
| wide4 | 0 | 0.00 | 28 | 11.88 | 10.35 | $67,423 | $188,417 |
| grid20 | 1 | 48.22 | 21 | 12.94 | 12.61 | $73,634 | $217,393 |

## March stress replay

| Arm | March 1 alive | March cohort deaths | March 31 alive | March same-signal peak | March 1 distinct / effective headroom groups |
|---|---:|---:|---:|---:|---|
| rr_1.00 | 20 | 20 | 0 | 20 | 1 / 1.00 |
| wide4 | 20 | 5 | 15 | 5 | 4 / 4.00 |
| center4 | 20 | 10 | 10 | 5 | 4 / 4.00 |
| edge4 | 20 | 0 | 20 | 0 | 4 / 4.00 |
| without050 | 20 | 5 | 15 | 5 | 4 / 4.00 |
| extremes2 | 20 | 0 | 20 | 0 | 2 / 2.00 |
| grid5 | 20 | 4 | 16 | 4 | 5 / 5.00 |
| grid10 | 20 | 4 | 16 | 2 | 10 / 10.00 |
| grid20 | 20 | 7 | 13 | 2 | 20 / 20.00 |
| ladder4 | 20 | 10 | 10 | 5 | 4 / 4.00 |
| ladder20 | 20 | 12 | 8 | 2 | 20 / 20.00 |
| uniform_low | 20 | 20 | 0 | 20 | 1 / 1.00 |
| uniform_high | 20 | 0 | 20 | 0 | 1 / 1.00 |
| grid20_reverse | 20 | 7 | 13 | 2 | 20 / 20.00 |
| ladder20_reverse | 20 | 12 | 8 | 2 | 20 / 20.00 |

### Actual March timing and capital, MAE-first

Dates below are recorded exit-day proxies; counts across different originating signals provide evidence beyond merely delaying the exit of one losing trade. Earlier deaths at low reserve levels are part of the trade-off.

| Arm | March death dates (day: count) | Largest recorded daily loss | March 1 retained positive equity |
|---|---|---:|---:|
| rr_1.00 | 26: 20 | 20 | $76,068.00 |
| wide4 | 26: 5 | 5 | $91,699.00 |
| center4 | 26: 5, 27: 5 | 5 | $77,529.00 |
| edge4 | none | 0 | $93,597.75 |
| without050 | 26: 5 | 5 | $89,957.50 |
| extremes2 | none | 0 | $97,261.00 |
| grid5 | 27: 4 | 4 | $87,289.40 |
| grid10 | 26: 4 | 4 | $86,741.80 |
| grid20 | 23: 2, 24: 2, 26: 1, 27: 2 | 2 | $80,725.60 |
| ladder4 | 19: 5, 24: 5 | 5 | $76,068.00 |
| ladder20 | 19: 2, 20: 1, 23: 4, 24: 2, 26: 2, 27: 1 | 4 | $76,068.00 |
| uniform_low | 19: 20 | 20 | $46,068.00 |
| uniform_high | none | 0 | $106,068.00 |
| grid20_reverse | 23: 2, 24: 2, 26: 1, 27: 2 | 2 | $80,725.60 |
| ladder20_reverse | 19: 3, 23: 4, 24: 2, 26: 2, 27: 1 | 4 | $75,726.15 |

## Intratrade-order sensitivity

Entries below show MAE-first → MFE-first. Each column is a within-policy paired replay.

| Arm | 2020 primary wipeouts | 2023 primary wipeouts | 2020 primary 20-day peak | 2023 primary 20-day peak | March cohort deaths |
|---|---|---|---|---|---|
| rr_1.00 | 2 → 2 | 1 → 1 | 13 → 13 | 6 → 6 | 20 → 20 |
| wide4 | 0 → 0 | 0 → 0 | 7 → 8 | 6 → 5 | 5 → 5 |
| center4 | 2 → 2 | 0 → 0 | 8 → 7 | 5 → 5 | 10 → 10 |
| edge4 | 0 → 0 | 1 → 1 | 11 → 11 | 7 → 6 | 0 → 0 |
| without050 | 2 → 2 | 0 → 0 | 9 → 9 | 6 → 5 | 5 → 5 |
| extremes2 | 0 → 0 | 1 → 1 | 12 → 13 | 6 → 6 | 0 → 0 |
| grid5 | 0 → 0 | 1 → 1 | 8 → 9 | 5 → 5 | 4 → 4 |
| grid10 | 0 → 0 | 1 → 1 | 6 → 6 | 6 → 6 | 4 → 4 |
| grid20 | 0 → 0 | 1 → 1 | 6 → 6 | 6 → 6 | 7 → 7 |
| ladder4 | 2 → 2 | 1 → 1 | 13 → 13 | 9 → 10 | 10 → 10 |
| ladder20 | 2 → 2 | 1 → 1 | 13 → 13 | 10 → 11 | 12 → 12 |
| uniform_low | 3 → 3 | 1 → 2 | 20 → 20 | 18 → 19 | 20 → 20 |
| uniform_high | 2 → 2 | 1 → 1 | 13 → 13 | 6 → 6 | 0 → 0 |
| grid20_reverse | 2 → 2 | 1 → 1 | 7 → 6 | 6 → 6 | 7 → 7 |
| ladder20_reverse | 2 → 2 | 1 → 1 | 13 → 13 | 6 → 6 | 12 → 12 |

## Homogeneous constituent controls

| RR | Primary operating wipeouts, 2020–2025 | Isolation deaths, 2020–2025 | March deaths, MAE-first |
|---|---|---|---:|
| 0.50 | 1 / 1 / 0 / 1 / 0 / 0 | 20 / 20 / 0 / 20 / 0 / 20 | 0 |
| 0.66 | 0 / 1 / 1 / 1 / 0 / 1 | 0 / 20 / 0 / 20 / 0 / 20 | 7 |
| 0.75 | 3 / 2 / 1 / 1 / 0 / 1 | 20 / 20 / 0 / 0 / 0 / 20 | 3 |
| 0.82 | 3 / 1 / 0 / 1 / 0 / 1 | 20 / 20 / 0 / 0 / 0 / 20 | 2 |
| 0.83 | 2 / 2 / 0 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 2 |
| 0.97 | 2 / 3 / 1 / 1 / 0 / 1 | 20 / 20 / 20 / 0 / 0 / 20 | 16 |
| 1.00 | 2 / 2 / 2 / 1 / 0 / 1 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.13 | 2 / 3 / 3 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 0 | 0 |
| 1.17 | 2 / 2 / 3 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.25 | 2 / 2 / 3 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.29 | 2 / 1 / 3 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.45 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.50 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.61 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.75 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.76 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 20 |
| 1.83 | 2 / 0 / 1 / 1 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 0 |
| 1.92 | 2 / 1 / 1 / 1 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 18 |
| 2.00 | 2 / 1 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.08 | 2 / 1 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.17 | 2 / 3 / 3 / 0 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 0 |
| 2.24 | 2 / 2 / 3 / 0 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 0 |
| 2.25 | 2 / 2 / 3 / 0 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 0 |
| 2.39 | 2 / 4 / 3 / 0 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 20 |
| 2.50 | 2 / 6 / 4 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.55 | 2 / 4 / 4 / 0 / 0 / 0 | 20 / 0 / 20 / 0 / 0 / 20 | 0 |
| 2.71 | 2 / 4 / 3 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.75 | 2 / 4 / 3 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.83 | 2 / 3 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 2.87 | 2 / 3 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.03 | 2 / 3 / 3 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.17 | 2 / 3 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.18 | 2 / 3 / 2 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.25 | 2 / 3 / 1 / 0 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.34 | 2 / 2 / 2 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |
| 3.50 | 2 / 2 / 2 / 1 / 0 / 0 | 20 / 20 / 20 / 0 / 0 / 20 | 0 |

## Interpretation boundaries

- Neither more labels nor more distinct balances establishes independent failures. Use portfolio loss clusters and empty duration.
- Same-signal grouping uses originating window and entry. Recorded days use exit proxies; interval clusters are conservative bounds, not exact crossing times.
- Twenty groups cannot guarantee twenty funded PAs. Assignment order can matter while the book is underfilled; reverse arms expose that sensitivity.
- Equal mean reserve targets do not equalize realized retained capital, withdrawals or replacement funding. Uniform reserve endpoints are controls, not an optimization.
- Do not compare the best constituent selected after seeing a period with a precommitted mixture as if both had been chosen prospectively.
- RR tapes have small entry-set differences; signal_alignment.csv records them. Cash and evaluation supply retain historical assumptions.
- These are overlapping historical experiments. Results do not establish a universally optimal count, reserve or RR setting.

Evidence: comparison.csv, deltas_vs_rr1.csv, constituent_comparisons.csv, contract.json, audit.json, independent_audit.json, signal_alignment.csv and cases/.
