"""
    This module provides a classes, which can be used with aiorest-ws routers
"""
import asyncio
__all__ = ('BaseView', 'ClassBasedView', )


class BaseView(object):
    """
        Base class for realization class-based views
    """
    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        raise NotImplementedError('`get` method should be overridden')

    @asyncio.coroutine
    def post(self, request, *args, **kwargs):
        raise NotImplementedError('`post` method should be overridden')

    @asyncio.coroutine
    def put(self, request, *args, **kwargs):
        raise NotImplementedError('`put` method should be overridden')

    @asyncio.coroutine
    def delete(self, request, *args, **kwargs):
        raise NotImplementedError('`delete` method should be overridden')

    @asyncio.coroutine
    def patch(self, request, *args, **kwargs):
        raise NotImplementedError('`patch` method should be overridden')

    @asyncio.coroutine
    def head(self, request, *args, **kwargs):
        raise NotImplementedError('`head` method should be overridden')


class ClassBasedView(BaseView):
    """
        Class-based view for aiorest-ws framework
    """
    pass
