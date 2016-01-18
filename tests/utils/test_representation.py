# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.db.orm import fields, serializers, relations
from aiorest_ws.db.orm.validators import BaseValidator
from aiorest_ws.utils.representation import smart_repr, field_repr, \
    serializer_repr, list_repr

from tests.fixtures.fakes import FakeView


class FakePkField(relations.PrimaryKeyRelatedField, relations.RelatedField):
    many_related_field = relations.ManyRelatedField


class FakeModelSerializer(serializers.ModelSerializer):
    child = None
    fields = {'pk': fields.IntegerField()}


class FakeListModelSerializer(serializers.ListSerializer):
    child = FakeModelSerializer()


class FakeNestedModelSerializer(serializers.ModelSerializer):
    child = None
    fields = {'nested': FakeModelSerializer()}


class FakeNestedModelSerializerWithList(serializers.ModelSerializer):
    child = None
    fields = {'nested': FakeListModelSerializer()}


class FakeModelSerializerWithRelatedField(serializers.ModelSerializer):
    child = None
    fields = {'related': relations.ManyRelatedField(
        child_relation=relations.RelatedField(read_only=True)
    )}


class FakeModelSerializerWithValidators(serializers.ModelSerializer):
    child = None
    fields = {'pk': fields.IntegerField()}
    validators = [BaseValidator, ]


@pytest.mark.parametrize("value, expected", [
    ("test_string", "test_string"),
    (["value_1", "value_2"], "['value_1', 'value_2']"),
    ({"key": "value"}, "{'key': 'value'}"),
    (FakeView(), "<tests.fixtures.fakes.FakeView object>")
])
def test_smart_repr(value, expected):
    assert smart_repr(value) == expected


@pytest.mark.parametrize("field, many, expected", [
    (fields.IntegerField(), False, 'IntegerField()'),
    (fields.LargeBinaryField(object, allow_null=True), False,
     "LargeBinaryField(<class 'object'>, allow_null=True)"),
    (FakePkField(many=True, read_only=True), True,
     "bool(child_relation=<utils.test_representation.FakePkField object>, "
     "many=True, read_only=True)")
])
def test_field_repr(field, many, expected):
    assert field_repr(field, force_many=many) == expected


@pytest.mark.parametrize("serializer, indent, force_many, expected", [
    (FakeModelSerializer(), 1, False,
     "FakeModelSerializer():\n"
     "    pk = IntegerField()"),
    (FakeNestedModelSerializer(), 1, False,
     "FakeNestedModelSerializer():\n"
     "    nested = FakeModelSerializer():\n"
     "        pk = IntegerField()"),
    (FakeNestedModelSerializerWithList(), 1, False,
     "FakeNestedModelSerializerWithList():\n"
     "    nested = FakeModelSerializer(many=True):\n"
     "        pk = IntegerField()"),
    (FakeModelSerializerWithRelatedField(), 1, False,
     "FakeModelSerializerWithRelatedField():\n"
     "    related = RelatedField(many=True, read_only=True)"),
    (FakeModelSerializerWithValidators(), 1, False,
     "FakeModelSerializerWithValidators():\n"
     "    pk = IntegerField()\n"
     "    class Meta:\n"
     "        validators = [<class "
     "'aiorest_ws.db.orm.validators.BaseValidator'>]"),
])
def test_serializer_repr(serializer, indent, force_many, expected):
    assert serializer_repr(serializer, indent, force_many) == expected


@pytest.mark.parametrize("serializer, indent, expected", [
    (FakeModelSerializer(), 1, "FakeModelSerializer()"),
    (FakeListModelSerializer(), 1,
     "FakeModelSerializer(many=True):\n"
     "    pk = IntegerField()")
])
def test_list_repr(serializer, indent, expected):
    assert list_repr(serializer, indent) == expected
