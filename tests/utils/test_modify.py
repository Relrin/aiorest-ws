# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.wrappers import Request
from aiorest_ws.utils.modify import add_property


def test_add_property():
    request = Request()
    add_property(request, 'token', None)

    assert '_token' in request.__dict__.keys()
    assert request.token is None


def test_attribute_error_for_added_property():
    request = Request()
    add_property(request, 'token', None)

    assert '_token' in request.__dict__.keys()
    with pytest.raises(AttributeError):
        request.token = "test_token"
        assert request.token is None
