"""Audit saved study arithmetic and comparisons without overwriting results."""
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import config_from_payload
from pa_milky.provenance import input_digest

ROOT = Path(__file__).resolve().parents[1]/'results'


def main():
    failures=[]; counts={'economic_identities':0,'paired_scores':0,'csv_rows':0,'summary_cash':0,'matched_candidates':0}
    studies={p.parent.name:json.loads(p.read_text()) for p in ROOT.glob('study__*/study.json')}
    def check(ok, message):
        if not ok: failures.append(message)
    def walk(value, location):
        if isinstance(value, dict):
            required=['booked_net_trading_usd','firm_split_usd','retained_profit_usd','failed_positive_ledger_usd','failed_negative_ledger_usd','purchase_fees_usd','pocket_usd']
            if all(k in value for k in required):
                e=value
                residual=round(e[required[0]]-e[required[1]]-e[required[2]]-e[required[3]]+e[required[4]]-e[required[5]]-e[required[6]],2)
                check(residual==0, location+': economic identity')
                counts['economic_identities']+=1
            for k,v in value.items(): walk(v,location+'/'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value): walk(v,location+'/'+str(i))
    for p in ROOT.rglob('*.json'):
        walk(json.loads(p.read_text()),str(p.relative_to(ROOT)))
    for name,d in studies.items():
        check(input_digest(config_from_payload(d['config']))==d['inputs'],name+': input files changed')
        rows=d['rows']
        with (ROOT/name/'candidates.csv').open(newline='',encoding='utf-8') as f: saved=list(csv.DictReader(f))
        check(len(saved)==len(rows),name+': CSV length')
        for i,(r,c) in enumerate(zip(rows,saved)):
            for k,v in c.items():
                check(v==str(r[k]) if r[k] is not None else v=='',f'{name}: CSV row {i} field {k}')
            counts['csv_rows']+=1
            ongoing=r.get('ongoing_pocket_usd',r.get('ongoing_net_cash_usd'))
            total=r.get('combined_pocket_usd',r.get('combined_net_cash_usd'))
            check(round(ongoing+r['terminal_received_usd']-total,2)==0,name+': paired scores')
            counts['paired_scores']+=1
            if 'acquisition_config' in r:
                check(round(r['ending_owner_cash_usd']-r['owner_contributions_usd']-total,2)==0,name+': owner cash')
                check(r['minimum_owner_cash_usd']>=0,name+': negative cash')
                check(r['alive_before_terminal']<=r['acquisition_config']['max_live_accounts'],name+': live cap')
    amount=next(d for n,d in studies.items() if 'amount_x_cushion' in n)
    cadence=next(d for n,d in studies.items() if d['schema']=='pa_milky.cadence_study.v1')
    check(amount['config']==cadence['config'],'Amount/cadence base configs differ')
    def policy_key(r):
        p=dict(r['policy_config']);p.pop('name',None)
        return tuple(sorted(p.items()))
    lookup={policy_key(r):r for r in amount['rows']}
    for r in cadence['rows']:
        a=lookup.get(policy_key(r))
        if a:
            for k in ['ongoing_pocket_usd','terminal_received_usd','combined_pocket_usd','alive_before_terminal','path_fingerprint','booked_net_trading_usd','economics']:
                check(a[k]==r[k],f'Amount/cadence overlap {r["policy"]}/{r["retained_balance_usd"]}: {k}')
            counts['matched_candidates']+=1
    check(counts['matched_candidates']>0, 'No amount/cadence controls matched')
    capped=next((d for d in studies.values() if d['schema']=='pa_milky.budget_cadence_study.v1'),None)
    if capped:
        purchase=next(d for d in studies.values() if d['schema']=='pa_milky.acquisition_study.v1')
        def funded_key(r):
            p=dict(r['withdrawal_config']);p.pop('name',None)
            return (r['initial_cash_usd'],r['monthly_contribution_usd'],tuple(sorted(p.items())))
        funded_lookup={funded_key(r):r for r in capped['rows']}
        counts['funded_shared_controls']=0
        for r in purchase['rows']:
            if r['purchase_policy']!='monthly_one': continue
            new=funded_lookup[funded_key(r)]
            for k,v in r.items():
                if k not in ('withdrawal_policy','withdrawal_config'):
                    check(new[k]==v,'Capped cadence/purchase shared control: '+k)
            counts['funded_shared_controls']+=1
        check(counts['funded_shared_controls']==12,'Expected 12 funded shared controls')
    for p in ROOT.rglob('summary.json'):
        s=json.loads(p.read_text()); c=s['cash']; b=s['book']
        check(round(c.get('received_usd',c['withdrawn_usd'])-c['spent_on_accounts_usd']-c['owner_cash_position_usd'],2)==0,str(p)+': summary cash')
        check(b['accounts_alive_at_end']+b['accounts_dead']==b['accounts_opened'],str(p)+': account counts')
        counts['summary_cash']+=1
    lines=['# Saved-results consistency audit','', 'This audit checks saved arithmetic, CSV/JSON agreement, current input hashes and identical candidate settings. It does not rerun every simulation or certify every sentence in reader-written notes.', '', '## Checks', '']
    lines += [f'- {k.replace("_"," ")}: {v}' for k,v in counts.items()]
    lines += ['',f'Failures: {len(failures)}.']+[f'- {f}' for f in failures]
    lines += ['', '## Comparability', '', '| Family | Acquisition / capacity | Funding | Status |','|---|---|---|---|']
    for name,d in studies.items():
        funded='acquisition_config' in d['rows'][0]
        acquisition_label=(f"{len({r['purchase_policy'] for r in d['rows']})} policies; 20 live maximum" if 'account_purchases' in name else 'One monthly; 20 live maximum') if funded else 'One monthly; no live cap'
        report_file='REPORT.generated.md' if (ROOT/name/'REPORT.generated.md').exists() else 'REPORT.md'
        lines.append(f'| [{name}]({name}/{report_file}) | '+acquisition_label+' | '+('Four explicit budgets' if funded else 'Purchases not cash-constrained')+' | '+('Internally comparable within each budget' if funded else 'Historical uncapped experiment')+' |')
    lines += ['', 'The amount and cadence studies agree on their overlapping settings. The purchase study changes both capacity and funding, so its monthly rows are not controls for the earlier uncapped studies. Its withdrawal settings were selected from those uncapped searches; they are not established capped optima.', '', 'Other scenario results and cushion sweeps are historical experiments with deliberately different rulebooks, terminal treatments, policies and (for GG) tapes. They must not be ranked as one common-policy study. Older sweep JSON files do not embed complete configurations or input/engine hashes, so their exact provenance cannot be verified from the saved files alone.', '', '## Common 20-account comparison', '', 'The budget-matched cadence study adds 372 capped candidates and 12 explicit shared controls against the purchase study. Earlier amount/cushion and cadence results remain historical uncapped experiments answering their original questions. No wholesale rerun is required. The purchase shortlist is not automatically optimal over the wider capped cadence grid.', '', 'A binding live cap also changes the acquisition schedule when withdrawals change survival. Consequently, the existing fixed-cohort claim that hold bounds survival does not carry over automatically. A capped study must compare activation dates/trade identities and label its hold reference as a different portfolio when cohorts differ.', '', '## Reader reports', '', 'REPORT.md and report_breakdown.txt are reader-maintained and are never overwritten by the study runners. Reruns write REPORT.generated.md; on a new directory only, REPORT.md is also initialized. Reader notes remain tied to their original results until reviewed. In particular, the cadence breakdown describes the uncapped 22-survivor experiment.', '']
    (ROOT/'CONSISTENCY_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'counts':counts,'failures':failures},indent=2))
    return bool(failures)


if __name__=='__main__': raise SystemExit(main())
