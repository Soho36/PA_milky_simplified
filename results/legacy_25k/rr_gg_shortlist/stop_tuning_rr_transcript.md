Why RR settings can't diversify each other much

Every RR setting takes the same entry with the same stop. Only the profit target moves. That makes the losses nested rather than independent:

At RR 1.00 and above, every trade that loses at 1.00 also loses at 1.50, 2.00, 2.50, 3.00 and 3.50, by exactly the same amount. The total difference across those losers was $0.00. Raising RR never removes a loss; it only turns some small wins into losses (the trade reaches 1R, reverses, and stops out before the higher target).
Below 1.00, a tight target can be hit before the stop, so some losers become small winners. At RR 0.50, 84% of RR 1.00's losing trades still lose. Nothing loses at a low RR that doesn't also lose at a higher one.

So in a hostile stretch, when trades run straight to their stops, every RR setting takes the same losses. The settings differ only in how much their winners banked beforehand. That's why none of the 78 ordinary RR pairs fails together less often than two independent books would.

The floor is already reached

The common-quarter survivor study tested all 301 RR settings and all 301 GG settings, in 0.01 steps, with a fresh account's $1,500 headroom:

Quarter	RR settings that survive	GG settings that survive
Q2 2022	none	none
Q3 2024	0.59–0.61 and 0.77–1.21	none
Q2 2025	none	none

No RR/GG combination on this tape can get below 2 of 26 complete-loss quarters. The pairs sit at 3, and the triples already reach 2. There's at most one quarter left to gain, and the triples have already taken it — at the cost of more ordinary losses. Swapping RR 0.50 for a Q3 2024 survivor doesn't help either: it trades Q3 2024 for Q1 2026 and leaves the count at 3.

Finer grids would mostly find noise

Moving RR by 0.01 already shifts a setting's failed-quarter count by one or two:

RR 0.79 → 7   0.80 → 6   0.82 → 5   0.86 → 6   0.92 → 7   0.94 → 6
RR 1.01 → 7   1.02 → 8   1.13 → 7   1.18 → 6   1.19 → 7

The gap between good and less good pairs, 3 against 4 shared quarters, is the same size as that jitter. Several results turn on trivial margins. RR 0.51 fails Q2 2022 by $0.05. RR 0.59–0.61 survives Q3 2024 with only $4.55–$8.05 to spare. Adjacent RR values give the same outcome in 5.29 of 6 starts, so the 301 values behave like about three regimes. Choosing between 45,150 possible pairs on 26 overlapping quarters will always produce a "winner", even if nothing real separates it from the rest.

The second value in the pair barely matters

The episode study also measured how often two settings are in deep drawdown on the same days (a Jaccard overlap: 0 = never together, 1 = always). Pairing RR 0.50 with anything from 1.75 upward lands on a plateau:

Pair	Deep-drawdown overlap
0.50 / 1.75	0.268
0.50 / 3.00	0.292
0.50 / 3.25	0.296
0.50 / 2.50	0.300
0.50 / 3.50	0.306
0.50 / 2.25	0.309
0.50 / 1.00	0.545
0.50 / 0.75	0.644

What matters is one low leg plus one leg well above it. Within that range, the exact second value is a matter of taste. So "stop tuning" is also good news: 0.50/2.50 isn't fragile, and 2.25, 3.00 or 3.50 would do about as well.

The ranking only exists for thin accounts

At the operating reserve of $6,800 headroom, no RR setting fails any quarter, and all 91 pairs show zero joint failures. The quarter ranking discriminates only at a fresh account's $1,500. That's the same message as the operating studies: what's being measured is establishment risk, not how a grown book holds up.

What "stop tuning" doesn't mean
RR still matters for returns. In the shortlist operating runs, mean net cash was about $122k for RR 0.50, $197k for RR 1.00 and $243k for RR 2.50. That's a return question with its own trade-offs — RR 2.50 alone averaged 2.0 wipeouts — and it's just as exposed to in-sample fitting.
Pairing still beats a single setting. 3 complete-loss quarters against 5–6 is real diversification.
Other levers are still open. They're the ones that change the loss leg or the cushion:
Different signals. RR × GG is the least associated family, directionally.
A different instrument. Q2 2022 and Q2 2025 kill all 602 settings of both strategies, so they behave like events for this symbol and signal family, not failures of any parameter.
Headroom and reserve.
Establishment design: starting cash, and deploying two sleeves from day one.
Stop placement. That's a change to the strategy, not an RR choice.

In short, the RR axis gives you one partial hedge — a low leg paired with a high leg — and the current pair already has it. Anything better has to come from the other levers.
