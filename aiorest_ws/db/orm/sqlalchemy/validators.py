# -*- coding: utf-8 -*-
"""
Special validator classes and functions, applied for checking passed data.
"""
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.sqlalchemy.mixins import ORMSessionMixin
from aiorest_ws.db.orm.validators import BaseValidator, \
    BaseUniqueFieldValidator

__all__ = ('ORMFieldValidator', 'UniqueORMValidator', )


class ORMFieldValidator(BaseValidator):
    message = u"Assertion error for `{field}` field with `{value}` value."

    def __init__(self, validator_func, model_field, field_name, **kwargs):
        super(ORMFieldValidator, self).__init__(**kwargs)
        self.validator_func = validator_func
        self.model_field = model_field
        self.field_name = field_name

    def __call__(self, value):
        try:
            self.validator_func(self.model_field, self.field_name, value)
        except AssertionError as exc:
            message = exc.args[0] if exc.args else self.message.format(
                field=self.field_name, value=value
            )
            raise ValidationError(message)


class UniqueORMValidator(BaseUniqueFieldValidator, ORMSessionMixin):
    """
    Validator that corresponds to `unique=True` on a model field.
    Should be applied to an individual field on the serializer.
    """
    def __init__(self, model, field_name, message=None):
        super(UniqueORMValidator, self).__init__(model, message)
        self.model = model
        self.field_name = field_name
        self.instance = None

    def filter_queryset(self, value, queryset):
        filter_field = getattr(self.model, self.field_name)
        return queryset.filter(filter_field == value)

    def exclude_current_instance(self, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        if self.instance:
            pk_fields = [
                column.name
                for column in self.instance.__mapper__.primary_key
            ]
            filter_args = [
                getattr(self.model, attr) != getattr(self.instance, attr)
                for attr in pk_fields
            ]
            return queryset.filter(*filter_args)
        return queryset

    def __call__(self, value):
        session = self._get_session()
        try:
            queryset = session.query(self.model)
            queryset = self.filter_queryset(value, queryset)
            queryset = self.exclude_current_instance(queryset)

            if session.query(queryset.exists()).scalar():
                raise ValidationError(self.message)
        finally:
            session.close()
