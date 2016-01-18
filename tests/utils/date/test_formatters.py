# -*- coding: utf-8 -*-
import pytest

from datetime import timedelta
from aiorest_ws.utils.date import formatters


@pytest.mark.parametrize("value, format, expected", [
    (timedelta(days=1, hours=2, minutes=3, seconds=4), None, 'P1DT2H3M4S'),
    (timedelta(hours=1, minutes=10, seconds=20), "alt", 'PT01:10:20'),
])
def test_iso8601_repr(value, format, expected):
    assert formatters.iso8601_repr(value, format=format) == expected


@pytest.mark.parametrize("value, format, exc_type", [
    (timedelta(days=1, hours=2, minutes=3, seconds=4), "alt", ValueError),
])
def test_iso8601_repr_raises_exception(value, format, exc_type):
    with pytest.raises(exc_type):
        formatters.iso8601_repr(value, format=format)
