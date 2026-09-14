"""Replacement service measured from actual deaths, including unfinished waits."""
from collections import Counter, deque
from datetime import datetime, timedelta
import math
import statistics


def replacement_records(result):
    """FIFO match deaths to explicitly recorded replacement deployments.

    Next-check service includes the normal midnight decision delay. Deaths at
    the last tape exit are retained as censored, even without another decision.
    """
    deaths=sorted((a.died_at,a.account_id) for a in result.accounts if a.died_at is not None)
    pending=deque(deaths)
    records=[]
    for event in result.acquisition.replacement_events:
        at=datetime.fromisoformat(event['at'])
        for _ in range(event['replacements']):
            died,account_id=pending.popleft()
            assert died<=at
            check=died.replace(hour=0,minute=0,second=0,microsecond=0)
            if check<died: check+=timedelta(days=1)
            records.append({'account_id':account_id,'died_at':died.isoformat(),
                'replaced_at':at.isoformat(),'wait_days':(at-died).total_seconds()/86400,
                'next_check':at==check,'censored':False})
    for died,account_id in pending:
        records.append({'account_id':account_id,'died_at':died.isoformat(),'replaced_at':None,
            'wait_days':(result.tape_last_exit-died).total_seconds()/86400,
            'next_check':False,'censored':True})
    return sorted(records,key=lambda r:(r['died_at'],r['account_id']))


def measure_pipeline(result):
    records=replacement_records(result)
    resolved=[r['wait_days'] for r in records if not r['censored']]
    days=result.acquisition.pipeline_daily
    # Integrate the daily state to the next boundary, clipped to the tape.
    duration=zero=occupied=0.0
    for i,d in enumerate(days):
        start=max(datetime.fromisoformat(d['at']),result.tape_first_entry)
        end=(datetime.fromisoformat(days[i+1]['at']) if i+1<len(days) else result.tape_last_exit)
        weight=max(0,(end-start).total_seconds()/86400)
        duration+=weight
        zero+=weight*(d['alive']==0)
        occupied+=weight*d['alive']
    financing=Counter(e['kind'] for e in result.acquisition.financing_events)
    passes=Counter(e.passed_at.strftime('%Y-%m') for e in result.acquisition.evaluations if e.passed_at)
    return {'deaths':len(records),'replacements_filled':len(resolved),
        'replacements_unfilled':sum(r['censored'] for r in records),
        'next_check_service':round(sum(r['next_check'] for r in records)/len(records),4) if records else None,
        'replacement_wait_median_days':round(statistics.median(resolved),2) if resolved else None,
        'replacement_wait_p95_days':round(sorted(resolved)[math.ceil(.95*len(resolved))-1],2) if resolved else None,
        'unfilled_account_days':round(sum(r['wait_days'] for r in records),2),
        'oldest_unfilled_days':round(max((r['wait_days'] for r in records if r['censored']),default=0),2),
        'zero_live_days':round(zero,2),'average_live_accounts':round(occupied/duration,2),
        'peak_subscriptions':max(d['subscriptions'] for d in days),
        'peak_in_flight':max(d['in_flight'] for d in days),
        'peak_passes_month':max(passes.values(),default=0),
        'activation_blocked_account_checks':financing['activation_blocked'],
        'renewals_unaffordable':financing['renewal_unaffordable'],
        'start_unaffordable_checks':financing['start_unaffordable'],
        'cash_blocked_days':len({e['at'] for e in result.acquisition.financing_events})}
