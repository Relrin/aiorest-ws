# -*- coding: utf-8 -*-
from aiorest_ws.utils.functional import cached_property


class FakeClass(object):

    @cached_property
    def test_property(self):
        return True


def test_cached_property():
    assert FakeClass().test_property is True
