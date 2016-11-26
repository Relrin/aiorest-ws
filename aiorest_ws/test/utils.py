# -*- coding: utf-8 -*-
"""
Django-like settings functions and classes, which help to modify basic
configuration on the fly, while tests performed.
"""
from functools import wraps
from unittest import TestCase

from aiorest_ws.conf import settings, UserSettingsHolder

__all__ = ('override_settings', )


class BaseContextDecorator(object):
    """
    A base class that can either be used as a context manager during tests
    or as a test function or unittest.TestCase subclass decorator to perform
    temporary alterations.
    `attr_name`: attribute assigned the return value of enable() if used as
                 a class decorator.
    `kwarg_name`: keyword argument passing the return value of enable() if
                  used as a function decorator.
    """
    def __init__(self, attr_name=None, kwarg_name=None):
        self.attr_name = attr_name
        self.kwarg_name = kwarg_name

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def __enter__(self):
        return self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def decorate_class(self, cls):
        if issubclass(cls, TestCase):
            decorated_setUp = cls.setUp
            decorated_tearDown = cls.tearDown

            def setUp(inner_self):
                context = self.enable()
                if self.attr_name:
                    setattr(inner_self, self.attr_name, context)
                decorated_setUp(inner_self)

            def tearDown(inner_self):
                decorated_tearDown(inner_self)
                self.disable()

            cls.setUp = setUp
            cls.tearDown = tearDown
            return cls
        raise TypeError('Can only decorate subclasses of unittest.TestCase')

    def decorate_callable(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self as context:
                if self.kwarg_name:
                    kwargs[self.kwarg_name] = context
                return func(*args, **kwargs)
        return inner

    def __call__(self, decorated):
        if isinstance(decorated, type):
            return self.decorate_class(decorated)
        elif callable(decorated):
            return self.decorate_callable(decorated)
        raise TypeError('Cannot decorate object of type %s' % type(decorated))


class override_settings(BaseContextDecorator):
    """
    Acts as either a decorator or a context manager. If it's a decorator it
    takes a function and returns a wrapped function. If it's a contextmanager
    it's used with the ``with`` statement. In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs
        super(override_settings, self).__init__()

    def enable(self):
        old_keys = set(key for key in settings.__dir__() if key.isupper())
        new_keys = set(self.options.keys())
        self._new_setting_keys = list(new_keys.difference(old_keys))

        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        self.wrapped = settings._wrapped
        settings._wrapped = override
        for key, new_value in self.options.items():
            setattr(settings, key, new_value)

    def disable(self):
        settings._wrapped = self.wrapped
        del self.wrapped
        # Rollback old values
        for key in self.options:
            new_value = getattr(settings, key, None)
            setattr(settings, key, new_value)
        # Other keys just remove from the settings
        for key in self._new_setting_keys:
            delattr(settings, key)

    def save_options(self, test_func):
        if test_func._overridden_settings is None:
            test_func._overridden_settings = self.options
        else:
            # Duplicate dict to prevent subclasses from altering their parent
            test_func._overridden_settings = dict(
                test_func._overridden_settings, **self.options
            )

    def decorate_class(self, cls):
        self.save_options(cls)
        return cls
