# -*- coding: utf-8 -*-
"""
    Handled exceptions raised by aiorest-ws framework, which inspired under
    Django REST framework
"""
import status


__all__ = ('BaseAPIException', 'NotSupportedArgumentType',
           'NotResolvedRequest')


class BaseAPIException(Exception):
    """
        Base class for aiorest-ws framework exceptions
        All subclasses should provide `.status_code` and `.default_detail`
        properties
    """
    status_code = status.WS_PROTOCOL_ERROR
    default_detail = "A server error occurred."

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = str(detail)
        else:
            self.detail = self.default_detail

    def __str__(self):
        return self.detail


class NotSupportedArgumentType(BaseAPIException):
    default_detail = "Check your arguments on supported types."


class NotResolvedRequest(BaseAPIException):
    default_detail = "For URL, typed in request, handler not specified."
