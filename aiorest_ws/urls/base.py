# -*- coding: utf-8 -*-
"""
Special module, which provide access to all registered URLs, defined in the
main application.
"""
from threading import local

__all__ = ('set_urlconf', 'get_urlconf')
_urlconfs = local()  # Overridden it for each thread are stored here


def set_urlconf(urlconf_data):
    """
    Set the _urlconf for the current thread
    """
    _urlconfs.data = urlconf_data


def get_urlconf(default=None):
    """
    Return the root data from the _urlconf variable, if it has been
    changed from the default one.
    """
    return getattr(_urlconfs, "data", default)
