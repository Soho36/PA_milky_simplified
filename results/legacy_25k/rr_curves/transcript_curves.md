The key point in that result is that there are really two different kinds of “diversification” happening, and the study suggests one is much stronger than the other.

The first is equity-curve diversification. Suppose two RR variants do not lose money at exactly the same times. When you average their curves, losses in one can partly coincide with gains or smaller losses in the other. That can reduce the portfolio-level drawdown. This is what RR0.50 + RR2.50 seems to be doing.

For example:

- RR0.50 alone: average MDD ≈ $2,810
- RR2.50 alone: average MDD ≈ $3,186
- 50/50 RR0.50 + RR2.50: average MDD ≈ $2,795

So the mixture is smoother than either constituent on average. But only slightly smoother than RR0.50: about $15. That is important. Most of the apparent improvement versus RR1 comes from including the inherently lower-drawdown RR0.50, not from some enormous diversification effect produced by mixing.

The more interesting result, in my view, is the account-death behavior.

With identical RR1 accounts, their trading paths are identical. If they all start at the same time with the same balance, they hit the failure threshold together. There is essentially zero diversification.

With RR0.50 and RR2.50, their paths diverge. In the $1,500-headroom test, RR1 had 8 of 23 yearly windows in which every account eventually breached. RR0.50/2.50 reduced that to only 3 of 23.

That is quite meaningful conceptually.

It means something like:

> “The mixture does not necessarily stop accounts from dying, but it makes it less likely that all types die in the same historical period.”

That is exactly the property you were originally looking for with RR diversification.

But there is a catch. The average fraction of accounts that died remained 34.8%.

Imagine 10 accounts.

With homogeneous RR1 you might have periods resembling:

`10 alive → 0 alive`

With a mixed portfolio you might instead get something resembling:

`10 alive → 5 alive`

more often.

But over the whole historical window, you are not necessarily reducing the total number of failed accounts. You are mainly preventing complete synchronized destruction.

That explains the sentence:

> “the evidence is stronger for preserving part of the portfolio than for spreading deaths across time.”

Those are different things.

If RR0.50 accounts die in March and RR2.50 accounts die six months later, that would be genuine temporal spreading.

But the actual five-day clustering statistic barely improved:

34.8% → 32.6%.

So deaths are not becoming dramatically separated on the calendar. What seems to happen more often is simply that some RR variants survive episodes that kill others.

That is still useful for your PA portfolio because complete wipeout is much more damaging operationally than losing a portion of the book.

There is another subtle result that I think is especially important:

> RR0.50/2.50 beat RR1 drawdown in 15/23 windows, but beat both RR0.50 and RR2.50 in only 5/23.

This tells us whether we are seeing genuine diversification alpha.

Suppose RR0.50 is simply much safer than RR1. If we mix RR0.50 with something else and the resulting portfolio beats RR1, that alone doesn't prove mixing helped. Perhaps we could simply trade RR0.50 everywhere.

For genuine diversification, we would ideally want:

`DD(mixture) < DD(RR0.50)`  
and  
`DD(mixture) < DD(RR2.50)`

That occurred only 5/23 times.

Therefore the study does not say:

“RR0.50 + RR2.50 is definitely the optimal portfolio.”

It says:

“Different RR strategies have sufficiently different paths that diversification exists, and some combinations materially reduce complete simultaneous failure.”

That is a much stronger foundation than we had before.

The `wide4` result also gives us a warning about regime dependence. It worked much better in the earlier part of the sample:

- earlier windows: 10/12 better than RR1
- later windows: only 2/11 better

So adding more RRs does not automatically mean more diversification. Some RRs may become highly correlated with each other during particular market regimes.

In fact, this makes your later decision to investigate low-RR/high-RR pairs quite logical. We probably don't want “many different RRs.” We want the smallest set of RRs whose bad periods are complementary.

Conceptually, the ideal combination would look something like this:

```text
             Bad period A   Bad period B   Bad period C

RR 0.50          BAD           OK             OK
RR 1.75           OK          BAD             OK
RR 2.75           OK           OK            BAD
```

Rather than:

```text
RR 0.50          BAD           OK            BAD
RR 1.00          BAD           OK            BAD
RR 1.50          BAD           OK            BAD
RR 2.00          BAD           OK            BAD
```

The second portfolio contains four settings, but effectively only one risk source.

And that is why I think the next conceptual step should not primarily be “find the RR pair with the lowest MDD.” It should be:

**identify which RR settings fail during genuinely different market episodes.**

We can think of each RR as having a historical “failure fingerprint.” Something like:

```text
RR0.50   001000100001000
RR1.00   001100100011000
RR1.75   000010101000100
RR2.50   100010001000010
```

where `1` represents a serious drawdown/failure episode.

Then we want combinations whose `1`s overlap as little as possible while still producing acceptable profit.

That would be much closer to the actual objective of your Apex portfolio than simply minimizing average equity-curve drawdown.

So the major conclusion from that experiment is:

**Yes, RR diversification appears to be real. But its strongest benefit is not dramatically lower total drawdown or widely separated death dates. It is reducing the probability that all strategy variants get destroyed by the same market episode.**

That is a property worth optimizing directly.
