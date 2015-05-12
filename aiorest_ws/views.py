"""
    This module provides class-based views inspired by Django/Flask
    frameworks and can be used with aiorest-ws routers.
"""
__all__ = ('View', 'MethodViewMeta', 'ClassBasedView',)

http_methods = frozenset(['GET', 'POST', 'HEAD', 'OPTIONS', 'DELETE', 'PUT',
                          'TRACE', 'PATCH'])


class View(object):
    """
        Subclass for implementing class-based views.
    """
    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """
            Converts the class into an actual view function that can be used
            with the routing system.
        """
        pass


class MethodViewMeta(type):
    """
        Metaclass, which helps to define list of supported methods in
        class-based views.
    """
    def __new__(cls, name, bases, attrs):
        obj = type.__new__(cls, name, bases, attrs)
        # if not defined 'method' attribute, then make and append him to
        # our class-based view
        if 'methods' not in attrs:
            methods = set(obj.methods or [])
            for key in attrs:
                if key in http_methods:
                    methods.add(key.upper())
            # this action necessary for appending list of supported methods
            if methods:
                obj.methods = sorted(methods)
        return obj


class ClassBasedView(View, metaclass=MethodViewMeta):
    """
        Class-based view for aiorest-ws framework.
    """
    # NOTE: HTTP handlers shall be wrapped into asyncio.coroutine decorator
    def dispatch_request(self, *args, **kwargs):
        # TODO: try to write code without using global request and resolve
        # there called method
        pass
