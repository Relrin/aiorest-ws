# -*- coding: utf-8 -*-
import copy
import unittest

from aiorest_ws.db.orm.abstract import AbstractSerializer, AbstractField, empty


class FakeValidator(object):
    pass


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
        instance = AbstractSerializer(validators=[FakeValidator, ])
        self.assertEqual(instance._validators, [FakeValidator, ])

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
        default_validators = [FakeValidator, ]
        instance.default_validators = default_validators
        self.assertEqual(instance.get_validators(), default_validators)

    def test_get_initial_method(self):
        instance = AbstractSerializer(initial='value')
        self.assertEqual(instance.get_initial(), 'value')

# class TestAbstractField(unittest.TestCase):
#     pass

