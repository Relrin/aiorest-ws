# -*- coding: utf-8 -*-
import unittest
from enum import Enum

from aiorest_ws.db.orm.abstract import AbstractField
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.validators import BaseValidator, MaxValueValidator, \
    MinValueValidator, MaxLengthValidator, MinLengthValidator, EnumValidator, \
    BaseUniqueFieldValidator


class FakeField(AbstractField):
    pass


class TestBaseValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBaseValidator, cls).setUpClass()
        cls.instance = BaseValidator()

    def test_validator_call(self):
        with self.assertRaises(NotImplementedError):
            self.instance("value")

    def test_validator_compare_returns_true(self):
        another_instance = BaseValidator()
        self.assertTrue(self.instance == another_instance)

    def test_validator_compare_returns_false(self):
        another_instance = BaseValidator(message="error message")
        self.assertFalse(self.instance == another_instance)


class TestMaxValueValidator(unittest.TestCase):

    def test_init(self):
        instance = MaxValueValidator(10)
        self.assertEqual(instance.max_value, 10)

    def test_init_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            MaxValueValidator(None)

    def test_validate(self):
        instance = MaxValueValidator(10)
        self.assertIsNone(instance(5))

    def test_validate_raises_validation_exception(self):
        instance = MaxValueValidator(10)

        with self.assertRaises(ValidationError):
            instance(11)


class TestMinValueValidator(unittest.TestCase):

    def test_init(self):
        instance = MinValueValidator(10)
        self.assertEqual(instance.min_value, 10)

    def test_init_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            MinValueValidator(None)

    def test_validate(self):
        instance = MinValueValidator(10)
        self.assertIsNone(instance(11))

    def test_validate_raises_validation_exception(self):
        instance = MinValueValidator(10)

        with self.assertRaises(ValidationError):
            instance(5)


class TestMaxLengthValidator(unittest.TestCase):

    def test_init(self):
        instance = MaxLengthValidator(5)
        self.assertEqual(instance.max_length, 5)

    def test_init_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            MaxLengthValidator(-1)

    def test_validate(self):
        instance = MaxLengthValidator(5)
        self.assertIsNone(instance("1234"))

    def test_validate_raises_validation_exception(self):
        instance = MaxLengthValidator(5)

        with self.assertRaises(ValidationError):
            instance("123456")


class TestMinLengthValidator(unittest.TestCase):

    def test_init(self):
        instance = MinLengthValidator(3)
        self.assertEqual(instance.min_length, 3)

    def test_init_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            MinLengthValidator(-1)

    def test_validate(self):
        instance = MinLengthValidator(3)
        self.assertIsNone(instance("1234"))

    def test_validate_raises_validation_exception(self):
        instance = MinLengthValidator(3)

        with self.assertRaises(ValidationError):
            instance("12")


class TestEnumValidator(unittest.TestCase):

    class TestEnum(Enum):
        ZERO = 0
        ONE = 1
        TWO = 2

    def test_call(self):
        instance = EnumValidator(self.TestEnum)
        self.assertIsNone(instance("ZERO"))

    def test_call_raises_validation_error(self):
        instance = EnumValidator(self.TestEnum)

        with self.assertRaises(ValidationError):
            instance("UNKNOWN")


class TestBaseUniqueFieldValidator(unittest.TestCase):

    def test_set_context(self):
        instance = BaseUniqueFieldValidator(None)
        field = FakeField()
        field.bind('attr', None)
        instance.set_context(field)
        self.assertEqual(instance.field_name, field.source_attrs[0])
        self.assertEqual(instance.instance, None)

    def test_filter_queryset_raises_not_implemented_exception(self):
        instance = BaseUniqueFieldValidator(None)

        with self.assertRaises(NotImplementedError):
            instance.filter_queryset(None, None)

    def test_exclude_current_instance_raises_not_implemented_exception(self):
        instance = BaseUniqueFieldValidator(None)

        with self.assertRaises(NotImplementedError):
            instance.exclude_current_instance(None)

    def test_validate_raises_not_implemented_exception(self):
        instance = BaseUniqueFieldValidator(None)

        with self.assertRaises(NotImplementedError):
            instance(None)

    def test_repr(self):
        instance = BaseUniqueFieldValidator(None)
        self.assertEqual(
            instance.__repr__(), "<BaseUniqueFieldValidator(queryset=None)>"
        )
