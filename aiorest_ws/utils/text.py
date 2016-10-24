# -*- coding: utf-8 -*-
"""
Special classes and function which help to work with strings correctly.
"""
from aiorest_ws.utils.encoding import force_text

__all__ = ('capfirst', )


def capfirst(x):
    return x and force_text(x)[0].upper() + force_text(x)[1:]
