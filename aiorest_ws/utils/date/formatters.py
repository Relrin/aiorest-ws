# -*- coding: utf-8 -*-
__all__ = ('iso8601_repr', )


def iso8601_repr(timedelta, format=None):
    """
    Represent a timedelta as an ISO8601 duration.
    http://en.wikipedia.org/wiki/ISO_8601#Durations
    """
    years = int(timedelta.days / 365)
    weeks = int((timedelta.days % 365) / 7)
    days = timedelta.days % 7

    hours = int(timedelta.seconds / 3600)
    minutes = int((timedelta.seconds % 3600) / 60)
    seconds = timedelta.seconds % 60

    if format == 'alt':
        if years or weeks or days:
            raise ValueError('Does not support `alt` format for durations '
                             'more then 1 day')
        return 'PT{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

    formatting = (
        ('P', (
            ('Y', years),
            ('W', weeks),
            ('D', days),
        )),
        ('T', (
            ('H', hours),
            ('M', minutes),
            ('S', seconds),
        )),
    )

    result = []
    for category, subcats in formatting:
        result += category
        for format, value in subcats:
            if value:
                result.append('%d%c' % (value, format))
    if result[-1] == 'T':
        result = result[:-1]

    return "".join(result)
