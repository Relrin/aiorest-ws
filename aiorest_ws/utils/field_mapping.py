# -*- coding: utf-8 -*-
"""
Helper functions for mapping model fields to a dictionary of default
keyword arguments that should be used for their equivalent serializer fields.
"""
import inspect

from aiorest_ws.utils.text import capfirst

__all__ = ('ClassLookupDict', 'needs_label')


class ClassLookupDict(object):
    """
    Takes a dictionary with classes as keys.
    Lookups against this object will traverses the object's inheritance
    hierarchy in method resolution order, and returns the first matching value
    from the dictionary or raises a KeyError if nothing matches.
    """
    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        if hasattr(key, '_proxy_class'):
            # Deal with proxy classes. Ie. BoundField behaves as if it
            # is a Field instance when using ClassLookupDict
            base_class = key._proxy_class
        else:
            base_class = key.__class__

        for cls in inspect.getmro(base_class):
            if cls in self.mapping:
                return self.mapping[cls]
        raise KeyError('Class %s not found in lookup.' % base_class.__name__)

    def __setitem__(self, key, value):
        self.mapping[key] = value


def needs_label(model_field_verbose_name, field_name):
    """
    Returns `True` if the label based on the model's verbose name is not equal
    to the default label it would have based on it's field name.
    """
    default_label = field_name.replace('_', ' ').capitalize()
    return capfirst(model_field_verbose_name) != default_label
