Yes. The important point is that these are actually describing two different optimization objectives, and the numbers can look contradictory until we separate them.

In the study, the earlier idea was essentially:

> “Withdraw as much as possible, as soon as possible, but keep some reserve so the PA survives.”

When you constrain the system to that behavior — daily maximum withdrawal — the optimization comes back to roughly the same place as your older reserve studies:

**about $6,800 above the frozen liquidation floor.**

That is significant. It suggests the old ~$6–7k reserve wasn't merely an artifact of assuming unlimited instant replacement accounts. Even after modeling evaluations, replacement delays, spare evaluations, etc., the system still finds roughly the same survival cushion when the withdrawal rule is aggressive.

For that policy:

| | 25K | 50K |
|---|---:|---:|
| Withdrawal | Maximum daily | Maximum daily |
| Reserve above frozen floor | ~$6,800 | ~$6,800 |
| Total extracted | ~$630k | ~$642k |

So this result says something fairly strong:

**If your objective is to take money out aggressively throughout the life of the account, keeping approximately $6,800 of extra buffer appears economically worthwhile.**

Why? Imagine an account has reached the frozen floor and then accumulated another $10,000.

You have two choices.

Aggressive strategy:

`floor + $10,000 → withdraw ~$3,200 → leave ~$6,800`

More extreme aggressive strategy:

`floor + $10,000 → withdraw ~$8,000 → leave ~$2,000`

The second strategy gives you an extra $4,800 immediately. But it dramatically increases the probability that the next adverse sequence kills the PA.

Previously that wasn't terribly expensive in the simulator because another PA could appear almost immediately.

Now it is expensive because:

`PA dies → need evaluation → evaluation must pass → activate PA → replacement becomes productive`

and that can take weeks.

Your earlier evaluation study found median successful evaluation times of roughly 35–40 days, with only a minority passing in the first month. Therefore a dead PA isn't merely a ~$100–$200 replacement expense. It represents potentially a month or more of **lost earning capacity**.

That is why the $6,800 reserve has economic value.

But then Codex allowed the optimizer to change the withdrawal policy itself, and something interesting happened.

Instead of:

**maximum withdrawal + $6,800 reserve**

it found:

**minimum monthly withdrawal + nominal ~$2,800 threshold**

and obtained:

25K → **$649,794**

50K → **$644,763**

At first glance that sounds like:

> “Ah, so $2,800 is actually better than $6,800.”

But that's not what happened.

The crucial sentence from Codex is:

> “Small monthly withdrawals allow balances to accumulate above that threshold.”

Suppose the threshold is $2,800, but you're only withdrawing the minimum once per month.

The account might evolve something like:

`$2,800 → $4,000 → $6,500 → $9,000 → $11,000`

because you're not constantly stripping profits out.

So although the configured reserve is only $2,800, the **actual average balance cushion may be much larger**.

By contrast, maximum daily withdrawal continually pushes the account back toward:

`floor + ~$6,800`

So comparing `$2,800 vs $6,800` directly is misleading. They're parameters inside very different withdrawal systems.

And there's another major issue with the $649,794/$644,763 winners: approximately **$183,000** isn't actually withdrawn during normal operation. It is the theoretical closing withdrawal at the end of July 2026.

For example, conceptually:

`$650k total = ~$467k actually extracted during operation + ~$183k sitting in accounts at end`

That distinction matters enormously for what you're trying to accomplish.

If this were a real prop-firm operation, I would regard **ongoing extracted cash** as substantially more important than a simulated terminal liquidation value. You don't know that all accounts will survive until an arbitrary study end date, nor that rules will remain unchanged, nor that the firm will continue operating under identical conditions.

The study endpoint itself is artificial.

So I would not interpret:

**$649,794 > $630,000**

as proof that minimum monthly withdrawals are economically superior.

They're optimizing different timing of cash realization.

There's another result I find more interesting:

> 25K ongoing-cash winner: $597,317, daily minimum, $3,900 cushion, 76 accounts.  
> 50K ongoing-cash winner: $582,835, daily minimum, $3,700 cushion, 69 accounts.

That starts to reveal a continuum.

Very aggressive extraction:

`MAX withdrawal → ~$6,800 reserve → fewer deaths`

Less aggressive extraction:

`MIN withdrawal → ~$3,700–3,900 configured reserve → balances naturally accumulate → somewhat more turnover`

And at the opposite extreme:

`very small reserve + MAX withdrawals → many deaths → replacement factory cannot keep up`

That's the economic tradeoff your simulator is discovering.

You can think about every PA as a small income-producing asset.

There are two forms of capital tied up in it:

`cash sitting in PA`

and

`replacement capacity`

Previously the simulator effectively priced replacement capacity near zero. Blow an account and another one arrives.

The new evaluation model gives replacement capacity a scarcity value.

Therefore the optimization becomes:

**How many dollars should I leave trapped in an existing PA to avoid consuming scarce replacement capacity?**

Apparently, under your historical strategy/tape, leaving approximately **$6,800** is worth it when you're otherwise extracting everything available.

And this explains another result that initially seems strange:

25K:

`57 accounts → 52 accounts`

50K:

`44 accounts → 39 accounts`

after making the replacement factory *better*.

You might expect more replacement capacity to result in more accounts being consumed.

Instead the optimizer says:

> “Even though I *can* replace them faster, killing them still isn't the best use of the system.”

That's quite important.

The aggressive fixed policy did benefit enormously from the improved factory:

25K:

`~$126k → ~$383k`

50K:

`~$192k → ~$376k`

So replacement capacity absolutely matters.

But even after that huge improvement, it couldn't catch the lower-turnover policies around $630–650k.

That means the conclusion isn't merely:

**“Our evaluation pipeline is too slow.”**

It is increasingly looking like:

**“The underlying economics favor preserving profitable PAs rather than treating them as disposable.”**

One caveat has become important since this simulation is explicitly about Apex Legacy accounts. Apex's current published rules say Legacy accounts have a 20-PA household cap, while evaluation limits are treated differently, and Legacy payout rules still use the old safety-net/payout framework.  The current site also states that Legacy evaluations have temporarily returned for a limited promotion, so assumptions about future replacement availability should not be treated as permanent. 

There's also a compliance consideration: Apex explicitly says deliberately cycling or blowing accounts for windfall-style profits is prohibited. So even apart from the simulation economics, the real implementation should represent normal risk-managed trading rather than intentional account destruction. 

The experiment I would run next is actually slightly different from another giant pipeline search. We now have enough evidence about pipeline capacity. I'd run a **reserve frontier** while holding the withdrawal mechanism fixed.

For daily maximum withdrawal, test perhaps:

`$0, $1k, $2k, $3k ... $10k`

and for every reserve report not just total profit, but **ongoing withdrawals, terminal balance, PA deaths, evaluations required, median replacement delay, unfilled PA-days, and average actual capital retained in PAs**.

That would let us see whether $6,800 is a sharp optimum or, much more likely, a broad plateau — perhaps $5,500–$7,500 produces almost identical results.

For a live system, I'd much rather choose the center of a broad stable plateau than optimize specifically to **$6,800**.

And I think that's now the most important unanswered question: **is $6,800 genuinely special, or is “roughly $6–7k” simply the robust survival zone for your strategy?**
