"""Replay headline winners and expose turnover and the owner-loss accounting."""
from dataclasses import asdict
from pathlib import Path
import json

import study_legacy_reserve_comparison as study
from pa_milky.config import PROJECT_ROOT, to_payload
from pa_milky.provenance import sha256_file, engine_digest, input_digest
from pa_milky.report import write_outputs

PRODUCT_LABEL = {'legacy_25k': '25K', 'legacy_50k': '50K'}
PURCHASE_LABEL = {'monthly_one': 'Monthly', 'weekly_one': 'Weekly',
                  'monthly_current_slot_replacements': 'Monthly + replacements'}
CADENCE_LABEL = {'calendar_month': 'monthly', 'weekly': 'weekly', 'daily': 'daily'}


def main():
    spec = json.loads(study.SPEC_PATH.read_text(encoding='utf-8'))
    out = PROJECT_ROOT / spec['output']
    payload = json.loads((out/'study.json').read_text(encoding='utf-8'))
    assert spec == payload['spec']
    study.sim.initialize()
    assert engine_digest() == payload['engine']
    assert input_digest(study.sim.C['legacy_25k']) == payload['inputs']
    assert {k: to_payload(v) for k, v in study.sim.C.items()} == payload['configs']
    rows = payload['rows']
    winners = []
    replayed = {}
    strict_rows = {}
    for i, m in spec['budgets']:
        for score in study.SCORES:
            for prod in spec['products']:
                group = [r for r in rows if (r['product'], r['initial_cash'], r['monthly_funding']) == (prod, i, m)]
                r = study.best(group, score)
                key = tuple(r['job'])
                if key not in replayed:
                    actual, result = study.sim.evaluate(key, detail=True)
                    assert all(actual[k] == r[k] for k in r if k != 'job'), 'Winner replay drift'
                    folder = out / f'{prod}__budget_{i}_{m}__best_{score}'
                    write_outputs(result, folder)
                    (folder/'experiment.json').write_text(json.dumps({
                        'run_config': to_payload(result.config),
                        'acquisition': asdict(result.acquisition.policy)}, indent=2), encoding='utf-8')
                    replayed[key] = folder.name
                    strict_rows[key] = study.sim.evaluate((*key[:-1], True))
                    print(f'Verified {prod} {i}+{m} {score}: {r[score]:,.2f}', flush=True)
                winners.append({**r, 'objective': score, 'ledger': replayed[key]})

    text = '# What the broader reserve comparison changes\n\n'
    text += ('The earlier $31,900 reserve was conditional on the tested operating setup. '
             'This paired search allows each purchase/withdrawal/cadence family to choose '
             'its own reserve, with identical headroom coverage for the two account sizes. '
             'Use the [complete policy tables](REPORT.generated.md) for every family; '
             'this page explains the headline winners and their turnover.\n\n'
             '**These are in-sample results under the inherited payout model.** '
             'They do not establish future returns or an optimum under the optional stricter '
             'post-payout-six balance interpretation. Account fees differ ($200 / $250), '
             'so this is an account-type-and-cost comparison.\n\n'
             '## Best complete tested bundles: terminal-inclusive cash\n\n'
             '| Budget | Product | Purchases | Withdrawal / checks | Reserve | Ongoing | Total | Bought / alive |\n'
             '|---|---|---|---|---:|---:|---:|---:|\n')
    for r in winners:
        if r['objective'] != 'total':
            continue
        text += f"| ${r['initial_cash']:,} + ${r['monthly_funding']:,}/mo | {PRODUCT_LABEL[r['product']]} | {PURCHASE_LABEL[r['acquisition']]} | {r['withdrawal']} / {CADENCE_LABEL[r['cadence']]} | ${r['reserve']:,.0f} | ${r['ongoing']:,.2f} | ${r['total']:,.2f} | {r['accounts']} / {r['alive']} |\n"
    text += ('\n## Where the ongoing-cash winner differs\n\n'
             'Only product/budget pairs with a different selected bundle are listed here. '
             'For the others, the same tested bundle leads both objectives.\n\n'
             '| Budget | Product | Purchases | Withdrawal / checks | Reserve | Ongoing | Total | Bought / alive |\n'
             '|---|---|---|---|---:|---:|---:|---:|\n')
    for r in winners:
        if r['objective'] != 'ongoing':
            continue
        terminal_winner = next(x for x in winners if (x['product'], x['initial_cash'],
            x['monthly_funding'], x['objective']) == (r['product'], r['initial_cash'], r['monthly_funding'], 'total'))
        if r['job'] == terminal_winner['job']:
            continue
        text += f"| ${r['initial_cash']:,} + ${r['monthly_funding']:,}/mo | {PRODUCT_LABEL[r['product']]} | {PURCHASE_LABEL[r['acquisition']]} | {r['withdrawal']} / {CADENCE_LABEL[r['cadence']]} | ${r['reserve']:,.0f} | ${r['ongoing']:,.2f} | ${r['total']:,.2f} | {r['accounts']} / {r['alive']} |\n"
    text += ('\n## What supports those cash results?\n\n'
             'A 20-live-account cap does not limit cumulative purchases to 20. Low reserves '
             'combined with prompt replacement can turn this into repeated withdrawal and '
             'replacement, rather than a stable book of mature accounts. Ending with 20 alive '
             'does not by itself establish low turnover or robust survival.\n\n'
             'A selected reserve equal to the frozen floor means zero voluntary headroom, '
             'not permission to ignore the firm\'s payout gates or withdraw below its floor.\n\n'
             'The economic ledger records **booked deficits not funded by the owner**: '
             'negative account profit that is excluded from the owner\'s losses. This is '
             'a descriptive ledger quantity, not observed firm losses, cash financing '
             'or a valuation of limited liability. '
             'The killing excursion is unbooked; see the '
             '[economic definitions](../../../../ECONOMIC_EFFECTS.md). '
             'Purchase fees below are already deducted from net cash.\n\n'
             '| Budget | Product | Accounts bought | Purchase fees | Booked deficits not funded by owner | Deficits / total cash | Ledger |\n'
             '|---|---|---:|---:|---:|---:|---|\n')
    for r in winners:
        if r['objective'] != 'total':
            continue
        e = r['economics']
        deficit = e['booked_deficits_not_funded_by_owner_usd']
        ratio = f"{100*deficit/r['total']:.1f}%" if r['total'] > 0 else 'n/a'
        text += f"| ${r['initial_cash']:,} + ${r['monthly_funding']:,}/mo | {PRODUCT_LABEL[r['product']]} | {r['accounts']} | ${e['purchase_fees_usd']:,.2f} | ${deficit:,.2f} | {ratio} | [Accounts and payouts]({r['ledger']}/report.txt) |\n"
    text += ('\nThat ratio is descriptive; it does not establish that profitability depends '
             'on the deficit amount. Removing limited liability could change subsequent '
             'funding, purchases and trading paths. It is not a re-optimized no-subsidy counterfactual. '
             'Large turnover makes the assumed immediate PA availability, fixed seat cost and '
             'absence of an evaluation phase especially material.\n\n'
             '## Same winners under the stricter later-payout interpretation\n\n'
             'Keep every selected operating setting fixed, but enforce the account-specific '
             'minimum balance after payout six and later. This can change future funding, '
             'cohorts and deaths, not just the final receipt. These are **sensitivity results, '
             'not re-optimized strict-rule winners**.\n\n'
             '| Budget | Product | Inherited total | Stricter total | Change | Stricter bought / alive |\n'
             '|---|---|---:|---:|---:|---:|\n')
    for r in winners:
        if r['objective'] != 'total':
            continue
        s = strict_rows[tuple(r['job'])]
        text += f"| ${r['initial_cash']:,} + ${r['monthly_funding']:,}/mo | {PRODUCT_LABEL[r['product']]} | ${r['total']:,.2f} | ${s['total']:,.2f} | ${s['total']-r['total']:,.2f} | {s['accounts']} / {s['alive']} |\n"
    text += ('\n## Fixed daily-minimum policy: best total-scoring reserve\n\n'
             'Example budget: $1,000 initial plus $200/month. Each row keeps the withdrawal '
             'family and cadence fixed, then selects the reserve within the named purchase policy. '
             'The complete report covers all four budgets and both objectives.\n\n'
             '| Product | Purchases | Selected reserve | Ongoing | Total | Bought / alive | Equally best tested reserves |\n'
             '|---|---|---:|---:|---:|---:|---:|\n')
    for r in payload['best_by_policy']:
        if (r['initial_cash'], r['monthly_funding'], r['withdrawal'], r['cadence'], r['objective']) != (1000, 200, 'minimum', 'daily', 'total'):
            continue
        text += f"| {PRODUCT_LABEL[r['product']]} | {PURCHASE_LABEL[r['acquisition']]} | ${r['reserve']:,.0f} | ${r['ongoing']:,.2f} | ${r['total']:,.2f} | {r['accounts']} / {r['alive']} | {len(r['tied_best_reserves'])} |\n"
    text += ('\n## Matched monthly-purchase reference\n\n'
             'Daily minimum withdrawals, headroom $6,800: reserve $31,900 for 25K and '
             '$56,900 for 50K. This holds the operating settings fixed, in contrast to the '
             'separately selected bundles above.\n\n'
             '| Budget | 25K total | 50K total | 50K minus 25K |\n|---|---:|---:|---:|\n')
    for i, m in spec['budgets']:
        pair = {r['product']: r for r in rows if (r['initial_cash'], r['monthly_funding'],
            r['acquisition'], r['withdrawal'], r['cadence'], r['headroom']) == (i, m, 'monthly_one', 'minimum', 'daily', 6800)}
        a, b = pair['legacy_25k']['total'], pair['legacy_50k']['total']
        text += f'| ${i:,} + ${m:,}/mo | ${a:,.2f} | ${b:,.2f} | ${b-a:,.2f} |\n'
    text += ('\n## How to interpret a selected reserve\n\n'
             'The old daily-minimum study tested up to $32,100. Reserves $31,900, $32,000 '
             'and $32,100 tied on total cash; $31,900 had the highest ongoing cash among '
             'those ties. It was not a uniquely optimal balance. See the '
             '[historical table and operating notes](HOW_THIS_STUDY_WORKS.md).\n\n'
             'The new [best-by-policy file](best_by_policy.csv) records exact ties and '
             'explicit tested reserves within 1% of each best positive score. These need '
             'not form a continuous band. A boundary winner is conditional on the tested '
             'limits; a flat loss across reserves means no useful reserve was found, '
             'not that the smallest displayed reserve is a sound choice.\n\n'
             'Best-complete-bundle comparisons answer which tested combination made more '
             'cash on this tape. They must not be described as a reserve-only improvement '
             'or evidence that a larger account always performs better. Before using high-turnover '
             'leaders operationally, the unresolved payout interpretation and acquisition '
             'assumptions are the next material questions to test.\n\n'
             'Regenerate this explanation and the verified winner ledgers with '
             '`scripts/explain_legacy_reserve_comparison.py` after the main study. Existing '
             '`FINDINGS.md` remains reader-owned; `FINDINGS.generated.md` is refreshed.\n')
    (out/'FINDINGS.generated.md').write_text(text, encoding='utf-8')
    if not (out/'FINDINGS.md').exists():
        (out/'FINDINGS.md').write_text(text, encoding='utf-8')
    (out/'winner_analysis.json').write_text(json.dumps({
        'study_sha256': sha256_file(out/'study.json'),
        'explainer_sha256': sha256_file(Path(__file__)),
        'verified_unique_replays': len(replayed), 'winners': winners,
        'strict_fixed_policy_sensitivity': list(strict_rows.values())}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
