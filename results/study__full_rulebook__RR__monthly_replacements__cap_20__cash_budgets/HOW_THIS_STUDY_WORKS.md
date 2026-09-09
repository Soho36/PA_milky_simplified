# How this study operates: current-month replacement rule

Keep the regular monthly purchase schedule, subject to cash and the 20-live-account cap.
Replace each death at the next midnight check when affordable.

- If this month has not had a successful regular purchase, the first successful
  replacement fills that month's slot.
- If the regular purchase has already happened, replacements are additional
  purchases this month. They never cancel next month's scheduled purchase.
- At the first-day boundary, process deaths and replacements before the regular
  purchase. A successful replacement fills the current slot, avoiding a duplicate
  scheduled purchase. Several deaths may still receive several replacements.
- Failed replacement attempts consume nothing and retry on subsequent daily
  checks. Skipped regular monthly attempts still expire; a later replacement
  can fill that month's otherwise unused slot.

The study compares this rule with monthly-one, weekly-one and monthly-plus-
replacements, which always preserves the regular monthly purchase even when
replacements occur on that same boundary. All use the same four budgets and
three withdrawal settings. Replacement accounts continue to be replaced if they die.

No future-slot debt exists under the current rule. The old future-slot experiment
is preserved in archives/studies/monthly_replacements_future_slots. Existing
REPORT.md may retain the older reader narrative; use REPORT.generated.md for
current results. The former operating note is preserved in that archive too.

Withdrawals begin in each account's second calendar month and respect the chosen
reserve and configured firm gates. Trading losses can take balances below the
reserve. Net cash excludes contributions and subtracts fees. Total includes one
permitted terminal request; its receipts never fund new purchases.

Occupancy covers the common calendar-month opening to tape end. FIFO death-to-
purchase waits are descriptive; inspect unmatched deaths too. Changing replacement
timing changes cohorts, survival and spending, so this is not a pure timing effect.
