# -*- coding: utf-8 -*-
import pytest
from datetime import timedelta as td

from aiorest_ws.utils.date.formatters import iso8601_repr
from aiorest_ws.utils.date.humanize_datetime import STRFDATETIME, \
    STRFDATETIME_REPL, datetime_formats, date_formats, time_formats, \
    humanize_strptime, humanize_timedelta


@pytest.mark.parametrize("value, expected", [
    (STRFDATETIME.match('d'), '%(d)s'),
    (STRFDATETIME.match('g'), '%(g)s'),
    (STRFDATETIME.match('G'), '%(G)s'),
    (STRFDATETIME.match('h'), '%(h)s'),
    (STRFDATETIME.match('H'), '%(H)s'),
    (STRFDATETIME.match('i'), '%(i)s'),
    (STRFDATETIME.match('s'), '%(s)s')
])
def test_STRFDATETIME_REPL(value, expected):
    assert STRFDATETIME_REPL(value) == expected


@pytest.mark.parametrize("value, expected", [
    (('iso-8601', ), 'YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]'),
])
def test_datetime_formats(value, expected):
    assert datetime_formats(value) == expected


@pytest.mark.parametrize("value, expected", [
    (('iso-8601', ), 'YYYY[-MM[-DD]]'),
    (('iso-8601', '%H:%M:%S'), 'YYYY[-MM[-DD]], hh:mm:ss'),
    (('iso-8601', '%I:%M:%S'), 'YYYY[-MM[-DD]], hh:mm:ss'),
    (('iso-8601', '%I:%M:%S:%f'), 'YYYY[-MM[-DD]], hh:mm:ss:uuuuuu'),
])
def test_date_formats(value, expected):
    assert date_formats(value) == expected


@pytest.mark.parametrize("value, expected", [
    (('iso-8601', ), 'hh:mm[:ss[.uuuuuu]]'),
    (('%Y-%m-%d', 'iso-8601', ), 'YYYY-MM-DD, hh:mm[:ss[.uuuuuu]]'),
    (('%y-%b-%d', 'iso-8601', ), 'YY-[Jan-Dec]-DD, hh:mm[:ss[.uuuuuu]]')
])
def test_time_formats(value, expected):
    assert time_formats(value) == expected


@pytest.mark.parametrize("value, expected", [
    ('%Y-%m-%d', 'YYYY-MM-DD'),
    ('%y-%b-%d', 'YY-[Jan-Dec]-DD'),
    ('%y-%B-%d', 'YY-[January-December]-DD'),
    ('%H:%M:%S', 'hh:mm:ss'),
    ('%I:%M:%S', 'hh:mm:ss'),
    ('%I:%M:%S:%f', 'hh:mm:ss:uuuuuu'),
    ('%a %H:%M:%S', '[Mon-Sun] hh:mm:ss'),
    ('%A %H:%M:%S', '[Monday-Sunday] hh:mm:ss'),
    ('%A %H:%M %p', '[Monday-Sunday] hh:mm [AM|PM]'),
    ('%A %H:%M %z', '[Monday-Sunday] hh:mm [+HHMM|-HHMM]'),
])
def test_humanize_strptime(value, expected):
    assert humanize_strptime(value) == expected


@pytest.mark.parametrize("value, kwargs, expected", [
    (td(days=1, hours=2, minutes=3, seconds=4), {},
     '1 day, 2 hours, 3 minutes, 4 seconds'),
    (td(days=1, seconds=1), {'display': 'minimal'}, '1d, 1s'),
    (td(days=1), {}, '1 day'),
    (td(days=0), {}, '0 seconds'),
    (td(seconds=1), {}, '1 second'),
    (td(seconds=10), {}, '10 seconds'),
    (td(seconds=30), {}, '30 seconds'),
    (td(seconds=60), {}, '1 minute'),
    (td(seconds=150), {}, '2 minutes, 30 seconds'),
    (td(seconds=1800), {}, '30 minutes'),
    (td(seconds=3600), {}, '1 hour'),
    (td(seconds=3601), {}, '1 hour, 1 second'),
    (td(seconds=19800), {}, '5 hours, 30 minutes'),
    (td(seconds=91800), {}, '1 day, 1 hour, 30 minutes'),
    (td(seconds=302400), {}, '3 days, 12 hours'),
    (td(seconds=0), {'display': 'minimal'}, '0s'),
    (td(seconds=0), {'display': 'short'}, '0 sec'),
    (td(seconds=0), {'display': 'long'}, '0 seconds'),
    (td(seconds=0), {'display': 'iso8601'}, iso8601_repr(td(seconds=0))),
    (td(hours=1, minutes=30), {'display': 'sql'}, '0 01:30:00'),
    (td(hours=1, minutes=30), {'display': 'h:i'}, '1:30')
])
def test_humanize_timedelta(value, kwargs, expected):
    assert humanize_timedelta(value, **kwargs) == expected
