"""The study clock.

Source timestamps are read as Europe/Tallinn local wall-clock labels, the
convention the parent study used. Because the labels are *already* in that
zone, a trading day is simply the label's own calendar date -- attaching the
zone does not move it. What the zone buys is validation: a label that falls in
a spring-forward gap never existed, and one in an autumn fold is ambiguous, so
both are worth detecting rather than silently trusting.

The modelled session runs 01:00 to 23:59 local on one calendar date. Following
the parent, that window describes the session; it is not a filter that deletes
authoritative completed fills.

Windows Python ships no IANA database, so a minimal Europe/Tallinn is provided
and ``zoneinfo`` is preferred whenever a real database is installed. The EU
rules implemented here cover the whole 2020-2026 tape.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TIMEZONE_NAME = "Europe/Tallinn"
SESSION_OPEN = time(1, 0)
SESSION_CLOSE = time(23, 59)

HOUR = timedelta(hours=1)
EET = timedelta(hours=2)
EEST = timedelta(hours=3)


def _last_sunday(year: int, month: int, day: int, hour: int) -> datetime:
    value = datetime(year, month, day, hour)
    return value - timedelta(days=(value.weekday() + 1) % 7)


class EuropeTallinn(tzinfo):
    """Modern Europe/Tallinn rules, with deterministic fold handling.

    Ported from the parent study so the two projects share one clock.
    """

    key = TIMEZONE_NAME

    @staticmethod
    def transitions(year: int) -> tuple[datetime, datetime]:
        # EU clocks advance at 01:00 UTC: 03:00 EET -> 04:00 EEST.
        # They retreat at 01:00 UTC: 04:00 EEST -> 03:00 EET.
        return _last_sunday(year, 3, 31, 3), _last_sunday(year, 10, 31, 4)

    def utcoffset(self, value: datetime | None) -> timedelta | None:
        if value is None:
            return None
        naive = value.replace(tzinfo=None)
        start, end = self.transitions(naive.year)
        if start <= naive < start + HOUR:  # spring gap
            return EEST if value.fold else EET
        if end - HOUR <= naive < end:  # autumn repeated hour
            return EET if value.fold else EEST
        if start + HOUR <= naive < end - HOUR:
            return EEST
        return EET

    def dst(self, value: datetime | None) -> timedelta | None:
        offset = self.utcoffset(value)
        return None if offset is None else offset - EET

    def tzname(self, value: datetime | None) -> str | None:
        offset = self.utcoffset(value)
        if offset is None:
            return None
        return "EEST" if offset == EEST else "EET"


def get_timezone() -> tzinfo:
    """Prefer a real IANA database; fall back to the built-in rules."""

    try:
        return ZoneInfo(TIMEZONE_NAME)
    except (ZoneInfoNotFoundError, KeyError):
        return EuropeTallinn()


TALLINN = get_timezone()


def localize(naive: datetime, *, fold: int = 0) -> datetime:
    """Attach the study zone to a naive wall-clock label."""

    if naive.tzinfo is not None:
        raise ValueError("expected a naive wall-clock label")
    return naive.replace(tzinfo=TALLINN, fold=fold)


def label_anomaly(naive: datetime) -> str | None:
    """Name the DST problem with a wall-clock label, if it has one.

    ``nonexistent`` labels fall inside the spring-forward gap and never
    happened. ``ambiguous`` labels fall inside the autumn fold and happened
    twice; the study takes the first occurrence.
    """

    start, end = EuropeTallinn.transitions(naive.year)
    bare = naive.replace(tzinfo=None)
    if start <= bare < start + HOUR:
        return "nonexistent"
    if end - HOUR <= bare < end:
        return "ambiguous"
    return None


def trading_day(moment: datetime) -> date:
    """The trading-day identifier for a moment.

    The labels are Europe/Tallinn wall-clock already, so the trading day is the
    label's own calendar date. PA profit and loss is credited on the *exit*, so
    callers pass the exit label.
    """

    return moment.date()


def in_session(moment: datetime) -> bool:
    """Whether a moment falls inside the modelled 01:00-23:59 session."""

    return SESSION_OPEN <= moment.time() <= SESSION_CLOSE
