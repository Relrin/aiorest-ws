# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.status import is_not_used, is_reserved, is_library, is_private


@pytest.mark.parametrize("code, expected", [
    (0, True),
    (999, True),
    (500, True),
    (1000, False),
    (-1, False),
])
def test_is_not_used(code, expected):
    assert is_not_used(code) is expected


@pytest.mark.parametrize("code, expected", [
    (1000, True),
    (2999, True),
    (2000, True),
    (3000, False),
    (999, False),
])
def test_is_reserved(code, expected):
    assert is_reserved(code) is expected


@pytest.mark.parametrize("code, expected", [
    (3000, True),
    (3999, True),
    (3500, True),
    (4000, False),
    (2999, False),
])
def test_is_library(code, expected):
    assert is_library(code) is expected


@pytest.mark.parametrize("code, expected", [
    (4000, True),
    (4999, True),
    (4500, True),
    (3999, False),
    (5000, False),
])
def test_is_private(code, expected):
    assert is_private(code) is expected
