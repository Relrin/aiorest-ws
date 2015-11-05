# -*- coding: utf-8 -*-
"""
    URL parsers, which help to define, with which endpoint router works.
"""
import re

from aiorest_ws.endpoints import PlainEndpoint, DynamicEndpoint
from aiorest_ws.exceptions import EndpointValueError

__all__ = ('URLParser', )


class URLParser(object):
    """Parser over endpoints paths, which returns one of the most suitable
    instances of route classes.
    """
    ANY_VALUE = r'[^{}/]+'
    DYNAMIC_PARAMETER = re.compile(r'({\s*[\w\d_]+\s*})')
    VALID_DYNAMIC_PARAMETER = re.compile(r'{(?P<var>[\w][\w\d_]*)}')

    def define_route(self, path, handler, methods, name=None):
        """Define a router as instance of BaseRoute subclass, which passed
        from register method in RestWSRouter.

        :param path: URL, which used to get access to API.
        :param handler: class inherited from MethodBasedView, which used for
                        processing request.
        :param methods: list of available for user methods or string with
                        concrete method name.
        :param name: the base to use for the URL names that are created.
        """
        # it's PlainRoute, when don't have any "dynamic symbols"
        if all(symbol not in path for symbol in ['{', '}']):
            return PlainEndpoint(path, handler, methods, name)

        # try to processing as a dynamic path
        pattern = ''
        for part in self.DYNAMIC_PARAMETER.split(path):
            match = self.VALID_DYNAMIC_PARAMETER.match(part)
            if match:
                pattern += '(?P<{}>{})'.format(match.group('var'),
                                               self.ANY_VALUE)
                continue

            if any(symbol in part for symbol in ['{', '}']):
                raise EndpointValueError("Invalid {} part of {} path"
                                         .format(part, path))

            pattern += re.escape(part)
        try:
            compiled = re.compile("^{}$".format(pattern))
        except re.error as exc:
            raise EndpointValueError("Bad pattern '{}': {}"
                                     .format(pattern, exc))
        return DynamicEndpoint(path, handler, methods, name, compiled)
