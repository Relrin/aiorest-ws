# -*- coding: utf-8 -*-
"""
    Endpoint classes for aiorest-ws router.

    :copyright: (c) 2015 by Savich Valeryi.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABCMeta, abstractmethod

__all__ = ('BaseRoute', 'StaticRoute', 'DynamicRoute')


class BaseRoute(metaclass=ABCMeta):

    path = None
    handler = None
    methods = []
    basename = None

    @abstractmethod
    def match(self, path):
        """The ."""
        pass


class StaticRoute(BaseRoute):

    def match(self, path):
        pass


class DynamicRoute(BaseRoute):

    def match(self, path):
        pass
