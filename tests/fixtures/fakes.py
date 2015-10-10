# -*- coding: utf-8 -*-
from aiorest_ws.abstract import AbstractEndpoint
from aiorest_ws.exceptions import BaseAPIException
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


class FakeTokenMiddleware(object):
    def process_request(self, request, handler):
        setattr(request, 'token', None)
        return request


class FakeTokenMiddlewareWithExc(object):
    def process_request(self, request, handler):
        raise BaseAPIException('No token provided')
