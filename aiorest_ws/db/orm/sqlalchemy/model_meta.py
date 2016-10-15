# -*- coding: utf-8 -*-
"""
Module with special functions, which using for extracting data from inner
`Meta` table of certain model serializer.
"""
from collections import OrderedDict
from sqlalchemy.orm.interfaces import MANYTOMANY, MANYTOONE, ONETOMANY

from aiorest_ws.utils.structures import FieldInfo, RelationInfo

__all__ = [
    '_get_pk', '_get_fields', '_get_to_field', '_get_relations',
    '_get_forward_relationships', '_get_reverse_relationships',
    '_merge_fields_and_pk', '_merge_relationships', 'get_field_info',
    'is_abstract_model', 'get_relations_data', 'model_pk'
]


def _get_pk(mapper):
    """
    Extract primary keys from passed table.
    Mapper of SQLAlchemy returns list of primary keys by default.
    """
    return [(column.name, column) for column in mapper.primary_key]


def _get_fields(mapper):
    """
    Extract list of available fields in the table.
    """
    return OrderedDict(mapper.columns.items())


def _get_relations(mapper, direction_symbol):
    """
    Return a 'RelationshipProperty' properties maintained by mapper.
    """
    return [
        (field_name, relation)
        for field_name, relation in mapper.relationships.items()
        if relation.direction == direction_symbol
    ]


def _get_to_field(field):
    """
    Extract remote field with which model had relation.
    """
    remote_side = getattr(field, 'remote_side', None)
    return list(remote_side)[0] if remote_side else None


def _get_forward_relationships(mapper):
    """
    Returns an `OrderedDict` of field names to `RelationInfo`.
    """
    forward_relations = OrderedDict()

    # Foreign keys (one to many)
    fk_relations = _get_relations(mapper, ONETOMANY)
    for field_name, relationship_property in fk_relations:
        forward_relations[field_name] = RelationInfo(
            model_field=relationship_property,
            related_model=mapper.class_,
            to_many=False,
            to_field=_get_to_field(relationship_property),
            has_through_model=False
        )

    return forward_relations


def _get_reverse_relationships(mapper):
    """
    Returns an `OrderedDict` of field names to `RelationInfo`.

    """
    reverse_relations = OrderedDict()

    # Foreign keys (many to one)
    reverse_fk_relations = _get_relations(mapper, MANYTOONE)
    for field_name, relationship_property in reverse_fk_relations:
        reverse_relations[field_name] = RelationInfo(
            model_field=relationship_property,
            related_model=mapper.class_,
            to_many=False,
            to_field=_get_to_field(relationship_property),
            has_through_model=False
        )

    # Many to many
    m2m_relations = _get_relations(mapper, MANYTOMANY)
    for field_name, relationship_property in m2m_relations:
        reverse_relations[field_name] = RelationInfo(
            model_field=relationship_property,
            related_model=mapper.class_,
            to_many=True,
            # manytomany do not have to_fields
            to_field=None,
            has_through_model=True
        )

    return reverse_relations


def _merge_fields_and_pk(pk, fields):
    """
    Collecting all fields into one dictionary object.
    """
    fields_and_pk = OrderedDict()
    fields_and_pk.update(pk)
    fields_and_pk.update(fields)
    return fields_and_pk


def _merge_relationships(forward_relations, reverse_relations):
    """
    Merge two different relations into one dictionary object.
    """
    return OrderedDict(
        list(forward_relations.items()) + list(reverse_relations.items())
    )


def get_field_info(model):
    """
    Given a model class, returns a `FieldInfo` instance, which is a
    `namedtuple`, containing metadata about the various field types on the
    model including information about their relationships.
    """
    mapper = model.__mapper__

    pk = _get_pk(mapper)
    fields = _get_fields(mapper)
    forward_relations = _get_forward_relationships(mapper)
    reverse_relations = _get_reverse_relationships(mapper)
    fields_and_pk = _merge_fields_and_pk(pk, fields)
    relationships = _merge_relationships(forward_relations, reverse_relations)

    return FieldInfo(pk, fields, forward_relations, reverse_relations,
                     fields_and_pk, relationships)


def is_abstract_model(model):
    """
    Checks model whether it abstract or not.
    """
    is_instantiated_table = hasattr(model, '__table__')
    has_specified_abstract_attribute = getattr(model, '__abstract__', False)
    return not is_instantiated_table and has_specified_abstract_attribute


def get_relations_data(model, validated_data):
    relations = {}
    info = get_field_info(model)
    for field_name, relation_info in info.relations.items():
        is_relation_field = False
        if relation_info.to_many or relation_info.to_field is not None:
            is_relation_field = True

        if is_relation_field and field_name in validated_data:
            relations[field_name] = validated_data.pop(field_name)

    return relations


def model_pk(model):
    field_name_and_column_pairs = _get_pk(model.__mapper__)
    field_mapper = dict(field_name_and_column_pairs)
    return list(field_mapper.keys())
