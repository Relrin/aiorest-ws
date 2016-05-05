# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import InvalidPathArgument, InvalidHandler, \
    NotSupportedArgumentType
from aiorest_ws.validators import BaseValidator, EndpointNameValidator, \
    RouteArgumentsValidator, HandlerValidator, MethodValidator, \
    PathValidator, check_and_set_subclass
from aiorest_ws.request import RequestHandlerFactory
from aiorest_ws.views import MethodBasedView


class BaseValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseValidatorTestCase, self).setUp()
        self.validator = BaseValidator()

    def test_check_path(self):
        self.assertIsNone(self.validator.validate())


class EndpointNameValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(EndpointNameValidatorTestCase, self).setUp()
        self.validator = EndpointNameValidator()

    def test_check_name(self):
        self.assertIsNone(self.validator.validate(None))

    def test_check_name_2(self):
        valid_name = 'basename'
        self.assertIsNone(self.validator.validate(valid_name))

    def test_check_name_failed(self):
        invalid_name = ('basename', )
        self.assertRaises(NotSupportedArgumentType, self.validator.validate,
                          invalid_name)


class HandlerValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(HandlerValidatorTestCase, self).setUp()
        self.validator = HandlerValidator()

    def test_check_handler(self):
        valid_handler = MethodBasedView
        self.assertIsNone(self.validator.validate(valid_handler))

    def test_check_handler_failed(self):
        invalid_handler = object
        self.assertRaises(
            InvalidHandler,
            self.validator.validate, invalid_handler
        )

    def test_check_handler_failed_2(self):
        invalid_handler = ['not a class', ]
        self.assertRaises(
            InvalidHandler,
            self.validator.validate, invalid_handler
        )


class MethodValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(MethodValidatorTestCase, self).setUp()
        self.validator = MethodValidator()

    def test_check_methods(self):
        valid_methods = ['get', ]
        self.assertIsNone(self.validator.validate(valid_methods))

    def test_check_methods_2(self):
        valid_methods = 'get'
        self.assertIsNone(self.validator.validate(valid_methods))

    def test_check_methods_failed(self):
        invalid_methods = ('get', )
        self.assertRaises(
            NotSupportedArgumentType,
            self.validator.validate, invalid_methods
        )


class PathValidatorTestCase(unittest.TestCase):

    def setUp(self):
        super(PathValidatorTestCase, self).setUp()
        self.validator = PathValidator()

    def test_check_path(self):
        valid_path = '/api'
        self.assertIsNone(self.validator.validate(valid_path))

    def test_check_path_failed(self):
        invalid_path = 'api'
        self.assertRaises(
            InvalidPathArgument,
            self.validator.validate, invalid_path
        )


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
        valid_handler = MethodBasedView
        self.assertIsNone(
            self.validator.handler_validator.validate(valid_handler)
        )

    def test_check_handler_failed(self):
        invalid_handler = object
        self.assertRaises(
            InvalidHandler,
            self.validator.handler_validator.validate, invalid_handler
        )

    def test_check_handler_with_none_function(self):
        invalid_handler = ['not a class', ]
        self.assertRaises(
            InvalidHandler,
            self.validator.handler_validator.validate, invalid_handler
        )

    def test_check_methods(self):
        valid_methods = ['get', ]
        self.assertIsNone(
            self.validator.methods_validator.validate(valid_methods)
        )

    def test_check_methods_2(self):
        valid_methods = 'get'
        self.assertIsNone(
            self.validator.methods_validator.validate(valid_methods)
        )

    def test_check_methods_failed(self):
        invalid_methods = ('get', )
        self.assertRaises(
            NotSupportedArgumentType,
            self.validator.methods_validator.validate, invalid_methods
        )

    def test_check_name(self):
        valid_name = 'basename'
        self.assertIsNone(
            self.validator.endpoint_name_validator.validate(valid_name)
        )

    def test_check_name_2(self):
        self.assertIsNone(
            self.validator.endpoint_name_validator.validate(None)
        )

    def test_check_name_failed(self):
        invalid_name = ('basename', )
        self.assertRaises(
            NotSupportedArgumentType,
            self.validator.endpoint_name_validator.validate, invalid_name
        )

    def test_validate(self):
        args = '/api/', MethodBasedView, 'GET', None
        self.validator.validate(*args)


class ValidateSubclassFunctionTestCase(unittest.TestCase):

    def setUp(self):
        super(ValidateSubclassFunctionTestCase, self).setUp()

        class FakeFactory(object):
            pass
        self.fake_factory = FakeFactory

        class FactorySubclass(RequestHandlerFactory):
            pass
        self.factory_subclass = FactorySubclass
        self.factory = RequestHandlerFactory

    def test_valid_subclass(self):
        check_and_set_subclass(
            self, 'factory', self.factory_subclass, RequestHandlerFactory
        )
        self.assertEqual(self.factory, self.factory_subclass)

    def test_valid_subclass_2(self):
        check_and_set_subclass(
            self, 'factory', self.factory_subclass, (RequestHandlerFactory, )
        )
        self.assertEqual(self.factory, self.factory_subclass)

    def test_valid_subclass_3(self):
        check_and_set_subclass(
            self, 'factory',
            self.factory_subclass(),
            (RequestHandlerFactory, )
        )
        self.assertEqual(type(self.factory), self.factory_subclass)

    def test_invalid_subclass(self):
        self.assertRaises(
            TypeError,
            check_and_set_subclass,
            self, 'factory', self.fake_factory, RequestHandlerFactory
        )

    def test_invalid_subclass_2(self):
        self.assertRaises(
            TypeError,
            check_and_set_subclass,
            self, 'factory', self.fake_factory, (RequestHandlerFactory, str)
        )

    def test_invalid_subclass_3(self):
        self.assertRaises(
            TypeError,
            check_and_set_subclass,
            self, 'factory', self.fake_factory(), (RequestHandlerFactory, str)
        )
