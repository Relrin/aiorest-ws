"""
    WebSocket status codes and functions for work with them

    For more detail information check link below:
        https://tools.ietf.org/html/rfc6455
"""
__all__ = ('WS_NORMAL', 'WS_GOING_AWAY', 'WS_PROTOCOL_ERROR',
           'WS_DATA_CANNOT_ACCEPT', 'WS_RESERVED', 'WS_NO_STATUS_CODE',
           'WS_CLOSED_ABNORMALLY', 'WS_MESSAGE_NOT_CONSISTENT',
           'WS_MESSAGE_VIOLATE_POLICY', 'WS_MESSAGE_TOO_BIG',
           'WS_SERVER_DIDNT_RETURN_EXTENSIONS', 'WS_UNEXPECTED_CONDITION',
           'WS_FAILURE_TLS',

           'is_not_used', 'is_reserved', 'is_library', 'is_private')


WS_NORMAL = 1000
WS_GOING_AWAY = 1001
WS_PROTOCOL_ERROR = 1002
WS_DATA_CANNOT_ACCEPT = 1003
WS_RESERVED = 1004
WS_NO_STATUS_CODE = 1005
WS_CLOSED_ABNORMALLY = 1006
WS_MESSAGE_NOT_CONSISTENT = 1007
WS_MESSAGE_VIOLATE_POLICY = 1008
WS_MESSAGE_TOO_BIG = 1009
WS_SERVER_DIDNT_RETURN_EXTENSIONS = 1010
WS_UNEXPECTED_CONDITION = 1011
WS_FAILURE_TLS = 1015


def is_not_used(code):
    return 0 <= code <= 999


def is_reserved(code):
    return 1000 <= code <= 2999


def is_library(code):
    return 3000 <= code <= 3999


def is_private(code):
    return 4000 <= code <= 4999
