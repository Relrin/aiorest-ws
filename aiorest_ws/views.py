# -*- coding: utf-8 -*-
"""
    This module provide a function and class-based views and can be used
    with aiorest-ws routers.
"""
__all__ = ('MethodBasedView', )

from .exceptions import NotSpecifiedHandler, NotSpecifiedMethodName, \
    IncorrectMethodNameType, InvalidSerializer
from .serializers import JSONSerializer


class MethodBasedView(object):
    """Method-based view for aiorest-ws framework."""
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
        # for that what we are doing:
        # 1) make string in lowercase (e.c. 'GET' -> 'get')
        # 2) look into class and try to get handler with this name
        # 3) if extracting is successful, then invoke handler with arguments
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
