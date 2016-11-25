# -*- coding: utf-8 -*-
"""
Special functions for additional and safety encoding passed data.
"""
import datetime
from decimal import Decimal

from aiorest_ws.utils.serializer_helpers import ReturnList, ReturnDict

__all__ = (
    '_PROTECTED_TYPES', 'is_protected_type', 'force_text',
    'force_text_recursive',
)

_PROTECTED_TYPES = (
    str, type(None), float, Decimal, datetime.datetime, datetime.date,
    datetime.time
)


def is_protected_type(obj):
    """
    Determine if the object instance is of a protected type.
    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons
    if issubclass(type(s), str):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not issubclass(type(s), str):
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            else:
                s = str(s)
        else:
            # Note: We use .decode() here, instead of six.text_type(s,
            # encoding, errors), so that if s is a SafeBytes, it ends up
            # being a SafeText at the end
            s = s.decode(encoding, errors)
    except UnicodeDecodeError:
        # If we get to here, the caller has passed in an Exception
        # subclass populated with non-ASCII bytestring data without a
        # working unicode method. Try to handle this without raising a
        # further exception by individually forcing the exception args
        # to unicode
        s = ' '.join(force_text(arg, encoding, strings_only, errors)
                     for arg in s)
    return s


def force_text_recursive(data):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings into plain text.
    """
    if isinstance(data, list):
        ret = [force_text_recursive(item) for item in data]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return data
    elif isinstance(data, dict):
        ret = {
            key: force_text_recursive(value)
            for key, value in data.items()
        }
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return data
    return force_text(data)
