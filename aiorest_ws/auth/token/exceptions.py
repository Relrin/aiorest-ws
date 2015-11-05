# -*- coding: utf-8 -*-
"""
    Exception classes for token authentication.
"""
from aiorest_ws.exceptions import BaseAPIException

__all__ = (
    'BaseTokenException', 'ParsingTokenException', 'InvalidSignatureException',
    'TokenNotBeforeException', 'TokenExpiredException',
    'TokenNotProvidedException',
)


class BaseTokenException(BaseAPIException):
    default_detail = u"Occurred error, when aiorest-ws processing token."


class ParsingTokenException(BaseTokenException):
    default_detail = u"Can't parse token: mismatch format."


class InvalidSignatureException(BaseTokenException):
    default_detail = u"Token signature is invalid."


class TokenNotBeforeException(BaseTokenException):
    default_detail = u"Time after which the token not be accepted has passed."


class TokenExpiredException(BaseTokenException):
    default_detail = u"Token has expired."


class TokenNotProvidedException(BaseTokenException):
    default_detail = u"Token has not provided in the request."
