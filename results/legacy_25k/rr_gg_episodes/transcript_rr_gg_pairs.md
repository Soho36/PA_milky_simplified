What this result is telling us is that RR 0.50 and GG 1.25 are not merely two profitable variants that happen to have different names. Their failure sets are genuinely different.

Across the 26 fresh-start quarters:

| Situation | Count | Interpretation |
|---|---:|---|
| Both fail | 3 | Diversification does not help in these periods |
| RR fails, GG survives | 2 | GG protects RR |
| GG fails, RR survives | 2 | RR protects GG |
| Neither fails | 19 | No complete failure in either |

So RR 0.50 fails in 5 quarters total: the 3 shared failures + 2 RR-only failures.

GG 1.25 also fails in 5 quarters total: the same 3 shared failures + 2 GG-only failures.

That is actually a fairly clean diversification pattern:

RR 0.50 failure set:
`[ A, B, C, D, E ]`

GG 1.25 failure set:
`[ A, B, C, F, G ]`

The intersection is only:

`[ A, B, C ]`

Therefore, if you ran only RR 0.50, you would historically have 5 bad quarters. If you ran only GG 1.25, also 5. If capital were split between the two, the periods where the entire two-strategy structure fails fall to 3 quarters.

The important caveat is the comparison with RR 0.50 + RR 2.50.

That pair also has only 3 shared failure quarters. Even more importantly, they are apparently the same three quarters. Conceptually:

RR 0.50:
`A B C D E`

RR 2.50:
`A B C H I ...`

GG 1.25:
`A B C F G`

So we have discovered several different ways of escaping the secondary failures, but none of them escapes the core `A/B/C` failure regime.

That distinction matters a lot. The problem is no longer simply:

> “Can we find strategies that fail at different times?”

We already can.

The more interesting question becomes:

> “Can we find something that survives one or more of those three common failure periods?”

That would be a much more valuable discovery than merely finding another pair with 3/26 both-fail quarters.

The RR 2.50 + GG 1.25 result illustrates the opposite case. GG 1.25 has five failing quarters, and apparently RR 2.50 fails in every one of those five. So GG is adding essentially no failure protection to RR 2.50:

`GG failures ⊆ RR 2.50 failures`

From a failure-diversification perspective, that relationship is weak even if their P&L curves look somewhat different.

This also changes how I would think about the eventual 20-account structure. We should not automatically conclude:

`10 RR 0.50 + 10 GG 1.25`

or

`10 RR 0.50 + 10 RR 2.50`

just because both give 3 shared quarters.

A four-group structure could still make sense:

`5 × RR 0.50`
`5 × RR 2.50`
`5 × GG 1.25`
`5 × something else`

But the fourth group should ideally be selected specifically for what it does during those three common quarters. Adding another strategy that survives D/E/F/G but also dies in A/B/C adds diversity, but it does not solve the main catastrophic-failure problem.

So I think we have learned something quite important: RR 0.50 seems to be a useful “anchor” because both RR 2.50 and GG 1.25 complement it. But the next search should probably focus less on general pair overlap and more on those exact three shared failure episodes.

In other words, ask of every candidate:

**What happened to this strategy during the three quarters where RR 0.50 + RR 2.50 and RR 0.50 + GG 1.25 both failed?**

If we find even one sensible strategy/r/r that survives one or two of those three periods, that could be substantially more valuable than finding another pair with attractive average overlap statistics.
