# -*- coding: utf-8 -*-
"""
Helper function for returning the field information that is associated
with a model class. This includes returning all the forward and reverse
relationships and their associated metadata.
"""
from collections import OrderedDict

from aiorest_ws.utils.structures import FieldInfo, RelationInfo
from aiorest_ws.db.orm.django.compat import get_related_model, \
    get_remote_field

__all__ = (
    '_get_pk', '_get_fields', '_get_to_field', '_get_forward_relationships',
    '_get_reverse_relationships', '_merge_fields_and_pk',
    '_merge_relationships', 'get_field_info', 'is_abstract_model'
)


def _get_pk(opts):
    pk = opts.pk
    rel = get_remote_field(pk)

    while rel and rel.parent_link:
        # If model is a child via multi-table inheritance, use parent's pk
        pk = get_related_model(pk)._meta.pk
        rel = get_remote_field(pk)

    return pk


def _get_fields(opts):
    fields = OrderedDict()
    opts_fields = [
        field for field in opts.fields
        if field.serialize and not get_remote_field(field)
    ]
    for field in opts_fields:
        fields[field.name] = field

    return fields


def _get_to_field(field):
    return getattr(field, 'to_fields', None) and field.to_fields[0]


def _get_forward_relationships(opts):
    """
    Returns an `OrderedDict` of field names to `RelationInfo`.
    """
    forward_relations = OrderedDict()
    forwards_fields = [
        field for field in opts.fields
        if field.serialize and get_remote_field(field)
    ]
    for field in forwards_fields:
        forward_relations[field.name] = RelationInfo(
            model_field=field,
            related_model=get_related_model(field),
            to_many=False,
            to_field=_get_to_field(field),
            has_through_model=False
        )

    # Deal with forward many-to-many relationships.
    many_to_many_fields = [
        field for field in opts.many_to_many
        if field.serialize
    ]
    for field in many_to_many_fields:
        forward_relations[field.name] = RelationInfo(
            model_field=field,
            related_model=get_related_model(field),
            to_many=True,
            # many-to-many do not have to_fields
            to_field=None,
            has_through_model=not get_remote_field(field).through._meta.auto_created  # NOQA
        )

    return forward_relations


def _get_reverse_relationships(opts):
    """
    Returns an `OrderedDict` of field names to `RelationInfo`.
    """
    reverse_relations = OrderedDict()
    all_related_objects = [
        r for r in opts.related_objects
        if not r.field.many_to_many
    ]
    for relation in all_related_objects:
        accessor_name = relation.get_accessor_name()
        related = getattr(relation, 'related_model', relation.model)
        reverse_relations[accessor_name] = RelationInfo(
            model_field=None,
            related_model=related,
            to_many=get_remote_field(relation.field).multiple,
            to_field=_get_to_field(relation.field),
            has_through_model=False
        )

    # Deal with reverse many-to-many relationships.
    all_related_many_to_many_objects = [
        r for r in opts.related_objects
        if r.field.many_to_many
    ]
    for relation in all_related_many_to_many_objects:
        has_through_model = False
        through = getattr(get_remote_field(relation.field), 'through', None)
        if through is not None:
            remote_field = get_remote_field(relation.field)
            has_through_model = not remote_field.through._meta.auto_created

        accessor_name = relation.get_accessor_name()
        related = getattr(relation, 'related_model', relation.model)
        reverse_relations[accessor_name] = RelationInfo(
            model_field=None,
            related_model=related,
            to_many=True,
            # many-to-many do not have to_fields
            to_field=None,
            has_through_model=has_through_model
        )

    return reverse_relations


def _merge_fields_and_pk(pk, fields):
    fields_and_pk = OrderedDict()
    fields_and_pk['pk'] = pk
    fields_and_pk[pk.name] = pk
    fields_and_pk.update(fields)

    return fields_and_pk


def _merge_relationships(forward_relations, reverse_relations):
    return OrderedDict(
        list(forward_relations.items()) +
        list(reverse_relations.items())
    )


def get_field_info(model):
    """
    Given a model class, returns a `FieldInfo` instance, which is a
    `namedtuple`, containing metadata about the various field types on the
    model including information about their relationships.
    """
    opts = model._meta.concrete_model._meta

    pk = _get_pk(opts)
    fields = _get_fields(opts)
    forward_relations = _get_forward_relationships(opts)
    reverse_relations = _get_reverse_relationships(opts)
    fields_and_pk = _merge_fields_and_pk(pk, fields)
    relationships = _merge_relationships(forward_relations, reverse_relations)

    return FieldInfo(pk, fields, forward_relations, reverse_relations,
                     fields_and_pk, relationships)


def is_abstract_model(model):
    """
    Given a model class, returns a boolean True if it is abstract and False
    if it is not.
    """
    has_meta_attribute = hasattr(model, '_meta')
    is_abstract = hasattr(model._meta, 'abstract') and model._meta.abstract
    return has_meta_attribute and is_abstract
