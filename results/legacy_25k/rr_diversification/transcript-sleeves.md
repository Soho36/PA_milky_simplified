That sentence means “empty-book episode” in the literal portfolio sense: a period when all 20 accounts in that simulated book are dead/unavailable, so there is nobody left to trade until replacements come in.

Across the six primary start years that were tested, the mixtures behaved differently:

- `wide` had 0 empty-book episodes.
- `modest` still had 1.
- `four` still had 2.
- `near` also had at least one, so it was not unique in having this problem.

So the important point is not merely that mixtures reduced the number of simultaneous deaths. Some mixtures still eventually reached a state where the entire currently available book disappeared. `wide` was the only tested mixture that completely avoided that outcome in all six runs.

That matters because your practical objective is closer to “keep enough PA accounts alive to continue trading” than “minimize the total number of account deaths.” A portfolio can actually have more cumulative deaths over several years but still be operationally safer if those deaths happen in different RR sleeves and replacements have time to enter before the remaining sleeves fail.

For example, imagine 20 accounts split 5/5/5/5 across four RRs. If one five-account sleeve dies today, you still have 15 accounts trading. Even if another sleeve dies months later, the first five may already have been replaced. Compare that with 20 identical RR1 accounts: one adverse regime can kill all 20 before the replacement pipeline can react.

That is why the zero-empty-book result for `wide` is more interesting than simply saying “March deaths dropped from 20 to 5.” The March result only proves that one shock hit one sleeve rather than the whole portfolio. The six-start result suggests that, historically, the different sleeves' bad periods did not line up enough to leave the portfolio with zero usable accounts.

There is still an important caveat: the six starts overlap heavily in calendar history, so this is not equivalent to six independent experiments. And we haven't yet established that `wide`'s exact RRs—0.50/1.50/2.50/3.50—are special. The benefit may primarily come from having sufficiently different RR behaviors rather than those exact four values.

That is exactly why the next controlled test should be designed around portfolio continuity: same number of sleeves, same five accounts per sleeve, same replacement rules, but different RR combinations. Then compare things like time with zero accounts, minimum live-account count, duration below 5/10/15 accounts, simultaneous sleeve failures, and replacement recovery time. That would tell us whether `wide` really has structural diversification value or was simply a fortunate combination over this history.
