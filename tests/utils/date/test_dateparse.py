# -*- coding: utf-8 -*-
import datetime as dt
import pytest

from aiorest_ws.utils.date import dateparse
from aiorest_ws.utils.date.humanize_datetime import humanize_timedelta
from aiorest_ws.utils.date.timezone import utc, get_fixed_timezone


@pytest.mark.parametrize("value, expected", [
    ("00:00:00.000", dt.time(0, 0, 0, 0)),
    ("1:30:55.150", dt.time(1, 30, 55, 150000)),
    ("0:5:0", dt.time(0, 5, 0, 0)),
    ("0:0:5", dt.time(0, 0, 5, 0)),
    ("0:0:0.5", dt.time(0, 0, 0, 500000)),
])
def test_parse_time(value, expected):
    assert dateparse.parse_time(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("2000-01-01", dt.date(2000, 1, 1)),
    ("2000-01-1", dt.date(2000, 1, 1)),
    ("2000-1-01", dt.date(2000, 1, 1)),
    ("2000-1-1", dt.date(2000, 1, 1)),
])
def test_parse_date(value, expected):
    assert dateparse.parse_date(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("2000-01-01 00:00:00.000", dt.datetime(2000, 1, 1)),
    ("2000-01-1 00:00:00.000", dt.datetime(2000, 1, 1)),
    ("2000-1-01 00:00:00.000", dt.datetime(2000, 1, 1)),
    ("2000-1-1 00:00:00.000", dt.datetime(2000, 1, 1)),
    ("2000-1-1 00:00:00.000", dt.datetime(2000, 1, 1, 0, 0, 0, 0)),
    ("2000-1-1 1:30:55.150", dt.datetime(2000, 1, 1, 1, 30, 55, 150000)),
    ("2000-1-1 0:5:0", dt.datetime(2000, 1, 1, 0, 5, 0, 0)),
    ("2000-1-1 0:0:5", dt.datetime(2000, 1, 1, 0, 0, 5, 0)),
    ("2000-1-1 0:0:0.5", dt.datetime(2000, 1, 1, 0, 0, 0, 500000)),
    ("2000-01-01T00:00:00.000", dt.datetime(2000, 1, 1)),
])
def test_parse_datetime(value, expected):
    assert dateparse.parse_datetime(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("2000-01-01 00:00:00.000Z", dt.datetime(2000, 1, 1, tzinfo=utc)),
    ("2000-01-01T00:00:00.000Z", dt.datetime(2000, 1, 1, tzinfo=utc)),
    ("2000-01-01 00:00:00.000+01",
     dt.datetime(2000, 1, 1, tzinfo=get_fixed_timezone(60))),
    ("2000-01-01T00:00:00.000+01",
     dt.datetime(2000, 1, 1, tzinfo=get_fixed_timezone(60))),
])
def test_parse_datetime_with_timezone(value, expected):
    result = dateparse.parse_datetime(value)
    if result.tzinfo == utc:
        assert result.tzinfo == expected.tzinfo
    else:
        result_offset = result.tzinfo._FixedOffset__offset
        expected_offset = expected.tzinfo._FixedOffset__offset
        assert result_offset == expected_offset


@pytest.mark.parametrize("value, expected", [
    ("1 day", dt.timedelta(1)),
    ("2 days", dt.timedelta(2)),
    ("1 d", dt.timedelta(1)),
    ("1 hour", dt.timedelta(0, 3600)),
    ("1 hours", dt.timedelta(0, 3600)),
    ("1 hr", dt.timedelta(0, 3600)),
    ("1 hrs", dt.timedelta(0, 3600)),
    ("1h", dt.timedelta(0, 3600)),
    ("1wk", dt.timedelta(7)),
    ("1 week", dt.timedelta(7)),
    ("1 weeks", dt.timedelta(7)),
    ("2 wks", dt.timedelta(14)),
    ("1 sec", dt.timedelta(0, 1)),
    ("1 secs", dt.timedelta(0, 1)),
    ("1 s", dt.timedelta(0, 1)),
    ("1 second", dt.timedelta(0, 1)),
    ("1 seconds", dt.timedelta(0, 1)),
    ("1 minute", dt.timedelta(0, 60)),
    ("1 min", dt.timedelta(0, 60)),
    ("1 m", dt.timedelta(0, 60)),
    ("1 minutes", dt.timedelta(0, 60)),
    ("1 mins", dt.timedelta(0, 60)),
    ("1.5 days", dt.timedelta(1, 43200)),
    ("3 weeks", dt.timedelta(21)),
    ("4.2 hours", dt.timedelta(0, 15120)),
    (".5 hours", dt.timedelta(0, 1800)),
    ("1 hour, 5 mins", dt.timedelta(0, 3900)),
    ("-2 days", dt.timedelta(-2)),
    ("-1 day 0:00:01", dt.timedelta(-1, 1)),
    ("-1 day, -1:01:01", dt.timedelta(-2, 82739)),
    ("-1 w, 2 d, -3 h, 4 min, -5 sec", dt.timedelta(-5, 11045)),
    ("0 seconds", dt.timedelta(0)),
    ("0 days", dt.timedelta(0)),
    ("0 weeks", dt.timedelta(0)),
    (humanize_timedelta(dt.timedelta(0)), dt.timedelta(0)),
    (humanize_timedelta(dt.timedelta(0), 'minimal'), dt.timedelta(0)),
    (humanize_timedelta(dt.timedelta(0), 'short'), dt.timedelta(0)),
    ('  50 days 00:00:00   ', dt.timedelta(50)),
])
def test_parse_timedelta(value, expected):
    assert dateparse.parse_timedelta(value) == expected


@pytest.mark.parametrize("value, exc_type", [
    ("2 ws", TypeError),
    ("2 ws", TypeError),
    ("2 ds", TypeError),
    ("2 hs", TypeError),
    ("2 ms", TypeError),
    ("2 ss", TypeError),
    ("", TypeError),
    (" ", TypeError),
    (" hours", TypeError),
])
def test_parse_timedelta_raises_exception(value, exc_type):
    with pytest.raises(exc_type):
        dateparse.parse_timedelta(value)
