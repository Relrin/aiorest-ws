# -*- coding: utf-8 -*-
from aiorest_ws.urls.base import get_urlconf, set_urlconf, _urlconfs


def test_set_urlconf():
    data = {"dict": object()}
    set_urlconf(data)
    assert hasattr(_urlconfs, "data") is True
    assert _urlconfs.data == data


def test_get_urlconf():
    data = {"list": [1, 2, 3]}
    set_urlconf(data)
    urlconfs = get_urlconf()
    assert urlconfs == data
