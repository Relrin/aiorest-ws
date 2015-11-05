# -*- coding: utf-8 -*-
"""
    Handled exceptions raised by aiorest-ws framework, which inspired under
    Django REST framework.
"""
from aiorest_ws.status import WS_PROTOCOL_ERROR, WS_DATA_CANNOT_ACCEPT

__all__ = (
    'BaseAPIException', 'EndpointValueError', 'IncorrectArgument',
    'IncorrectMethodNameType', 'InvalidHandler', 'InvalidPathArgument',
    'InvalidSerializer', 'NotImplementedMethod', 'NotSpecifiedError',
    'NotSpecifiedHandler', 'NotSpecifiedMethodName', 'NotSpecifiedURL',
    'NotSupportedArgumentType', 'SerializerError',
)


class BaseAPIException(Exception):
    """Base class for aiorest-ws framework exceptions.

    All subclasses should provide `.status_code` and `.default_detail`
    properties.
    """
    status_code = WS_PROTOCOL_ERROR
    default_detail = u"A server error occurred."

    def __init__(self, detail=None):
        """Create an instance of exception with users detail information if
        it is passed.

        :param detail: users detail information (string).
        """
        if detail is not None:
            self.detail = str(detail)
        else:
            self.detail = self.default_detail

    def __str__(self):
        return self.detail


class EndpointValueError(BaseAPIException):
    default_detail = u"Incorrect endpoint. Check path to your API."


class IncorrectArgument(BaseAPIException):
    status_code = WS_DATA_CANNOT_ACCEPT
    default_detail = u"Check `args` in query on errors and try again."


class IncorrectMethodNameType(BaseAPIException):
    default_detail = u"Method name should be a string type."


class InvalidHandler(BaseAPIException):
    default_detail = u"Received handler isn't correct. It shall be function" \
                     u" or class, inherited from the MethodBasedView class."


class InvalidPathArgument(BaseAPIException):
    default_detail = u"Received path value not valid."


class InvalidSerializer(BaseAPIException):
    default_detail = "Attribute `serializers` should be defined as list or " \
                     "tuple of inherited from BaseSerializer classes."


class NotImplementedMethod(BaseAPIException):
    default_detail = u"Error occurred in not implemented method."


class NotSpecifiedError(BaseAPIException):
    default_detail = u"Not specified parameter."


class NotSpecifiedHandler(NotSpecifiedError):
    default_detail = u"For URL, typed in request, handler not specified."


class NotSpecifiedMethodName(NotSpecifiedError):
    default_detail = u"In query not specified `method` argument."


class NotSpecifiedURL(NotSpecifiedError):
    default_detail = u"In query not specified `url` argument."


class NotSupportedArgumentType(BaseAPIException):
    status_code = WS_DATA_CANNOT_ACCEPT
    default_detail = u"Check your arguments on supported types."


class SerializerError(BaseAPIException):
    default_detail = u"Error occurred inside serializer class."
