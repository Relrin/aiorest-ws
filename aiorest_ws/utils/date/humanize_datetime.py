# -*- coding: utf-8 -*-
"""
Helper functions that convert strftime formats into more readable
representations.
"""
import datetime
import re

from aiorest_ws.conf.global_settings import ISO_8601
from aiorest_ws.utils.date.formatters import iso8601_repr

__all__ = (
    'STRFDATETIME', 'STRFDATETIME_REPL',
    'date_formats', 'datetime_formats', 'time_formats',
    'humanize_strptime', 'humanize_timedelta',
)

STRFDATETIME = re.compile('([dgGhHis])')


def STRFDATETIME_REPL(match):
    return '%%(%s)s' % match.group()


def datetime_formats(formats):
    format = ', '.join(formats).replace(
        ISO_8601, 'YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]'
    )
    return humanize_strptime(format)


def date_formats(formats):
    format = ', '.join(formats).replace(ISO_8601, 'YYYY[-MM[-DD]]')
    return humanize_strptime(format)


def time_formats(formats):
    format = ', '.join(formats).replace(ISO_8601, 'hh:mm[:ss[.uuuuuu]]')
    return humanize_strptime(format)


def humanize_strptime(format_string):
    # Note that we're missing some of the locale specific mappings that
    # don't really make sense
    mapping = {
        "%Y": "YYYY",
        "%y": "YY",
        "%m": "MM",
        "%b": "[Jan-Dec]",
        "%B": "[January-December]",
        "%d": "DD",
        "%H": "hh",
        "%I": "hh",  # Requires '%p' to differentiate from '%H'
        "%M": "mm",
        "%S": "ss",
        "%f": "uuuuuu",
        "%a": "[Mon-Sun]",
        "%A": "[Monday-Sunday]",
        "%p": "[AM|PM]",
        "%z": "[+HHMM|-HHMM]"
    }
    for key, val in mapping.items():
        format_string = format_string.replace(key, val)
    return format_string


def humanize_timedelta(timedelta, display="long", sep=", "):
    """
    Turns a datetime.timedelta object into a nice string representation.
    """
    assert isinstance(timedelta, datetime.timedelta), "First argument must be a timedelta."  # NOQA

    result = []

    weeks = int(timedelta.days / 7)
    days = timedelta.days % 7
    hours = int(timedelta.seconds / 3600)
    minutes = int((timedelta.seconds % 3600) / 60)
    seconds = timedelta.seconds % 60

    if display == "sql":
        days += weeks * 7
        return "%i %02i:%02i:%02i" % (days, hours, minutes, seconds)
    elif display == "iso8601":
        return iso8601_repr(timedelta)
    elif display == 'minimal':
        words = ["w", "d", "h", "m", "s"]
    elif display == 'short':
        words = [" wks", " days", " hrs", " min", " sec"]
    elif display == 'long':
        words = [" weeks", " days", " hours", " minutes", " seconds"]
    else:
        # Use django template-style formatting.
        # Valid values are: d,g,G,h,H,i,s
        return STRFDATETIME.sub(STRFDATETIME_REPL, display) % {
            'd': days,
            'g': hours,
            'G': hours if hours > 9 else '0%s' % hours,
            'h': hours,
            'H': hours if hours > 9 else '0%s' % hours,
            'i': minutes if minutes > 9 else '0%s' % minutes,
            's': seconds if seconds > 9 else '0%s' % seconds
        }

    values = [weeks, days, hours, minutes, seconds]

    for i in range(len(values)):
        if values[i]:
            if values[i] == 1 and len(words[i]) > 1:
                result.append("%i%s" % (values[i], words[i].rstrip('s')))
            else:
                result.append("%i%s" % (values[i], words[i]))

    # Values with less than one second, which are considered zeroes
    if len(result) == 0:
        # Display as 0 of the smallest unit
        result.append('0%s' % (words[-1]))

    return sep.join(result)
