# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.utils.text import capfirst


@pytest.mark.parametrize("value, expected", [
    (None, None),
    ([], []),
    ({}, {}),
    ('test', 'Test'),
])
def test_capfirst(value, expected):
    assert capfirst(value) == expected
