# -*- coding: utf-8 -*-
"""
    Abstract classes for future implementation.
"""
from abc import ABCMeta, abstractmethod

__all__ = (
    'AbstractEndpoint', 'AbstractRouter', 'AbstractMiddleware',
    'AbstractPermission',
)


class AbstractEndpoint(metaclass=ABCMeta):
    """Base class for endpoints."""

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
    """Base class for routers."""
    _middlewares = []

    def __init__(self, *args, **kwargs):
        self._urls = []
        self._routes = {}

    @property
    def middlewares(self):
        """Get list of used middlewares."""
        return self._middlewares

    @abstractmethod
    def process_request(self, request):
        """Handling received request from user.

        :param request: request from user.
        """
        pass


class AbstractMiddleware(metaclass=ABCMeta):
    """Base class for middlewares."""
    @abstractmethod
    def process_request(self, request, handler):
        """Processing request before calling handler.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        pass


class AbstractPermission(metaclass=ABCMeta):
    """Base class for permissions."""
    @staticmethod
    def check(request, handler):
        """Check permission method.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        pass
