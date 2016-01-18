# -*- coding: utf-8 -*-
"""
Classes and functions, which might be used for easier development purposes.
"""
__all__ = ('cached_property', )


class cached_property(object):
    """
    Decorator that transform a method with a single `self` argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
