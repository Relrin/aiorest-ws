# -*- coding: utf-8 -*-
"""
Functions to parse datetime objects.
"""
# We're using regular expressions rather than time.strptime because:
# - They provide both validation and parsing.
# - They're more flexible for datetimes.
# - The date/datetime/time constructors produce friendlier error messages.
import datetime
import re

from aiorest_ws.utils.date.timezone import utc, get_fixed_timezone

__all__ = [
    'date_re', 'time_re', 'datetime_re', 'standard_duration_re',
    'iso8601_duration_re', 'parse_date', 'parse_time', 'parse_datetime',
    'parse_timedelta'
]

date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)

time_re = re.compile(
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
)

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)

standard_duration_re = re.compile(
    r'^'
    r'(?:(?P<days>-?\d+) (days?, )?)?'
    r'((?:(?P<hours>\d+):)(?=\d+:\d+))?'
    r'(?:(?P<minutes>\d+):)?'
    r'(?P<seconds>\d+)'
    r'(?:\.(?P<microseconds>\d{1,6})\d{0,6})?'
    r'$'
)

# Support the sections of ISO 8601 date representation that are accepted by
# timedelta
iso8601_duration_re = re.compile(
    r'^(?P<sign>[-+]?)'
    r'P'
    r'(?:(?P<days>\d+(.\d+)?)D)?'
    r'(?:T'
    r'(?:(?P<hours>\d+(.\d+)?)H)?'
    r'(?:(?P<minutes>\d+(.\d+)?)M)?'
    r'(?:(?P<seconds>\d+(.\d+)?)S)?'
    r')?'
    r'$'
)


def parse_date(value):
    """
    Parses a string and return a datetime.date.

    Raises ValueError if the input is well formatted but not a valid date.
    Returns None if the input isn't well formatted.
    """
    match = date_re.match(value)
    if match:
        kw = {k: int(v) for k, v in iter(match.groupdict().items())}
        return datetime.date(**kw)


def parse_time(value):
    """
    Parses a string and return a datetime.time.

    This function doesn't support time zone offsets.

    Raises ValueError if the input is well formatted but not a valid time.
    Returns None if the input isn't well formatted, in particular if it
    contains an offset.
    """
    match = time_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw = {k: int(v) for k, v in iter(kw.items()) if v is not None}
        return datetime.time(**kw)


def parse_datetime(value):
    """
    Parses a string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raises ValueError if the input is well formatted but not a valid datetime.
    Returns None if the input isn't well formatted.
    """
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = get_fixed_timezone(offset)
        kw = {k: int(v) for k, v in iter(kw.items()) if v is not None}
        kw['tzinfo'] = tzinfo
        return datetime.datetime(**kw)


def parse_timedelta(value):
    """
    Parse a string into a timedelta object.
    """
    string = value.strip()

    if string == "":
        raise TypeError("'%s' is not a valid time interval" % string)
    # This is the format we get from sometimes Postgres, sqlite,
    # and from serialization
    d = re.match(
        r'^((?P<days>[-+]?\d+) days?,? )?(?P<sign>[-+]?)(?P<hours>\d+):'
        r'(?P<minutes>\d+)(:(?P<seconds>\d+(\.\d+)?))?$',
        str(string)
    )
    if d:
        d = d.groupdict(0)
        if d['sign'] == '-':
            for k in 'hours', 'minutes', 'seconds':
                d[k] = '-' + d[k]
        d.pop('sign', None)
    else:
        # This is the more flexible format
        d = re.match(
            r'^((?P<weeks>-?((\d*\.\d+)|\d+))\W*w((ee)?(k(s)?)?)(,)?\W*)?'
            r'((?P<days>-?((\d*\.\d+)|\d+))\W*d(ay(s)?)?(,)?\W*)?'
            r'((?P<hours>-?((\d*\.\d+)|\d+))\W*h(ou)?(r(s)?)?(,)?\W*)?'
            r'((?P<minutes>-?((\d*\.\d+)|\d+))\W*m(in(ute)?(s)?)?(,)?\W*)?'
            r'((?P<seconds>-?((\d*\.\d+)|\d+))\W*s(ec(ond)?(s)?)?)?\W*$',
            str(string)
        )
        if not d:
            raise TypeError("'%s' is not a valid time interval" % string)
        d = d.groupdict(0)

    return datetime.timedelta(**dict(((k, float(v)) for k, v in d.items())))


def parse_duration(value):
    """
    Parses a duration string and returns a datetime.timedelta.
    The preferred format for durations in Django is '%d %H:%M:%S.%f'.
    Also supports ISO 8601 representation.
    """
    match = standard_duration_re.match(value)
    if not match:
        match = iso8601_duration_re.match(value)
    if match:
        kw = match.groupdict()
        sign = -1 if kw.pop('sign', '+') == '-' else 1
        if kw.get('microseconds'):
            kw['microseconds'] = kw['microseconds'].ljust(6, '0')
        kw = {k: float(v) for k, v in kw.items() if v is not None}
        return sign * datetime.timedelta(**kw)
