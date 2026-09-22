What I meant by “retain RR 0.50 / RR 2.50 as the operating benchmark” is not that it dominates every metric. It means that, given what we have tested so far, it is the cleanest reference portfolio against which future variants should be compared.

The key distinction is between two different objectives: surviving a disastrous quarter versus keeping the whole operating system functioning over time.

The triples improve the first objective. Adding RR 1.00 changes complete-loss quarters from 3/26 to 2/26. In Q3 2024, instead of all components dying, RR 1.00 survives, so roughly one-third of the equal-weight portfolio remains alive. That is real diversification.

But it comes at a cost. For the RR-only version:

- RR 0.50 + RR 2.50: 3 complete-loss quarters, 21.2% average accounts lost.
- RR 0.50 + RR 1.00 + RR 2.50: 2 complete-loss quarters, but 23.1% average accounts lost.

So RR 1.00 saves us from one “everybody dies” event, but across ordinary quarters it loses accounts more frequently. The triple therefore changes the shape of the risk rather than simply reducing it.

That becomes even clearer in the operating simulation. Once withdrawals, reserves, replacement accounts, funding rules, etc. were restored, the extra survival in Q3 2024 did not translate into a new continuity advantage. All four mixtures were already continuously operational for the 2023, 2024 and 2025 starts. For earlier starts, all remained sensitive to which strategy was assigned first.

And this is the important part: the original RR 0.50 / RR 2.50 pair had the lowest average number of whole-book wipeouts and the least time with no active accounts. Those are very important operational metrics because your actual problem is not merely “how many PAs die?” It is “can I keep the machine running?”

There is another interesting wrinkle: RR 0.50 + GG 1.25 actually had the lowest average account-loss fraction among the four mixtures:

21.2% — RR pair  
19.2% — RR/GG pair  
23.1% — RR triple  
21.8% — RR/GG triple

So the cross pair deserves to remain a serious candidate too. It loses fewer accounts on average. But in the full operating runs it did not establish better continuity than RR 0.50 / RR 2.50.

That is why I would currently think of the candidates like this:

| Portfolio | Main advantage | Main disadvantage |
|---|---|---|
| RR 0.50 + RR 2.50 | Strongest demonstrated operating continuity | Still has 3 common failure quarters |
| RR 0.50 + GG 1.25 | Fewer accounts fail on average | No demonstrated continuity improvement |
| RR 0.50 + RR 1.00 + RR 2.50 | Only 2 complete-loss quarters | More normal account deaths, worse DD/P&L |
| RR 0.50 + GG 1.25 + RR 1.00 | Only 2 complete-loss quarters | Same general triple tradeoff |

So “benchmark” means: don’t throw away RR 0.50 / RR 2.50 merely because we discovered something that survives one extra historical crash. Keep it as the control.

The most interesting conclusion, in my view, is that RR 1.00 behaves somewhat like an insurance component. It helps specifically when the other two fail together, but that insurance has a premium: more failures during the rest of the history, lower average P&L, and worse worst-quarter drawdown.

And that suggests a potentially more interesting question than simply “2 strategies or 3 strategies”:

What if RR 1.00 should not receive a full one-third allocation?

For example, rather than:

33% RR 0.50  
33% RR 1.00  
33% RR 2.50

we could test something like:

45% RR 0.50  
10% RR 1.00  
45% RR 2.50

Then RR 1.00 acts as a small hedge against the common failure mode without imposing as much of its 7/26-quarter failure burden on the whole portfolio.

That, I think, is the most natural next experiment from these results.
