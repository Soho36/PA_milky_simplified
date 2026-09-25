"""Event-time measurements for a book built from zero through monthly purchases."""
from collections import Counter
from datetime import datetime


def add_months(start, months):
    index = start.year * 12 + start.month - 1 + months
    return datetime(index // 12, index % 12 + 1, 1)


def book_metrics(accounts, start, end):
    """Half-open observation interval; only positive-duration empty episodes.

    Purchases and deaths at an identical timestamp are netted. Initial zero
    before activation is excluded; a terminal empty spell is right-censored.
    """
    events = Counter()
    deaths = purchased = 0
    for a in accounts:
        born = datetime.fromisoformat(a['activated_at'])
        if born >= end:
            continue
        assert born >= start
        events[born] += 1
        purchased += 1
        if a['died_at']:
            died = datetime.fromisoformat(a['died_at'])
            if died < end:
                events[died] -= 1
                deaths += 1
    live = peak = 0
    previous = start
    first = None
    first20 = None
    empty_start = None
    empty_peak = 0
    empty_days = below5 = below10 = 0.0
    episodes = []
    for at, delta in sorted(events.items()):
        days = (at-previous).total_seconds()/86400
        if first is not None:
            empty_days += days * (live == 0)
            below5 += days * (live < 5)
            below10 += days * (live < 10)
        after = live + delta
        assert 0 <= after <= 20
        if live > 0 and after == 0:
            empty_start, empty_peak = at, peak
        if empty_start is not None and after > 0:
            if at > empty_start:
                episodes.append(dict(start=empty_start.isoformat(), end=at.isoformat(),
                                     days=(at-empty_start).total_seconds()/86400,
                                     historical_peak=empty_peak, censored=False))
            empty_start = None
        if first is None and after > 0:
            first = at
        peak = max(peak, after)
        if first20 is None and after == 20:
            first20 = at
        live, previous = after, at
    if first is not None:
        days = (end-previous).total_seconds()/86400
        empty_days += days * (live == 0)
        below5 += days * (live < 5)
        below10 += days * (live < 10)
    if empty_start is not None and end > empty_start:
        episodes.append(dict(start=empty_start.isoformat(), end=end.isoformat(),
                             days=(end-empty_start).total_seconds()/86400,
                             historical_peak=empty_peak, censored=True))
    assert abs(empty_days-sum(e['days'] for e in episodes)) < 1e-7
    assert live == purchased-deaths
    return dict(purchased=purchased, deaths=deaths, end_alive=live, peak_alive=peak,
                empty_episodes=len(episodes), empty_days=round(empty_days,6),
                continuous=len(episodes)==0, days_below5=round(below5,6), days_below10=round(below10,6),
                reached20=first20 is not None,
                first20_at=first20.isoformat() if first20 else '',
                days_to20=round((first20-start).total_seconds()/86400,6) if first20 else '',
                observed_days=round((end-start).total_seconds()/86400,6)), episodes
