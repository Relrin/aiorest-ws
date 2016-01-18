# -*- coding: utf-8 -*-
"""
Field entities, implemented for support SQLAlchemy ORM.

Every class, represented here, is associated with one certain field type of
table relatively to SQLAlchemy ORM. Each of them field also used later for
serializing/deserializing object of ORM.
"""
from aiorest_ws.conf import settings
from aiorest_ws.db.orm import fields
from sqlalchemy import processors

__all__ = (
    'IntegerField', 'BigIntegerField', 'SmallIntegerField', 'BooleanField',
    'NullBooleanField', 'CharField', 'TextField', 'EnumField', 'FloatField',
    'DecimalField', 'TimeField', 'DateField', 'DateTimeField', 'IntervalField',
    'JSONField', 'ModelField', 'PickleField', 'LargeBinaryField',
    'ReadOnlyField', 'ListField', 'DictField', 'HStoreField',
    'SerializerMethodField'
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


class TextField(fields.TextField):
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

    For more details, I recommend to read the next page in SQLAlchemy docs:
    http://docs.sqlalchemy.org/en/latest/core/type_api.html
    """
    def __init__(self, model_field, **kwargs):
        super(ModelField, self).__init__(model_field, **kwargs)
        self.field_type = self.model_field.type

    @property
    def dialect(self):
        return settings.ENGINE.dialect

    def to_internal_value(self, data):
        # Custom implementation of converting data
        if hasattr(self.field_type, 'process_literal_param'):
            self.field_type.process_literal_param(data, self.dialect)
        return self.field_type.literal_processor(self.dialect)(data)

    def to_representation(self, obj):
        # Custom implementation of representation of data
        if hasattr(self.field_type, 'process_result_value'):
            self.field_type.process_result_value(obj, self.dialect)

        default_processor = self.field_type.result_processor(
            self.dialect, self.field_type
        )
        if default_processor:
            return default_processor(obj)
        return processors.to_str(obj)


class ReadOnlyField(fields.ReadOnlyField):
    pass


class PickleField(fields.PickleField):
    pass


class LargeBinaryField(fields.LargeBinaryField):
    pass


class SerializerMethodField(fields.SerializerMethodField):
    pass
