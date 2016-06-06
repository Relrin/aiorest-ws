# -*- coding: utf-8 -*-
import copy
import unittest

from aiorest_ws.db.orm.abstract import AbstractSerializer, AbstractField, \
    empty, SkipField
from aiorest_ws.db.orm.exceptions import ValidationError


class FakeValidator(object):

    def __call__(self, value):
        pass


class FakeValidatorWithValidationError(object):

    def __call__(self, value):
        raise ValidationError("error")


class FakeField(object):
    attr = 'value'


class TestAbstractSerializer(unittest.TestCase):

    def test_init_save_args_and_kwargs(self):
        instance = AbstractSerializer(read_only=True)
        self.assertEqual(instance._args, ())
        self.assertIn('read_only', instance._kwargs)
        self.assertEqual(instance._kwargs['read_only'], True)

    def test_init_required_as_false_value(self):
        instance = AbstractSerializer(required=False)
        self.assertFalse(instance.required)

    def test_init_required_as_true_value(self):
        instance = AbstractSerializer(required=True)
        self.assertTrue(instance.required)

    def test_init_required_with_false_read_only_flag(self):
        instance = AbstractSerializer(read_only=False)
        self.assertTrue(instance.required)

    def test_init_required_with_true_read_only_flag(self):
        instance = AbstractSerializer(read_only=True)
        self.assertFalse(instance.required)

    def test_init_required_with_empty_default_value_and_false_read_only(self):
        instance = AbstractSerializer(default=empty, read_only=False)
        self.assertTrue(instance.required)

    def test_init_required_with_empty_default_value_and_true_read_only(self):
        instance = AbstractSerializer(default=empty, read_only=True)
        self.assertFalse(instance.required)

    def test_init_required_with_default_value(self):
        instance = AbstractSerializer(default='value')
        self.assertFalse(instance.required)

    def test_init_without_validators(self):
        instance = AbstractSerializer()
        self.assertEqual(instance.validators, [])

    def test_init_with_validators(self):
        validators = [FakeValidator(), ]
        instance = AbstractSerializer(validators=validators)
        self.assertEqual(instance._validators, validators)

    def test_deepcopy(self):
        instance = AbstractSerializer(validators=[FakeValidator, ])
        instance_copy = copy.deepcopy(instance)
        self.assertIsInstance(instance_copy, AbstractSerializer)
        self.assertNotEqual(instance, instance_copy)
        self.assertEqual(instance.validators, instance_copy.validators)

    def test_bind(self):
        instance = AbstractSerializer(label='test_value')
        instance.bind('field', None)
        self.assertEqual(instance.field_name, 'field')
        self.assertEqual(instance.label, 'test_value')
        self.assertIsNone(instance.parent)
        self.assertEqual(instance.source_attrs, ['field', ])

    def test_bind_with_defined_label(self):
        instance = AbstractSerializer()
        instance.bind('test_field', None)
        self.assertEqual(instance.field_name, 'test_field')
        self.assertEqual(instance.label, 'Test field')
        self.assertIsNone(instance.parent)
        self.assertEqual(instance.source_attrs, ['test_field', ])

    def test_bind_with_defined_source(self):
        instance = AbstractSerializer(source='FakeModel.pk')
        instance.bind('test_field', None)
        self.assertEqual(instance.field_name, 'test_field')
        self.assertEqual(instance.label, 'Test field')
        self.assertIsNone(instance.parent)
        self.assertEqual(instance.source_attrs, ['FakeModel', 'pk'])

    def test_bind_with_defined_source_as_a_star_value(self):
        instance = AbstractSerializer(source='*')
        instance.bind('test_field', None)
        self.assertEqual(instance.field_name, 'test_field')
        self.assertEqual(instance.label, 'Test field')
        self.assertIsNone(instance.parent)
        self.assertEqual(instance.source_attrs, [])

    def test_get_root_as_none(self):
        instance = AbstractSerializer(source='*')
        instance.bind('field', None)
        self.assertEqual(instance.root, instance)

    def test_get_root_nested(self):
        parent_serializer = AbstractSerializer()
        instance = AbstractSerializer(source='*')
        instance.bind('field', AbstractSerializer())
        parent_serializer.bind('field', None)
        self.assertNotEqual(instance.root, parent_serializer.root)

    def test_context_property_returns_object(self):
        instance = AbstractSerializer(source='*')
        instance._context = object()
        self.assertIsInstance(instance.context, object)

    def test_context_property_returns_empty_dict(self):
        instance = AbstractSerializer(source='*')
        self.assertEqual(instance.context, {})

    def test_validators_getter(self):
        instance = AbstractSerializer()
        self.assertEqual(instance.validators, [])

    def test_validators_setter(self):
        validators = [FakeValidator, ]
        instance = AbstractSerializer()
        instance.validators = validators
        self.assertEqual(instance.validators, validators)

    def test_not_implemented_get_default_method_returns_none(self):
        instance = AbstractSerializer()
        self.assertIsNone(instance.get_default())

    def test_not_implemented_get_value_method_returns_none(self):
        instance = AbstractSerializer()
        self.assertIsNone(instance.get_value({"key": "value"}))

    def test_not_implemented_get_attribute_method_returns_none(self):
        instance = AbstractSerializer()
        self.assertIsNone(instance.get_attribute(object()))

    def test_not_implemented_to_internal_value_method_returns_none(self):
        instance = AbstractSerializer()
        self.assertIsNone(instance.to_internal_value({"key": "value"}))

    def test_not_implemented_to_representation_method_returns_none(self):
        instance = AbstractSerializer()
        self.assertIsNone(instance.to_representation({"key": "value"}))

    def test_get_validators(self):
        instance = AbstractSerializer()
        self.assertEqual(instance.get_validators(), [])

    def test_get_initialized_validators(self):
        instance = AbstractSerializer()
        default_validators = [FakeValidator(), ]
        instance.default_validators = default_validators
        self.assertEqual(instance.get_validators(), default_validators)

    def test_get_initial_method(self):
        instance = AbstractSerializer(initial='value')
        self.assertEqual(instance.get_initial(), 'value')

    def test_validate_empty_values_returns_default(self):
        instance = AbstractSerializer(read_only=True)
        self.assertEqual(
            instance.validate_empty_values({"key": "value"}),
            (True, None)
        )

    def test_validate_empty_values_raises_skip_field_exception(self):
        instance = AbstractSerializer()

        with self.assertRaises(SkipField):
            instance.partial = True
            instance.validate_empty_values(empty)

    def test_validate_empty_values_raises_field_is_required(self):
        instance = AbstractSerializer(required=True)

        with self.assertRaises(ValidationError):
            instance.validate_empty_values(empty)

    def test_validate_empty_values_returns_default_value_for_empty(self):
        instance = AbstractSerializer(required=False)
        self.assertEqual(
            instance.validate_empty_values(empty),
            (True, None)
        )

    def test_validate_empty_values_raises_field_is_not_null(self):
        instance = AbstractSerializer(allow_null=False)

        with self.assertRaises(ValidationError):
            instance.validate_empty_values(None)

    def test_validate_empty_values_returns_none(self):
        instance = AbstractSerializer(allow_null=True)
        self.assertEqual(
            instance.validate_empty_values(None),
            (True, None)
        )

    def test_validate_empty_values_returns_value(self):
        instance = AbstractSerializer()
        self.assertEqual(
            instance.validate_empty_values({"key": "value"}),
            (False, {"key": "value"})
        )

    def test_run_validators_passed(self):
        validators = [FakeValidator(), ]
        instance = AbstractSerializer(validators=validators)
        self.assertIsNone(instance.run_validators({"key": "value"}))

    def test_run_validators_raises_validation_exception(self):
        validators = [FakeValidatorWithValidationError(), ]
        instance = AbstractSerializer(validators=validators)

        with self.assertRaises(ValidationError):
            instance.run_validators({"key": "value"})

    def test_run_validation_with_empty_value(self):

        def get_default():
            return empty

        instance = AbstractSerializer(required=False)
        instance.get_default = get_default
        self.assertEqual(instance.run_validation(empty), empty)

    def test_run_validation_with_dictionary(self):

        def to_internal_value(value):
            return value

        instance = AbstractSerializer(required=False)
        instance.to_internal_value = to_internal_value
        self.assertEqual(
            instance.run_validation({"key": "value"}), {"key": "value"}
        )

    def test_raise_error_returns_validator_error(self):
        instance = AbstractSerializer(required=False)

        with self.assertRaises(ValidationError):
            instance.raise_error('null')

    def test_raise_error_returns_message_not_found(self):
        instance = AbstractSerializer(required=False)

        with self.assertRaises(AssertionError):
            instance.raise_error('unknown')


class TestAbstractField(unittest.TestCase):

    def test_get_default(self):
        instance = AbstractField(default=None)
        self.assertIsNone(instance.get_default())

    def test_get_default_returns_SkipField_exception(self):
        instance = AbstractField()

        with self.assertRaises(SkipField):
            instance.get_default()

    def test_get_value(self):
        instance = AbstractField()
        instance.bind('pk', None)
        self.assertEqual(instance.get_value({'pk': 1}), 1)

    def test_get_value_returns_empty_value(self):
        instance = AbstractField()
        instance.bind('pk', None)
        self.assertEqual(instance.get_value({'not_pk': 1}), empty)

    def test_get_attribute(self):
        instance = AbstractField()
        fake_field = FakeField()
        instance.bind('attr', None)
        self.assertEqual(instance.get_attribute(fake_field), 'value')

    def test_get_attribute_raises_skip_field_exception(self):
        instance = AbstractField(required=False)
        fake_field = FakeField()
        instance.bind('unknown', None)
        with self.assertRaises(SkipField):
            instance.get_attribute(fake_field)

    def test_get_attribute_raises_key_error_exception(self):
        instance = AbstractField()
        fake_object = {}
        instance.bind('attribute', None)
        with self.assertRaises(KeyError):
            instance.get_attribute(fake_object)

    def test_get_attribute_raises_attribute_error_exception(self):
        instance = AbstractField()
        fake_object = object()
        instance.bind('attribute', None)
        with self.assertRaises(AttributeError):
            instance.get_attribute(fake_object)

    def test_to_internal_value_raises_not_implemented_error(self):
        instance = AbstractField()

        with self.assertRaises(NotImplementedError):
            instance.to_internal_value({"key": "value"})

    def test_to_representation_raises_not_implemented_error(self):
        instance = AbstractField()

        with self.assertRaises(NotImplementedError):
            instance.to_representation({"key": "value"})
