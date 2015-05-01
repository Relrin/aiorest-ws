"""
    WebSocket status codes and functions for work with them

    For more detail information check link below:
        https://tools.ietf.org/html/rfc6455
"""
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
    return code >= 0 and code <= 999


def is_reserved(code):
    return code >= 1000 and code <= 2999


def is_library(code):
    return code >= 3000 and code <= 3999


def is_private(code):
    return code >= 4000 and code <= 4999
