# -*- coding: utf-8 -*-
import unittest

import copy
from collections import OrderedDict

from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm import fields
from aiorest_ws.db.orm.abstract import empty, SkipField
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.serializers import BaseSerializer, Serializer, \
    raise_errors_on_nested_writes, ListSerializer, ModelSerializer, \
    HyperlinkedModelSerializerMixin
from aiorest_ws.db.orm.validators import MinValueValidator, \
    BaseUniqueFieldValidator
from aiorest_ws.utils.serializer_helpers import BoundField, NestedBoundField, \
    ReturnList, ReturnDict
from aiorest_ws.utils.structures import FieldInfo, RelationInfo


class TestBaseSerializer(unittest.TestCase):

    def test_init_with_initial_data(self):
        initial_data = {"key": "value"}
        instance = BaseSerializer(data=initial_data)
        self.assertEqual(instance.initial_data, initial_data)

    def test_many_init_raises_improperly_configured_exception(self):

        with self.assertRaises(ImproperlyConfigured):
            BaseSerializer(many=True, allow_empty=True)

    def test_many_init_with_overridden_list_serializer(self):

        class FakeSerializer(BaseSerializer):
            default_list_serializer = ListSerializer

        instance = FakeSerializer(many=True)
        self.assertIsInstance(instance, ListSerializer)

    def test_error_property_raises_assertion_error(self):
        instance = BaseSerializer()

        with self.assertRaises(AssertionError):
            instance.errors

    def test_error_property_returns_lists_of_error(self):

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=5, validators=[MinValueValidator(10), ])

        with self.assertRaises(ValidationError):
            instance.is_valid(raise_exception=True)

        self.assertEqual(
            instance.errors,
            ['Ensure this value is greater than or equal to 10.']
        )

    def test_validated_data_property_raises_assertion_error(self):
        instance = BaseSerializer()

        with self.assertRaises(AssertionError):
            instance.validated_data

    def test_validated_data_property_returns_lists_of_error(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=5)
        self.assertTrue(instance.is_valid(raise_exception=True))
        self.assertEqual(instance.validated_data, 5)

    def test_data_property_raises_assertion_error(self):
        instance = BaseSerializer(data=5)

        with self.assertRaises(AssertionError):
            instance.data

    def test_data_property_returns_instance(self):

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def to_representation(self, instance):
                return instance

        value = object()
        instance = FakeSerializer(instance=value)
        self.assertEqual(instance.data, value)

    def test_data_returns_validated_data(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def to_representation(self, instance):
                return instance

        instance = FakeSerializer(data=5)
        self.assertTrue(instance.is_valid(raise_exception=True))
        self.assertEqual(instance.data, 5)

    def test_data_returns_initial_data(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=5, validators=[MinValueValidator(10), ])

        with self.assertRaises(ValidationError):
            instance.is_valid(raise_exception=True)

        self.assertIsNone(instance.data, None)

    def test_to_internal_value_raises_not_implemented_error(self):
        instance = BaseSerializer()

        with self.assertRaises(NotImplementedError):
            instance.to_internal_value({"key": "value"})

    def test_to_representation_raises_not_implemented_error(self):
        instance = BaseSerializer()

        with self.assertRaises(NotImplementedError):
            instance.to_representation({"key": "value"})

    def test_update_raises_not_implemented_error(self):
        instance = BaseSerializer()

        with self.assertRaises(NotImplementedError):
            instance.create({"key": "value"})

    def test_create_raises_not_implemented_error(self):
        instance = BaseSerializer()

        with self.assertRaises(NotImplementedError):
            instance.update(object(), {"key": "value"})

    def test_save_raises_assertion_error_for_not_called_is_valid_method(self):
        instance = BaseSerializer()

        with self.assertRaises(AssertionError):
            instance.save()

    def test_save_raises_assertion_error_for_invalid_data(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=5, validators=[MinValueValidator(10), ])

        with self.assertRaises(ValidationError):
            instance.is_valid(raise_exception=True)

        with self.assertRaises(AssertionError):
            instance.save()

    def test_save_raises_assertion_error_for_commit_in_kwargs(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data={"key": "value"})
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save(commit=True)

    def test_save_raises_assertion_error_for_data_property(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def to_representation(self, instance):
                return instance

        instance = FakeSerializer(data={"key": "value"})
        self.assertTrue(instance.is_valid(raise_exception=True))
        self.assertEqual(instance.data, {"key": "value"})

        with self.assertRaises(AssertionError):
            instance.save()

    def test_save_returns_updated_instance(self):
        class Instance(object):
            data = {}

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def update(self, instance, validated_data):
                instance.data = validated_data
                return instance

        old_value = {"test": "value"}
        obj = Instance()
        obj.data = old_value
        instance = FakeSerializer(instance=obj, data={"key": "data"})
        self.assertTrue(instance.is_valid(raise_exception=True))
        updated_obj = instance.save()
        self.assertNotEqual(updated_obj.data, old_value)

    def test_save_returns_assertion_arror_for_not_updated_instance(self):
        class Instance(object):
            data = {}

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def update(self, instance, validated_data):
                return None

        obj = Instance()
        obj.data = {"key": "data"}
        instance = FakeSerializer(instance=obj, data={"key": "data"})
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save()

    def test_save_returns_created_instance(self):

        class Instance(object):
            data = {}

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def create(self, validated_data):
                obj = Instance()
                obj.data = validated_data
                return obj

        instance = FakeSerializer(data={"key": "value"})
        self.assertTrue(instance.is_valid(raise_exception=True))
        obj = instance.save()
        self.assertIsInstance(obj, Instance)
        self.assertEqual(obj.data, {"key": "value"})

    def test_save_returns_assertion_arror_for_not_created_instance(self):
        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

            def create(self, validated_data):
                return None

        instance = FakeSerializer(data={"key": "value"})
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save()

    def test_is_valid_raises_assertion_error(self):
        instance = BaseSerializer()

        with self.assertRaises(AssertionError):
            instance.is_valid(raise_exception=True)

    def test_is_valid_raises_validation_error(self):

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=5, validators=[MinValueValidator(10), ])

        with self.assertRaises(ValidationError):
            instance.is_valid(raise_exception=True)

    def test_is_valid_returns_valid_data(self):

        class FakeSerializer(BaseSerializer):
            def to_internal_value(self, data):
                return data

        instance = FakeSerializer(data=[1, 2, 3])
        self.assertTrue(instance.is_valid(raise_exception=True))


class TestSerializer(unittest.TestCase):

    def test_fields_property(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        serialzier_fields = instance.fields
        self.assertIn('pk', serialzier_fields.keys())
        self.assertIsInstance(serialzier_fields['pk'], fields.IntegerField)

    def test_writable_fields_property(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField()

        instance = FakeSerializer()
        serialzier_fields = instance._writable_fields
        self.assertEqual(len(serialzier_fields), 1)
        self.assertEqual(serialzier_fields[0].source, 'value')
        self.assertIsInstance(
            serialzier_fields[0],
            fields.SmallIntegerField
        )

    def test_readable_fields_property(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField(write_only=True)

        instance = FakeSerializer()
        serialzier_fields = instance._readable_fields
        self.assertEqual(len(serialzier_fields), 1)
        self.assertEqual(serialzier_fields[0].source, 'pk')
        self.assertIsInstance(serialzier_fields[0], fields.IntegerField)

    def test_get_fields(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        serialzier_fields = instance.get_fields()
        self.assertIn('pk', serialzier_fields.keys())
        self.assertIsInstance(serialzier_fields['pk'], fields.IntegerField)

    def test_get_validators(self):

        class UniqueTogetherValidator(BaseUniqueFieldValidator):

            def __init__(self, queryset, fields, message=None):
                super(UniqueTogetherValidator, self).__init__(
                    queryset=queryset,
                    message=message
                )
                self.queryset = queryset
                self.fields = fields
                self.serializer_field = None
                self.message = message or self.message

        class FakeSerializer(Serializer):

            class Meta:
                validators = [
                    UniqueTogetherValidator(
                        queryset=None, fields=('list', 'position')
                    )
                ]

        instance = FakeSerializer()
        validators = instance.get_validators()
        self.assertEqual(len(validators), 1)
        self.assertIsInstance(validators[0], UniqueTogetherValidator)

    def test_get_initial_data_without_defined_data_arg(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        result = instance.get_initial()
        self.assertIsInstance(result, OrderedDict)
        self.assertEqual(result, {'pk': None})

    def test_get_initial_data_with_defined_data_arg(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        initial_data = {"pk": 1}
        instance = FakeSerializer(data=initial_data)
        result = instance.get_initial()
        self.assertIsInstance(result, OrderedDict)
        self.assertEqual(result, initial_data)

    def test_get_value(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        data = {'model': {"pk": 1}}
        instance = FakeSerializer()
        instance.bind('model', None)
        self.assertEqual(instance.get_value(data), {"pk": 1})

    def test_get_values_return_empty(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        data = {'another_model': {"pk": 1}}
        instance = FakeSerializer()
        instance.bind('model', None)
        self.assertEqual(instance.get_value(data), empty)

    def test_run_validation_raises_not_implemented_error(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()

        with self.assertRaises(NotImplementedError):
            instance.run_validation({"pk": 1})

    def test_to_internal_value_raises_validation_error_for_invalid_data(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()

        with self.assertRaises(ValidationError):
            instance.to_internal_value([{'pk': 1}, ])

    def test_to_internal_value_with_custom_validate_returns_dict(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField()

            def validate_value(self, value):
                return value

        instance = FakeSerializer()
        self.assertEqual(
            instance.to_internal_value({'pk': 1, 'value': 5}),
            {'value': 5}
        )

    def test_to_internal_value_with_validate_raises_validation_error(self):
        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField()

            def validate_value(self, value):
                if value is None:
                    raise ValidationError("Value can't be None")
                return value

        instance = FakeSerializer()

        with self.assertRaises(ValidationError):
            instance.to_internal_value({'pk': 1, 'value': None})

    def test_to_internal_value_returns_empty_dict(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField(required=False)

            def validate_value(self, value):
                if value is None:
                    raise ValidationError("Value can't be None")
                return value

        instance = FakeSerializer()
        self.assertEqual(instance.to_internal_value({'pk': 1}), {})

    def test_to_internal_value_returns_dict(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

        instance = FakeSerializer()
        self.assertEqual(
            instance.to_internal_value({'pk': 1, 'string': 'test'}),
            {'string': 'test'}
        )

    def test_to_representation(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

        class FakeModel(object):

            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        instance = FakeSerializer()
        fake_model_instance = FakeModel(1, 'test')
        self.assertEqual(
            instance.to_representation(fake_model_instance),
            {'pk': 1, 'string': 'test'}
        )

    def test_to_representation_with_none_value(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.IntegerField(allow_null=True)
            string = fields.CharField()

        class FakeModel(object):
            def __init__(self, pk, value, string):
                self.pk = pk
                self.value = value
                self.string = string

        instance = FakeSerializer()
        fake_model_instance = FakeModel(1, None, 'test')
        self.assertEqual(
            instance.to_representation(fake_model_instance),
            {'pk': 1, 'value': None, 'string': 'test'}
        )

    def test_to_representation_returns_dict_with_empty_value(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.IntegerField(required=False)
            string = fields.CharField()

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        instance = FakeSerializer()
        fake_model_instance = FakeModel(1, 'test')
        self.assertEqual(
            instance.to_representation(fake_model_instance),
            {'pk': 1, 'string': 'test'}
        )

    def test_validate(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        self.assertEqual(instance.validate({'pk': 1}), {'pk': 1})

    def test_repr(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        self.assertEqual(
            instance.__repr__(),
            'FakeSerializer():\n    pk = IntegerField()'
        )

    def test_iter(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer()
        self.assertEqual(
            [field.source for field in instance],
            ['pk', ]
        )

    def test_getitem(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer(data={'pk': 1})
        instance._validated_data = instance.initial_data
        field = instance['pk']
        self.assertIsInstance(field, BoundField)
        self.assertEqual(field.name, 'pk')
        self.assertEqual(field.value, 1)
        self.assertEqual(field.errors, None)

    def test_getitem_for_nested_serializers(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        class NestedSerializer(Serializer):
            value = FakeSerializer(data={'pk': 1})

        instance = NestedSerializer(data={'value': {'pk': 1}})
        instance._validated_data = instance._data = instance.initial_data
        field = instance['value']
        self.assertIsInstance(field, NestedBoundField)
        self.assertEqual(field.name, 'value')
        self.assertEqual(field.value, {'pk': 1})
        self.assertEqual(field.errors, None)

    def test_data_property(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        instance = FakeSerializer(data={'pk': 1})
        instance._validated_data = instance.initial_data
        self.assertIsInstance(instance.data, ReturnDict)
        self.assertEqual(instance.data, {'pk': 1})

    def test_error_property(self):

        class FakeSerializer(Serializer):
            pk = fields.IntegerField()

        errors = {'pk': ["Field doesn't accept NoneType", ]}
        instance = FakeSerializer()
        instance._errors = errors
        self.assertIsInstance(instance.errors, ReturnDict)
        self.assertEqual(instance.errors, errors)


class TestRaiseErrorsOnNestedWritesFunction(unittest.TestCase):

    def test_raise_writes_raises_error_for_writable_nested_field(self):

        class UserModelSerializer(Serializer):
            pk = fields.IntegerField()

        class AddressSerializer(Serializer):
            user = UserModelSerializer()

        instance = AddressSerializer()

        with self.assertRaises(AssertionError):
            raise_errors_on_nested_writes(
                method_name='some_func',
                serializer=instance,
                validated_data={'user': {'pk': 1}}
            )

    def test_raise_writes_raises_error_for_writable_dotted_source_field(self):

        class AddressSerializer(Serializer):
            user = fields.IntegerField(source='user.pk')

        instance = AddressSerializer()

        with self.assertRaises(AssertionError):
            raise_errors_on_nested_writes(
                method_name='some_func',
                serializer=instance,
                validated_data={'user': {'pk': 1}}
            )


class TestListSerializer(unittest.TestCase):

    def test_init_raises_assertion_error_for_missed_child_argument(self):

        with self.assertRaises(AssertionError):
            ListSerializer()

    def test_init_raises_assertion_error_for_not_instantiated_child(self):

        with self.assertRaises(AssertionError):
            ListSerializer(child=object)

    def test_get_initial(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True)
        self.assertEqual(instance.get_initial(), [])

    def test_get_initial_returns_empty_list(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True, data=[{'pk': 1}, {'pk': 2}])
        self.assertEqual(instance.get_initial(), [{'pk': 1}, {'pk': 2}])

    def test_get_value(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'model': {"pk": 1}}
        instance = FakeSerializer(many=True)
        instance.bind('model', None)
        self.assertEqual(instance.get_value(data), {"pk": 1})

    def test_get_values_return_empty(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'another_model': {"pk": 1}}
        instance = FakeSerializer(many=True)
        instance.bind('model', None)
        self.assertEqual(instance.get_value(data), empty)

    def test_get_attribute(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'model': {"pk": 1}}
        instance = FakeSerializer(many=True)
        instance.bind('model', None)
        self.assertEqual(instance.get_attribute(data), {"pk": 1})

    def test_get_attribute_raises_skip_field(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'another_model': {"pk": 1}}
        instance = FakeSerializer(many=True, required=False)
        instance.bind('model', None)

        with self.assertRaises(SkipField):
            instance.get_attribute(data)

    def test_get_attribute_raises_key_error(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'another_model': {"pk": 1}}
        instance = FakeSerializer(many=True)
        instance.bind('model', None)

        with self.assertRaises(KeyError):
            instance.get_attribute(data)

    def test_run_validation_raises_not_implemented_error(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        data = {'another_model': {"pk": 1}}
        instance = FakeSerializer(many=True)

        with self.assertRaises(NotImplementedError):
            instance.run_validation(data)

    def test_to_internal_value_raises_validation_error_for_invalid_data(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True)

        with self.assertRaises(ValidationError):
            instance.to_internal_value({'model': {'pk': 1}, })

    def test_to_internal_value_raises_validation_error_for_empty_data(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True, allow_empty=False)

        with self.assertRaises(ValidationError):
            instance.to_internal_value([])

    def test_to_internal_value_with_custom_validate_returns_dict(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField()

            def validate_value(self, value):
                return value

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        instance = FakeSerializer(many=True)
        self.assertEqual(
            instance.to_internal_value([{'pk': 1, 'value': 5}]),
            [{'value': 5}]
        )

    def test_to_internal_value_with_validate_raises_validation_error(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField()

            def validate_value(self, value):
                if value is None:
                    raise ValidationError("Value can't be None")
                return value

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        instance = FakeSerializer(many=True)

        with self.assertRaises(ValidationError):
            instance.to_internal_value([{'pk': 1, 'value': None}])

    def test_to_internal_value_returns_empty_dict(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            value = fields.SmallIntegerField(required=False)

            def validate_value(self, value):
                if value is None:
                    raise ValidationError("Value can't be None")
                return value

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        instance = FakeSerializer(many=True)
        self.assertEqual(
            instance.to_internal_value([{'pk': 1}]),
            [OrderedDict(), ]
        )

    def test_to_internal_value_returns_list(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        instance = FakeSerializer(many=True)
        self.assertEqual(
            instance.to_internal_value([{'pk': 1, 'string': 'test'}]),
            [{'string': 'test'}, ]
        )

    def test_to_representation_return_list_of_objects(self):

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

        instance = FakeSerializer(many=True)
        fake_model_instance = FakeModel(1, 'test')
        self.assertEqual(
            instance.to_representation([fake_model_instance, ]),
            [{'pk': 1, 'string': 'test'}, ]
        )

    def test_validate(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True)
        self.assertEqual(instance.validate([{'pk': 1}, ]), [{'pk': 1}, ])

    def test_update_raises_not_implemented_error(self):

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

        instance = FakeSerializer(many=True)
        fake_model_instance = FakeModel(1, 'test')

        with self.assertRaises(NotImplementedError):
            instance.update(fake_model_instance, {'pk': 1, 'string': 'value'})

    def test_create(self):

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()
            string = fields.CharField()

            def create(self, validated_data):
                return FakeModel(
                    validated_data['pk'], validated_data['string']
                )

        serializer = FakeSerializer(many=True)
        model_instances = serializer.create([{'pk': 1, 'string': 'value'}, ])
        self.assertIsInstance(model_instances, list)
        self.assertEqual(len(model_instances), 1)
        self.assertIsInstance(model_instances[0], FakeModel)
        self.assertEqual(model_instances[0].pk, 1)
        self.assertEqual(model_instances[0].string, 'value')

    def test_save_raises_assertion_error_for_commit_in_kwargs(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        class FakeSerializer(Serializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField()

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        instance = FakeSerializer(many=True, data=[{"pk": 1}, ])
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save(commit=True)

    def test_save_returns_created_instance(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField()
            string = fields.CharField()

            def create(self, validated_data):
                return FakeModel(
                    validated_data['pk'], validated_data['string']
                )

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        initial_data = [{'pk': 1, 'string': 'value'}, ]
        instance = FakeSerializer(many=True, data=initial_data)
        self.assertTrue(instance.is_valid(raise_exception=True))
        model_instances = instance.save()
        self.assertIsInstance(model_instances, list)
        self.assertEqual(len(model_instances), 1)
        self.assertIsInstance(model_instances[0], FakeModel)
        self.assertEqual(model_instances[0].pk, 1)
        self.assertEqual(model_instances[0].string, 'value')

    def test_save_raises_assertion_error_for_none_type_in_create(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

            def create(self, validated_data):
                return None

        class FakeSerializer(Serializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField()
            string = fields.CharField()

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        initial_data = [{'pk': 1, 'string': 'value'}, ]
        instance = FakeSerializer(many=True, data=initial_data)
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save()

    def test_save_returns_updated_objects(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

            def update(self, instances, validated_data):
                for instance, new_data in zip(instances, validated_data):
                    instance.string = new_data['string']
                return instances

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        initial_data = [{'pk': 1, 'string': 'new_value'}, ]
        instance = FakeSerializer(
            many=True, instance=[FakeModel(1, 'old_value')], data=initial_data
        )
        self.assertTrue(instance.is_valid(raise_exception=True))
        model_instances = instance.save()
        self.assertIsInstance(model_instances, list)
        self.assertEqual(len(model_instances), 1)
        self.assertIsInstance(model_instances[0], FakeModel)
        self.assertEqual(model_instances[0].pk, 1)
        self.assertEqual(model_instances[0].string, 'new_value')

    def test_save_raises_assertion_error_for_none_type_in_update(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

            def update(self, instances, validated_data):
                return None

        class FakeModel(object):
            def __init__(self, pk, string):
                self.pk = pk
                self.string = string

        class FakeSerializer(Serializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField(read_only=True)
            string = fields.CharField()

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        initial_data = [{'pk': 1, 'string': 'new_value'}, ]
        instance = FakeSerializer(
            many=True, instance=[FakeModel(1, 'old_value')], data=initial_data
        )
        self.assertTrue(instance.is_valid(raise_exception=True))

        with self.assertRaises(AssertionError):
            instance.save()

    def test_repr(self):

        class FakeSerializer(Serializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        instance = FakeSerializer(many=True)
        self.assertEqual(
            instance.__repr__(),
            'FakeSerializer(many=True):\n    pk = IntegerField()'
        )

    def test_data_property(self):

        class FakeListSerializer(ListSerializer):

            def run_validation(self, data=empty):
                value = self.to_internal_value(data)
                try:
                    self.run_validators(value)
                    value = self.validate(value)
                    assert value is not None
                except (ValidationError, AssertionError) as exc:
                    raise ValidationError(detail=exc.detail)
                return value

        class FakeSerializer(BaseSerializer):
            default_list_serializer = FakeListSerializer
            pk = fields.IntegerField()

            def to_internal_value(self, data):
                return data

            def to_representation(self, instance):
                return instance

        instance = FakeSerializer(many=True, data=[{'pk': 1}, ])
        self.assertTrue(instance.is_valid(raise_exception=True))
        self.assertIsInstance(instance.data, ReturnList)
        self.assertEqual(len(instance.data), 1)
        self.assertEqual(instance.data[0], {'pk': 1})

    def test_error_property_returns_dict(self):

        class FakeSerializer(BaseSerializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        errors = {'pk': ["Field doesn't accept NoneType", ]}
        instance = FakeSerializer(many=True)
        instance._errors = errors
        self.assertIsInstance(instance.errors, ReturnDict)
        self.assertEqual(instance.errors, errors)

    def test_error_property_returns_list(self):

        class FakeSerializer(BaseSerializer):
            default_list_serializer = ListSerializer
            pk = fields.IntegerField()

        errors = [{'pk': ["Field doesn't accept NoneType", ]}, ]
        instance = FakeSerializer(many=True)
        instance._errors = errors
        self.assertIsInstance(instance.errors, ReturnList)
        self.assertEqual(instance.errors, errors)


class TestModelSerialiazer(unittest.TestCase):

    def test_is_abstract_model_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.is_abstract_model(object)

    def test_get_field_info_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.get_field_info(object)

    def test_create_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.create({'pk': 1})

    def test_update_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

        instance = ModelSerializer()
        fake_model_instance = FakeModel()

        with self.assertRaises(NotImplementedError):
            instance.update(fake_model_instance, {'pk': 1, 'value': 'test'})

    def test_get_fields_raises_assertion_error_for_missing_meta_attr(self):

        class FakeSerializer(ModelSerializer):
            pass

        instance = FakeSerializer()

        with self.assertRaises(AssertionError):
            instance.get_fields()

    def test_get_fields_raises_assertion_error_for_missing_model_attr(self):

        class FakeSerializer(ModelSerializer):

            class Meta:
                pass

        instance = FakeSerializer()

        with self.assertRaises(AssertionError):
            instance.get_fields()

    def test_get_fields_raises_value_error_for_abstract_model(self):

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object

            def is_abstract_model(self, model):
                return True

        instance = FakeSerializer()

        with self.assertRaises(ValueError):
            instance.get_fields()

    def test_get_fields_raises_assertion_error_for_negative_depth_value(self):

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                depth = -1

            def is_abstract_model(self, model):
                return False

        instance = FakeSerializer()

        with self.assertRaises(AssertionError):
            instance.get_fields()

    def test_get_fields_raises_assertion_error_for_too_big_depth_value(self):

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                depth = 100

            def is_abstract_model(self, model):
                return False

        instance = FakeSerializer()

        with self.assertRaises(AssertionError):
            instance.get_fields()

    def test_get_fields_returns_all_declared_fields(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object

            def is_abstract_model(self, model):
                return False

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value']

            def get_uniqueness_extra_kwargs(self, field_names, declared_fields,
                                            extra_kwargs):
                return extra_kwargs, {}

        instance = FakeSerializer()
        self.assertEqual(list(instance.get_fields().keys()), ['pk', 'value'])

    def test_get_fields_returns_fields_with_instantiated_property_field(self):

        class FakeModel(object):
            pk = int
            value = str

            @property
            def property_field(self):
                return None

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                extra_kwargs = {'property_field': {'required': False}}

            def is_abstract_model(self, model):
                return False

            def get_field_info(self, model):
                fields = OrderedDict([
                    ('value', FakeModel.value),
                    ('property_field', FakeModel.property_field)
                ])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value),
                     ('property_field', FakeModel.property_field)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value', 'property_field']

            def build_field(self, field_name, info, model_class, nested_depth):
                return fields.ReadOnlyField, {}

            def get_uniqueness_extra_kwargs(self, field_names, declared_fields,
                                            extra_kwargs):
                return extra_kwargs, {}

        instance = FakeSerializer()
        self.assertEqual(
            list(instance.get_fields().keys()),
            ['pk', 'value', 'property_field']
        )

    def test_get_extra_kwargs(self):

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                extra_kwargs = {'value': {'required': False}}

        instance = FakeSerializer()
        self.assertEqual(
            instance.get_extra_kwargs(),
            {'value': {'required': False}}
        )

    def test_get_field_names_raises_error_for_invalid_fields_attr(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                fields = {'pk', }

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        with self.assertRaises(TypeError):
            instance.get_field_names(declared_fields, info)

    def test_get_field_names_raises_error_for_invalid_exclude_attr(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                exclude = {'value', }

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        with self.assertRaises(TypeError):
            instance.get_field_names(declared_fields, info)

    def test_get_field_names_raises_error_for_defined_fields_and_exclude(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                fields = ['pk', ]
                exclude = ['value', ]

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        with self.assertRaises(AssertionError):
            instance.get_field_names(declared_fields, info)

    def test_get_field_names_returns_all_fields(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                fields = '__all__'

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value']

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        self.assertEqual(
            instance.get_field_names(declared_fields, info),
            ['pk', 'value']
        )

    def test_get_field_names_raises_assertion_error_for_a_missing_field(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                fields = ['pk', ]

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value']

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        with self.assertRaises(AssertionError):
            instance.get_field_names(declared_fields, info)

    def test_get_field_names_returns_pk(self):

        class FakeModel(object):
            pk = int

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)

            class Meta:
                model = object
                fields = ['pk', ]

            def get_field_info(self, model):
                fields = OrderedDict()
                all_fields = OrderedDict([('pk', FakeModel.pk), ])
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', ]

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        self.assertEqual(
            instance.get_field_names(declared_fields, info),
            ['pk', ]
        )

    def test_get_field_names_raises_assetion_error_for_invalid_exclude(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                exclude = ['wrong_field', ]

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value']

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        with self.assertRaises(AssertionError):
            instance.get_field_names(declared_fields, info)

    def test_get_field_names_returns_pk_with_exclude_value_field(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object
                exclude = ['value', ]

            def get_field_info(self, model):
                fields = OrderedDict([('value', FakeModel.value)])
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'value']

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        self.assertEqual(
            instance.get_field_names(declared_fields, info),
            ['pk', ]
        )

    def test_get_default_field_names_raises_not_implemented_error(self):
        instance = ModelSerializer()
        declared_fields = {'pk': int}
        model_info = FieldInfo(
            'pk', {}, OrderedDict(), OrderedDict(), {'pk': int}, {}
        )

        with self.assertRaises(NotImplementedError):
            instance.get_default_field_names(declared_fields, model_info)

    def test_build_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_field(
                'pk',
                FieldInfo('pk', {}, OrderedDict(), OrderedDict(), {}, {}),
                fields.IntegerField, 1
            )

    def test_build_standard_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_standard_field('pk', fields.IntegerField)

    def test_build_relational_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_relational_field('addresses', {})

    def test_build_nested_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_nested_field('addresses', {}, 1)

    def test_build_property_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_property_field(
                'property_field', fields.ReadOnlyField
            )

    def test_build_url_field_raises_not_implemented_error(self):
        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance.build_url_field('url', fields.CharField)

    def test_build_unknown_field_raises_improperty_configured_exception(self):
        instance = ModelSerializer()

        with self.assertRaises(ImproperlyConfigured):
            instance.build_unknown_field('pk', object)

    def test_include_extra_kwargs_for_read_only_field(self):
        instance = ModelSerializer()
        field_kwargs = {'source': 'pk'}
        extra_kwargs = {'read_only': True}
        self.assertEqual(
            instance.include_extra_kwargs(field_kwargs, extra_kwargs),
            {'source': 'pk', 'read_only': True}
        )

    def test_include_extra_kwargs_for_required_field(self):
        instance = ModelSerializer()
        field_kwargs = {'source': 'pk'}
        extra_kwargs = {'required': True}
        self.assertEqual(
            instance.include_extra_kwargs(field_kwargs, extra_kwargs),
            {'source': 'pk', 'required': True}
        )

    def test_include_extra_kwargs_for_a_field_with_default_value(self):
        instance = ModelSerializer()
        field_kwargs = {'source': 'pk', 'required': False}
        extra_kwargs = {'default': -1}
        self.assertEqual(
            instance.include_extra_kwargs(field_kwargs, extra_kwargs),
            {'source': 'pk', 'default': -1}
        )

    def test_get_extra_kwargs_with_specified_read_only_fields(self):

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField()
            value = fields.CharField()

            class Meta:
                model = object
                extra_kwargs = {'value': {'default': None}}
                read_only_fields = ['pk', ]

        instance = FakeSerializer()
        self.assertEqual(
            instance.get_extra_kwargs(),
            {'pk': {'read_only': True}, 'value': {'default': None}}
        )

    def test_get_uniqueness_extra_kwargs_for_primary_key_field(self):

        class FakeModel(object):
            pk = int

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)

            class Meta:
                model = FakeModel

            def get_field_info(self, model):
                fields = OrderedDict()
                all_fields = OrderedDict([('pk', FakeModel.pk), ])
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'key', 'value']

            def _get_unique_field(self, model, unique_field_name):
                return getattr(model, unique_field_name)

            def _get_unique_constraint_names(self, model, model_fields):
                return {'pk', }

            def _get_unique_together_constraints(self, model):
                return set()

            def _get_default_field_value(self, unique_constraint_field):
                return 0

            def _bind_field(self, model, source, model_fields):
                model_fields[source] = getattr(model, source, None)

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)

        extra_kwargs, hidden_fields = instance.get_uniqueness_extra_kwargs(
            ['pk', ], declared_fields, {}
        )

        self.assertEqual(extra_kwargs, {'pk': {'default': 0}})
        self.assertEqual(hidden_fields, {})

    def test_get_uniqueness_extra_kwargs_for_a_composite_field(self):

        class FakeModel(object):
            pk = int
            key = dict
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            key = fields.CharField()
            value = fields.CharField()

            class Meta:
                model = FakeModel

            def get_field_info(self, model):
                fields = OrderedDict([
                    ('key', FakeModel.key), ('value', FakeModel.value),
                ])
                all_fields = OrderedDict([
                    ('pk', FakeModel.pk), ('key', FakeModel.key),
                    ('value', FakeModel.value),
                ])
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'key', 'value']

            def _get_unique_field(self, model, unique_field_name):
                return getattr(model, unique_field_name)

            def _get_unique_constraint_names(self, model, model_fields):
                return {'pk', }

            def _get_unique_together_constraints(self, model):
                return {'key', 'value'}

            def _get_default_field_value(self, unique_constraint_field):
                if unique_constraint_field is str:
                    return 'default'
                elif unique_constraint_field is int:
                    return 0
                else:
                    return empty

            def _bind_field(self, model, source, model_fields):
                model_fields[source] = getattr(model, source, None)

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)

        extra_kwargs, hidden_fields = instance.get_uniqueness_extra_kwargs(
            ['pk', 'key', 'value'], declared_fields, {'key': {'requred': True}}
        )

        self.assertEqual(
            extra_kwargs,
            {'key': {'required': True, 'requred': True}, 'pk': {'default': 0},
             'value': {'default': 'default'}}
        )
        self.assertEqual(hidden_fields, {})

    def test_get_uniqueness_extra_kwargs_for_a_nested_field(self):

        class FakeModel(object):
            pk = int
            user = object

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            user = fields.CharField()

            class Meta:
                model = FakeModel

            def get_field_info(self, model):
                fields = OrderedDict([('user', FakeModel.user), ])
                all_fields = OrderedDict([
                    ('pk', FakeModel.pk), ('user', FakeModel.user)
                ])
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

            def get_default_field_names(self, declared_fields, model_info):
                return ['pk', 'user']

            def _get_unique_field(self, model, unique_field_name):
                return getattr(model, unique_field_name)

            def _get_unique_constraint_names(self, model, model_fields):
                return {'pk', 'user'}

            def _get_unique_together_constraints(self, model):
                return set()

            def _get_default_field_value(self, unique_constraint_field):
                if unique_constraint_field is int:
                    return 0
                else:
                    return None

            def _bind_field(self, model, source, model_fields):
                model_fields[source] = getattr(model, source, None)

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)

        extra_kwargs, hidden_fields = instance.get_uniqueness_extra_kwargs(
            ['pk', ], declared_fields, {}
        )

        self.assertEqual(
            extra_kwargs, {'pk': {'default': 0}}
        )
        self.assertIn('user', hidden_fields.keys())
        self.assertIsInstance(hidden_fields['user'], fields.HiddenField)

    def test_get_model_fields(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()
            property = fields.SerializerMethodField()

            class Meta:
                model = FakeModel

            def _bind_field(self, model, source, model_fields):
                model_fields[source] = getattr(model, source, None)

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)

        self.assertEqual(
            instance._get_model_fields(
                ['pk', 'value', 'property'], declared_fields, {}
            ),
            {'pk': int, 'value': str}
        )

    def test_get_model_fields_for_model_with_non_field(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()
            property = fields.SerializerMethodField()

            def non_field(self, obj):
                return None

            class Meta:
                model = FakeModel

            def _bind_field(self, model, source, model_fields):
                model_fields[source] = getattr(model, source, None)

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)

        self.assertEqual(
            instance._get_model_fields(
                ['pk', 'value', 'property', 'non_field'], declared_fields, {}
            ),
            {'non_field': None, 'pk': int, 'value': str}
        )

    def test_get_unique_constraint_names_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = int

        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance._get_unique_constraint_names(
                FakeModel, {'pk': fields.IntegerField()}
            )

    def test_get_unique_together_constraint_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = int

        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance._get_unique_together_constraints(FakeModel)

    def test_get_unique_field_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = int

        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance._get_unique_field(FakeModel, 'pk')

    def test_get_default_field_value_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = int

        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance._get_default_field_value(int)

    def test_bind_field_raises_not_implemented_error(self):

        class FakeModel(object):
            pk = int

        instance = ModelSerializer()

        with self.assertRaises(NotImplementedError):
            instance._bind_field(FakeModel, 'pk', int)

    def test_get_validators(self):

        class FakeModel(object):
            pk = int

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)

            class Meta:
                model = FakeModel
                validators = [BaseUniqueFieldValidator(None), ]

        instance = FakeSerializer()
        validators = instance.get_validators()
        self.assertEqual(len(validators), 1)
        self.assertIsInstance(validators[0], BaseUniqueFieldValidator)

    def test_get_validators_return_empty_list(self):

        class FakeModel(object):
            pk = int

        class FakeSerializer(ModelSerializer):
            pk = fields.IntegerField(read_only=True)

            class Meta:
                model = FakeModel

        instance = FakeSerializer()
        self.assertEqual(instance.get_validators(), [])


class TestHyperlinkedModelSerializerMixin(unittest.TestCase):

    def test_default_field_names_returns(self):

        class FakeModel(object):
            pk = int
            value = str

        class FakeSerializer(HyperlinkedModelSerializerMixin, ModelSerializer):
            url_field_name = 'url'
            pk = fields.IntegerField(read_only=True)
            value = fields.CharField()

            class Meta:
                model = object

            def get_field_info(self, model):
                fields = OrderedDict()
                all_fields = OrderedDict(
                    [('pk', FakeModel.pk), ('value', FakeModel.value)]
                )
                return FieldInfo(
                    FakeModel.pk, fields, OrderedDict(), OrderedDict(),
                    all_fields, {}
                )

        instance = FakeSerializer()
        declared_fields = copy.deepcopy(instance._declared_fields)
        info = instance.get_field_info(FakeSerializer.Meta.model)

        self.assertEqual(
            set(instance.get_default_field_names(declared_fields, info)),
            set(['url', 'pk', 'value'])
        )

    def test_build_nested_field_raises_not_implemented_error(self):

        class UserModel(object):
            pk = int
            address_id = int

        class AddressModel(object):
            pk = int

        class FakeUserSerializer(HyperlinkedModelSerializerMixin,
                                 ModelSerializer):
            pk = fields.IntegerField(read_only=True)
            address_id = fields.IntegerField()

        instance = FakeUserSerializer()
        relation_info = RelationInfo(
            model_field=UserModel.address_id,
            related_model=AddressModel,
            to_many=False,
            to_field=AddressModel.pk,
            has_through_model=False
        )

        with self.assertRaises(NotImplementedError):
            instance.build_nested_field('user_id', relation_info, 1)
