"""
    Exception classes for authentication.
"""
__all__ = ('BaseAuthException', 'PermissionDeniedException', )

from aiorest_ws.exceptions import BaseAPIException


class BaseAuthException(BaseAPIException):
    default_detail = u"Error occurred in the authentication process."


class PermissionDeniedException(BaseAuthException):
    default_detail = u"Permission denied: user doesn't have enough rights."
