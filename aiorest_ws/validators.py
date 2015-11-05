# -*- coding: utf-8 -*-
"""
    Validator classes and functions for checking passed arguments.
"""
import inspect

from aiorest_ws.exceptions import NotSupportedArgumentType, \
    InvalidPathArgument, InvalidHandler
from aiorest_ws.views import MethodBasedView
from aiorest_ws.utils.validators import to_str, get_object_type

__all__ = (
    'BaseValidator', 'EndpointNameValidator', 'HandlerValidator',
    'MethodValidator', 'PathValidator', 'RouteArgumentsValidator',
    'check_and_set_subclass',
)


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
        if name and type(name) is not str:
            raise NotSupportedArgumentType(u'name variable must '
                                           u'be string type')

    def validate(self, name):
        """Validate passed name variable.

        :param name: the base to use for the URL names that are created.
        """
        self._check_name(name)


class HandlerValidator(BaseValidator):
    """Validator for handler argument."""
    def _check_handler(self, handler):
        """Validate passed handler for requests.

        :param handler: class or function (wrapped into MethodBasedView),
                        which used for generating response.
        """
        if inspect.isclass(handler):
            if not issubclass(handler, (MethodBasedView, )):
                raise InvalidHandler(u"Your class should be inherited from "
                                     u"the MethodBasedView class")
        else:
            raise InvalidHandler()

    def validate(self, handler):
        """Validate passed handler for requests.

        :param handler: class or function, used for generating response.
        """
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
        """Validate passed methods variable.

        :param methods: list of methods or string with concrete method name.
        """
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
        """Validate passed path for endpoint.

        :param path: path to endpoint (string)
        """
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


def check_and_set_subclass(instance, attribute, value, subclasses):
    """Validate subclass of passed value on supported type and set him for
    instance of some class.

    :param instance: object, for with necessary make check and sets value.
    :param attribute: name of attribute (string), at which write ``value``
                      when checking passed without any errors.
    :param value: passed value to validate.
    :param subclasses: class or a list/tuple with acceptable classes.
    """
    obj_type = get_object_type(value)
    if issubclass(obj_type, subclasses):
        setattr(instance, attribute, value)
    else:
        raise TypeError('Custom class must be inherited from the '
                        '{} class.'.format(to_str(subclasses)))
