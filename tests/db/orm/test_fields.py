# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.db.orm import fields
from aiorest_ws.db.orm.exceptions import ValidationError


class TestIntegerField(unittest.TestCase):

    def test_init_without_borders(self):
        instance = fields.IntegerField()
        self.assertIsNone(instance.max_value)
        self.assertIsNone(instance.min_value)

    def test_init_with_min_value(self):
        instance = fields.IntegerField(min_value=10)
        self.assertEqual(instance.min_value, 10)
        self.assertIsNone(instance.max_value)

    def test_init_with_max_value(self):
        instance = fields.IntegerField(max_value=10)
        self.assertIsNone(instance.min_value)
        self.assertEqual(instance.max_value, 10)

    def test_init_with_min_and_max_values(self):
        instance = fields.IntegerField(min_value=1, max_value=10)
        self.assertEqual(instance.min_value, 1)
        self.assertEqual(instance.max_value, 10)

    def test_to_internal_value(self):
        instance = fields.IntegerField()
        self.assertEqual(instance.to_internal_value(1), 1)

    def test_to_internal_value_raises_max_string_length_exception(self):
        instance = fields.IntegerField()

        with self.assertRaises(ValidationError):
            data = 'value' * 250
            instance.to_internal_value(data)

    def test_to_internal_value_raises_validate_exception(self):
        instance = fields.IntegerField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('object')

    def test_to_to_representation(self):
        instance = fields.IntegerField()
        self.assertEqual(instance.to_representation('1'), 1)


class TestBigIntegerField(unittest.TestCase):

    def test_init_default(self):
        instance = fields.BigIntegerField()
        self.assertEqual(instance.min_value, -instance.MAX_BIG_INTEGER - 1)
        self.assertEqual(instance.max_value, instance.MAX_BIG_INTEGER)

    def test_to_internal_value(self):
        instance = fields.BigIntegerField()
        self.assertEqual(instance.to_internal_value(1), 1)

    def test_to_internal_value_raises_max_string_length_exception(self):
        instance = fields.BigIntegerField()

        with self.assertRaises(ValidationError):
            data = 'value' * 250
            instance.to_internal_value(data)

    def test_to_internal_value_raises_validate_exception(self):
        instance = fields.BigIntegerField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('object')

    def test_to_to_representation(self):
        instance = fields.BigIntegerField()
        self.assertEqual(instance.to_representation('1'), 1)


class TestSmallIntegerField(unittest.TestCase):

    def test_init_default(self):
        instance = fields.SmallIntegerField()
        self.assertEqual(instance.min_value, -instance.MAX_SMALL_INTEGER - 1)
        self.assertEqual(instance.max_value, instance.MAX_SMALL_INTEGER)

    def test_to_internal_value(self):
        instance = fields.SmallIntegerField()
        self.assertEqual(instance.to_internal_value(1), 1)

    def test_to_internal_value_raises_max_string_length_exception(self):
        instance = fields.SmallIntegerField()

        with self.assertRaises(ValidationError):
            data = 'value' * 250
            instance.to_internal_value(data)

    def test_to_internal_value_raises_validate_exception(self):
        instance = fields.SmallIntegerField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('object')

    def test_to_to_representation(self):
        instance = fields.SmallIntegerField()
        self.assertEqual(instance.to_representation('1'), 1)


class TestBooleanField(unittest.TestCase):

    def test_init_raises_assertion_error(self):
        with self.assertRaises(AssertionError):
            fields.BooleanField(allow_null=True)

    def test_to_internal_value_returns_true_value(self):
        instance = fields.BooleanField()

        for value in instance.TRUE_VALUES:
            self.assertTrue(instance.to_internal_value(value))

    def test_to_internal_value_returns_false_value(self):
        instance = fields.BooleanField()

        for value in instance.FALSE_VALUES:
            self.assertFalse(instance.to_internal_value(value))

    def test_to_internal_value_raises_validate_exception(self):
        instance = fields.BooleanField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(object())

    def test_to_internal_value_with_unhashable_value(self):
        instance = fields.BooleanField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value({})

    def test_to_representation_returns_true_value(self):
        instance = fields.BooleanField()

        for value in instance.TRUE_VALUES:
            self.assertTrue(instance.to_representation(value))

    def test_to_representation_returns_false_value(self):
        instance = fields.BooleanField()

        for value in instance.FALSE_VALUES:
            self.assertFalse(instance.to_representation(value))

    def test_to_representation_return_true_for_not_defined_values(self):
        instance = fields.BooleanField()
        self.assertTrue(instance.to_representation(object()))
        self.assertTrue(instance.to_representation("value"))

    def test_to_representation_return_false_for_not_defined_values(self):
        instance = fields.BooleanField()
        self.assertFalse(instance.to_representation(()))
        self.assertFalse(instance.to_representation(""))


class TestNullBooleanField(unittest.TestCase):

    def test_to_internal_value_returns_true_value(self):
        instance = fields.NullBooleanField()

        for value in instance.TRUE_VALUES:
            self.assertTrue(instance.to_internal_value(value))

    def test_to_internal_value_returns_false_value(self):
        instance = fields.NullBooleanField()

        for value in instance.FALSE_VALUES:
            self.assertFalse(instance.to_internal_value(value))

    def test_to_internal_value_returns_none_value(self):
        instance = fields.NullBooleanField()

        for value in instance.NULL_VALUES:
            self.assertIsNone(instance.to_internal_value(value))

    def test_to_internal_value_raises_validate_exception(self):
        instance = fields.NullBooleanField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(object())

    def test_to_representation_returns_true_value(self):
        instance = fields.NullBooleanField()

        for value in instance.TRUE_VALUES:
            self.assertTrue(instance.to_representation(value))

    def test_to_representation_returns_false_value(self):
        instance = fields.NullBooleanField()

        for value in instance.FALSE_VALUES:
            self.assertFalse(instance.to_representation(value))

    def test_to_representation_returns_none_value(self):
        instance = fields.NullBooleanField()

        for value in instance.NULL_VALUES:
            self.assertIsNone(instance.to_representation(value))

    def test_to_representation_return_true_for_not_defined_values(self):
        instance = fields.NullBooleanField()
        self.assertTrue(instance.to_representation(object()))
        self.assertTrue(instance.to_representation("value"))

    def test_to_representation_return_false_for_not_defined_values(self):
        instance = fields.NullBooleanField()
        self.assertFalse(instance.to_representation(()))
        self.assertFalse(instance.to_representation(""))


class TestCharField(unittest.TestCase):

    def test_init_default(self):
        instance = fields.CharField()
        self.assertFalse(instance.allow_blank)
        self.assertTrue(instance.trim_whitespace)
        self.assertIsNone(instance.min_length)
        self.assertIsNone(instance.max_length)

    def test_run_validation(self):
        instance = fields.CharField()
        self.assertEqual(instance.to_internal_value('test'), 'test')

    def test_run_validation_raise_validation_error_for_too_short_string(self):
        instance = fields.CharField(min_length=5)

        with self.assertRaises(ValidationError):
            instance.run_validation('test')

    def test_run_validation_raise_validation_error_for_too_long_string(self):
        instance = fields.CharField(max_length=3)

        with self.assertRaises(ValidationError):
            instance.run_validation('test')

    def test_run_validation_raise_validation_error_for_blank_field(self):
        instance = fields.CharField(allow_blank=False)

        with self.assertRaises(ValidationError):
            instance.run_validation('')

    def test_run_validation_returns_empty_string(self):
        instance = fields.CharField(allow_blank=True)
        self.assertEqual(instance.run_validation(''), '')

    def test_to_internal_value(self):
        instance = fields.CharField()
        self.assertEqual(instance.to_internal_value(' value '), 'value')

    def test_to_internal_value_without_trim_whitespace(self):
        instance = fields.CharField(trim_whitespace=False)
        self.assertEqual(instance.to_internal_value(' value '), ' value ')

    def test_to_representation(self):
        instance = fields.CharField()
        self.assertEqual(instance.to_representation('test'), 'test')
