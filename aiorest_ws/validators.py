# -*- coding: utf-8 -*-
"""
    Validator classes for checkign passed arguments
"""
__all__ = ('BaseValidator', 'RouterArgumentsValidator', )

import inspect

from .exceptions import NotSupportedArgumentType, InvalidPathArgument, \
    InvalidHandler
from .views import MethodBasedView


class BaseValidator(object):
    """Base class for validators."""

    def validate(self, *args, **kwargs):
        """Validating passed arguments and kwargs."""
        pass


class RouterArgumentsValidator(BaseValidator):
    """Validator for arguments of RestWSRouter."""
    supported_methods_types = (list, str)

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
        else:
            raise InvalidHandler()

    def _check_methods(self, methods):
        """Validate passed methods variable.

        :param methods: list of methods or string with concrete method name.
        """
        if type(methods) not in self.supported_methods_types:
            raise NotSupportedArgumentType('Variable with name "methods" must'
                                           ' be `list` or `str` type.')

    def _check_name(self, name):
        """Validate passed name variable.

        :param name: the base to use for the URL names that are created.
        """
        if name:
            if type(name) is not str:
                raise NotSupportedArgumentType(u'name variable must '
                                               u'be string type')

    def validate(self, path, handler, methods, name):
        """Validating passed arguments and kwargs."""
        self._check_path(path)
        self._check_handler(handler)
        self._check_methods(methods)
        self._check_name(name)
