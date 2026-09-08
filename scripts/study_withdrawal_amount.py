"""Run the amount x cushion study; independent simulations use worker processes."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import csv
from dataclasses import replace
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pa_milky.config import CONFIG_ROOT, load_config, to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.policy_study import annotate_against_benchmark, measure, policies
from pa_milky.provenance import input_digest, engine_digest, git_revision, sha256_file
from pa_milky.simulator import run_book
from pa_milky.report import write_outputs
from pa_milky.study_reports import write_study_report
from pa_milky.study_config import load_study_profile, study_path, study_policies, profile_provenance
STUDY = load_study_profile()

CONFIG = None
TRADES = None


def initialize():
    global CONFIG, TRADES
    CONFIG = load_config(study_path(STUDY, 'scenario'))
    TRADES = load_tape(CONFIG)


def work(job):
    policy, level, stage = job
    return {**measure(TRADES, CONFIG, policy, level), "stage": stage}


def cushion(row):
    if row['retained_balance_usd'] is None: return "none"
    return f"${row['retained_balance_usd']:,.0f}"


def table(rows):
    lines = ["| Policy | Retained balance | Ongoing net cash | Terminal receipt | Combined net cash "
             "| Accounts | Alive | Trading-neutral | Ceiling capture |",
             "|---|---:|---:|---:|---:|---:|---:|:-:|---:|"]
    for r in rows:
        capture = "n/a" if r['ceiling_capture'] is None else f"{r['ceiling_capture']:.2%}"
        lines.append(f"| {r['policy']} | {cushion(r)} | ${r['ongoing_pocket_usd']:,.2f} | "
                     f"${r['terminal_received_usd']:,.2f} | ${r['combined_pocket_usd']:,.2f} | "
                     f"{int(r['economics']['purchase_fees_usd'] / CONFIG.purchase_fee_usd)} | {r['alive_before_terminal']} | {'yes' if r['trading_neutral'] else 'no'} | {capture} |")
    return "\n".join(lines)


def ceiling_section(rows, benchmark):
    """State, in its own numbers, the reference the capture column is scored against."""
    tested = [r for r in rows if r['stage'] != 'benchmark']
    neutral = [r for r in tested if r['trading_neutral']]
    richer = [r for r in tested if r['earnings_vs_benchmark_usd'] > 0]
    best = max(tested, key=lambda r: r['combined_pocket_usd'])
    text = "## Extraction ceiling\n\n"
    text += (f"The {benchmark['policy']} benchmark makes no withdrawal during trading, so no account "
             f"dies from one and no candidate outlives it. Its path books "
             f"${benchmark['booked_net_trading_usd']:,.2f} of trading earnings, and emptying that path "
             f"completely -- nothing left standing in live accounts, no profit split -- would put "
             f"${benchmark['book_ceiling_usd']:,.2f} in the pocket. Ceiling capture scores combined net "
             f"cash against that one number, so candidates are read on a fixed yardstick instead of "
             f"each against the smaller path its own withdrawals left it.\n\n")
    text += ("Outliving the benchmark is impossible; out-earning it is not. An account that dies early "
             "sits out whatever the benchmark went on to trade, and that stretch can lose money, so a "
             "capture above 100% is recorded rather than treated as an error. ")
    if richer:
        top = max(richer, key=lambda r: r['earnings_vs_benchmark_usd'])
        text += (f"{len(richer)} of {len(tested)} tested settings do out-earn it, the largest by "
                 f"${top['earnings_vs_benchmark_usd']:,.2f} ({top['policy']} at {cushion(top)}), so "
                 f"the benchmark is a reference path here, not the earnings maximum.\n\n")
    else:
        text += (f"None of the {len(tested)} tested settings out-earn it, so on this tape the reference "
                 f"path is the earnings maximum as well. That is an observed result, not a property of "
                 f"the rulebook.\n\n")
    text += (f"Trading-neutral means every account took exactly the trades it took under the benchmark. "
             f"It is decided on a per-account fingerprint of trade counts, booked results and killing "
             f"trade, never on the earnings total, which two different paths can share. "
             f"{len(neutral)} of {len(tested)} tested settings qualify. Best capture is "
             f"{best['ceiling_capture']:.2%} ({best['policy']} at {cushion(best)}), leaving "
             f"${best['unextracted_usd']:,.2f} unextracted -- ${best['firm_split_usd']:,.2f} to the "
             f"firm's split and ${best['profit_after_terminal_usd']:,.2f} still standing in live "
             f"accounts. The benchmark captures {benchmark['ceiling_capture']:.2%} of its own ceiling: "
             f"one permitted request per account strands "
             f"${benchmark['profit_after_terminal_usd']:,.2f} of its equity.\n\n")
    text += ("Both columns are properties of this tape and this monthly acquisition cadence. Capture "
             "is an accounting ratio, not a probability of success, and not a comparison against any "
             "alternative anyone could actually run.\n")
    return text


def findings(rows):
    ongoing = max(rows, key=lambda r:r['ongoing_pocket_usd'])
    closing = max(rows, key=lambda r:r['combined_pocket_usd'])
    ties = [r for r in rows if r['policy']==closing['policy'] and
            r['combined_pocket_usd']==closing['combined_pocket_usd']]
    levels = ", ".join(f"${r['retained_balance_usd']:,.0f}" for r in ties)
    text = "\n## What the experiment says\n\n"
    text += f"The ongoing-cash leader is {ongoing['policy']} at ${ongoing['retained_balance_usd']:,.0f}, "
    text += f"with ${ongoing['ongoing_pocket_usd']:,.2f} and {ongoing['alive_before_terminal']} survivors. "
    text += f"The closing-cash leader is {closing['policy']} at ${closing['retained_balance_usd']:,.0f}, "
    text += f"with ${closing['combined_pocket_usd']:,.2f}, including ${closing['terminal_received_usd']:,.2f} at exit.\n\n"
    for label, best in (("ongoing-cash", ongoing), ("closing-cash", closing)):
        if best['trading_neutral']:
            text += f"The {label} leader is trading-neutral: its withdrawals cost no trade. "
        else:
            text += (f"The {label} leader is not trading-neutral: its withdrawals changed which "
                     f"trades were taken, moving booked trading earnings by "
                     f"${best['earnings_vs_benchmark_usd']:,.2f} against the benchmark path, and it "
                     f"captures {best['ceiling_capture']:.2%} of the ceiling. ")
    text = text.rstrip(" ") + "\n\n"
    text += f"The closing leader ties at these tested retained balances: {levels}. "
    text += "A tie in closing cash can still hide different cash timing. The first table selects only one representative per family.\n\n"
    text += "Minimum monthly requests are fundamentally different from a $500 backlog entitlement: "
    text += "missed monthly requests do not accumulate into larger future withdrawals. "
    text += "This experiment identifies policy bundles, not a pure causal effect of the nominal target. "
    text += "The local refinement is not exhaustive, and survivor cliffs make exact winning thresholds fragile.\n\n"
    text += "### Nearby tested settings for the two leaders\n\n"
    selected=[]
    for best in (ongoing,closing):
        selected += [r for r in rows if r['policy']==best['policy'] and
                     r['retained_balance_usd'] is not None and
                     abs(r['retained_balance_usd']-best['retained_balance_usd'])<=300]
    text += table(selected)+"\n"
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', default=STUDY['_source'])
    parser.add_argument('--workers', type=int, default=STUDY['workers'])
    parser.add_argument('--out', type=Path, default=study_path(STUDY, 'amount'))
    args = parser.parse_args()
    if args.workers < 1: parser.error('workers must be positive')
    initialize()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    floor = CONFIG.trailing_floor_balance_usd
    levels = [None] + [floor + value for value in STUDY['amount']['headroom_grid']]
    choices = study_policies(STUDY)
    jobs = [(p, level, 'coarse') for p in choices for level in levels]
    jobs.append((WithdrawalPolicy(name='hold'), None, 'benchmark'))
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize) as pool:
        for row in pool.map(work, jobs):
            rows.append(row)
            if len(rows)%20 == 0: print(f"Coarse: {len(rows)}/{len(jobs)}", flush=True)
        seen = {(r['policy'], r['retained_balance_usd']) for r in rows}
        refined = []
        for p in choices:
            family = [r for r in rows if r['policy']==p.name]
            for metric in ('ongoing_pocket_usd','combined_pocket_usd'):
                best = max(family, key=lambda r:r[metric])
                center = best['retained_balance_usd']
                if center is None: continue
                for offset in range(-STUDY['amount']['refinement_radius'],STUDY['amount']['refinement_radius']+1,STUDY['amount']['refinement_step']):
                    level = center+offset
                    key = (p.name,level)
                    if level >= floor and key not in seen:
                        seen.add(key)
                        refined.append((p,level,'local_refinement'))
        for i,row in enumerate(pool.map(work,refined),1):
            rows.append(row)
            if i%20 == 0: print(f"Refinement: {i}/{len(refined)}",flush=True)
    benchmark = next(r for r in rows if r['stage'] == 'benchmark')
    annotate_against_benchmark(rows, benchmark)
    rows.sort(key=lambda r:(r['policy'], -1 if r['retained_balance_usd'] is None else r['retained_balance_usd']))
    payload = {'schema':'pa_milky.amount_cushion_study.v1',
               'generated_utc':datetime.now(timezone.utc).isoformat(),
               'study_profile':profile_provenance(STUDY),'config':to_payload(CONFIG),'inputs':input_digest(CONFIG),
               'engine':engine_digest(),'git_revision':git_revision(),
               'runner_sha256':sha256_file(Path(__file__)),
               'benchmark':{'policy':benchmark['policy'],
                            'booked_net_trading_usd':benchmark['booked_net_trading_usd'],
                            'book_ceiling_usd':benchmark['book_ceiling_usd'],
                            'ceiling_definition':'pocket identity with zero retained profit and zero '
                                                 'profit split, taken on the no-withdrawal path. That '
                                                 'path bounds survival, because a withdrawal only ever '
                                                 'lowers a balance, but it does not bound earnings: '
                                                 'trades an early death avoids can be losing ones',
                            'neutrality_test':'per-account fingerprint of trade count, booked gross and '
                                              'commission, and killing trade; not equality of totals'},
               'design':{'coarse_retained_balances':levels, 'local_refinement_step':STUDY['amount']['refinement_step'],
                         'local_refinement_radius':STUDY['amount']['refinement_radius'], 'objectives':['ongoing_pocket_usd','combined_pocket_usd'],
                         'terminal':'one firm-permitted request, voluntary cushion released',
                         'selection':'in-sample; local refinement around each family/objective coarse winner'},
               'rows':rows}
    (out/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','policy_config')]
    with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        writer.writerows({k:r[k] for k in fields} for r in rows)
    best_ongoing=[];best_combined=[]
    for p in choices:
        family=[r for r in rows if r['policy']==p.name]
        best_ongoing.append(max(family,key=lambda r:r['ongoing_pocket_usd']))
        best_combined.append(max(family,key=lambda r:r['combined_pocket_usd']))
    best_ongoing.sort(key=lambda r:r['ongoing_pocket_usd'],reverse=True)
    best_combined.sort(key=lambda r:r['combined_pocket_usd'],reverse=True)
    report = "# Withdrawal amount x cushion\n\n"
    report += f"{len(rows)} candidates, configured full payout rulebook (processing delay off), {CONFIG.strategy} tape. "
    report += "One new account monthly; identical trading path for each candidate's two endpoint scores.\n\n"
    report += ceiling_section(rows, benchmark)
    report += "\n## Best tested cushion per policy: ongoing cash\n\n"+table(best_ongoing)
    report += "\n\n## Best tested cushion per policy: cash including terminal request\n\n"+table(best_combined)
    report += "\n\n## Hold benchmark\n\n"+table([r for r in rows if r['policy']=='hold'])
    report += "\n\n## Design and interpretation\n\n"
    report += "Fixed targets accrue backlog and permit partial requests after caps; they are not monthly ceilings. "
    report += "The legacy control rounds to whole $500 blocks. Minimum requests $500 monthly without backlog; "
    report += "maximum requests everything permitted above the voluntary cushion. A $250 target can build enough backlog for the $500 minimum.\n\n"
    report += "All net cash deducts the same purchase fees and applicable split. Terminal scoring releases the voluntary cushion "
    report += "and makes one request through the same rulebook; it does not turn paper profit into unrestricted cash. "
    report += "Alive counts are before terminal withdrawal. The two scores are alternative objectives, not independent simulations.\n\n"
    report += "The coarse headroom grid is recorded in the study profile, plus no cushion. "
    report += f"Each policy's coarse winner is refined within ${STUDY['amount']['refinement_radius']:,} in ${STUDY['amount']['refinement_step']:,} steps. "
    report += "This local search can miss other peaks; winning settings are in-sample, not validated operating recommendations. "
    report += "Acquisition cadence, withdrawal cadence, execution assumptions and tape remain fixed.\n\n"
    report += "Reproduce from project root: `venv/Scripts/python.exe scripts/study_withdrawal_amount.py`. "
    report += "See study.json for embedded config, candidate policies, exact grids, input/engine hashes and accounting; candidates.csv for all scores.\n"
    report += findings(rows)
    for metric, label in [('ongoing_pocket_usd', 'best_ongoing'), ('combined_pocket_usd', 'best_terminal')]:
        best = max(rows, key=lambda r: r[metric])
        policy = WithdrawalPolicy.from_payload(best['policy_config'])
        config = replace(CONFIG, policy=policy, scenario=f'amount_cushion_study_{label}',
                         brick_name=f'amount_cushion_study_{label}')
        result = run_book(TRADES, config)
        assert result.pocket_usd == best['combined_pocket_usd']
        write_outputs(result, out/label)
        (out/label/'config.json').write_text(json.dumps(to_payload(config), indent=2), encoding='utf-8')
    report += "\n## Reproduced leading runs\n\n[Ongoing-cash leader](best_ongoing/report.txt) and [closing-cash leader](best_terminal/report.txt) include account/payout ledgers and embedded config.json files runnable with the normal CLI --config option.\n"
    write_study_report(out, report)
    print(report,flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
