# -*- coding: utf-8 -*-
"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs.

    For example, we can use this features something like this:

        router = RestWSRouter()
        router.add('user/info', info_handler, methods='GET')
        router.add('user/register', register_handler, methods='POST')
        router.add('user/{user_name}', user_handler, methods=['GET', 'PUT'])

    :copyright: (c) 2015 by Savich Valeryi.
    :license: MIT, see LICENSE for more details.
"""

from exceptions import BaseAPIException, NotSupportedArgumentType

__all__ = ('RestWSRouter', )


class RestWSRouter(object):
    """Default router class, used for working with REST over WebSockets."""

    def __init__(self):
        super(RestWSRouter, self).__init__()
        self._urls = []
        self._routes = {}

    def _check_methods_variable(self, methods):
        """Validate passed from user methods variable.

        :param methods: list of methods or string with concrete name of method
        """
        supported_types = (list, str)
        if type(methods) not in supported_types:
            raise NotSupportedArgumentType('Variable with name "methods" must'
                                           ' he `list` or `str` type.')

    def add(self, path, handler, methods, base_name=None):
        """Add new endpoint to server router.

        :param path: URL, which used to get access to API.
        :param handler: callable function, which used for processing request.
        :param methods: list of supported HTTP methods.
        :param base_name: the base to use for the URL names that are created.
        """
        # TODO: Add support for "dynamic ulrs" (e.c. "/api/{username}/")

        if not path.endswith('/'):
            path = path + '/'

        self._check_methods_variable(methods)
        # add static endpoint

    def dispatch(self, request, *args, **kwargs):
        """Handling received request from user.

        :param request: request from user.
        """
        # TODO: 1) find the most suitable endpoint handler
        # TODO: 2) get response serializer (if not specified - use `json`)
        # TODO: 3) invoke serialize() method for generated response
        response = {}
        try:
            pass
        except BaseAPIException as exc:
            response = {'details': exc.detail}
        return response

    def reverse(self, endpoint_name):
        """Get path to endpoint, using his short name (basename).

        :param endpoint_name: short name of endpoint.
        """
        pass
