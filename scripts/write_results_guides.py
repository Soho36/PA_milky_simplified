"""Add short, evidence-based folder guides without altering saved results."""
from pathlib import Path
import hashlib
import json
import sys
import textwrap
from report_names import report_path

ROOT = Path(__file__).resolve().parents[1]/'results'
NAME = 'START_HERE.txt'
COMPARE = 'comparisons/legacy_25k_vs_50k'
# The blocked-copying twin of COMPARE: same studies, one position per account.
BLOCKED = 'comparisons_blocking'
COMPARE_BLOCKED = BLOCKED+'/legacy_25k_vs_50k'

# Questions and conclusions are editorial; run-specific numbers below come
# directly from the saved summaries, rather than from folder-name guesses.
GUIDES = {
    '.': ('Where should I start?',
        'This is the history of the account-management research, from simple withdrawal examples to evaluations and replacement risk. Start with comparisons/legacy_25k_vs_50k/reserve_frontier_minimum for the paired daily-minimum/maximum reserve curves, march_failure_review for the explanation of synchronized failures, and reserve_frontier for the earlier daily-maximum study.',
        'Earlier folders use different assumptions. Some have unlimited live accounts; some assume instantly available replacements. Later studies impose cash budgets and then model evaluations. Compare settings within a study before comparing totals across studies.'),
    'comparisons': ('How do products and operating assumptions compare?',
        'The legacy_25k_vs_50k folder follows the comparison from instant account purchases to limited replacement supply, actual evaluations, and reserve/recovery diagnostics. This folder is a navigation container, not a separate experiment.',
        'Product comparisons include account rules and costs as well as the nominal account size.'),
    COMPARE: ('Which account size and withdrawal/replacement approach works best in the model?',
        'The answer changes with replacement availability and the cash objective. Instant supply favors aggressive extraction. Evaluation constraints make survival and cash financing matter. Daily minimum led ongoing cash in the broad pipeline search; the later daily-maximum frontier was conditional on that fixed withdrawal mechanism.',
        'Read reserve_frontier_minimum for the paired daily withdrawal frontiers, march_failure_review for the failure/recovery traces, pipeline_capacity for broader policy rankings, and reserve_frontier for the earlier maximum-policy study. The historical studies reuse the same market data.'),
    COMPARE+'/reserve_by_policy': ('What reserve works best for each withdrawal and purchase policy?',
        'This matched 25K/50K search finds that the preferred reserve depends on the withdrawal rule, purchase schedule, budget and whether closing cash is counted. Aggressive replacement policies can produce high cash when replacement accounts are immediately available.',
        'There is no evaluation delay here. This is the instant-supply reference for the later replacement studies; its winners do not prove that enough real replacements can be produced.'),
    COMPARE+'/spare_shelf': ('How much does a limited monthly replacement supply hurt, and do spare accounts help?',
        'Limiting supply changes the preferred policy and reserve. A shelf of spares can bridge gaps, but it costs money and occupies funded-account capacity. The detailed folders show selected winners with an assumed three passes per month.',
        'Passes arrive at an assumed monthly rate; evaluations are not traded on the actual history here. The spares are paid, activated funded accounts. A smooth monthly supply is more dependable than the clustered successes and failures modeled later.'),
    COMPARE+'/eval_supply': ('Can evaluations traded on the strategy supply enough replacement PAs?',
        'Replacing the assumed pass rate with actual evaluations substantially weakens the earlier aggressive policies. Retuning withdrawals and reserves recovers much of the cash while using fewer funded accounts. Successful evaluations typically take weeks, and the waiting time varies with their start date.',
        'This earlier pipeline allows up to five evaluations at once and reserves capacity for them. Later pipeline_capacity explores more capacity and persistent demand. These results predate the strict first-check activation-or-forfeiture policy.'),
    COMPARE+'/pipeline_capacity': ('Is replacement capacity limiting profit, and does a larger or staggered evaluation pipeline help?',
        'More capacity helps, but the withdrawal policy still matters. In the main shared-seat comparison, daily minimum leads ongoing cash: about $597,317 for 25K and $582,835 for 50K. Monthly minimum leads total cash including the closing withdrawal. These are best tested bundles, including their different pipeline settings.',
        'shared_seats reserves one of 20 places for each live PA, activated spare, or in-flight evaluation. evals_outside_cap allows evaluations outside the PA cap and is a separate sensitivity. Older runs can wait for activation cash; the later reserve frontier uses first-check activation or forfeiture.'),
    COMPARE+'/reserve_frontier': ('With daily maximum fixed, where is the reserve survival boundary and how much cash does extra cushion defer?',
        'The 566 runs show a full-history March boundary between $6,780.10 and $6,780.11. This is cumulative cushion depletion, not one huge trade. Some 2024 starts need a tested $7,100 reserve in 25K to avoid deaths of PAs older than a year. Above the boundary, total cash is almost flat while ongoing cash declines. $5,700 leads ongoing cash on the full-history grid but loses the established book.',
        'Daily maximum and each product’s pipeline are fixed. Evaluations reserve seats and must activate at the next daily check or be forfeited. New accounts can still fail before accumulating their target cushion. This folder does not contain a full daily-minimum frontier.'),
    COMPARE+'/march_failure_review': ('Does minimum withdrawal reduce synchronized failure, and did replacements really restore the book quickly?',
        'At the same $6,700 reserve and pipeline, maximum loses all 20 PAs on March 30; minimum loses one in 25K and none in 50K. Minimum preserves balance differences and more equity. The maximum runs do not recover all 20 within a month. The 25K minimum cash winner instead activates 19 replacements in April after earlier March failures.',
        'The review contains 14 baseline replays and eight evaluation-supply interruptions. Low-reserve minimum winners can still lose the entire book. Large lifetime cash totals can hide zero remaining earning capacity when failure occurs near the end of the data.'),
    BLOCKED: ('How do the product comparisons change when each account holds one position at a time?',
        'legacy_25k_vs_50k here repeats comparisons/legacy_25k_vs_50k with blocked copying: an account copies a signal only while flat, instead of adding every signal on top of open positions. Each study keeps its non-blocking grid, budgets, fees and rules.',
        'The non-blocking tree is the preserved reference. Compare matching folders; only the execution rule differs. Studies are rerun in chain order, so a folder missing here has not been rerun yet.'),
    COMPARE_BLOCKED: ('Which account size and withdrawal/replacement approach works best when each account holds one position?',
        'So far reserve_by_policy and spare_shelf have been rerun. Blocking lowers cash in most matched settings. With instant supply the winners keep their shape (prompt replacement, maximum withdrawals, little or no reserve) and 25K leads 50K in every funded budget. Once supply is limited, winners switch to minimum withdrawals and buy far fewer accounts, and at 1–2 passes a month 50K leads in every budget.',
        'Remaining reruns, in order: eval_supply, pipeline_capacity, reserve_frontier, reserve_frontier_minimum, march_failure_review. Each blocked study reads its predecessor from this tree, never from the non-blocking one.'),
    COMPARE_BLOCKED+'/reserve_by_policy': ('What reserve works best for each withdrawal and purchase policy when each account holds one position?',
        'Across 2,936 settings run in both modes, blocking lowers total cash in 2,334 and raises it in 188; the other 414 lose the whole seed either way. Headline winners fall 11–49%. 25K with $1,000 + $200/month drops from $749,859 to $665,421 and still buys 531 PAs. 50K with $1,000 and no contributions falls from $530,386 to $268,478, and its winner switches to monthly purchases with maximum weekly withdrawals.',
        'There is no evaluation delay here: seats cost $200 / $250 and are available at once, so the high-turnover winners depend on that supply. 206 settings shared with the 25K blocked-copying optimization reproduce exactly, and no replayed winner account ever held two trades at once.'),
    COMPARE_BLOCKED+'/spare_shelf': ('How much does a limited monthly replacement supply hurt when each account holds one position, and do spare accounts help?',
        'Across 10,840 settings run in both modes, blocking lowers total cash in 7,468 and raises it in 1,832; the other 1,540 lose the seed either way. Limited supply cuts turnover sharply: 25K with $1,000 + $200/month earns $473,076 at 3 passes a month with 96 PAs bought, against $665,421 and 531 PAs with unlimited supply. At 1–2 passes a month 50K leads 25K in every budget; 25K catches up at 10 passes in the funded budgets and at 3 with $5,000 and no contributions, later than without blocking. Most winners hold no spares.',
        'Passes arrive at an assumed fixed monthly rate; evaluations are not traded here, which flatters replacement policies. 1,280 rows whose supply cannot bind reproduce the blocked reserve comparison exactly, including per-trade account assignments.'),
    'legacy_50k': ('What changed when the earlier 25K model was extended to 50K?',
        'operating_policies contains the first 50K operating search and matched 25K controls. The later comparisons/legacy_25k_vs_50k studies provide a broader paired search and introduce replacement supply.',
        'This is a navigation folder, not a separate simulation. Its operating study predates actual evaluation supply.'),
    'legacy_50k/operating_policies': ('How do 50K account mechanics and fees change withdrawal and purchasing choices?',
        'The 50K results depend on budget, purchase policy and reserve. The study separates ongoing cash from closing withdrawals and checks an alternative interpretation of later payout restrictions. Matched 25K controls reproduce the earlier model.',
        'Accounts can be purchased immediately here; no evaluation phase is modeled. The search is coarse plus local refinement, not every possible setting. The more extensive matched reserve comparison is in comparisons/legacy_25k_vs_50k/reserve_by_policy.'),
    'study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores': ('How much should be withdrawn monthly, and how much should remain in each PA?',
        'The best ongoing setting is a $750 monthly request with a $29,800 balance target, yielding about $371,497 net. The best closing-inclusive setting is monthly minimum at $30,000, yielding about $460,512. Maximizing cash already withdrawn and maximizing total including closing can select different policies.',
        'Historical 25K study: one new account monthly, without the later 20-live-account cap or evaluation supply. The target is a nominal balance, not a cushion above the failure floor.'),
    'study__full_rulebook__RR__withdrawal_cadence__monthly_purchases': ('Does checking for withdrawals daily, weekly or monthly improve extraction?',
        'Checking frequency changes the result and interacts with the amount rule and retained balance. Minimum means $500 per eligible check, not a monthly spending budget. A daily check can pull out money sooner but can also reduce survival.',
        'This is the historical uncapped monthly-purchase study and a narrow reserve band. Its winner is conditional on that band. Use the capped cash-budget cadence study for direct comparisons with later purchase policies.'),
    'study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets': ('Do the cadence findings hold under the same cash budgets and 20-live-PA limit?',
        'This provides the fairer bridge between the old cadence study and the purchase studies: shared settings reproduce exactly when the assumptions match. Funding and capacity constraints can change which withdrawal/purchase combination is attractive.',
        'There are 372 cadence settings across four funding scenarios, with separate fixed-withdrawal purchase comparisons. Replacement accounts are immediately available when affordable; evaluations are not modeled.'),
    'study__full_rulebook__RR__account_purchases__cash_budgets': ('When should new PAs be bought, and should payouts finance replacements or expansion?',
        'Faster buying is not automatically better: with limited seed money it can exhaust funding before accounts pay out. The main schedules compare one quarterly, monthly or weekly purchase. Two monthly purchases are an expansion comparison; replacement and reinvestment are separate policy families.',
        'The 132 saved candidates use cash budgets and a 20-live-account cap, with immediate funded-account supply. Some saved detailed winners are historical quarterly-three bundles, now excluded from the main schedule rankings. Consult REPORT.generated.md for the current grouping.'),
    'study__full_rulebook__RR__monthly_replacements__cap_20__cash_budgets': ('Does replacing dead PAs sooner improve ordinary monthly buying?',
        'Earlier replacement changes the path, but results depend on funding and withdrawals. In the small unfunded budget, some replacement settings spend the seed and fail, while monthly buying survives. Current-slot replacements can use an unfilled month’s purchase slot without cancelling future months.',
        '48 settings compare monthly and weekly controls with two replacement rules. Funded accounts are immediately available when affordable. Comparisons also change account start dates, so differences are not caused by waiting time alone.'),
    'sweeps': ('What did the early retained-balance sweeps find?',
        'These are historical reserve searches for fixed monthly withdrawals, with different trading tapes and grid resolutions. They show that the preferred balance depends on the tape and withdrawal rule; they are not the later evaluation-aware reserve frontier.',
        'File names identify RR or GG data, minimum/fixed or maximum withdrawals, and a coarse or fine grid. cushion_usd in these old files is the nominal retained balance; headroom_usd is the amount above the failure floor. No closing withdrawal is counted.'),
}

SINGLE = {
    'full_rulebook__hold__terminal_request': ('Can holding all profit and asking once at the end extract it?', 'One closing request is restricted by the configured payout rules, so retained trading profit and cash received can differ greatly.'),
    'full_rulebook__monthly_500__no_cushion__no_terminal': ('What happens with $500 monthly requests and no voluntary reserve?', 'This is the early configured-rulebook baseline. It extracts cash but leaves relatively few survivors; later studies investigate whether retaining a reserve improves that trade-off.'),
    'full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search': ('How does the baseline change when the cushion is re-optimized for rule changes?', 'The summary is the same fixed-policy baseline as the ordinary monthly-$500 folder. Additional adapted-search files examine re-optimization; do not read the baseline summary as the optimized winner.'),
    'full_rulebook__monthly_500__retain_30000__terminal_request': ('How does a $30,000 balance target affect monthly $500 withdrawals?', 'This example retains a voluntary buffer and also attempts a final permitted withdrawal. It separates cash received during trading from cash only extracted at closing.'),
    'full_rulebook__monthly_maximum__no_cushion__no_terminal': ('What happens when monthly withdrawals take all permitted excess without a voluntary reserve?', 'This is an aggressive extraction example. Read the cash and survival figures together; a high withdrawal rate is not evidence that the accounts remain durable.'),
    'legacy_rules__monthly_100__no_cushion__no_terminal': ('What happens with small $100 monthly withdrawals under the early partial rule model?', 'This is an early model-building example, not a current full-rulebook policy comparison. Only the historical minimum-balance and safety-net restrictions are enabled.'),
    'no_payout_rules__hold__no_terminal': ('How much trading profit can accumulate if nothing is withdrawn?', 'This is the hold benchmark. Trading profit can build in accounts while owner cash is negative because account purchases still cost money. Paper profit is not a withdrawal.'),
    'no_payout_rules__hold__terminal_idealized': ('What is the idealized cash result if all surviving profit can be withdrawn at the end?', 'This is a reference ceiling for the hold path. The closing withdrawal bypasses payout restrictions, so it should not be presented as a firm-permitted live outcome.'),
    'no_payout_rules__monthly_500__retain_26100__no_terminal': ('What does a voluntary $26,100 balance target do when payout restrictions are removed?', 'This isolates our withdrawal restraint from firm payout gates. Drawdown failure mechanics still apply even though payout restrictions are disabled.'),
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dollars(value):
    return f'${value:,.2f}'


def paragraph(text):
    return textwrap.fill(text, width=95)+'\n\n'


def section(label, text):
    return label+'\n'+paragraph(text)


def family_key(relative):
    choices = [key for key in GUIDES if key != '.' and
               (relative == key or relative.startswith(key+'/'))]
    return max(choices, key=len) if choices else None


def saved_run(folder, relative):
    s = read(folder/'summary.json')
    if 'book' not in s:
        # Reserve-frontier trace summaries use a compact schema.
        rule = s.get('withdrawal', 'maximum')
        question = f"What happened with {s['product'].replace('legacy_', '')} daily {rule} at a {dollars(s['headroom'])} reserve?"
        finding = (f"This full-history replay produced {dollars(s['ongoing'])} ongoing net cash and "
            f"{dollars(s['total'])} including closing. {s['alive']} PAs remained alive, with {s['deaths']} "
            f"deaths over the whole run. On March 30, {s['deaths_2026_03_30']} PAs failed.")
        if 'march30_pretrade_alive' in s:
            finding += f" There were {s['march30_pretrade_alive']} live PAs immediately before the March 30 event."
            if s['march30_pretrade_alive'] == 0:
                finding += ' Zero deaths that day therefore does not demonstrate survival: the book was already empty.'
        return question, finding, ('The reserve is above the frozen failure floor, not the nominal account balance. '
            'This is one detailed replay within the parent frontier; the pipeline stays fixed. Shared seats and first-check activation apply. '
            'Read the parent study for cash rankings, account-age effects and comparisons at similar actual retained capital.')
    book, cash = s['book'], s['cash']
    terminal = s.get('terminal', {})
    total = cash['owner_cash_position_usd']
    closing = terminal.get('received_usd', 0)
    ongoing = round(total-closing, 2)
    finding = (f"The saved run produced {dollars(ongoing)} net cash during operation; "
        f"{dollars(closing)} was received at closing, making {dollars(total)} combined net cash. "
        f"It opened {book['accounts_opened']} PAs in total and had {terminal.get('accounts_alive_at_horizon', book['accounts_alive_at_end'])} "
        'alive before any closing withdrawal. Net cash subtracts account/evaluation costs and excludes owner contributions.')
    if relative in SINGLE:
        q, conclusion = SINGLE[relative]
        return q, conclusion+' '+finding, ('Historical 25K example with one account bought each month and no live-account cap or evaluation stage. '
            'The saved configured rules apply; “no payout rules” does not remove drawdown failures.')
    experiment = read(folder/'experiment.json') if (folder/'experiment.json').exists() else {}
    config = experiment.get('run_config', {})
    if not config and (folder/'config.json').exists():
        config = read(folder/'config.json')
    policy = config.get('policy', {})
    acq = experiment.get('acquisition') or s.get('acquisition', {}).get('policy') or {}
    selection = ('ongoing cash' if 'best_ongoing' in folder.name else
                 'combined cash including the closing withdrawal')
    q = f'What does this saved selected setting for {selection} actually produce?'
    context = 'This is one selected run; compare alternatives in the parent study. “Best” means best among the settings tested at the time, not a guaranteed optimum.'
    if policy:
        cadence = {'calendar_month': 'monthly', 'daily': 'daily', 'weekly': 'weekly', 'never': 'no'}.get(policy['cadence'], policy['cadence'])
        rule = policy['amount_rule']
        amount = 'the permitted maximum' if rule == 'maximum' else ('the firm’s minimum' if rule == 'minimum' else dollars(policy['amount_usd']))
        target = policy.get('min_retained_balance_usd')
        context += f' It checks {cadence} and requests {amount} when eligible.'
        if target is not None:
            context += f' Its retained balance target is {dollars(target)} (nominal balance).'
    if acq:
        context += f" Funding is {dollars(acq['initial_cash_usd'])} initially plus {dollars(acq['monthly_contribution_usd'])} per later month; the PA cap is {acq['max_live_accounts']}."
        if acq.get('evaluation'):
            if acq.get('evaluations_reserve_seats', True):
                context += ' Live PAs, activated spares and evaluations share reserved capacity.'
            else:
                context += ' Evaluations run outside the PA cap; live PAs and activated spares still count toward it.'
            context += ' This older run permits waiting for activation cash.'
        elif acq.get('spare_capacity') is not None:
            context += f" Supply is an assumed {acq['passes_per_month']} passes per month, not traded evaluations."
        else:
            context += ' Funded accounts are immediately available when affordable; evaluations are absent.'
        if relative.startswith(BLOCKED+'/'):
            context += ' Each PA copies a signal only while flat (blocked copying).'
        if acq.get('name') == 'quarterly_three':
            context += ' This historical three-account quarterly batch is excluded from the parent’s newer main schedule rankings.'
    else:
        context += ' This earlier run buys one PA monthly without the later live-account cap or evaluation supply.'
    return q, finding, context


def march_run(folder):
    rows = read(folder.parent/'baselines.json')
    r = next(r for r in rows if r['label'] == folder.name)
    question = f"How did {r['product'].replace('legacy_', '')} daily {r['rule']} at {dollars(r['reserve'])} behave around March 2026?"
    finding = (f"Before the March 30 final trade, {r['pre_event_alive']} PAs were live with "
        f"{r['pre_event_distinct_balances']} distinct profit balances. {r['deaths_on_event']} died on that trade. "
        f"The run ended with {r['alive_at_end']} live PAs, {dollars(r['ongoing'])} ongoing net cash and "
        f"{dollars(r['total'])} including closing.")
    if r['pre_event_alive'] == 0:
        finding += ' Zero deaths on March 30 does not indicate safety here: the book had already emptied earlier in March.'
    context = ('This is a baseline replay, not one of the supply interruptions. ' +
        ('Passed evaluations must activate at the first daily check or be forfeited.' if r['first_check'] else
         'This reproduces the older policy, which could wait for activation cash.'))
    if 'winner' in folder.name:
        context += ' It uses the earlier minimum-policy winner’s own pipeline; the plain numbered reserve folders use the matched comparison pipeline.'
    return question, finding, context


def build(folder):
    relative = folder.relative_to(ROOT).as_posix()
    if relative == COMPARE+'/reserve_frontier_minimum':
        study = read(folder/'study.json')
        summaries = [s for s in study['window_summaries'] if s['window'] == 'full' and s['withdrawal'] == 'minimum']
        q = 'Does daily minimum improve the reserve cash/survival trade-off compared with daily maximum?'
        finding = f"The {len(study['rows']):,} runs compare both mechanisms on the same pipelines and reserve grid. "
        for s in summaries:
            finding += (f"For {s['product'].replace('legacy_', '')}, the best tested ongoing minimum-policy reserve is "
                f"{dollars(s['best_ongoing_headroom'])}, producing {dollars(s['best_ongoing'])} net and ending with "
                f"{s['best_ongoing_alive']} live PAs. ")
        finding += ('Minimum preserves more balance differences and can retain more actual capital at the same nominal reserve. '
            'The full-history cash plateau is around $4,000, while avoiding deaths of year-old PAs requires $6,800 for 25K and $6,700 for 50K. '
            'Some later starts need $7,000. Minimum does not win ongoing cash in every window. The cash winner and survival boundary are different choices.')
        context = ('This extends the maximum frontier with a matched minimum comparison. Both use shared seats and first-check activation. '
            'The pipelines are fixed, including seven-day evaluation starts for 25K; this is not a repeat of the old minimum winner’s separately optimized pipeline. '
            'Similar-capital matches are descriptive and cannot isolate a causal benefit from desynchronization. Historical windows overlap.')
    elif relative in GUIDES:
        q, finding, context = GUIDES[relative]
    elif folder.parent.name == 'march_failure_review':
        q, finding, context = march_run(folder)
    elif (folder/'summary.json').exists():
        q, finding, context = saved_run(folder, relative)
    else:
        raise ValueError(f'No reviewed description for {relative}')
    text = 'START HERE — '+q+'\n\n'
    text += section('Question answered', q)
    text += section('What we learned', finding)
    text += section('How to interpret it', context)
    if relative == 'sweeps':
        text += 'Best ongoing result in each saved sweep (within its own grid):\n'
        for p in sorted(folder.glob('*.json')):
            rows = read(p)['rows']
            best = max(rows, key=lambda r: r['pocket_usd'])
            text += f"- {p.name}: {dollars(best['pocket_usd'])} net at {dollars(best['cushion_usd'])} retained balance.\n"
        text += '\n'
    choices = [n for n in (report_path(folder, 'REPORT.generated.md').name, report_path(folder, 'REPORT.md').name,
        'report.txt', 'frontier.csv',
        'baselines.csv', 'all_settings.csv', 'candidates.csv', 'summary.json', 'snapshots.json',
        'march_trade_trace.csv', 'replacement_waits.csv', 'pipeline_daily.csv') if (folder/n).exists()]
    if choices:
        text += 'Files to open first\n'
        for name in choices[:4]:
            text += '- '+name+'\n'
        text += '\n'
    children = sorted(p for p in folder.iterdir() if p.is_dir())
    if children:
        text += 'Subfolders\n'
        for child in children:
            text += '- '+child.name+' (has its own START_HERE.txt)\n'
        text += '\n'
    if folder != ROOT:
        text += 'For the surrounding study, open ../START_HERE.txt.\n\n'
    text += 'Reading note: ongoing cash is received during trading, after costs. Total cash also includes any closing withdrawal. These are historical simulations, not forecasts.\n'
    return text


def main(scope=None):
    # A scope documents one subtree, e.g. comparisons_blocking, leaving every other guide alone.
    top = ROOT/scope if scope else ROOT
    folders = [top]+sorted(p for p in top.rglob('*') if p.is_dir())
    # Build everything before writing, so an unsupported schema cannot leave
    # only a subset of directories documented.
    documents = {p/NAME: build(p) for p in folders}
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    protected = {p: sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name != NAME}
    for p, text in documents.items():
        if p.exists() and not p.read_text(encoding='utf-8').startswith('START HERE — '):
            raise ValueError(f'Refusing to overwrite a reader-maintained file: {p}')
    for p, text in documents.items():
        p.write_text(text, encoding='utf-8')
    assert all(p.is_file() and sha(p) == digest for p, digest in protected.items())
    assert all((p/NAME).is_file() for p in folders)
    print(f'Wrote {len(documents)} folder guides; {len(protected)} pre-existing result files unchanged.')


if __name__ == '__main__':
    main(*sys.argv[1:])
