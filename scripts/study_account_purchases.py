"""Compare acquisition policies with explicit owner cash budgets."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace, asdict
from datetime import datetime,timezone
from pathlib import Path
import csv,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from pa_milky.config import CONFIG_ROOT,load_config,to_payload
from pa_milky.loader import load_tape
from pa_milky.policy import WithdrawalPolicy
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.simulator import run_book
from pa_milky.economics import Economics
from pa_milky.provenance import input_digest,engine_digest,git_revision,sha256_file
from pa_milky.report import write_outputs
C=None
T=None


def initialize():
    global C,T
    C=load_config(CONFIG_ROOT/'scenarios/full_rulebook_monthly_500.json')
    T=load_tape(C)


def withdrawal_choices():
    return [WithdrawalPolicy(name='daily_minimum_retain_31900',cadence='daily',amount_rule='minimum',
                quantize_to_amount=False,min_retained_balance_usd=31900,terminal_withdrawal='firm_permitted'),
            WithdrawalPolicy(name='weekly_excess_retain_31600',cadence='weekly',amount_rule='maximum',
                quantize_to_amount=False,min_retained_balance_usd=31600,terminal_withdrawal='firm_permitted'),
            WithdrawalPolicy(name='monthly_minimum_retain_30000',cadence='calendar_month',amount_rule='minimum',
                quantize_to_amount=False,min_retained_balance_usd=30000,terminal_withdrawal='firm_permitted')]


def purchase_choices(initial,monthly):
    base=dict(initial_cash_usd=initial,monthly_contribution_usd=monthly,max_live_accounts=20)
    return [(name,AcquisitionPolicy(name=name,**base)) for name in
            ('monthly_one','quarterly_one','quarterly_three')]+[
            ('replace_one',AcquisitionPolicy(name='replace',replacement_target=1,**base)),
            ('replace_five',AcquisitionPolicy(name='replace',replacement_target=5,**base)),
            ('reinvest_50pct',AcquisitionPolicy(name='reinvest',reinvest_fraction=.5,**base)),
            ('reinvest_100pct',AcquisitionPolicy(name='reinvest',reinvest_fraction=1,**base)),
            ('reinvest_restart_50pct',AcquisitionPolicy(name='reinvest',reinvest_fraction=.5,restart_when_empty=True,**base)),
            ('reinvest_restart_100pct',AcquisitionPolicy(name='reinvest',reinvest_fraction=1,restart_when_empty=True,**base))]


def evaluate(job,details=False):
    label,acquisition,policy=job
    result=run_book(T,replace(C,policy=policy,scenario=f"purchase_study_{label}",brick_name=f"purchase_study_{label}"),acquisition=acquisition)
    economics=Economics.measure(result)
    cash=result.acquisition.summary()
    assert cash['cash_identity_residual_usd']==0 and economics.residual_usd==0
    assert cash['net_cash_created_usd']==result.pocket_usd
    terminal=round(sum(e.received_usd for e in result.terminal_payouts),2)
    rows={'purchase_policy':label,'withdrawal_policy':policy.name,
          'initial_cash_usd':acquisition.initial_cash_usd,'monthly_contribution_usd':acquisition.monthly_contribution_usd,
          'ongoing_net_cash_usd':round(result.pocket_usd-terminal,2),
          'terminal_received_usd':terminal,'combined_net_cash_usd':result.pocket_usd,
          'owner_contributions_usd':cash['owner_contributions_usd'],
          'ending_owner_cash_usd':cash['ending_owner_cash_usd'],
          'purchase_spend_usd':cash['purchase_spend_usd'],
          'accounts_bought':len(result.accounts),'alive_before_terminal':result.alive_at_horizon,
          'cash_limited_decisions':cash['cash_limited_decisions'],
          'capacity_limited_decisions':cash['capacity_limited_decisions'],
          'minimum_owner_cash_usd':min(e['cash_after_usd'] for e in result.acquisition.cash_events),
          'economics':economics.to_payload(),'acquisition_config':asdict(acquisition),
          'withdrawal_config':policy.to_payload()}
    return (rows,result) if details else rows


def table(rows):
    lines=['| Purchase policy | Withdrawal policy | Accounts | Alive | Purchase spend | Ongoing net cash | Total net cash | Ending owner cash |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['purchase_policy']} | {r['withdrawal_policy']} | {r['accounts_bought']} | "
                     f"{r['alive_before_terminal']} | ${r['purchase_spend_usd']:,.0f} | "
                     f"${r['ongoing_net_cash_usd']:,.2f} | ${r['combined_net_cash_usd']:,.2f} | ${r['ending_owner_cash_usd']:,.2f} |")
    return '\n'.join(lines)


def main():
    initialize()
    out=Path('results/study__full_rulebook__RR__account_purchases__cash_budgets')
    out.mkdir(parents=True,exist_ok=True)
    budgets=[(1000,0),(1000,200),(5000,0),(5000,200)]
    jobs=[(name,a,p) for initial,monthly in budgets for name,a in purchase_choices(initial,monthly) for p in withdrawal_choices()]
    rows=[]
    if '--reuse-rows' in sys.argv:
        cached=json.loads((out/'study.json').read_text(encoding='utf-8'))
        assert cached['inputs']==input_digest(C)
        assert cached['config']==to_payload(C)
        current=engine_digest()
        for name,entry in cached['engine']['files'].items():
            if name != 'report.py': assert current['files'][name]==entry, 'Computation changed; rerun without --reuse-rows'
        assert len(cached['rows'])==len(jobs)
        rows=cached['rows']
    else:
        with ProcessPoolExecutor(max_workers=4,initializer=initialize) as pool:
            for i,row in enumerate(pool.map(evaluate,jobs),1):
                rows.append(row)
                if i%10==0:print(f'Completed {i}/{len(jobs)}',flush=True)
    payload={'schema':'pa_milky.acquisition_study.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
             'config':to_payload(C),'inputs':input_digest(C),'engine':engine_digest(),
             'git_revision':git_revision(),'runner_sha256':sha256_file(Path(__file__)),
             'design':{'budgets':budgets,'max_live_accounts':20,'purchase_checks':'midnight daily',
                       'monthly_contributions_start':'second calendar month',
                       'quarterly_anchor':'every third month from tape start',
                       'reinvestment_seed_accounts':1,'restart_variants':'one replacement from available owner cash when empty','terminal_payouts_reinvested':False},'rows':rows}
    (out/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','acquisition_config','withdrawal_config')]
    with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report='# Account purchases under explicit cash budgets\n\n'
    report+='108 candidates: nine purchase policies x three fixed withdrawal policies x four funding scenarios. Full configured payout rules; processing delay off; RR tape.\n\n'
    for initial,monthly in budgets:
        family=[r for r in rows if r['initial_cash_usd']==initial and r['monthly_contribution_usd']==monthly]
        best=[max([r for r in family if r['purchase_policy']==label],key=lambda r:(r['combined_net_cash_usd'],r['ongoing_net_cash_usd']))
              for label,_ in purchase_choices(initial,monthly)]
        report+=f'## ${initial:,} starting cash; ${monthly:,}/month thereafter\n\n'
        report+=f"Every candidate receives ${family[0]['owner_contributions_usd']:,.0f} total contributions. Best tested withdrawal policy per purchase policy, ranked by terminal-inclusive net cash:\n\n"
        report+=table(sorted(best,key=lambda r:r['combined_net_cash_usd'],reverse=True))+'\n\n'
        # Persist both objective leaders, even when different policies win.
        for metric,kind in [('ongoing_net_cash_usd','ongoing'),('combined_net_cash_usd','terminal')]:
            winner=max(family,key=lambda r:(r[metric],r['ongoing_net_cash_usd']))
            report+=f"**{kind.capitalize()} objective leader:** {winner['purchase_policy']} / {winner['withdrawal_policy']}: ${winner[metric]:,.2f}. "
            job=(winner['purchase_policy'],AcquisitionPolicy(**winner['acquisition_config']),WithdrawalPolicy.from_payload(winner['withdrawal_config']))
            reproduced,result=evaluate(job,True)
            assert reproduced==winner
            folder=out/f'budget_{initial}_monthly_{monthly}__best_{kind}'
            write_outputs(result,folder)
            (folder/'experiment.json').write_text(json.dumps({'run_config':to_payload(result.config),'acquisition':winner['acquisition_config']},indent=2),encoding='utf-8')
            for filename,events in [('owner_cash.csv',result.acquisition.cash_events),('purchase_decisions.csv',result.acquisition.decisions)]:
                if events:
                    with (folder/filename).open('w',newline='',encoding='utf-8') as f:
                        w=csv.DictWriter(f,fieldnames=events[0].keys());w.writeheader();w.writerows(events)
            report+=f'[{kind.capitalize()}-cash leader ledger]({folder.name}/report.txt). '
        report+='\n\n'
    report+='## Reading the comparison\n\n'
    report+='The ranking changes with the budget: restarting reinvestment leads terminal-inclusive cash with $1,000 and no contributions; quarterly batches of three lead the other scenarios. The ongoing-cash objective can select a different withdrawal policy. Strict reinvestment loses its initial seat before receiving a payout and never restarts, so its -$200 result diagnoses startup dependence rather than the merits of the reinvestment fraction.\n\n'
    report+='Three quarterly purchases and one monthly purchase have the same planned purchase count per quarter, but enter different cohorts. Their difference combines entry timing, funding constraints, survival and capacity occupancy. It does not establish that quarterly buying is generally superior. Test alternative calendar phases, starting dates and live-account caps before treating these rankings as robust.\n\n'
    report+='Net cash is received payouts minus account fees, never owner contributions. Ending owner cash equals cumulative owner contributions plus net cash, and includes unused principal. '
    report+='Ongoing net cash excludes the final receipt. Live account paper balances are never purchase funds. Cash cannot go negative. Contributions are scheduled equally, even when unused; no $200 contribution is added in the opening month.\n\n'
    report+='Monthly buys one at each month boundary; quarterly buys one or three every third month. Missed scheduled buys expire. '
    report+='Replacement retries at midnight to maintain one or five live accounts, including the opening purchase. Strict reinvestment starts with one account and never restarts; the restart variants buy one replacement from available owner cash when the portfolio is empty. Both then spend 50% or 100% of cumulative received payouts on additional accounts; unused payout allocation carries forward. '
    report+='Other purchase policies may use both contributed cash and received payouts. All share a modelled capacity of 20 live accounts; it is not a verified firm limit. Capacity and funding blocks are in candidates.csv.\n\n'
    report+='Trades settle before requests and purchases. Purchases use only already-received payouts, with activation at the check time, so earlier entries are excluded. '
    report+='All account types are the same $200 seat. No evaluation cost, personal trading margin, or economic firm-failure model is added. '
    report+='All withdrawal policies begin requests in the second calendar month of each account. Midnight reinvestment can buy near the endpoint; the experiment does not add a hindsight stop-buying rule. Terminal proceeds are never reinvested.\n\n'
    report+='Changing acquisition changes cohorts and the offered book of trades, so the old fixed-acquisition hold fingerprint and reference capture are not comparable here. '
    report+='The withdrawal choices are held at previously tested settings; this is not a joint global optimization. Results are in-sample and conditional on the starting date, cash budget and capacity cap. '
    report+='Reproduce with `venv/Scripts/python.exe scripts/study_account_purchases.py`. Each leading run has an experiment.json containing both run configuration and acquisition policy; replay through run_book(..., acquisition=AcquisitionPolicy(...)).\n'
    (out/'REPORT.md').write_text(report,encoding='utf-8')
    print(report,flush=True)


if __name__=='__main__':main()
