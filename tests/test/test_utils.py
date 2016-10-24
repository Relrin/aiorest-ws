# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.conf import settings
from aiorest_ws.test.utils import BaseContextDecorator, override_settings


class TestBaseContextDecorator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBaseContextDecorator, cls).setUpClass()
        cls.instance = BaseContextDecorator()

    def test_enable(self):
        with self.assertRaises(NotImplementedError):
            self.instance.enable()

    def test_disable(self):
        with self.assertRaises(NotImplementedError):
            self.instance.disable()

    def test_enter(self):
        with self.assertRaises(NotImplementedError):
            self.instance.__enter__()

    def test_disable_for_with_operator(self):
        with self.assertRaises(NotImplementedError):
            self.instance.__exit__(ValueError, 'error', None)

    def test_decorate_class(self):

        @BaseContextDecorator()
        class TestClass(unittest.TestCase):
            pass

        test_instance = TestClass()

        with self.assertRaises(NotImplementedError):
            test_instance.setUp()

        with self.assertRaises(NotImplementedError):
            test_instance.tearDown()

    def test_decorate_class_with_overriden_enable_and_disable(self):
        class OverriddenContextDecorator(BaseContextDecorator):
            def enable(self):
                pass

            def disable(self):
                pass

        @OverriddenContextDecorator(attr_name='test')
        class TestClass(unittest.TestCase):
            pass

        test_instance = TestClass()
        test_instance.setUp()
        test_instance.tearDown()

    def test_decorate_class_raises_type_error(self):
        with self.assertRaises(TypeError):

            @BaseContextDecorator()
            class DecoratedCls(object):
                pass

    def test_decorate_callable(self):
        @BaseContextDecorator()
        def decorated_func():
            pass

        with self.assertRaises(NotImplementedError):
            decorated_func()

    def test_decorate_callable_with_kwargs(self):
        class OverriddenContextDecorator(BaseContextDecorator):
            def enable(self):
                pass

        @OverriddenContextDecorator(kwarg_name='context')
        def decorated_func(context=None):
            pass

        with self.assertRaises(NotImplementedError):
            decorated_func()


class TestOverrideSettings(unittest.TestCase):

    def test_enable_and_disable_override_setting(self):
        with override_settings(UNKNOWN_KEY='value'):
            self.assertTrue(hasattr(settings, 'UNKNOWN_KEY'))
        self.assertFalse(hasattr(settings, 'UNKNOWN_KEY'))

    def test_decorate_class_must_set_options(self):

        @override_settings(key='value')
        class TestClass(unittest.TestCase):
            _overridden_settings = None

        test_instance = TestClass()
        test_instance.setUp()
        test_instance.tearDown()
        self.assertIsNotNone(test_instance._overridden_settings)

    def test_decorate_class_must_override_options(self):

        @override_settings(key='value')
        class TestClass(unittest.TestCase):
            _overridden_settings = {'db': 'PostgreSQL'}

        test_instance = TestClass()
        test_instance.setUp()
        test_instance.tearDown()
        self.assertIsNotNone(test_instance._overridden_settings)
        self.assertEqual(
            test_instance._overridden_settings,
            {'db': 'PostgreSQL', 'key': 'value'}
        )
