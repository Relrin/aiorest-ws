# -*- coding: utf-8 -*-
"""
The `compat` module provides support for backwards compatibility with older
versions of Django, and compatibility wrappers around optional packages.
"""
import inspect

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models


try:
    from django.contrib.postgres import fields as postgres_fields
except ImportError:
    postgres_fields = None


try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    JSONField = None


__all__ = [
    'postgres_fields', 'JSONField', '_resolve_model',
    'get_related_model', 'get_remote_field', 'value_from_object'
]


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
    return field.remote_field.model


def get_remote_field(field, **kwargs):
    return field.remote_field


def value_from_object(field, obj):
    return field.value_from_object(obj)
