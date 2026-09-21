"""Pure calculations for unrestricted, non-compounding realized RR curves."""
from collections import Counter
from datetime import datetime
from math import sqrt


def select_trades(tape, start, end):
    """Native entry priority; unfinished final positions still occupy their slot."""
    until = start
    selected = []
    for t in sorted(tape, key=lambda t:(t.entry_at,t.window_order,t.source_row,t.ticket)):
        if start <= t.entry_at < end and t.entry_at >= until:
            selected.append(t)
            until = t.exit_at
    return selected


def net_cents(trade, commission):
    return round(round(trade.gross_pnl_usd-commission,2)*100)


def daily_path(selected, dates, end, commission):
    changes = Counter()
    for t in selected:
        if t.exit_at < end:
            changes[t.exit_at.date().isoformat()] += net_cents(t,commission)
    running=0; values=[]
    for day in dates:
        running += changes[day]
        values.append(running/100)
    return values


def drawdowns(values):
    peak=0.0; out=[]
    for value in values:
        peak=max(peak,value)
        out.append(peak-value)
    return out


def curve_metrics(values, dates, start):
    dd=drawdowns(values)
    max_dd=max(dd,default=0)
    peak=0.0; peak_i=-1; active=None; episodes=[]
    for i,value in enumerate(values):
        if value >= peak-1e-8:
            if active is not None:
                active.update(end=dates[i],recovered=True,trading_dates=i-active['peak_index'])
                episodes.append(active); active=None
            peak=max(peak,value); peak_i=i
        else:
            if active is None:
                active=dict(peak_index=peak_i,peak_at=dates[peak_i] if peak_i>=0 else start[:10],
                            began=dates[i],depth=0.0)
            active['depth']=max(active['depth'],peak-value)
    if active is not None:
        active.update(end=dates[-1],recovered=False,trading_dates=len(values)-1-active['peak_index'])
        episodes.append(active)
    for e in episodes:
        e['calendar_days']=(datetime.fromisoformat(e['end'])-datetime.fromisoformat(e['peak_at'])).days
    result=dict(net_pnl=values[-1] if values else 0,max_drawdown=max_dd,
        worst_drawdown_at=dates[dd.index(max_dd)] if max_dd else None,
        longest_underwater_trading_dates=max((e['trading_dates'] for e in episodes),default=0),
        longest_underwater_calendar_days=max((e['calendar_days'] for e in episodes),default=0),
        unrecovered_at_end=bool(episodes and not episodes[-1]['recovered']),
        recovered_episodes=sum(e['recovered'] for e in episodes))
    padded=[0.0,*values]
    for width in (1,5,20):
        result[f'worst_{width}d_change']=min((padded[i]-padded[i-width] for i in range(width,len(padded))),default=0)
    return result,episodes


def first_markers(selected, budget, end, commission):
    """Fixed-floor markers use full MAE only for trades completed by the horizon."""
    pnl=0; peak=0; result={'closed_floor':None,'excursion_floor':None,'closed_peak_dd':None}
    for t in selected:
        if t.exit_at >= end:
            continue
        before=pnl/100
        pnl+=net_cents(t,commission)
        close=pnl/100; adverse=before+min(t.mae_usd,0)
        common=dict(trade_key=t.trade_key,window=t.window_id,entry=t.entry_at.isoformat(),
                    exit=t.exit_at.isoformat(),pnl_before=before,pnl_after=close)
        if result['closed_floor'] is None and close<=-budget:
            result['closed_floor']=dict(common,kind='close',interval_start=t.exit_at.isoformat())
        if result['excursion_floor'] is None and min(adverse,close)<=-budget:
            result['excursion_floor']=dict(common,kind='mae' if adverse<=-budget else 'close',
                interval_start=t.entry_at.isoformat() if adverse<=-budget else t.exit_at.isoformat())
        peak=max(peak,close)
        if result['closed_peak_dd'] is None and peak-close>=budget:
            result['closed_peak_dd']=dict(common,kind='realized_drawdown',interval_start=t.exit_at.isoformat())
    return result


def failure_metrics(components, markers, dates):
    """Each component is an independently funded seat; weights sum to one."""
    points=[markers[rr] for rr in components if markers[rr] is not None]
    total=len(components)
    same=Counter((m['window'],m['entry']) for m in points)
    result=dict(fraction_breached=len(points)/total,
        max_same_signal_fraction=max(same.values(),default=0)/total,
        recorded_death_dates=len({m['exit'][:10] for m in points}))
    for width in (1,5,20):
        recorded=possible=0
        for i,day in enumerate(dates):
            # Date comparisons are inclusive through the last covered observed day.
            last=dates[min(len(dates)-1,i+width-1)]
            recorded=max(recorded,sum(day<=m['exit'][:10]<=last for m in points))
            possible=max(possible,sum(m['interval_start'][:10]<=last and m['exit'][:10]>=day for m in points))
        result[f'max_recorded_{width}d_fraction']=recorded/total
        result[f'possible_{width}d_fraction']=possible/total
    return result


def pair_metrics(left,right):
    a=[left[0],*[left[i]-left[i-1] for i in range(1,len(left))]]
    b=[right[0],*[right[i]-right[i-1] for i in range(1,len(right))]]
    av=sum(a)/len(a); bv=sum(b)/len(b)
    denom=sqrt(sum((x-av)**2 for x in a)*sum((x-bv)**2 for x in b))
    corr=sum((x-av)*(y-bv) for x,y in zip(a,b))/denom if denom else None
    both=sum(x<0 and y<0 for x,y in zip(a,b)); either=sum(x<0 or y<0 for x,y in zip(a,b))
    da=drawdowns(left); db=drawdowns(right)
    ma=max(da); mb=max(db)
    deepa=[ma>0 and x>=ma*.5 for x in da]; deepb=[mb>0 and x>=mb*.5 for x in db]
    deep_union=sum(x or y for x,y in zip(deepa,deepb))
    return dict(daily_pnl_correlation=corr,joint_negative_days=both,
        negative_day_jaccard=both/either if either else None,
        joint_underwater_fraction=sum(x>0 and y>0 for x,y in zip(da,db))/len(da),
        deep_drawdown_jaccard=sum(x and y for x,y in zip(deepa,deepb))/deep_union if deep_union else None)
