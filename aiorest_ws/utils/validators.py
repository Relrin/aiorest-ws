# -*- coding: utf-8 -*-
"""
    This module contains function, which using at validators.py for type
    checking issues.
"""
from inspect import isclass

__all__ = ('to_str', 'get_object_type', )


def to_str(obj):
    """Custom convert object to string representation."""
    if type(obj) in (list, tuple):
        string = "/".join([item.__name__ for item in obj])
    else:
        string = obj.__name__
    return string


def get_object_type(value):
    """Getting object type."""
    if not isclass(value):
        obj_type = type(value)
    else:
        obj_type = value
    return obj_type
