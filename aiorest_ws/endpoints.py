# -*- coding: utf-8 -*-
"""
    Endpoint classes for aiorest-ws router.
"""
__all__ = ('BaseRoute', 'PlainRoute', 'DynamicRoute', )

from abc import ABCMeta, abstractmethod


class BaseRoute(metaclass=ABCMeta):

    path = None     # URL, used for get access to API
    handler = None  # class/function for processing request
    methods = []    # list of supported methods (GET, POST, etc.)
    name = None     # short name for route

    def __init__(self, path, methods, handler, name):
        self.path = path
        if type(methods) is str:
            self.methods.append(methods)
        else:
            self.methods.extend(methods)
        self.handler = handler
        self.name = name

    @abstractmethod
    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        pass


class PlainRoute(BaseRoute):

    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        match_result = None
        if self.path == path:
            match_result = {}
        return match_result


class DynamicRoute(BaseRoute):

    def __init__(self, path, methods, handler, name, pattern):
        super(DynamicRoute, self).__init__(path, methods, handler, name)
        self._pattern = pattern

    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        match_result = self._pattern.match(path)
        # if comparing has successful, then return list of parsed values
        if match_result:
            match_result = match_result.groups()
        return match_result
