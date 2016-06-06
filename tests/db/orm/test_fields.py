# -*- coding: utf-8 -*-
import datetime
import pickle
import unittest
from decimal import Decimal

from aiorest_ws.conf import settings
from aiorest_ws.db.orm import fields
from aiorest_ws.db.orm.abstract import empty, SkipField
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.date import timezone


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

    def test_disallow_blank_with_trim_whitespace(self):
        instance = fields.CharField(allow_blank=False, trim_whitespace=True)

        with self.assertRaises(ValidationError):
            instance.run_validation(' ')

    def test_to_representation(self):
        instance = fields.CharField()
        self.assertEqual(instance.to_representation('test'), 'test')


class TestChoiceField(unittest.TestCase):

    choices = (
        (1, 'one'),
        (2, 'two'),
        (3, 'three')
    )

    def test_to_internal_value(self):
        instance = fields.ChoiceField(choices=self.choices)
        self.assertEqual(instance.to_internal_value(1), 1)

    def test_to_internal_value_for_empty_string(self):
        instance = fields.ChoiceField(self.choices, allow_blank=True)
        self.assertEqual(instance.to_internal_value(''), '')

    def test_to_internal_value_raise_validation_error(self):
        instance = fields.ChoiceField(self.choices)

        with self.assertRaises(ValidationError):
            instance.to_internal_value(4)

    def test_to_representation(self):
        instance = fields.ChoiceField(self.choices)
        self.assertEqual(instance.to_representation(2), 2)

    def test_to_representation_empty_string(self):
        instance = fields.ChoiceField(self.choices)
        self.assertEqual(instance.to_representation(''), '')

    def test_to_representation_none_value(self):
        instance = fields.ChoiceField(self.choices)
        self.assertEqual(instance.to_representation(None), None)

    def test_to_representation_not_found_key(self):
        instance = fields.ChoiceField(self.choices)
        self.assertEqual(instance.to_representation(4), 4)


class TestFloatField(unittest.TestCase):

    def test_init_default(self):
        instance = fields.FloatField()
        self.assertIsNone(instance.min_value)
        self.assertIsNone(instance.max_value)

    def test_run_validation_without_borders(self):
        instance = fields.FloatField()
        self.assertEqual(instance.run_validation(5.0), 5.0)

    def test_run_validation_with_defined_min_value(self):
        instance = fields.FloatField(min_value=10.0)

        with self.assertRaises(ValidationError):
            instance.run_validation(5.0)

    def test_run_validation_with_defined_max_value(self):
        instance = fields.FloatField(max_value=10.0)

        with self.assertRaises(ValidationError):
            instance.run_validation(11.0)

    def test_to_internal_value(self):
        instance = fields.FloatField()
        self.assertEqual(instance.to_internal_value(5), 5)

    def test_to_internal_value_raises_validation_error(self):
        instance = fields.FloatField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_raises_validation_error_for_too_long_str(self):
        instance = fields.FloatField(max_value=10)

        with self.assertRaises(ValidationError):
            instance.to_internal_value('test' * 255)

    def test_to_representation(self):
        instance = fields.FloatField()
        self.assertEqual(instance.to_representation(5), 5.0)


class TestPickleField(unittest.TestCase):

    def test_to_internal_value(self):
        instance = fields.PickleField()
        dump_dict = pickle.dumps({'key': 'value'})
        self.assertEqual(instance.to_internal_value(dump_dict), dump_dict)

    def test_to_internal_value_raises_validation_error(self):
        instance = fields.PickleField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_representation(self):
        instance = fields.PickleField()
        dump_dict = pickle.dumps({'key': 'value'})
        self.assertEqual(
            instance.to_representation(dump_dict), dump_dict
        )


class TestLargeBinaryField(unittest.TestCase):

    def test_to_internal_value(self):
        instance = fields.LargeBinaryField()
        self.assertEqual(instance.to_internal_value('value'), b'value')

    def test_to_internal_value_raises_validation_error(self):
        instance = fields.LargeBinaryField(length=10)

        with self.assertRaises(ValidationError):
            dump_dict = pickle.dumps({'key': 'value'})
            instance.to_internal_value(dump_dict)

    def test_to_representation(self):
        instance = fields.LargeBinaryField()
        self.assertEqual(instance.to_representation('value'), b'value')


class TestTimeField(unittest.TestCase):

    def test_run_validation_raise_validation_error(self):
        instance = fields.TimeField()

        with self.assertRaises(ValidationError):
            instance.run_validation('value')

    def test_to_internal_value_string(self):
        instance = fields.TimeField()
        self.assertEqual(
            instance.to_internal_value('03:00'),
            datetime.time(3, 0)
        )

    def test_to_internal_value_time(self):
        instance = fields.TimeField()
        self.assertEqual(
            instance.to_internal_value(datetime.time(3, 0)),
            datetime.time(3, 0)
        )

    def test_to_internal_value_for_non_iso8601(self):
        instance = fields.TimeField(input_formats=('%H:%M', ))
        self.assertEqual(
            instance.to_internal_value('10:00'),
            datetime.time(10, 0)
        )

    def test_to_internal_value_raises_validation_error_with_empty_format(self):
        instance = fields.TimeField(input_formats=())

        with self.assertRaises(ValidationError):
            instance.to_internal_value('99:99')

    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        instance = fields.TimeField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_raises_error_for_wrong_value_and_format(self):
        instance = fields.TimeField(input_formats=('%H:%M',))

        with self.assertRaises(ValidationError):
            instance.to_internal_value('99:99')

    def test_to_internal_value_raises_error_for_none_value_and_format(self):
        instance = fields.TimeField(input_formats=('%H:%M',))

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_raises_validation_error_for_wrong_value(self):
        instance = fields.TimeField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('99:99')

    def test_to_representation(self):
        instance = fields.TimeField(format='%H:%M:%S')
        timestamp = datetime.time(3, 0)
        self.assertEqual(
            instance.to_representation(timestamp), '03:00:00'
        )

    def test_to_representation_returns_none_for_empty_string(self):
        instance = fields.TimeField()
        self.assertIsNone(instance.to_representation(''))

    def test_to_representation_returns_none(self):
        instance = fields.TimeField()
        self.assertIsNone(instance.to_representation(None))

    def test_to_representation_return_value(self):
        instance = fields.TimeField(format=None)
        timestamp = datetime.time(13, 0)
        self.assertEqual(instance.to_representation(timestamp), timestamp)

    def test_to_representation_parse_string_into_iso8601_string(self):
        instance = fields.TimeField()
        self.assertEqual(
            instance.to_representation('10:00:00'), '10:00:00'
        )

    def test_to_representation_parse_time_into_iso8601_string(self):
        instance = fields.TimeField()
        self.assertEqual(
            instance.to_representation(datetime.time(10, 0)), '10:00:00'
        )

    def test_to_representation_raise_assertion_error(self):
        instance = fields.TimeField(format=settings.ISO_8601)
        with self.assertRaises(AssertionError):
            instance.to_representation(datetime.datetime(2000, 1, 1, 10, 00))


class TestDecimalField(unittest.TestCase):

    def test_init_default(self):
        instance = fields.DecimalField(max_digits=5, decimal_places=2)
        self.assertEqual(instance.max_digits, 5)
        self.assertEqual(instance.decimal_places, 2)
        self.assertEqual(instance.max_whole_digits, 3)

    def test_init_with_not_defined_max_whole_digits(self):
        instance = fields.DecimalField(max_digits=None, decimal_places=None)
        self.assertIsNone(instance.max_digits)
        self.assertIsNone(instance.decimal_places)
        self.assertIsNone(instance.max_whole_digits)

    def test_run_validation(self):
        instance = fields.DecimalField(max_digits=5, decimal_places=2)
        self.assertEqual(instance.run_validation(99), 99)

    def test_run_validation_raises_validation_error_for_gt_max_value(self):
        instance = fields.DecimalField(
            max_digits=5, decimal_places=2, max_value=90
        )

        with self.assertRaises(ValidationError):
            instance.run_validation(99)

    def test_run_validation_raises_validation_error_for_lt_min_value(self):
        instance = fields.DecimalField(
            max_digits=5, decimal_places=2, min_value=10,
        )

        with self.assertRaises(ValidationError):
            instance.run_validation(9)

    def test_validate_precision_with_exponent(self):
        instance = fields.DecimalField(max_digits=5, decimal_places=0)

        value = Decimal('12345')
        self.assertEqual(instance.validate_precision(value), value)

    def test_validate_precision_with_digittuple(self):
        instance = fields.DecimalField(max_digits=7, decimal_places=2)

        value = Decimal('12345.0')
        self.assertEqual(instance.validate_precision(value), value)

    def test_validate_precision_with_fraction(self):
        instance = fields.DecimalField(max_digits=7, decimal_places=5)

        value = Decimal('0.01234')
        self.assertEqual(instance.validate_precision(value), value)

    def test_validate_precision_raise_validation_exc_max_digits(self):
        instance = fields.DecimalField(max_digits=5, decimal_places=2)

        with self.assertRaises(ValidationError):
            instance.validate_precision(Decimal('1234500.0'))

    def test_validate_precision_raise_validation_exc_max_decimal_places(self):
        instance = fields.DecimalField(max_digits=9, decimal_places=0)

        with self.assertRaises(ValidationError):
            instance.validate_precision(Decimal('1234500.0'))

    def test_validate_precision_raise_validation_exc_max_whole_digits(self):
        instance = fields.DecimalField(max_digits=9, decimal_places=7)

        with self.assertRaises(ValidationError):
            instance.validate_precision(Decimal('1234500.0'))

    def test_to_internal_value(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)
        self.assertEqual(
            instance.to_internal_value(12345.0), Decimal('12345.0')
        )

    def test_to_internal_value_raises_validation_error_for_max_length(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)

        with self.assertRaises(ValidationError):
            instance.to_internal_value('test' * 255)

    def test_to_internal_value_raises_validation_error_for_not_decimal(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)

        with self.assertRaises(ValidationError):
            instance.to_internal_value('None')

    def test_to_internal_value_raises_validation_error_for_NaN(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)

        with self.assertRaises(ValidationError):
            instance.to_internal_value('NaN')

    def test_to_internal_value_raises_validation_error_for_infinity(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)

        with self.assertRaises(ValidationError):
            instance.to_internal_value(float('inf'))  # positive infinite
            instance.to_internal_value(-float('inf'))  # negative infinite

    def test_to_representation_with_decimal_as_a_string(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)
        self.assertEqual(instance.to_representation('12345.0'), '12345.00000')

    def test_to_representation_without_coerce_to_string(self):
        instance = fields.DecimalField(
            max_digits=10, decimal_places=5, coerce_to_string=False
        )
        value = Decimal('12345.0')
        self.assertEqual(instance.to_representation(value), value)

    def test_quantize(self):
        instance = fields.DecimalField(max_digits=10, decimal_places=5)

        value = Decimal('12345.0')
        self.assertEqual(instance.quantize(value), value)


class TestDateFields(unittest.TestCase):

    def test_run_validation_raises_validation_error_for_wrong_value(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.run_validation('value')

    def test_run_validation_raises_validation_error_for_wrong_datetime(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.run_validation('2001-99-99')

    def test_run_validation_raises_validation_error_for_a_wrong_type(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.run_validation(datetime.datetime(2000, 1, 1, 1, 0))

    def test_to_internal_value_raises_validation_error_for_wrong_type(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(datetime.datetime(2000, 1, 1, 1, 0))

    def test_to_internal_value_returns_date_instance(self):
        instance = fields.DateField()
        value = datetime.date(2000, 1, 1)
        self.assertEqual(instance.to_internal_value(value), value)

    def test_to_internal_value_returns_parsed_string_for_iso8601(self):
        instance = fields.DateField()
        self.assertEqual(
            instance.to_internal_value('2000-01-01'),
            datetime.date(2000, 1, 1)
        )

    def test_to_internal_value_raises_validation_error_for_wrong_date(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('2000-99-99')

    def test_to_internal_value_raises_validation_error_for_wrong_value(self):
        instance = fields.DateField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_with_user_format(self):
        instance = fields.DateField(input_formats=('%Y-%m-%d', ))
        self.assertEqual(
            instance.to_internal_value('2000-01-01'),
            datetime.date(2000, 1, 1)
        )

    def test_to_internal_value_with_format_raises_error_for_wrong_value(self):
        instance = fields.DateField(input_formats=('%Y-%m-%d', ))

        with self.assertRaises(ValidationError):
            instance.to_internal_value('2000-99-99')

    def test_to_internal_value_with_format_raises_error_for_wrong_type(self):
        instance = fields.DateField(input_formats=('%Y-%m-%d', ))

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_representation_returns_none(self):
        instance = fields.DateField()
        self.assertIsNone(instance.to_representation(None))

    def test_to_representation_returns_empty_string(self):
        instance = fields.DateField()
        self.assertEqual(instance.to_representation(''), None)

    def test_to_representation_with_none_output_format(self):
        instance = fields.DateField(format=None)
        self.assertEqual(
            instance.to_representation('2000-01-01'), '2000-01-01'
        )

    def test_to_representation_raises_assertion_error_for_a_wrong_type(self):
        instance = fields.DateField()

        with self.assertRaises(AssertionError):
            instance.to_representation(datetime.datetime(2000, 1, 1))

    def test_to_representation_returns_value_in_uso8601_for_string(self):
        instance = fields.DateField()
        self.assertEqual(
            instance.to_representation('2000-01-01'), '2000-01-01'
        )

    def test_to_representation_returns_value_in_uso8601_for_date(self):
        instance = fields.DateField()
        self.assertEqual(
            instance.to_representation(datetime.date(2000, 1, 1)), '2000-01-01'
        )

    def test_to_representation_with_custom_date_format(self):
        instance = fields.DateField(format="%Y-%m-%d")
        self.assertEqual(
            instance.to_representation(datetime.date(2000, 1, 1)), '2000-01-01'
        )


class TestDateTimeField(unittest.TestCase):

    def test_run_validation_raises_validation_error_for_a_wrong_type(self):
        instance = fields.DateTimeField()

        with self.assertRaises(ValidationError):
            instance.run_validation(None)

    def test_run_validation_raises_validation_error_for_a_wrong_value(self):
        instance = fields.DateTimeField()

        with self.assertRaises(ValidationError):
            instance.run_validation('value')

    def test_enforce_timezone_returns_naive_datetime(self):
        instance = fields.DateTimeField()
        value = datetime.datetime(2000, 1, 1, 10, 0)
        self.assertEqual(instance.enforce_timezone(value), value)

    def test_enforce_timezone_returns_aware_datetime_with_utc_timezone(self):
        instance = fields.DateTimeField(default_timezone=timezone.UTC())
        self.assertEqual(
            instance.enforce_timezone(datetime.datetime(2000, 1, 1, 10, 0)),
            datetime.datetime(2000, 1, 1, 10, 0, tzinfo=timezone.UTC())
        )

    def test_enforce_timezone_returns_naive_datetime_with_utc_timezone(self):
        instance = fields.DateTimeField()
        value = datetime.datetime(2000, 1, 1, 10, 0, tzinfo=timezone.UTC())
        self.assertEqual(
            instance.enforce_timezone(value),
            datetime.datetime(2000, 1, 1, 10, 0)
        )

    def test_to_internal_value_returns_datetime_with_enforce_datetime(self):
        instance = fields.DateTimeField()
        self.assertEqual(
            instance.to_internal_value(datetime.datetime(2000, 1, 1)),
            datetime.datetime(2000, 1, 1)
        )

    def test_to_internal_value_raises_validation_error_for_date_type(self):
        instance = fields.DateTimeField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(datetime.date(2000, 1, 1))

    def test_to_internal_value_returns_datetime_in_iso8601(self):
        instance = fields.DateTimeField()

        self.assertEqual(
            instance.to_internal_value('2000-01-01 10:00'),
            datetime.datetime(2000, 1, 1, 10, 0)
        )

    def test_to_internal_value_raises_validation_error_with_a_wrong_type(self):
        instance = fields.DateTimeField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_raises_validation_error_for_invalid_value(self):
        instance = fields.DateTimeField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('2000-99-99 10:00')

    def test_to_internal_value_with_format_returns_datetime(self):
        instance = fields.DateTimeField(input_formats=("%Y-%m-%d %H:%M", ))
        self.assertEqual(
            instance.to_internal_value('2000-01-01 10:00'),
            datetime.datetime(2000, 1, 1, 10, 0)
        )

    def test_to_internal_value_with_format_raises_exc_for_a_wrong_type(self):
        instance = fields.DateTimeField(input_formats=("%Y-%m-%d %H:%M",))

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_with_format_raises_exc_for_invalid_value(self):
        instance = fields.DateTimeField(input_formats=("%Y-%m-%d %H:%M",))

        with self.assertRaises(ValidationError):
            instance.to_internal_value('2000-99-99 10:00')

    def test_to_representation_returns_none_for_empty_string(self):
        instance = fields.DateTimeField()
        self.assertIsNone(instance.to_representation(''))

    def test_to_representation_returns_none_for_none_type(self):
        instance = fields.DateTimeField()
        self.assertIsNone(instance.to_representation(None))

    def test_to_representation_with_none_output_format_returns_value(self):
        instance = fields.DateTimeField(format=None)
        self.assertEqual(
            instance.to_representation('2000-01-01T10:00:00Z'),
            '2000-01-01T10:00:00Z'
        )

    def test_to_representation_returns_value_in_iso8601(self):
        instance = fields.DateTimeField()
        value = datetime.datetime(2000, 1, 1, 10, 0, tzinfo=timezone.UTC())
        self.assertEqual(
            instance.to_representation(value),
            '2000-01-01T10:00:00Z'
        )

    def test_to_representation_returns_value_in_custom_format(self):
        instance = fields.DateTimeField(format="%Y-%m-%d %H:%M")
        self.assertEqual(
            instance.to_representation(datetime.datetime(2000, 1, 1, 10, 0)),
            '2000-01-01 10:00'
        )


class TestTimeDeltaField(unittest.TestCase):

    def test_init_raises_assetion_error_for_wrong_display_argument(self):

        with self.assertRaises(AssertionError):
            fields.TimeDeltaField(display="unknown")

    def test_to_internal_value_return_timedelta(self):
        instance = fields.TimeDeltaField()
        self.assertEqual(
            instance.to_internal_value("1 day"),
            datetime.timedelta(1)
        )

    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        instance = fields.TimeDeltaField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(None)

    def test_to_internal_value_raises_validation_error_for_invalid_value(self):
        instance = fields.TimeDeltaField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_representation(self):
        instance = fields.TimeDeltaField()
        self.assertEqual(
            instance.to_representation(datetime.timedelta(days=1)),
            "1 day"
        )


class TestHiddenField(unittest.TestCase):

    def test_init_raises_validation_error_for_the_missed_default_arg(self):

        with self.assertRaises(AssertionError):
            fields.HiddenField()

    def test_get_value_returns_empty(self):
        instance = fields.HiddenField(default='value')
        self.assertEqual(instance.get_value({}), empty)

    def test_to_internal_value_returns_data(self):
        instance = fields.HiddenField(default='value')
        self.assertEqual(instance.to_internal_value('test'), 'test')


class TestCreateOnlyField(unittest.TestCase):

    class FakeDefault(object):

        @staticmethod
        def set_context(field):
            field.test_attr = 'value'

    def test_can_set_context_returns_false(self):
        instance = fields.CreateOnlyDefault('default')
        instance.is_update = False
        self.assertFalse(instance._can_set_context())

    def test_can_set_context_returns_true_for_instance_class(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        instance.is_update = False
        self.assertTrue(instance._can_set_context())

    def test_can_set_context_returns_false_for_instance_class(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        instance.is_update = True
        self.assertFalse(instance._can_set_context())

    def test_can_set_context_returns_false_for_not_instance_class(self):
        instance = fields.CreateOnlyDefault('default')
        instance.is_update = True
        self.assertFalse(instance._can_set_context())

    def test_set_context_function_add_context_for_default(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        fake_parent = type('FakeParent', (), {'instance': None})
        serializer_field = fields.IntegerField()
        serializer_field.bind('pk', fake_parent)
        instance.set_context(serializer_field)
        self.assertFalse(instance.is_update)
        self.assertTrue(hasattr(serializer_field, 'test_attr'))
        self.assertEqual(serializer_field.test_attr, 'value')

    def test_set_context_function_not_add_context_for_default(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        fake_parent = type('FakeParent', (), {'instance': object()})
        serializer_field = fields.IntegerField()
        serializer_field.bind('pk', fake_parent)
        instance.set_context(serializer_field)
        self.assertTrue(instance.is_update)
        self.assertFalse(hasattr(serializer_field, 'test_attr'))

    def test_call_returns_default(self):
        instance = fields.CreateOnlyDefault('value')
        instance.is_update = False
        self.assertEqual(instance(), instance.default)

    def test_call_returns_default_from_callable(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        instance.is_update = False
        self.assertIsInstance(instance(), self.FakeDefault)

    def test_call_raise_skip_field_exception(self):
        instance = fields.CreateOnlyDefault(self.FakeDefault)
        instance.is_update = True

        with self.assertRaises(SkipField):
            instance()

    def test_repr(self):
        instance = fields.CreateOnlyDefault('value')
        self.assertEqual(instance.__repr__(), 'CreateOnlyDefault(value)')


class TestReadOnlyField(unittest.TestCase):

    def test_to_representation(self):
        instance = fields.ReadOnlyField()
        self.assertEqual(instance.to_representation('value'), 'value')


class TestUnvalidatedField(unittest.TestCase):

    def test_to_internal_value(self):
        instance = fields._UnvalidatedField()
        self.assertEqual(instance.to_internal_value('value'), 'value')

    def test_to_representation(self):
        instance = fields._UnvalidatedField()
        self.assertEqual(instance.to_representation('value'), 'value')


class TestListField(unittest.TestCase):

    def test_init_raises_assertion_error_for_defined_child_as_a_class(self):

        with self.assertRaises(AssertionError):
            fields.ListField(child=fields.IntegerField)

    def test_init_raises_assertion_error_for_child_without_source(self):

        with self.assertRaises(AssertionError):
            fields.ListField(child=fields.IntegerField(source='value'))

    def test_get_value(self):
        instance = fields.ListField(child=fields.IntegerField())
        instance.bind('test', None)
        self.assertEqual(instance.get_value({'test': [1, 2, 3]}), [1, 2, 3])

    def test_get_value_returns_empty_value(self):

        class FakeModelSerializer(object):
            partial = True
            parent = None

        instance = fields.ListField(child=fields.IntegerField())
        instance.bind('test', FakeModelSerializer())
        self.assertEqual(instance.get_value({'key': [1, 2, 3]}), empty)

    def test_to_internal_value_empty_list(self):
        instance = fields.ListField(child=fields.IntegerField())
        self.assertEqual(instance.to_internal_value([]), [])

    def test_to_internal_value_for_integer_list(self):
        instance = fields.ListField(child=fields.IntegerField())
        self.assertEqual(instance.to_internal_value([1, 2, 3]), [1, 2, 3])

    def test_to_internal_value_for_list_with_integer_as_a_string(self):
        instance = fields.ListField(child=fields.IntegerField())
        self.assertEqual(
            instance.to_internal_value(['1', '2', '3']),
            [1, 2, 3]
        )

    def test_to_internal_value_raises_validation_error_for_wrong_type(self):
        instance = fields.ListField(child=fields.IntegerField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value({"key": "value"})

    def test_to_internal_value_raises_validation_error_for_wrong_value(self):
        instance = fields.ListField(child=fields.IntegerField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value([1, 2, 'error'])

    def test_to_internal_value_raises_validation_error_for_empty_list(self):
        instance = fields.ListField(
            child=fields.IntegerField(), allow_empty=False
        )

        with self.assertRaises(ValidationError):
            instance.to_internal_value([])

    def test_to_representation(self):
        instance = fields.ListField(child=fields.IntegerField())
        self.assertEqual(instance.to_representation([1, 2, 3]), [1, 2, 3])

    def test_to_representation_for_string_list(self):
        instance = fields.ListField(child=fields.IntegerField())
        self.assertEqual(
            instance.to_representation(['1', '2', '3']),
            [1, 2, 3]
        )

    def test_to_iternal_value_without_child_instance(self):
        instance = fields.ListField()
        self.assertEqual(
            instance.to_internal_value([1, '2', True, [4, 5, 6]]),
            [1, '2', True, [4, 5, 6]]
        )

    def test_to_iternal_value_without_child_instance_raises_an_error(self):
        instance = fields.ListField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_representation_without_child_instance(self):
        instance = fields.ListField()
        self.assertEqual(
            instance.to_representation([1, '2', True, [4, 5, 6]]),
            [1, '2', True, [4, 5, 6]]
        )


class TestDictField(unittest.TestCase):

    def test_init_raises_assertion_error_for_defined_child_as_a_class(self):

        with self.assertRaises(AssertionError):
            fields.DictField(child=fields.CharField)

    def test_init_raises_assertion_error_for_child_without_source(self):

        with self.assertRaises(AssertionError):
            fields.DictField(child=fields.CharField(source='value'))

    def test_get_value(self):
        instance = fields.DictField(child=fields.CharField())
        instance.bind('test', None)
        self.assertEqual(instance.get_value({'test': 'value'}), 'value')

    def test_get_value_returns_empty_value(self):
        instance = fields.DictField(child=fields.CharField())
        instance.bind('test', None)
        self.assertEqual(instance.get_value({'key': 'value'}), empty)

    def test_to_internal_value(self):
        instance = fields.DictField(child=fields.CharField())
        self.assertEqual(
            instance.to_internal_value({'a': 1, 'b': '2'}),
            {'a': '1', 'b': '2'}
        )

    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        instance = fields.DictField(child=fields.CharField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_internal_value_raises_validation_error_for_a_wrong_value(self):
        instance = fields.DictField(child=fields.CharField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value({'key': None})

    def test_to_representation(self):
        instance = fields.DictField(child=fields.CharField())
        self.assertEqual(
            instance.to_representation({'a': 1, 'b': '2'}),
            {'a': '1', 'b': '2'}
        )

    def test_to_iternal_value_without_child_instance(self):
        instance = fields.DictField()
        self.assertEqual(
            instance.to_internal_value({'a': 1, 'b': [1, 2], 'c': 'c'}),
            {'a': 1, 'b': [1, 2], 'c': 'c'}
        )

    def test_to_iternal_value_without_child_instance_raises_an_error(self):
        instance = fields.DictField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_representation_without_child_instance(self):
        instance = fields.DictField()
        self.assertEqual(
            instance.to_representation({'a': 1, 'b': [1, 2], 'c': 'c'}),
            {'a': 1, 'b': [1, 2], 'c': 'c'}
        )


class TestHStoreField(unittest.TestCase):

    def test_init_raises_assertion_error_for_defined_child_as_a_class(self):
        with self.assertRaises(AssertionError):
            fields.HStoreField(child=fields.CharField)

    def test_init_raises_assertion_error_for_child_without_source(self):
        with self.assertRaises(AssertionError):
            fields.HStoreField(child=fields.CharField(source='value'))

    def test_get_value(self):
        instance = fields.HStoreField()
        instance.bind('test', None)
        self.assertEqual(instance.get_value({'test': 'value'}), 'value')

    def test_get_value_returns_empty_value(self):
        instance = fields.HStoreField(child=fields.CharField())
        instance.bind('test', None)
        self.assertEqual(instance.get_value({'key': 'value'}), empty)

    def test_to_internal_value(self):
        instance = fields.HStoreField(child=fields.CharField())
        self.assertEqual(
            instance.to_internal_value({'a': 1, 'b': '2'}),
            {'a': '1', 'b': '2'}
        )

    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        instance = fields.HStoreField(child=fields.CharField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_internal_value_raises_validation_error_for_a_wrong_value(self):
        instance = fields.HStoreField(child=fields.CharField())

        with self.assertRaises(ValidationError):
            instance.to_internal_value({'key': None})

    def test_to_representation(self):
        instance = fields.HStoreField(child=fields.CharField())
        self.assertEqual(
            instance.to_representation({'a': 1, 'b': '2'}),
            {'a': '1', 'b': '2'}
        )

    def test_to_iternal_value_without_child_instance(self):
        instance = fields.HStoreField()
        self.assertEqual(
            instance.to_internal_value({'a': 1, 'b': [1, 2], 'c': 'c'}),
            {'a': '1', 'b': '[1, 2]', 'c': 'c'}
        )

    def test_to_iternal_value_without_child_instance_raises_an_error(self):
        instance = fields.HStoreField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value('value')

    def test_to_representation_without_child_instance(self):
        instance = fields.HStoreField()
        self.assertEqual(
            instance.to_representation({'a': 1, 'b': [1, 2], 'c': 'c'}),
            {'a': '1', 'b': '[1, 2]', 'c': 'c'}
        )


class TestJSONField(unittest.TestCase):

    # simple JSON

    def test_run_validation_raises_validation_error(self):
        instance = fields.JSONField()

        with self.assertRaises(ValidationError):
            instance.run_validation({'key': [1, '2', [3, set()]]})

    def test_to_internal_value(self):
        instance = fields.JSONField()
        self.assertEqual(
            instance.to_internal_value({'key': [0.0, 1, [2, 'nested', {}]]}),
            {'key': [0.0, 1, [2, 'nested', {}]]}
        )

    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        instance = fields.JSONField()

        with self.assertRaises(ValidationError):
            instance.to_internal_value(set())

    def test_to_representation(self):
        instance = fields.JSONField()
        self.assertEqual(
            instance.to_representation({'key': [0.0, 1, [2, 'nested', {}]]}),
            {'key': [0.0, 1, [2, 'nested', {}]]}
        )

    # binary JSON

    def test_run_validation_raises_validation_error_for_binary_json(self):
        instance = fields.JSONField(binary=True)

        with self.assertRaises(ValidationError):
            instance.run_validation("{'key': \"str)")

    def test_to_internal_value_for_binary_json(self):
        instance = fields.JSONField(binary=True)
        self.assertEqual(
            instance.to_internal_value(b'{"key": [0.0, 1, [2, {}]]}'),
            {"key": [0.0, 1, [2, {}]]}
        )

    def test_to_representation_for_binary_json(self):
        instance = fields.JSONField(binary=True)
        self.assertEqual(
            instance.to_representation({'key': [0.0, 1, [2, {}]]}),
            b'{"key": [0.0, 1, [2, {}]]}'
        )


class TestModelField(unittest.TestCase):

    def test_get_attribute(self):
        instance = fields.ModelField(fields.IntegerField())
        self.assertEqual(instance.get_attribute(10), 10)

    def test_to_internal_value_raises_not_implemented_error(self):
        instance = fields.ModelField(fields.IntegerField())

        with self.assertRaises(NotImplementedError):
            instance.to_internal_value(10)

    def test_to_representation_raises_not_implemented_error(self):
        instance = fields.ModelField(fields.IntegerField())

        with self.assertRaises(NotImplementedError):
            instance.to_representation(10)


class TestSerializerMethodField(unittest.TestCase):

    class FakeModelSerializer(object):

        def get_none(self, obj):  # NOQA
            return {"key": "value"}

    def test_bind(self):
        model_serializer = self.FakeModelSerializer()
        instance = fields.SerializerMethodField()
        instance.bind('none', model_serializer)
        self.assertEqual(instance.parent, model_serializer)
        self.assertEqual(instance.method_name, 'get_none')

    def test_bind_raises_assertion_error_for_method_name_argument(self):
        model_serializer = self.FakeModelSerializer()
        instance = fields.SerializerMethodField(method_name='get_none')

        with self.assertRaises(AssertionError):
            instance.bind('none', model_serializer)

    def test_to_internal_value_raises_not_implemented_error(self):
        instance = fields.SerializerMethodField()

        with self.assertRaises(NotImplementedError):
            instance.to_internal_value({"key": "value"})

    def test_to_representation(self):
        model_serializer = self.FakeModelSerializer()
        instance = fields.SerializerMethodField()
        instance.bind('none', model_serializer)
        self.assertEqual(
            instance.to_representation(object()),
            {"key": "value"}
        )
