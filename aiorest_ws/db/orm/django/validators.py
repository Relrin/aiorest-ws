# -*- coding: utf-8 -*-
"""
We perform uniqueness checks explicitly on the serializer class, rather
the using Django's `.full_clean()`.

This gives us better separation of concerns, allows us to use single-step
object creation, and makes it possible to switch between using the implicit
`ModelSerializer` class and an equivalent explicit `Serializer` class.
"""
from django.db import DataError
from django.utils.translation import ugettext_lazy as _

from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.representation import smart_repr

__all__ = ('qs_exists', 'qs_filter', 'UniqueValidator', )


def qs_exists(queryset):
    try:
        return queryset.exists()
    except (TypeError, ValueError, DataError):
        return False


def qs_filter(queryset, **kwargs):
    try:
        return queryset.filter(**kwargs)
    except (TypeError, ValueError, DataError):
        return queryset.none()


class UniqueValidator(object):
    """
    Validator that corresponds to `unique=True` on a model field.
    Should be applied to an individual field on the serializer.
    """
    message = _('This field must be unique.')

    def __init__(self, queryset, message=None):
        self.queryset = queryset
        self.serializer_field = None
        self.message = message or self.message

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set
        self.field_name = serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation
        self.instance = getattr(serializer_field.parent, 'instance', None)

    def filter_queryset(self, value, queryset):
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {self.field_name: value}
        return qs_filter(queryset, **filter_kwargs)

    def exclude_current_instance(self, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        if self.instance is not None:
            return queryset.exclude(pk=self.instance.pk)
        return queryset

    def __call__(self, value):
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset)
        queryset = self.exclude_current_instance(queryset)
        if qs_exists(queryset):
            raise ValidationError(self.message)

    def __repr__(self):
        return repr('<%s(queryset=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        ))
