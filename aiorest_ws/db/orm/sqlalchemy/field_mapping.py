# -*- coding: utf-8 -*-
"""
Helper functions for mapping model fields to a dictionary or any other
types, which help to serialize or deserialize data.
"""
from aiorest_ws.db.orm.sqlalchemy.validators import UniqueORMValidator, \
    ORMFieldValidator

from sqlalchemy import types, Column
from aiorest_ws.utils.field_mapping import needs_label
from aiorest_ws.utils.text import capfirst


__all__ = (
    'STRING_TYPES', 'get_detail_view_name', 'get_field_kwargs',
    'get_relation_kwargs', 'get_nested_relation_kwargs', 'get_url_kwargs'
)

STRING_TYPES = (
    types.String, types.Text, types.Unicode, types.UnicodeText, types.CHAR,
    types.NCHAR, types.NVARCHAR, types.CLOB, types.TEXT
)


def get_detail_view_name(model):
    """
    Given a model class, return the view name to use for URL relationships
    that refer to instances of the model.
    """
    return '%(model_name)s-detail' % {
        'model_name': model.__tablename__.lower()
    }


def get_field_kwargs(field_name, model_field, model_class):
    """
    Creates a default instance of a basic non-relational field.
    """
    mapper = model_class.__mapper__

    kwargs = {}
    field_validator = mapper.validators.get(field_name, None)
    validator_kwarg = []

    # The following will only be used by ModelField classes.
    # Gets removed for everything else
    kwargs['model_field'] = model_field

    if model_field.primary_key:
        # If this field is read-only, then return early.
        # Further keyword arguments are not valid
        kwargs['read_only'] = True
        return kwargs

    if model_field.default or model_field.nullable:
        kwargs['required'] = False

    if model_field.nullable:
        kwargs['allow_null'] = True

    if model_field.nullable and isinstance(model_field.type, STRING_TYPES):
        kwargs['allow_blank'] = True

    if isinstance(model_field.type, types.Enum):
        # If this model field contains choices, then return early.
        # Further keyword arguments are not valid
        kwargs['choices'] = model_field.type.enums
        return kwargs

    # Ensure that max_length is passed explicitly as a keyword arg, rather
    # than as a validator
    max_length = getattr(model_field.type, 'length', None)
    if max_length is not None and isinstance(model_field.type, STRING_TYPES):
        kwargs['max_length'] = max_length

    if getattr(model_field, 'unique', False):
        validator = UniqueORMValidator(model_class, field_name)
        validator_kwarg.append(validator)

    # If described table has a validator, then wrap him and call him later
    # when it will be necessary
    if field_validator:
        validator_func = field_validator[0]
        wrapper = ORMFieldValidator(validator_func, model_field, field_name)
        validator_kwarg.append(wrapper)

    if validator_kwarg:
        kwargs['validators'] = validator_kwarg

    return kwargs


def get_relation_kwargs(field_name, relation_info):
    """
    Creates a default instance of a flat relational field.
    """
    model_field = relation_info.model_field
    related_model = relation_info.related_model
    to_many = relation_info.to_many
    to_field = relation_info.to_field
    has_through_model = relation_info.has_through_model

    kwargs = {
        'queryset': related_model,
        'view_name': get_detail_view_name(related_model)
    }

    if to_many:
        kwargs['many'] = True

    if isinstance(to_field, Column):
        kwargs['to_field'] = to_field

    if has_through_model:
        kwargs['read_only'] = True
        kwargs.pop('queryset', None)

    if model_field:

        field_verbose_name = model_field.argument.arg or None
        if field_verbose_name and needs_label(field_verbose_name, field_name):
            kwargs['label'] = capfirst(field_verbose_name)

        if kwargs.get('read_only', False):
            # If this field is read-only, then return early.
            # No further keyword arguments are valid
            return kwargs

    return kwargs


def get_nested_relation_kwargs(relation_info):
    kwargs = {'read_only': True}
    if relation_info.to_many:
        kwargs['many'] = True
    return kwargs


def get_url_kwargs(model_field):
    return {
        'view_name': get_detail_view_name(model_field)
    }
