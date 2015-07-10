# -*- coding: utf-8 -*-
"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs.

    For example, we can use this features something like this:

        router = RestWSRouter()
        router.add('user/info', info_handler, methods='GET')
        router.add('user/register', register_handler, methods='POST')
        router.add('user/{user_name}', user_handler, methods=['GET', 'PUT'])
"""
__all__ = ('RestWSRouter', )

import inspect

from exceptions import BaseAPIException, NotSupportedArgumentType, \
    InvalidPathArgument, InvalidHandler, EndpointValueError, \
    IncompatibleResponseType, NotSpecifiedHandler
from routes import BaseRoute
from views import MethodBasedView
from url_parser import URLParser


class RestWSRouter(object):
    """Default router class, used for working with REST over WebSockets."""
    url_parser = URLParser()
    supported_methods_types = (list, str)

    def __init__(self):
        super(RestWSRouter, self).__init__()
        self._urls = []
        self._routes = {}

    def _check_path(self, path):
        """Validate passed path for endpoint.

        :param path: path to endpoint (string)
        """
        if not path.startswith('/'):
            raise InvalidPathArgument(u"Path should be started with `/` "
                                      u"symbol")

    def _check_handler(self, handler):
        """Validate passed handler for requests.

        :param handler: class or function, used for generating response.
        """
        if inspect.isclass(handler):
            if not issubclass(handler, (MethodBasedView, )):
                raise InvalidHandler(u"Your class should be inherited from "
                                     u"the MethodBasedView class")
        raise InvalidHandler()

    def _check_methods(self, methods):
        """Validate passed methods variable.

        :param methods: list of methods or string with concrete method name.
        """
        if type(methods) not in self.supported_methods_types:
            raise NotSupportedArgumentType('Variable with name "methods" must'
                                           ' he `list` or `str` type.')

    def _check_name(self, name):
        """Validate passed name variable.

        :param name: the base to use for the URL names that are created.
        """
        if name:
            if type(name) is not str:
                raise NotSupportedArgumentType(u'name variable must '
                                               u'be string type')

    def add(self, path, handler, methods, name=None):
        """Add new endpoint to server router.

        :param path: URL, which used to get access to API.
        :param handler: inherited class from the MethodBasedView, which used
                        for processing request.
        :param methods: list of available for user methods or string with
                        concrete method name.
        :param name: the base to use for the URL names that are created.
        """
        if not path.endswith('/'):
            path = path + '/'

        self._check_path(path)
        self._check_methods(methods)
        self._check_handler(handler)
        self._check_name(name)

        route = URLParser.define_route(path, methods, handler, name)
        self._register_url(route)

    def dispatch(self, request, *args, **kwargs):
        """Handling received request from user.

        :param request: request from user.
        """
        # TODO: 1) find the most suitable endpoint handler
        # TODO: 2) get response serializer (if not specified - use `json`)
        # TODO: 3) invoke serialize() method for generated response
        try:
            url = request.get('url', None)
            if not url:
                raise IncompatibleResponseType()

            handler = None
            for route in self._urls:
                match = route.match(url)
                if match:
                    handler = route.handler
                    kwargs.update({'vars': match})
                    break

            if handler:
                response = handler.dispatch(request, *args, **kwargs)
                # serializer there result
                # don't forget check format from args in request
                # response = handler.get_serializer(...).serialize()
                if type(response) is not dict:
                    raise IncompatibleResponseType()

            raise NotSpecifiedHandler()
        except BaseAPIException as exc:
            response = {'details': exc.detail}
        return response

    def reverse(self, name):
        """Get path to endpoint, using his short name.

        :param name: short name of endpoint.
        """
        try:
            path = self._routes[name].path
        except KeyError:
            path = None
        return path

    def _register_url(self, route):
        """Register new route.

        :param route: instance of class, which inherited from BaseRouter.
        """
        if not issubclass(route, (BaseRoute, )):
            raise TypeError(u"Custom route must be inherited from the "
                            u"BaseRouter class.")

        name = route.name
        if name is not None:
            if name in self._routes.keys():
                raise EndpointValueError(
                    'Duplicate {}, already handled by {}'
                    .format(name, self._routes[name]))
            else:
                self._routes[name] = route
        self._urls.append(route)
