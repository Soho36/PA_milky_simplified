What that result is really saying is that GG behaves differently from RR. For RR, the 0.50 / 2.50 pair gave fairly convincing evidence that the two r/r settings encounter some genuinely different bad market regimes. For GG, the separation exists, but it is weaker and much more asymmetric.

Take GG 0.50 / 1.00:

- In 5 of the 26 quarters, both GG 0.50 and GG 1.00 would breach the $1,500 headroom.
- In 4 quarters, GG 0.50 fails while GG 1.00 survives.
- In only 1 quarter, GG 1.00 fails while GG 0.50 survives.

So there is diversification, because their failure sets are not identical. But most of the diversification is effectively flowing in one direction: GG 1.00 often protects you from GG 0.50, while GG 0.50 rarely protects you from GG 1.00.

That is quite different from what we ideally want. The ideal pair would look something more like:

> A fails in several periods where B survives, and B also fails in several periods where A survives, while relatively few periods kill both.

That would indicate two genuinely complementary failure modes.

The important complication is GG 1.25. GG 1.25 by itself also failed in only 5/26 quarters. So imagine 10 accounts split as:

5 × GG 0.50  
5 × GG 1.00

There are still five quarters where all ten would fail.

Now compare that conceptually with:

10 × GG 1.25

That also has five failing quarters.

This means the 0.50/1.00 mixture hasn't actually reduced the number of quarters in which the entire GG allocation can be wiped out compared with simply using GG 1.25. And according to the study, the mixture also had a higher average fraction of accounts failing overall.

That's why I wouldn't yet say:

> “GG 0.50 + GG 1.00 is the GG equivalent of RR 0.50 + RR 2.50.”

It isn't, at least from this evidence.

The GG 1.25 / 1.50 result is even clearer. Those two failed in exactly the same five quarters. That means, from the perspective we're studying, splitting accounts between them buys essentially no failure-regime diversification. They may have different P&L distributions or trade outcomes, but when the environment becomes sufficiently hostile to kill one, it killed the other too.

So for your proposed 5×4 structure:

5 RR 0.50  
5 RR 2.50  
5 GG lower-r/r  
5 GG higher-r/r

the RR half already has a fairly logical lower/higher pair.

The GG half does not yet have an equally convincing lower/higher pair.

And I think this is the key point: we should not force GG into the same architectural shape just because RR happened to produce a good low/high combination.

It could turn out that the best structure is something like:

5 RR 0.50  
5 RR 2.50  
10 GG 1.25

rather than 5/5/5/5.

Or perhaps another GG pair from the 78 combinations provides a better compromise than 0.50/1.00 once we consider several things simultaneously rather than just counting failure quarters.

What I'd examine next for GG is not simply "which pair has the lowest overlap." I would compare candidate GG pairs on four quantities together:

1. Number of quarters where both fail.
2. Failures unique to each side — preferably reasonably balanced.
3. Average fraction of accounts lost.
4. Combined equity drawdown/P&L.

For example, a GG pair with 6 both-fail quarters but strong two-way separation might actually be less attractive for your objective than GG 1.25 alone with only 5 failure quarters.

Conversely, if we find a GG pair with 5 both-fail quarters but something like 3 failures unique to A and 3 unique to B, that would be much more interesting than 0.50/1.00's asymmetric 4 versus 1.

So the current picture is roughly:

**RR:** 0.50 / 2.50 → meaningful evidence of complementary failure regimes.

**GG:** 0.50 / 1.00 → some diversification, but weak/asymmetric; not clearly superior to GG 1.25 alone.

**GG:** 1.25 / 1.50 → almost no useful regime diversification despite different r/r settings.

That actually makes the next question quite interesting: rather than assuming GG must contribute two groups of five accounts, we can determine whether GG statistically deserves one group or two groups. That could materially change the eventual 20-account allocation.
