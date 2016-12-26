# -*- coding: utf-8 -*-
import pytest
import datetime as dt

from aiorest_ws.conf import settings
from aiorest_ws.utils.date.timezone import UTC, ZERO, FixedOffset, \
    get_fixed_timezone, get_default_timezone, get_current_timezone, \
    get_current_timezone_name, localtime, now, is_aware, is_naive, \
    make_aware, make_naive, LocalTimezone, utc
from aiorest_ws.test.utils import override_settings

EAT = get_fixed_timezone(180)  # Africa/Nairobi
ICT = get_fixed_timezone(420)  # Asia/Bangkok
INVALID_TIMEZONE = get_fixed_timezone(0.777)


def test_utc_class():
    utc = UTC()
    assert utc.__repr__() == "<UTC>"
    assert utc.utcoffset(dt.timedelta(0)) == ZERO
    assert utc.tzname(dt.timedelta(0)) == "UTC"
    assert utc.dst(dt.timedelta(0)) == ZERO

try:
    # If pytz module has installed
    import pytz  # NOQA

    def test_get_default_timezone():
        timezone = get_default_timezone()
        assert timezone.zone == settings.TIME_ZONE

    def test_get_current_timezone():
        timezone = get_current_timezone()
        assert timezone.zone == settings.TIME_ZONE

    def test_get_current_timezone_name():
        timezone_name = get_current_timezone_name()
        assert timezone_name == settings.TIME_ZONE
except ImportError:
    # Otherwise test without it. Use LocalTimezone instances
    def test_get_default_timezone():
        timezone = get_default_timezone()
        assert isinstance(timezone, LocalTimezone)

    def test_get_current_timezone():
        timezone = get_current_timezone()
        assert isinstance(timezone, LocalTimezone)

    def test_get_current_timezone_name():
        timezone_name = get_current_timezone_name()
        assert isinstance(timezone_name, str)
        assert timezone_name == LocalTimezone().tzname(None)


@pytest.mark.parametrize("offset, name", [
    (None, None),
    (60, None),
    (None, 'offset'),
    (60, 'offset'),
])
def test_fixed_offset_class(offset, name):
    instance = FixedOffset(offset=offset, name=name)

    if offset:
        assert instance.utcoffset(None) == dt.timedelta(minutes=offset)
    if name:
        assert instance.tzname(None) == name
    assert instance.dst(None) == ZERO


@pytest.mark.parametrize("offset, name", [
    (1, "+0001"),
    (3600, "+6000"),
])
def test_get_fixed_timezone(offset, name):
    fixed_timezone = get_fixed_timezone(offset)
    assert fixed_timezone.utcoffset(None) == dt.timedelta(minutes=offset)
    assert fixed_timezone.tzname(None) == name


@pytest.mark.parametrize("offset, timedelta, name", [
    (dt.timedelta(seconds=1), dt.timedelta(0), "+0000"),
    (dt.timedelta(seconds=3600), dt.timedelta(0, 3600), "+0100"),
])
def test_get_fixed_timezone_with_timedelta(offset, timedelta, name):
    fixed_timezone = get_fixed_timezone(offset)
    assert fixed_timezone.utcoffset(None) == timedelta
    assert fixed_timezone.tzname(None) == name


def test_localtime():
    datetime_now = dt.datetime.utcnow().replace(tzinfo=utc)
    local_tz = LocalTimezone()
    local_now = localtime(datetime_now, local_tz)
    assert local_now.tzinfo == local_tz


@pytest.mark.parametrize("use_tz, func, expected", [
    (True, is_aware, True),
    (False, is_naive, True)
])
def test_now(use_tz, func, expected):
    with override_settings(USE_TZ=use_tz):
        assert func(now()) == expected


@pytest.mark.parametrize("value, expected", [
    (dt.datetime(2011, 9, 1, 13, 20, 30, tzinfo=EAT), True),
    (dt.datetime(2011, 9, 1, 13, 20, 30), False)
])
def test_is_aware(value, expected):
    assert is_aware(value) == expected


@pytest.mark.parametrize("value, expected", [
    (dt.datetime(2011, 9, 1, 13, 20, 30, tzinfo=EAT), False),
    (dt.datetime(2011, 9, 1, 13, 20, 30), True)
])
def test_is_naive(value, expected):
    assert is_naive(value) == expected


@pytest.mark.parametrize("value, timezone, is_dst, expected", [
    (dt.datetime(2011, 9, 1, 13, 20, 30), EAT, None,
     dt.datetime(2011, 9, 1, 13, 20, 30, tzinfo=EAT))
])
def test_make_aware(value, timezone, is_dst, expected):
    assert make_aware(value, timezone, is_dst) == expected


@pytest.mark.parametrize("value, timezone, is_dst, exc_class", [
    (dt.datetime(2011, 9, 1, 13, 20, 30, tzinfo=EAT), EAT, None, ValueError)
])
def test_make_aware_value_error(value, timezone, is_dst, exc_class):
    with pytest.raises(exc_class):
        make_aware(value, timezone, is_dst)


@pytest.mark.parametrize("value, timezone, expected", [
    (dt.datetime(2011, 9, 1, 13, 20, 30, tzinfo=EAT), EAT,
     dt.datetime(2011, 9, 1, 13, 20, 30)),
    (dt.datetime(2011, 9, 1, 17, 20, 30, tzinfo=ICT), EAT,
     dt.datetime(2011, 9, 1, 13, 20, 30)),
])
def test_make_naive(value, timezone, expected):
    assert make_naive(value, timezone) == expected


@pytest.mark.parametrize("value, timezone, exc_class", [
    (dt.datetime(2011, 9, 1, 13, 20, 30), INVALID_TIMEZONE, ValueError)
])
def test_make_naive_value_error(value, timezone, exc_class):
    with pytest.raises(exc_class):
        make_naive(value, timezone)
