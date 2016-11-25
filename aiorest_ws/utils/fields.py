# -*- coding: utf-8 -*-
"""
This module provide special classes and functions, which using for make
work with model fields more user-friendly.
"""
import collections
import inspect

__all__ = (
    'is_simple_callable', 'method_overridden', 'get_attribute', 'set_value',
    'to_choices_dict', 'flatten_choices_dict'
)


def is_simple_callable(obj):
    """
    True if the object is a callable that takes no arguments.
    """
    function = inspect.isfunction(obj)
    method = inspect.ismethod(obj)

    if not (function or method):
        return False

    args, _, _, defaults = inspect.getargspec(obj)
    len_args = len(args) if function else len(args) - 1
    len_defaults = len(defaults) if defaults else 0
    return len_args <= len_defaults


def method_overridden(method_name, cls, instance):
    """
    Determine if a method has been overridden.
    """
    method = getattr(cls, method_name)
    default_method = getattr(method, '__func__', method)
    return default_method is not getattr(instance, method_name).__func__


def get_attribute(instance, attrs):
    """
    Similar to Python's built in `getattr(instance, attr)`, but takes a list
    of nested attributes, instead of a single attribute. Also accepts either
    attribute lookup on objects or dictionary lookups.
    """
    for attr in attrs:
        if instance is None:
            # Break out early if we get `None` at any point in a nested lookup
            return None

        if isinstance(instance, collections.Mapping):
            instance = instance[attr]
        else:
            instance = getattr(instance, attr)

        if is_simple_callable(instance):
            try:
                instance = instance()
            except (AttributeError, KeyError) as exc:
                # If we raised an Attribute or KeyError here it'd get treated
                # as an omitted field in `Field.get_attribute()`. Instead we
                # raise a ValueError to ensure the exception is not masked
                raise ValueError(
                    'Exception raised in callable attribute "{0}"; '
                    'original exception was: {1}'.format(attr, exc)
                )

    return instance


def set_value(dictionary, keys, value):
    """
    Similar to Python's built in `dictionary[key] = value`,
    but takes a list of nested keys instead of a single key.
    set_value({'a': 1}, [], {'b': 2}) -> {'a': 1, 'b': 2}
    set_value({'a': 1}, ['x'], 2) -> {'a': 1, 'x': 2}
    set_value({'a': 1}, ['x', 'y'], 2) -> {'a': 1, 'x': {'y': 2}}
    """
    if not keys:
        dictionary.update(value)
        return

    for key in keys[:-1]:
        if key not in dictionary:
            dictionary[key] = {}
        dictionary = dictionary[key]

    dictionary[keys[-1]] = value


def to_choices_dict(choices):
    """
    Convert choices into key/value dicts.
    to_choices_dict([1]) -> {1: 1}
    to_choices_dict([(1, '1st'), (2, '2nd')]) -> {1: '1st', 2: '2nd'}
    to_choices_dict([('Group', ((1, '1'), 2))]) -> {'Group': {1: '1', 2: '2'}}
    """
    # Allow single, paired or grouped choices style:
    # choices = [1, 2, 3]
    # choices = [(1, 'First'), (2, 'Second'), (3, 'Third')]
    # choices = [('Category', ((1, 'First'), (2, 'Second'))), (3, 'Third')]
    ret = collections.OrderedDict()
    for choice in choices:
        if (not isinstance(choice, (list, tuple))):
            # Single choice
            ret[choice] = choice
        else:
            key, value = choice
            if isinstance(value, (list, tuple)):
                # Grouped choices (category, sub choices)
                ret[key] = to_choices_dict(value)
            else:
                # Paired choice (key, display value)
                ret[key] = value
    return ret


def flatten_choices_dict(choices):
    """
    Convert a group choices dict into a flat dict of choices.
    flatten_choices_dict({1: '1st', 2: '2nd'}) -> {1: '1st', 2: '2nd'}
    flatten_choices_dict({'Key': {1: '1st', 2: '2nd'}}) -> {1: '1st', 2: '2nd'}
    """
    ret = collections.OrderedDict()
    for key, value in choices.items():
        if isinstance(value, dict):
            # Grouped choices (category, sub choices)
            for sub_key, sub_value in value.items():
                ret[sub_key] = sub_value
        else:
            # Choice (key, display value)
            ret[key] = value
    return ret
