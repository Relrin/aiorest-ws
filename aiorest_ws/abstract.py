# -*- coding: utf-8 -*-
"""
    Abstract classes for future implementation.
"""
__all__ = (
    'AbstractEndpoint', 'AbstractRouter', 'AbstractMiddleware',
    'AbstractPermission',
)

from abc import ABCMeta, abstractmethod


class AbstractEndpoint(metaclass=ABCMeta):

    path = None     # URL, used for get access to API
    handler = None  # class/function for processing request
    methods = []    # list of supported methods (GET, POST, etc.)
    name = None     # short name for route

    def __init__(self, path, handler, methods, name):
        self.path = path
        self.handler = handler
        if type(methods) is str:
            self.methods.append(methods)
        else:
            self.methods.extend(methods)
        self.name = name

    @abstractmethod
    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        pass


class AbstractRouter(metaclass=ABCMeta):

    _middlewares = ()

    def __init__(self, *args, **kwargs):
        pass

    @property
    def middlewares(self):
        return self._middlewares

    @abstractmethod
    def process_request(self, request):
        """Handling received request from user.

        :param request: request from user.
        """
        pass


class AbstractMiddleware(metaclass=ABCMeta):

    @abstractmethod
    def process_request(self, request, handler):
        """Processing request before calling handler.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        pass


class AbstractPermission(metaclass=ABCMeta):

    @staticmethod
    def check(request, handler):
        """Check permission method.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        pass
