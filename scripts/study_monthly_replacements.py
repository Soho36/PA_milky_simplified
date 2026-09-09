"""Monthly replacements: consume the current monthly slot or add purchases; matched controls."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from collections import deque
from pathlib import Path
from datetime import datetime,timezone
import csv,json
import study_account_purchases as purchases
from pa_milky.acquisition import AcquisitionPolicy
from pa_milky.provenance import input_digest,engine_digest,sha256_file
from pa_milky.config import to_payload
from pa_milky.study_reports import write_study_report

OUT=purchases.study_path(purchases.STUDY, 'replacements')
NAMES=('monthly_one','weekly_one','monthly_current_slot_replacements','monthly_plus_replacements')


def diagnostics(result):
    start=result.tape_first_entry.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    end=result.tape_last_exit
    # Birth/death event-time integral; zero-duration terminal events add no exposure.
    events=[]
    for a in result.accounts:
        events.append((a.activated_at,1))
        if a.died_at is not None and a.died_at<=end: events.append((a.died_at,-1))
    events.sort(key=lambda x:(x[0],x[1]))
    queue=deque();waits=[];alive=0;last=start;area=0.;below=0.;firstcap=None
    for at,delta in events+[(end,0)]:
        seconds=max(0,(at-last).total_seconds());area+=alive*seconds
        if alive<result.acquisition.policy.max_live_accounts:below+=seconds
        if delta<0:queue.append(at)
        if delta>0 and queue:waits.append((at-queue.popleft()).total_seconds()/86400)
        alive+=delta
        if alive==result.acquisition.policy.max_live_accounts and firstcap is None:firstcap=at
        last=at
    duration=(end-start).total_seconds()
    return {'average_live_accounts':round(area/duration,4) if duration else 0,
        'days_below_cap':round(below/86400,3),
        'first_cap_date':firstcap.isoformat() if firstcap else None,
        'matched_death_purchase_pairs':len(waits),'unmatched_deaths':len(queue),
        'mean_wait_days':round(sum(waits)/len(waits),4) if waits else None,
        'max_wait_days':round(max(waits),4) if waits else None,
        'unmatched_death_wait_days':round(sum((end-at).total_seconds()/86400 for at in queue),3),
        'replacement_purchases':sum(e['replacements'] for e in result.acquisition.replacement_events),
        'future_slots_owed_at_end':result.acquisition.future_slots_used}


def work(job):
    row,result=purchases.evaluate(job,True)
    row.update(diagnostics(result))
    return row


def main():
    purchases.initialize();profile=purchases.STUDY
    jobs=[(name,AcquisitionPolicy(name,initial,monthly,max_live_accounts=profile['max_live_accounts']),p)
          for initial,monthly in profile['budgets'] for name in NAMES for p in purchases.withdrawal_choices()]
    rows=[]
    with ProcessPoolExecutor(max_workers=profile['workers'],initializer=purchases.initialize) as pool:
        for i,r in enumerate(pool.map(work,jobs),1):
            rows.append(r)
            if i%12==0:print(f'Completed {i}/{len(jobs)}',flush=True)
    source=purchases.study_path(profile,'purchases')/'study.json'
    previous=json.loads(source.read_text())
    assert previous['config']==to_payload(purchases.C)
    assert previous['inputs']==input_digest(purchases.C)
    key=lambda r:(r['initial_cash_usd'],r['monthly_contribution_usd'],r['purchase_policy'],r['withdrawal_policy'])
    lookup={key(r):r for r in previous['rows']}
    controls=0
    for r in rows:
        if r['purchase_policy'] in ('monthly_one','weekly_one'):
            old=lookup[key(r)];assert all(r[k]==v for k,v in old.items()),key(r);controls+=1
    OUT.mkdir(parents=True,exist_ok=True)
    payload={'schema':'pa_milky.monthly_replacements.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
        'config':to_payload(purchases.C),'inputs':input_digest(purchases.C),'engine':engine_digest(),
        'study_profile':purchases.profile_provenance(profile),'runner_sha256':sha256_file(Path(__file__)),
        'control_source_sha256':sha256_file(source),'matching_controls':controls,'rows':rows}
    (OUT/'study.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    fields=[k for k in rows[0] if k not in ('economics','acquisition_config','withdrawal_config')]
    with (OUT/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    report=f'# Monthly growth with earlier replacements\n\n{len(rows)} candidates; {controls} monthly/weekly controls reproduce the existing purchase study exactly.\n\n'
    report+='The main question is whether earlier replacement improves monthly buying under the same funding, live cap and withdrawal settings. The weekly control also changes initial growth and cohort dates. None of these comparisons is proof that replacement delay alone caused a cash difference.\n\n'
    report+='## Policy definitions\n\nMonthly-one and weekly-one retain their existing schedules. **Current-slot replacements** replaces deaths at the next midnight check. If the current month has no successful scheduled purchase yet, the first successful replacement fills the current month slot. If the scheduled purchase already happened, replacements do not affect next month. **Plus replacements** retains monthly purchases and buys additional replacements. Both retry pending replacements daily when unaffordable; failures create no slot debt. Multiple deaths can trigger multiple replacements, limited by cash and capacity. A replacement account that dies creates a new replacement obligation.\n\n'
    report+='At the first-day monthly boundary, deaths are processed before purchases. A successful replacement fills the current slot, so no extra scheduled purchase is made that day. Multiple deaths may still receive multiple replacements. After a completed monthly purchase, later replacements never cancel future purchases. A skipped unaffordable monthly attempt expires as before, but a later successful replacement can fill that otherwise unused slot. Failed replacement attempts consume no slot. There are no purchases after terminal receipts. The former future-slot rule is retained only in archives/studies/monthly_replacements_future_slots.\n\n'
    report+='## Matched withdrawal comparisons\n\n'
    for initial,monthly in profile['budgets']:
        for policy in purchases.withdrawal_choices():
            family=[r for r in rows if (r['initial_cash_usd'],r['monthly_contribution_usd'],r['withdrawal_policy'])==(initial,monthly,policy.name)]
            report+=f'### ${initial:,} initial; ${monthly:,}/month; {policy.name}\n\n'+purchases.table(family)+'\n\n'
            report+='| Purchase policy | Average live | First at cap | Days below cap | Mean matched wait (days) | Unmatched deaths | Future slots owed |\n|---|---:|---|---:|---:|---:|---:|\n'
            for r in family:
                report+=f"| {r['purchase_policy']} | {r['average_live_accounts']} | {r['first_cap_date'] or 'never'} | {r['days_below_cap']} | {r['mean_wait_days']} | {r['unmatched_deaths']} | {r['future_slots_owed_at_end']} |\n"
            report+='\n'
    report+='## Reading the diagnostics\n\nAverage live accounts and days below cap integrate account births/deaths in event time from the common opening calendar-month boundary to tape end. They include ramp-up. Death-to-purchase waits pair each purchase with the oldest unmatched prior death (FIFO). For scheduled controls this is a descriptive vacancy measure, not a claim the purchase was caused by that death. Unmatched deaths are censored at the endpoint; their aggregate unresolved wait is in CSV, so a short matched mean alone cannot establish prompt replacement. Same-timestamp deaths are processed before purchases.\n\n'
    report+='All results use the existing Legacy 25K rules, no processing delay, and one permitted terminal request. Net cash excludes contributions and deducts fees. These variants change replacement timing or expand buying; neither guarantees the same total purchases or cohort exposure as monthly-one. Historical in-sample results only.\n'
    write_study_report(OUT,report)
    print(f'All {controls} shared controls matched. {OUT}/REPORT.md',flush=True)


if __name__=='__main__':main()
