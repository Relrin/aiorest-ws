# -*- coding: utf-8 -*-
"""
This module provide structures for data representation of received model.
"""
from collections import namedtuple

__all__ = ('FieldInfo', 'RelationInfo')


FieldInfo = namedtuple('FieldResult', [
    'pk',  # Model field instance
    'fields',  # Dict of field name -> model field instance
    'forward_relations',  # Dict of field name -> RelationInfo
    'reverse_relations',  # Dict of field name -> RelationInfo
    'fields_and_pk',  # Shortcut for 'pk' + 'fields'
    'relations'  # Shortcut for 'forward_relations' + 'reverse_relations'
])

RelationInfo = namedtuple('RelationInfo', [
    'model_field',
    'related_model',
    'to_many',
    'to_field',
    'has_through_model'
])
