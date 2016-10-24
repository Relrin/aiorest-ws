# -*- coding: utf-8 -*-
"""
Utility exceptions for resolve/reverse URLs purposes.
"""
__all__ = ('NoMatch', 'NoReverseMatch')


class NoMatch(Exception):
    pass


class NoReverseMatch(Exception):
    pass
