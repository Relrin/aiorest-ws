# -*- coding: utf-8 -*-
"""
    This module provide a class-based views inspired by Django/Flask
    frameworks and can be used with aiorest-ws routers.
"""
__all__ = ('http_methods', 'View', 'MethodViewMeta', 'MethodBasedView', )

from .exceptions import NotSpecifiedHandler, NotSpecifiedMethodName, \
    IncorrectMethodNameType, InvalidSerializer
from .serializers import JSONSerializer

http_methods = frozenset(['get', 'post', 'head', 'options', 'delete', 'put',
                          'trace', 'patch'])


class View(object):
    """Subclass for implementing class-based views."""
    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """Converts the class into an actual view function that can be used
        with the routing system.
        """
        pass


class MethodViewMeta(type):
    """Metaclass, which helps to define list of supported methods in
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


class MethodBasedView(View, metaclass=MethodViewMeta):
    """Class-based view for aiorest-ws framework."""
    serializers = ()

    def dispatch(self, request, *args, **kwargs):
        """Search the most suitable handler for request.

        :param request: passed request from user.
        """
        method = request.get('method', None)

        # invoked, when user not specified method in query (e.c. get, post)
        if not method:
            raise NotSpecifiedMethodName()

        # invoked, when user specified method name as not a string
        if not isinstance(method, str):
            raise IncorrectMethodNameType()

        # trying to find the most suitable handler
        method = method.lower().strip()
        handler = getattr(self, method, None)
        if not handler:
            raise NotSpecifiedHandler()
        return handler(request, *args, **kwargs)

    def get_serializer(self, preferred_format, *args, **kwargs):
        """Get serialize class, which using to converting response to
        some users format.

        :param preferred_format: string, which means serializing response to
                                 required format (e.c. json, xml).
        """
        if self.serializers:
            if type(self.serializers) not in (list, tuple):
                raise InvalidSerializer()

            serializer = None
            if preferred_format:
                # try to find suitable serializer
                for serializer_class in self.serializers:
                    if serializer_class.format == preferred_format:
                        serializer = serializer_class
                        break

            # when can't find required serializer, use first of them
            if not serializer:
                serializer = self.serializers[0]

            return serializer()
        else:
            return JSONSerializer()
