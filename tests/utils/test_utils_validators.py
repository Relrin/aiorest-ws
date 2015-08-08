# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.routers import RestWSRouter
from aiorest_ws.endpoints import PlainEndpoint, DynamicEndpoint
from aiorest_ws.utils.validators import to_str, get_object_type


@pytest.mark.parametrize("value, expected", [
    (PlainEndpoint, 'PlainEndpoint'),
    ((PlainEndpoint, ), 'PlainEndpoint'),
    ((PlainEndpoint, DynamicEndpoint), 'PlainEndpoint/DynamicEndpoint'),
])
def test_to_str(value, expected):
    assert to_str(value) == expected


@pytest.mark.parametrize("value, expected", [
    (PlainEndpoint, PlainEndpoint),
    (RestWSRouter(), RestWSRouter),
    (list, list),
])
def test_get_object_type(value, expected):
    assert get_object_type(value) is expected
