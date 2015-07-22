# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import InvalidPathArgument, InvalidHandler, \
    NotSupportedArgumentType
from aiorest_ws.validators import BaseValidator, RouteArgumentsValidator
from aiorest_ws.views import MethodBasedView


class BaseValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseValidatorTestCase, self).setUp()
        self.validator = BaseValidator()

    def test_check_path(self):
        self.assertIsNone(self.validator.validate())


class RouterArgumentsValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(RouterArgumentsValidatorTestCase, self).setUp()
        self.validator = RouteArgumentsValidator()

    def test_check_path(self):
        invalid_path = 'api'
        self.assertRaises(
            InvalidPathArgument,
            self.validator.path_validator.validate, invalid_path
        )

        valid_path = '/api'
        self.assertIsNone(self.validator.path_validator.validate(valid_path))

    def test_check_handler(self):
        invalid_handler = object
        self.assertRaises(
            InvalidHandler,
            self.validator.handler_validator.validate, invalid_handler
        )

        valid_handler = MethodBasedView
        self.assertIsNone(
            self.validator.handler_validator.validate(valid_handler)
        )

        invalid_handler = ['not a class', ]
        self.assertRaises(
            InvalidHandler,
            self.validator.handler_validator.validate, invalid_handler
        )

    def test_check_methods(self):
        invalid_methods = ('get', )
        self.assertRaises(
            NotSupportedArgumentType,
            self.validator.methods_validator.validate, invalid_methods
        )

        valid_methods = ['get', ]
        self.assertIsNone(
            self.validator.methods_validator.validate(valid_methods)
        )

        valid_methods = 'get'
        self.assertIsNone(
            self.validator.methods_validator.validate(valid_methods)
        )

    def test_check_name(self):
        self.assertIsNone(
            self.validator.endpoint_name_validator.validate(None)
        )

        invalid_name = ('basename', )
        self.assertRaises(
            NotSupportedArgumentType,
            self.validator.endpoint_name_validator.validate, invalid_name
        )

        valid_name = 'basename'
        self.assertIsNone(
            self.validator.endpoint_name_validator.validate(valid_name)
        )

    def test_validate(self):
        args = '/api/', MethodBasedView, 'GET', None
        self.validator.validate(*args)
