# -*- coding: utf-8 -*-
import datetime
import pytest
from decimal import Decimal

from aiorest_ws.utils.encoding import is_protected_type, force_text, \
    force_text_recursive
from aiorest_ws.utils.serializer_helpers import ReturnList, ReturnDict


class CustomType(object):

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data

    __unicode__ = __str__


@pytest.mark.parametrize("value, expected", [
    (10, False),  # int
    ("test_string", True),  # string
    (None, True),  # NoneType
    (1.0, True),  # float
    (Decimal('3.14'), True),  # Decimal
    (datetime.datetime(year=2016, month=6, day=1), True),  # datetime.datetime
    (datetime.date(year=2016, month=6, day=1), True),  # datetime.date
    (datetime.time(hour=12), True),  # datetime.time
])
def test_is_protected_type(value, expected):
    assert is_protected_type(value) is expected


@pytest.mark.parametrize("value, kwargs, expected", [
    ("string", {}, "string"),
    (bytes("string", encoding='utf-8'), {}, "string"),
    (datetime.time(hour=12), {"strings_only": True}, datetime.time(hour=12)),
    (b'test', {}, "test"),
    (CustomType("test"), {}, "test"),
    (b'\x80abc', {"encoding": 'utf-8', "errors": 'strict'}, "128 97 98 99")
])
def test_force_text(value, kwargs, expected):
    assert force_text(value, **kwargs) == expected


@pytest.mark.parametrize("value, kwargs, exception_cls", [
    (CustomType(b'\xc3\xb6\xc3\xa4\xc3\xbc'), {}, TypeError),
])
def test_force_text_failed(value, kwargs, exception_cls):
    with pytest.raises(exception_cls):
        force_text(value, **kwargs)


@pytest.mark.parametrize("value, expected", [
    ("string", "string"),
    (bytes("string", encoding='utf-8'), "string"),
    (["test", "string"], ["test", "string"]),
    ({"key": "value"}, {"key": "value"}),
    (ReturnDict({"key": "value"}, serializer=object()), {"key": "value"}),
    (ReturnList(["test", "string"], serializer=object()), ['test', 'string'])
])
def test_force_text_recursive(value, expected):
    assert force_text_recursive(value) == expected
