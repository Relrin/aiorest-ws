# -*- coding: utf-8 -*-
"""
    Exception classes for authentication.
"""
from aiorest_ws.exceptions import BaseAPIException

__all__ = ('BaseAuthException', 'PermissionDeniedException', )


class BaseAuthException(BaseAPIException):
    default_detail = u"Error occurred in the authentication process."


class PermissionDeniedException(BaseAuthException):
    default_detail = u"Permission denied: user doesn't have enough rights."
