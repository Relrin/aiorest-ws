# -*- coding: utf-8 -*-
"""
The `compat` module provides support for backwards compatibility with older
versions of Django, and compatibility wrappers around optional packages.
"""
import inspect

import django

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models


__all__ = [
    '_resolve_model', 'get_related_model', 'get_remote_field'
]


try:
    # DecimalValidator is unavailable in Django < 1.9
    from django.core.validators import DecimalValidator
except ImportError:
    DecimalValidator = None


def _resolve_model(obj):
    """
    Resolve supplied `obj` to a Django model class.
    `obj` must be a Django model class itself, or a string
    representation of one.  Useful in situations like GH #1225 where
    Django may not have resolved a string-based reference to a model in
    another model's foreign key definition.
    String representations should have the format:
        'appname.ModelName'
    """
    if isinstance(obj, str) and len(obj.split('.')) == 2:
        app_name, model_name = obj.split('.')
        resolved_model = apps.get_model(app_name, model_name)
        if resolved_model is None:
            msg = "Django did not return a model for {0}.{1}"
            raise ImproperlyConfigured(msg.format(app_name, model_name))
        return resolved_model
    elif inspect.isclass(obj) and issubclass(obj, models.Model):
        return obj
    raise ValueError("{0} is not a Django model".format(obj))


def get_related_model(field):
    if django.VERSION < (1, 9):
        return _resolve_model(field.rel.to)
    return field.remote_field.model


# field.rel is deprecated from 1.9 onwards
def get_remote_field(field, **kwargs):
    if 'default' in kwargs:
        if django.VERSION < (1, 9):
            return getattr(field, 'rel', kwargs['default'])
        return getattr(field, 'remote_field', kwargs['default'])

    if django.VERSION < (1, 9):
        return field.rel
    return field.remote_field
