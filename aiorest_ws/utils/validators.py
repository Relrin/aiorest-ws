# -*- coding: utf-8 -*-
"""
This module contains function, which using at validators.py for type
checking issues.
"""
from inspect import isclass

__all__ = ('to_str', 'get_object_type', )


def to_str(obj):
    """
    Custom convert object to string representation.
    """
    if isinstance(obj, (list, tuple)):
        string = "/".join([item.__name__ for item in obj])
    else:
        string = obj.__name__
    return string


def get_object_type(value):
    """
    Getting object type.
    """
    return type(value) if not isclass(value) else value
