# Shortlist reconciliation, 2026-09-24

This note reconciles [FINDINGS.md](FINDINGS.md) with a later review of its
operating comparison. `FINDINGS.md`, its presentation audit and the transcript
are left unchanged as the frozen record. Every figure below is measured from
the same saved `operating_cases/` and the existing episode tables; nothing was
rerun.

## 1. The operating ranking depends on which component deploys first

Averaging every assignment order gives each component the first seat in 1/n of
cases: a pair puts RR 0.50 first in 6 of its 12 cases, a triple in 12 of 36.
That average is valid for a uniformly chosen order. It does not isolate
composition, because changing the portfolio also changes how often each
component is assigned first.

| First seat | RR pair | RR/GG pair | RR triple | RR/GG triple |
|---|---:|---:|---:|---:|
| RR 0.50: wipeouts / cases | 1/6 | 1/6 | 1/12 | 1/12 |
| RR 0.50: mean empty days | 3.67 | 8.17 | 0.35 | 2.75 |
| Any other: wipeouts / cases | 4/6 | 6/6 | 24/24 | 19/24 |

With RR 0.50 first, the triples have fewer wipeouts per case and less empty
time. Each subset contains a single wipeout, so the difference is weak, but it
runs against the uniform-order ranking. The four are separate events, all from
the 2021 start: 2021-05-18 (RR/GG pair), 2021-06-03 (RR/GG triple), 2021-06-10
(RR pair) and 2022-01-10 (RR triple).

The uniform-order result is not only a first-seat proportion effect. The two
pairs have identical proportions and still differ, because RR 2.50 first
(4 wipeouts in 6 cases) did better than GG 1.25 first (6 in 6).

RR 0.50 first reduces startup failures here but does not eliminate them: three
of the four RR 0.50-first wipeouts happen before the book reaches five PAs. In
[wide4_permutations](../wide4_permutations/permutation_summary.csv), RR 0.50
first had no startup failures across 36 cases.

**Narrowed wording:** RR 0.50 / RR 2.50 had the lowest average wipeouts and
empty time under a uniformly chosen assignment order. That is a property of the
portfolio together with its deployment order, not of composition alone.

## 2. The operating wipeouts measure establishment risk

- 49 of the 57 mixture wipeouts occur before the book has ever held five PAs;
  29 of them when its historical maximum is one PA.
- The other 8 are all in the 2021 start, in books that peaked at 7-9 of 20 seats.
- No mixture empties a book that has exceeded nine PAs.

The comparison therefore says little about diversification inside an
established book. Surviving past nine accounts is not evidence of safety
either: those paths have already come through the build-up.

## 3. Quarter overlap: partial diversification, strong shared vulnerability

For RR 0.50 / RR 2.50, the product-of-marginals benchmark is
5 x 6 / 26 = 1.15 joint failed quarters; observed is 3. The pair is strongly
positively associated. Three complete-loss quarters, against five for RR 0.50
alone and six for RR 2.50 alone, is still diversification: partially different
failure sets with substantial shared vulnerability, not independent protection.

No pair in any family falls below the product-of-marginals benchmark. The
ordinary RR grid has 78 pairs; the 13 RR1000 pairs cover only 24 eligible
quarters and are excluded here. Among the 78, three pairs share the fewest
joint failed quarters, three each: RR 0.50/2.25, RR 0.50/2.50 and RR 1.00/2.25.
These counts are not a significance test; quarters are not independent draws.

Overlap ratios depend on how often each setting fails on its own. GG settings
fail in 7.46 of 26 quarters on average, RR settings in 6.31. A marginal-adjusted
measure (phi, the correlation of the two failure indicators) reorders the
families:

| Family | Pairs | Median observed / benchmark | Median phi | Median P(both fail, given the rarer fails) |
|---|---:|---:|---:|---:|
| RR x RR | 78 | 3.11 | 0.697 | 0.82 |
| GG x GG | 78 | 2.89 | 0.804 | 1.00 |
| RR x GG | 169 | 2.60 | 0.584 | 0.80 |

GG pairs are the most strongly associated, which supports the GG-only finding
that no GG pair improves on GG 1.25 alone. Cross-strategy pairs are lowest on
phi but level with RR pairs on the conditional measure. That is directionally
interesting; it does not establish that different signals cause better
diversification.

## What stands

- The quarter-isolation counts in `FINDINGS.md`: 3/26 complete-loss quarters for
  each pair and 2/26 for each triple, with the triples losing a larger fraction
  of accounts on average.
- RR 0.50 / RR 2.50 as a reference portfolio for future comparisons - a
  reference, not a demonstrated best.
- Operating continuity among these four mixtures is not resolved by this
  design. Separating them needs the first seat held fixed, or a test that
  starts from an established book.
