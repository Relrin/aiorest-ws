# -*- coding: utf-8 -*-
"""
    Validator classes for checkign passed arguments
"""
__all__ = ('BaseValidator', 'EndpointNameValidator', 'HandlerValidator',
           'MethodValidator', 'PathValidator', 'RouteArgumentsValidator', )

import inspect

from .exceptions import NotSupportedArgumentType, InvalidPathArgument, \
    InvalidHandler
from .views import MethodBasedView


class BaseValidator(object):
    """Base class for validators."""

    def validate(self, *args, **kwargs):
        """Validating passed arguments and kwargs."""
        pass


class EndpointNameValidator(BaseValidator):
    """Validator for endpoint name argument."""
    def _check_name(self, name):
        """Validate passed name variable.

        :param name: the base to use for the URL names that are created.
        """
        if name:
            if type(name) is not str:
                raise NotSupportedArgumentType(u'name variable must '
                                               u'be string type')

    def validate(self, name):
        self._check_name(name)


class HandlerValidator(BaseValidator):
    """Validator for handler argument."""
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

    def validate(self, handler):
        self._check_handler(handler)


class MethodValidator(BaseValidator):
    """Validator for methods argument."""
    supported_methods_types = (list, str)

    def _check_methods(self, methods):
        """Validate passed methods variable.

        :param methods: list of methods or string with concrete method name.
        """
        if type(methods) not in self.supported_methods_types:
            raise NotSupportedArgumentType('Variable with name "methods" must'
                                           ' be `list` or `str` type.')

    def validate(self, methods):
        self._check_methods(methods)


class PathValidator(BaseValidator):
    """Validator for path argument."""
    def _check_path(self, path):
        """Validate passed path for endpoint.

        :param path: path to endpoint (string)
        """
        if not path.startswith('/'):
            raise InvalidPathArgument(u"Path should be started with `/` "
                                      u"symbol")

    def validate(self, path):
        self._check_path(path)


class RouteArgumentsValidator(BaseValidator):
    """Validator for arguments of RestWSRouter."""
    path_validator = PathValidator()
    handler_validator = HandlerValidator()
    methods_validator = MethodValidator()
    endpoint_name_validator = EndpointNameValidator()

    def validate(self, path, handler, methods, name):
        """Validating passed arguments and kwargs."""
        self.path_validator.validate(path)
        self.handler_validator.validate(handler)
        self.methods_validator.validate(methods)
        self.endpoint_name_validator.validate(name)
