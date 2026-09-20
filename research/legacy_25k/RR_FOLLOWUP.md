# RR composition, group count and reserve-ladder experiment

Frozen before simulation on 2026-09-21. This is a historical mechanism study,
not an optimization or out-of-sample validation. The objective is fewer clustered
account losses and continued operation; cash and retained equity are constraints.

## Contrasts

- Reproduce the equal-weight 0.50/1.50/2.50/3.50 four-group baseline.
- Requested centered arm: 1.25/1.75/2.25/2.75. Its range is 1.50, versus
  3.00 for wide; it does not hold width fixed. Both means are 2.00.
- Same endpoints, mean and count: 0.50/0.75/3.25/3.50. This changes interior
  composition at fixed width. Individual RR outcomes can be nonlinear.
- Single substitution: 0.75/1.50/2.50/3.50 removes 0.50. This changes the
  mean and width as well; interpret as an ablation, not a pure width effect.
- Equal-weight evenly spaced 2, 4, 5, 10 and 20 RR groups between 0.50 and
  3.50 (nearest exported hundredth, symmetric around 2.00). Twenty paid
  accounts in isolation give one account per group. Operating supply shares
  20 slots with evaluations/spares, so fewer groups may actually be populated.
  Increasing count necessarily adds constituents: no contrast isolates a
  universal pure group-count effect independently of composition.
- All RR1, four reserve targets at offsets -1500/-500/+500/+1500 and twenty
  equally spaced targets from -1500 to +1500 around the baseline reserve.
  Average targets and full-book aggregate target match the uniform baseline.
  Uniform low/high targets distinguish dispersion from simply retaining more.
- Reverse assignment order for twenty-RR and twenty-reserve arms checks
  whether incomplete books favor the first targets in the allocation list.

Accounts keep their assignment for life. Replacements fill the least populated
group, with fixed list order breaking ties. No starting equity is gifted and no
money moves between accounts. A reserve is a withdrawal threshold above the
frozen trailing floor, not a promise to maintain that realized headroom. Daily
minimum withdrawals may fail to create the intended balance differences.
The ladder is inexpensive to simulate, but is not economically costless.

## Matched experiments

Reuse the original study's policy, cash, evaluation tape and fees. Primary:
daily minimum, mean reserve 6800, starts 2020--2025, isolation (20 initially
identical paid accounts, no replacements) and operating (cash-funded RR1
evaluations, replacements, shared 20-slot cap). Every distinct constituent has
a homogeneous control under both phases and all six starts.

Replay the March stress policy separately: daily maximum, mean reserve 5700,
original evaluation settings, full 2020 history. Run both extrema orders.
Primary operating MFE-first sensitivities use 2020/2023 starts for experimental
arms and RR1. Do not interpret the March withdrawal/pipeline policy as primary.

## Measurements and verification

Retain portfolio wipeouts, empty duration, 1/5/20 observed-trading-day death
clusters and conservative entry-to-exit interval bounds. Separately record:

- Deaths and actual participating accounts per sleeve for each killing signal;
  fractions refer to copiers, not all nominal seats. Full participating-sleeve
  loss can remain 100% even when whole-book signal loss decreases.
- How many sleeves lose accounts on a common signal or recorded calendar day.
- Daily actual sleeve occupancy, equal-headroom concentration, effective
  headroom groups (inverse concentration), and actual retained equity/headroom.
- March cohort survivors and detailed pre-event balances; lifetime account
  assignments, cash flows, per-sleeve death records and source trade identities.

Death times remain exported-exit proxies. RR-specific entry sets differ slightly;
report their alignment, never invent absent outcomes. Historical starts overlap.
Preserve the existing engine and earlier results; extensions live in study
scripts. Reproduce prior baseline account ledgers/cash, validate assignment and
reserve enforcement, independently reconstruct death metrics, and hash inputs,
code, protocol and output cases. No settings are selected after observing results.
