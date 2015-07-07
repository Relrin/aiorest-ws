# -*- coding: utf-8 -*-
"""
    Handled exceptions raised by aiorest-ws framework, which inspired under
    Django REST framework

    :copyright: (c) 2015 by Savich Valeryi.
    :license: MIT, see LICENSE for more details.
"""
import status


__all__ = ('BaseAPIException', 'NotSupportedArgumentType',
           'NotSpecifiedHandler', 'NotSpecifiedMethodName',
           'IncorrectMethodNameType', 'NotImplementedSerializerMethod', )


class BaseAPIException(Exception):
    """Base class for aiorest-ws framework exceptions.

    All subclasses should provide `.status_code` and `.default_detail`
    properties.
    """
    status_code = status.WS_PROTOCOL_ERROR
    default_detail = u"A server error occurred."

    def __init__(self, detail=None):
        """Create an instance of exception with users detail information if
         it is passed.

        :param detail: users detail information (string)
        """
        if detail is not None:
            self.detail = str(detail)
        else:
            self.detail = self.default_detail

    def __str__(self):
        return self.detail


class NotSupportedArgumentType(BaseAPIException):
    default_detail = u"Check your arguments on supported types."


class NotSpecifiedHandler(BaseAPIException):
    default_detail = u"For URL, typed in request, handler not specified."


class NotSpecifiedMethodName(BaseAPIException):
    default_detail = u"In query not specified `method` argument."


class IncorrectMethodNameType(BaseAPIException):
    default_detail = u"Method name should be a string type."


class NotImplementedSerializerMethod(BaseAPIException):
    default_detail = u"Error occurred in not implemented method of serializer."
