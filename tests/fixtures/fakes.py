# -*- coding: utf-8 -*-
from aiorest_ws.abstract import AbstractEndpoint
from aiorest_ws.views import MethodBasedView


class InvalidEndpoint(object):
    pass


class FakeEndpoint(AbstractEndpoint):
    def match(self, path):
        pass


class FakeView(MethodBasedView):
    def get(self, request, *args, **kwargs):
        pass


class FakeGetView(MethodBasedView):
    def get(self, request, *args, **kwargs):
        return "fake"
