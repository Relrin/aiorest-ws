# -*- coding: utf-8 -*-
"""
Field entities, implemented for support SQLAlchemy ORM.

Every class, represented here, is associated with one certain field type of
table relatively to SQLAlchemy ORM. Each of them field also used later for
serializing/deserializing object of ORM.
"""
from aiorest_ws.conf import settings
from aiorest_ws.db.orm import fields
from aiorest_ws.utils.fields import method_overridden

from sqlalchemy import TypeDecorator

__all__ = (
    'IntegerField', 'BigIntegerField', 'SmallIntegerField', 'BooleanField',
    'NullBooleanField', 'CharField', 'EnumField', 'FloatField', 'DecimalField',
    'TimeField', 'DateField', 'DateTimeField', 'IntervalField', 'JSONField',
    'ModelField', 'PickleField', 'LargeBinaryField', 'ReadOnlyField',
    'ListField', 'DictField', 'HStoreField', 'SerializerMethodField'
)


class IntegerField(fields.IntegerField):
    pass


class BigIntegerField(fields.BigIntegerField):
    pass


class SmallIntegerField(fields.SmallIntegerField):
    pass


class BooleanField(fields.BooleanField):
    pass


class CharField(fields.CharField):
    pass


class EnumField(fields.ChoiceField):
    pass


class FloatField(fields.FloatField):
    pass


class NullBooleanField(fields.NullBooleanField):
    pass


class DecimalField(fields.DecimalField):
    pass


class TimeField(fields.TimeField):
    pass


class DateField(fields.DateField):
    pass


class DateTimeField(fields.DateTimeField):
    pass


class IntervalField(fields.TimeDeltaField):
    pass


class ListField(fields.ListField):
    pass


class DictField(fields.DictField):
    pass


class HStoreField(fields.HStoreField):
    pass


class JSONField(fields.JSONField):
    pass


class ModelField(fields.ModelField):
    """
    A generic field that can be used against an arbitrary model field.
    This is used by `ModelSerializer` when dealing with custom model fields,
    that do not have a serializer field to be mapped to.

    For more details recommended to read the next page in SQLAlchemy docs:
    http://docs.sqlalchemy.org/en/latest/core/type_api.html
    """
    def __init__(self, model_field, **kwargs):
        super(ModelField, self).__init__(model_field, **kwargs)
        self.field_type = self.model_field.type

    @property
    def dialect(self):
        return settings.SQLALCHEMY_ENGINE.dialect

    def type_has_custom_behaviour(self, func_name):
        return hasattr(self.field_type, func_name) and \
            method_overridden(func_name, TypeDecorator, self.field_type)

    def to_internal_value(self, data):
        # Custom implementation of converting data for database
        if self.type_has_custom_behaviour('process_bind_param'):
            return self.field_type.process_bind_param(data, self.dialect)

        processor_func = self.field_type.bind_processor(self.dialect)
        if processor_func:
            return processor_func(data)
        return data

    def to_representation(self, obj):
        # Custom implementation of representation of data
        if self.type_has_custom_behaviour('process_result_value'):
            return self.field_type.process_result_value(obj, self.dialect)

        processor_func = self.field_type.result_processor(
            self.dialect, self.field_type
        )
        if processor_func:
            return processor_func(obj)
        return obj


class ReadOnlyField(fields.ReadOnlyField):
    pass


class PickleField(fields.PickleField):
    pass


class LargeBinaryField(fields.LargeBinaryField):
    pass


class SerializerMethodField(fields.SerializerMethodField):
    pass
