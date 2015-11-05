# -*- coding: utf-8 -*-
"""
    Endpoint classes for aiorest-ws router.
"""
from aiorest_ws.abstract import AbstractEndpoint

__all__ = ('PlainEndpoint', 'DynamicEndpoint', )


class PlainEndpoint(AbstractEndpoint):

    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        match_result = None
        if self.path == path:
            match_result = ()
        return match_result


class DynamicEndpoint(AbstractEndpoint):

    def __init__(self, path, methods, handler, name, pattern):
        super(DynamicEndpoint, self).__init__(path, methods, handler, name)
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
