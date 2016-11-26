# -*- coding: utf-8 -*-
"""
Default implementations of ORM column types.

This fields doesn't used with ORMs by default, like Django or SQLAlchemy ORM.
For every field which are provided by ORM, necessary to implement special
mixin class, which extract value from container.
"""
import datetime
import decimal
import inspect
import json
import collections
import copy
import re

from aiorest_ws.conf import settings
from aiorest_ws.db.orm import validators
from aiorest_ws.db.orm.abstract import AbstractField, SkipField, empty
from aiorest_ws.utils.encoding import force_text
from aiorest_ws.utils.date import humanize_datetime, timezone, dateparse
from aiorest_ws.utils.fields import to_choices_dict, flatten_choices_dict

__all__ = (
    'IntegerField', 'BigIntegerField', 'SmallIntegerField', 'BooleanField',
    'NullBooleanField', 'CharField', 'ChoiceField', 'FloatField',
    'LargeBinaryField', 'DecimalField', 'TimeField', 'DateField',
    'PickleField', 'DateTimeField', 'TimeDeltaField', 'ListField', 'DictField',
    'JSONField', 'HStoreField', 'ModelField', 'HiddenField',
    'CreateOnlyDefault', 'ReadOnlyField', 'SerializerMethodField',
    '_UnvalidatedField'
)


class IntegerField(AbstractField):
    default_error_messages = {
        'invalid': u"Passed value must be an integer.",
        'max_value': u"Ensure this value is less than or equal "
                     u"to {max_value}.",
        'min_value': u"Ensure this value is greater than or equal "
                     u"to {min_value}.",
        'max_string_length': u"String value too large."
    }
    MAX_STRING_LENGTH = 1000  # protect against extremely string inputs
    re_decimal = re.compile(r'\.0*$')  # allow to use .0 at the end of number

    def __init__(self, **kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(IntegerField, self).__init__(**kwargs)
        if self.max_value is not None:
            message = self.error_messages['max_value'].format(max_value=self.max_value)  # NOQA
            self.validators.append(validators.MaxValueValidator(self.max_value, message=message))  # NOQA
        if self.min_value is not None:
            message = self.error_messages['min_value'].format(min_value=self.min_value)  # NOQA
            self.validators.append(validators.MinValueValidator(self.min_value, message=message))  # NOQA

    def to_internal_value(self, data):
        if isinstance(data, str) and len(data) > self.MAX_STRING_LENGTH:
            self.raise_error('max_string_length')

        try:
            data = int(self.re_decimal.sub('', str(data)))
        except (ValueError, TypeError):
            self.raise_error('invalid')
        return data

    def to_representation(self, value):
        return int(value)


class BigIntegerField(IntegerField):
    MAX_BIG_INTEGER = 9223372036854775807

    def __init__(self, **kwargs):
        kwargs['min_value'] = -self.MAX_BIG_INTEGER - 1
        kwargs['max_value'] = self.MAX_BIG_INTEGER
        super(BigIntegerField, self).__init__(**kwargs)


class SmallIntegerField(IntegerField):
    MAX_SMALL_INTEGER = 32767

    def __init__(self, **kwargs):
        kwargs['min_value'] = -self.MAX_SMALL_INTEGER - 1
        kwargs['max_value'] = self.MAX_SMALL_INTEGER
        super(SmallIntegerField, self).__init__(**kwargs)


class BooleanField(AbstractField):
    default_error_messages = {
        'invalid': u'"{input}" is not a valid boolean."'
    }
    initial = False
    TRUE_VALUES = {'true', 'True', 'TRUE', '1', 1, True}
    FALSE_VALUES = {'false', 'False', 'FALSE', '0', 0, 0.0, False}

    def __init__(self, **kwargs):
        assert 'allow_null' not in kwargs, \
            '`allow_null` is not a valid option. ' \
            'Use `NullBooleanField` instead.'
        super(BooleanField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            if data in self.TRUE_VALUES:
                return True
            elif data in self.FALSE_VALUES:
                return False
        except TypeError:  # Input is an unhashable type
            pass
        self.raise_error('invalid', input=data)

    def to_representation(self, value):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        return bool(value)


class NullBooleanField(AbstractField):
    default_error_messages = {
        'invalid': u'"{input}" is not a valid boolean."'
    }
    initial = None
    TRUE_VALUES = {'true', 'True', 'TRUE', '1', 1, True}
    FALSE_VALUES = {'false', 'False', 'FALSE', '0', 0, 0.0, False}
    NULL_VALUES = {'null', 'Null', 'NULL', '', None}

    def __init__(self, **kwargs):
        kwargs['allow_null'] = True
        super(NullBooleanField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if data in self.TRUE_VALUES:
            return True
        elif data in self.FALSE_VALUES:
            return False
        elif data in self.NULL_VALUES:
            return None
        self.raise_error('invalid', input=data)

    def to_representation(self, value):
        if value in self.NULL_VALUES:
            return None
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        return bool(value)


class CharField(AbstractField):
    default_error_messages = {
        'blank': u"This field may not be blank.",
        'max_length': "Ensure this field has no more than "
                      "{max_length} characters.",
        'min_length': "Ensure this field has at least "
                      "{min_length} characters."
    }
    initial = ''

    def __init__(self, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        super(CharField, self).__init__(**kwargs)
        if self.max_length is not None:
            message = self.error_messages['max_length'].format(
                max_length=self.max_length
            )
            self.validators.append(
                validators.MaxLengthValidator(self.max_length, message=message)
            )
        if self.min_length is not None:
            message = self.error_messages['min_length'].format(
                min_length=self.min_length
            )
            self.validators.append(
                validators.MinLengthValidator(self.min_length, message=message)
            )

    def run_validation(self, data=empty):
        # Test for the empty string here so that it does not get validated,
        # and so that subclasses do not need to handle it explicitly inside
        # the `to_internal_value()` method
        if data == '' or (self.trim_whitespace and str(data).strip() == ''):
            if not self.allow_blank:
                self.raise_error('blank')
            return ''
        return super(CharField, self).run_validation(data)

    def to_internal_value(self, data):
        value = str(data)
        return value.strip() if self.trim_whitespace else value

    def to_representation(self, value):
        return str(value)


class ChoiceField(AbstractField):
    default_error_messages = {
        'invalid_choice': '"{input}" is not a valid choice.'
    }

    def __init__(self, choices, **kwargs):
        self.grouped_choices = to_choices_dict(choices)
        self.choices = flatten_choices_dict(self.grouped_choices)

        # Map the string representation of choices to the underlying value.
        # Allows us to deal with eg. integer choices while supporting either
        # integer or string input, but still get the correct datatype out
        self.choice_strings_to_values = {
            str(key): key for key in self.choices.keys()
        }

        self.allow_blank = kwargs.pop('allow_blank', False)
        super(ChoiceField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        try:
            return self.choice_strings_to_values[str(data)]
        except KeyError:
            self.raise_error('invalid_choice', input=data)

    def to_representation(self, value):
        if value in ('', None):
            return value
        return self.choice_strings_to_values.get(str(value), value)


class FloatField(AbstractField):
    default_error_messages = {
        'invalid': u"Passed value must be a float.",
        'max_value': u"Ensure this value is less than or equal "
                     u"to {max_value}.",
        'min_value': u"Ensure this value is greater than or equal "
                     u"to {min_value}.",
        'max_string_length': u"String value too large."
    }
    MAX_STRING_LENGTH = 1000  # protect against extremely string inputs

    def __init__(self, **kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(FloatField, self).__init__(**kwargs)
        if self.max_value is not None:
            message = self.error_messages['max_value'].format(
                max_value=self.max_value
            )
            self.validators.append(
                validators.MaxValueValidator(self.max_value, message=message)
            )
        if self.min_value is not None:
            message = self.error_messages['min_value'].format(
                min_value=self.min_value
            )
            self.validators.append(
                validators.MinValueValidator(self.min_value, message=message)
            )

    def to_internal_value(self, data):
        if isinstance(data, str) and len(data) > self.MAX_STRING_LENGTH:
            self.raise_error('max_string_length')

        try:
            return float(data)
        except (TypeError, ValueError):
            self.raise_error('invalid')

    def to_representation(self, value):
        return float(value)


class PickleField(AbstractField):
    default_error_messages = {
        'invalid': u"Passed value must be a bytes.",
    }

    def to_internal_value(self, data):
        if not isinstance(data, bytes):
            self.raise_error('invalid')
        return data

    def to_representation(self, value):
        return bytes(value)


class LargeBinaryField(AbstractField):
    default_error_messages = {
        'max_binary_length': u"Binary value too large."
    }

    def __init__(self, length=None, *args, **kwargs):
        self.length = length
        super(LargeBinaryField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if self.length and len(data) > self.length:
            self.raise_error('max_binary_length')

        return bytes(data, encoding='utf-8')

    def to_representation(self, value):
        return bytes(value, encoding='utf-8')


class TimeField(AbstractField):
    default_error_messages = {
        'invalid': u"Time has wrong format. Use one of these "
                   u"formats instead: {format}.",
    }
    datetime_parser = datetime.datetime.strptime

    def __init__(self, format=empty, input_formats=None, *args, **kwargs):
        if format is not empty:
            self.format = format
        if input_formats is not None:
            self.input_formats = input_formats
        super(TimeField, self).__init__(*args, **kwargs)

    def to_internal_value(self, value):
        input_formats = getattr(
            self, 'input_formats', settings.TIME_INPUT_FORMATS
        )

        if isinstance(value, datetime.time):
            return value

        for input_format in input_formats:
            if input_format.lower() == settings.ISO_8601:
                try:
                    parsed = dateparse.parse_time(value)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return parsed
            else:
                try:
                    parsed = self.datetime_parser(value, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return parsed.time()

        humanized_format = humanize_datetime.time_formats(input_formats)
        self.raise_error('invalid', format=humanized_format)

    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', settings.TIME_FORMAT)

        if output_format is None:
            return value

        # Applying a `TimeField` to a datetime value is almost always not a
        # sensible thing to do, as it means naively dropping any explicit or
        # implicit timezone info
        assert not isinstance(value, datetime.datetime), (
            'Expected a `time`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        if output_format.lower() == settings.ISO_8601:
            if isinstance(value, str):
                value = datetime.datetime.strptime(value, '%H:%M:%S').time()
            return value.isoformat()
        return value.strftime(output_format)


class DecimalField(AbstractField):
    default_error_messages = {
        'invalid': u"A valid number is required.",
        'max_value': u"Ensure this value is less than or equal "
                     u"to {max_value}.",
        'min_value': u"Ensure this value is greater than or equal "
                     u"to {min_value}.",
        'max_digits': u"Ensure that there are no more than {max_digits} "
                      u"digits in total.",
        'max_decimal_places': u"Ensure that there are no more than "
                              u"{max_decimal_places} decimal places.",
        'max_whole_digits': u"Ensure that there are no more than "
                            u"{max_whole_digits} digits before the "
                            u"decimal point.",
        'max_string_length': u"String value too large."
    }
    MAX_STRING_LENGTH = 1000  # Guard against malicious string inputs

    def __init__(self, max_digits, decimal_places, coerce_to_string=None,
                 max_value=None, min_value=None, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        if coerce_to_string is not None:
            self.coerce_to_string = coerce_to_string

        self.max_value = max_value
        self.min_value = min_value

        if self.max_digits is not None and self.decimal_places is not None:
            self.max_whole_digits = self.max_digits - self.decimal_places
        else:
            self.max_whole_digits = None

        super(DecimalField, self).__init__(**kwargs)

        if self.max_value is not None:
            message = self.error_messages['max_value'].format(
                max_value=self.max_value
            )
            self.validators.append(
                validators.MaxValueValidator(self.max_value, message=message)
            )
        if self.min_value is not None:
            message = self.error_messages['min_value'].format(
                min_value=self.min_value
            )
            self.validators.append(
                validators.MinValueValidator(self.min_value, message=message)
            )

    def to_internal_value(self, data):
        """
        Validate that the input is a decimal number and return a Decimal
        instance.
        """
        data = force_text(data).strip()
        if len(data) > self.MAX_STRING_LENGTH:
            self.raise_error('max_string_length')

        try:
            value = decimal.Decimal(data)
        except decimal.DecimalException:
            self.raise_error('invalid')

        # Check for NaN. It is the only value that isn't equal to itself,
        # so we can use this to identify NaN values.
        if value != value:
            self.raise_error('invalid')

        # Check for infinity and negative infinity.
        if value in (decimal.Decimal('Inf'), decimal.Decimal('-Inf')):
            self.raise_error('invalid')

        return self.validate_precision(value)

    def validate_precision(self, value):
        """
        Ensure that there are no more than max_digits in the number, and no
        more than decimal_places digits after the decimal point.
        Override this method to disable the precision validation for input
        values or to enhance it in any way you need to.
        """
        sign, digittuple, exponent = value.as_tuple()

        if exponent >= 0:
            # 1234500.0
            total_digits = len(digittuple) + exponent
            whole_digits = total_digits
            decimal_places = 0
        elif len(digittuple) > abs(exponent):
            # 123.45
            total_digits = len(digittuple)
            whole_digits = total_digits - abs(exponent)
            decimal_places = abs(exponent)
        else:
            # 0.001234
            total_digits = abs(exponent)
            whole_digits = 0
            decimal_places = total_digits

        if self.max_digits is not None and total_digits > self.max_digits:
            self.raise_error('max_digits', max_digits=self.max_digits)
        if self.decimal_places is not None and \
                decimal_places > self.decimal_places:
            self.raise_error(
                'max_decimal_places', max_decimal_places=self.decimal_places
            )
        if self.max_whole_digits is not None and \
                whole_digits > self.max_whole_digits:
            self.raise_error(
                'max_whole_digits', max_whole_digits=self.max_whole_digits
            )

        return value

    def to_representation(self, value):
        coerce_to_string = getattr(
            self, 'coerce_to_string', settings.COERCE_DECIMAL_TO_STRING
        )

        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value).strip())

        quantized = self.quantize(value)

        if not coerce_to_string:
            return quantized
        return '{0:f}'.format(quantized)

    def quantize(self, value):
        """
        Quantize the decimal value to the configured precision.
        """
        context = decimal.getcontext().copy()
        context.prec = self.max_digits
        return value.quantize(
            decimal.Decimal('.1') ** self.decimal_places,
            context=context
        )


class DateField(AbstractField):
    default_error_messages = {
        'invalid': u"Date has wrong format. Use one of these "
                   u"formats instead: {format}.",
        'datetime': u"Expected a date but got a datetime.",
    }
    datetime_parser = datetime.datetime.strptime

    def __init__(self, format=empty, input_formats=None, *args, **kwargs):
        if format is not empty:
            self.format = format
        if input_formats is not None:
            self.input_formats = input_formats
        super(DateField, self).__init__(*args, **kwargs)

    def to_internal_value(self, value):
        input_formats = getattr(
            self, 'input_formats', settings.DATE_INPUT_FORMATS
        )

        if isinstance(value, datetime.datetime):
            self.raise_error('datetime')

        if isinstance(value, datetime.date):
            return value

        for input_format in input_formats:
            if input_format.lower() == settings.ISO_8601:
                try:
                    parsed = dateparse.parse_date(value)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return parsed
            else:
                try:
                    parsed = self.datetime_parser(value, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return parsed.date()

        humanized_format = humanize_datetime.date_formats(input_formats)
        self.raise_error('invalid', format=humanized_format)

    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', settings.DATE_FORMAT)

        if output_format is None:
            return value

        # Applying a `DateField` to a datetime value is almost always not a
        # sensible thing to do, as it means naively dropping any explicit or
        # implicit timezone info
        assert not isinstance(value, datetime.datetime), (
            'Expected a `date`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        if output_format.lower() == settings.ISO_8601:
            if isinstance(value, str):
                value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            return value.isoformat()

        return value.strftime(output_format)


class DateTimeField(AbstractField):
    default_error_messages = {
        'invalid': u"Datetime has wrong format. Use one of these "
                   u"formats instead: {format}.",
        'date': u"Expected a datetime but got a date.",
    }
    datetime_parser = datetime.datetime.strptime

    def __init__(self, format=empty, input_formats=None, default_timezone=None,
                 *args, **kwargs):
        if format is not empty:
            self.format = format
        if input_formats is not None:
            self.input_formats = input_formats
        if default_timezone is not None:
            self.timezone = default_timezone
        super(DateTimeField, self).__init__(*args, **kwargs)

    def enforce_timezone(self, value):
        """
        When `self.timezone` is `None`, always return naive datetimes.
        When `self.timezone` is not `None`, always return aware datetimes.
        """
        field_timezone = getattr(self, 'timezone', self.default_timezone())

        if (field_timezone is not None) and not timezone.is_aware(value):
            return timezone.make_aware(value, field_timezone)
        elif (field_timezone is None) and timezone.is_aware(value):
            return timezone.make_naive(value, timezone.UTC())
        return value

    def default_timezone(self):
        return timezone.get_default_timezone() if settings.USE_TZ else None

    def to_internal_value(self, value):
        input_formats = getattr(
            self, 'input_formats', settings.DATETIME_INPUT_FORMATS
        )

        if isinstance(value, datetime.date) and \
                not isinstance(value, datetime.datetime):
            self.raise_error('date')

        if isinstance(value, datetime.datetime):
            return self.enforce_timezone(value)

        for input_format in input_formats:
            if input_format.lower() == settings.ISO_8601:
                try:
                    parsed = dateparse.parse_datetime(value)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return self.enforce_timezone(parsed)
            else:
                try:
                    parsed = self.datetime_parser(value, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return self.enforce_timezone(parsed)

        humanized_format = humanize_datetime.datetime_formats(input_formats)
        self.raise_error('invalid', format=humanized_format)

    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', settings.DATETIME_FORMAT)

        if output_format is None:
            return value

        if output_format.lower() == settings.ISO_8601:
            value = value.isoformat()
            if value.endswith('+00:00'):
                value = value[:-6] + 'Z'
            return value
        return value.strftime(output_format)


class TimeDeltaField(AbstractField):
    ACCEPTABLE_DISPLAY_TYPES = ["sql", "iso8601", "minimal", "short", "long"]
    default_error_messages = {
        'timedelta': u"Expected a string of the form '1w, 2d, 5h, 45m, 5s'",
    }

    def __init__(self, **kwargs):
        self.display = kwargs.pop("display", "long")
        self.separator = kwargs.pop("separator", ", ")

        assert self.display in self.ACCEPTABLE_DISPLAY_TYPES, (
            "Attribute `display` can take one of the following values: "
            "'sql, 'iso8601', 'minimal', 'short' or 'long'."
        )

        super(TimeDeltaField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            data = dateparse.parse_timedelta(data)
        except (AttributeError, TypeError):
            self.raise_error('timedelta', type=type(data))
        return data

    def to_representation(self, value):
        return humanize_datetime.humanize_timedelta(
            value, display=self.display, sep=self.separator
        )


class HiddenField(AbstractField):
    """
    A hidden field does not take input from the user, or present any output,
    but it does populate a field in `validated_data`, based on its default
    value. This is particularly useful when we have a `unique_for_date`
    constraint on a pair of fields, as we need some way to include the date in
    the validated data.
    """
    def __init__(self, **kwargs):
        assert 'default' in kwargs, 'default is a required argument.'
        kwargs['write_only'] = True
        super(HiddenField, self).__init__(**kwargs)

    def get_value(self, dictionary):
        # We always use the default value for `HiddenField` and user input
        # is never provided or accepted
        return empty

    def to_internal_value(self, data):
        return data


class CreateOnlyDefault(object):
    """
    This class may be used to provide default values that are only used
    for create operations, but that do not return any value for update
    operations.
    """
    def __init__(self, default):
        self.default = default

    def _can_set_context(self):
        return hasattr(self.default, 'set_context') and not self.is_update

    def set_context(self, serializer_field):
        self.is_update = serializer_field.parent.instance is not None
        if callable(self.default) and self._can_set_context():
            self.default.set_context(serializer_field)

    def __call__(self):
        if self.is_update:
            raise SkipField()
        elif callable(self.default):
            return self.default()
        return self.default

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.default)


class ReadOnlyField(AbstractField):
    """
    A read-only field that simply returns the field value.
    If the field is a method with no parameters, the method will be called
    and it's return value used as the representation.
    For example, the following would call `get_expiry_date()` on the object:

    class ExampleSerializer(Serializer):
        expiry_date = ReadOnlyField(source='get_expiry_date')
    """
    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super(ReadOnlyField, self).__init__(**kwargs)

    def to_representation(self, value):
        return value


class _UnvalidatedField(AbstractField):
    def __init__(self, *args, **kwargs):
        super(_UnvalidatedField, self).__init__(*args, **kwargs)
        self.allow_blank = True
        self.allow_null = True

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class ListField(AbstractField):
    child = _UnvalidatedField()
    initial = []
    default_error_messages = {
        'not_a_list': u'Expected a list of items but got type "{input_type}".',
        'empty': u"This list may not be empty."
    }

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(self.child))
        self.allow_empty = kwargs.pop('allow_empty', True)

        assert not inspect.isclass(self.child), (
            '`child` has not been instantiated.'
        )
        assert self.child.source is None, (
            "The `source` argument is not meaningful when applied to a "
            "`child=` field. Remove `source=` from the field declaration."
        )

        super(ListField, self).__init__(*args, **kwargs)
        self.child.bind(field_name='', parent=self)

    def get_value(self, dictionary):
        if self.field_name not in dictionary:
            if getattr(self.root, 'partial', False):
                return empty
        return dictionary.get(self.field_name, empty)

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if isinstance(data, str) or isinstance(data, collections.Mapping) \
                or not hasattr(data, '__iter__'):
            self.raise_error('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            self.raise_error('empty')
        return [self.child.run_validation(item) for item in data]

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return [
            self.child.to_representation(item) if item is not None else None
            for item in data
        ]


class DictField(AbstractField):
    child = _UnvalidatedField()
    initial = {}
    default_error_messages = {
        'not_a_dict': u'Expected a dictionary of items but got '
                      u'type "{input_type}".'
    }

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(self.child))

        assert not inspect.isclass(self.child), (
            '`child` has not been instantiated.'
        )
        assert self.child.source is None, (
            "The `source` argument is not meaningful when applied to "
            "a `child=` field. Remove `source=` from the field declaration."
        )

        super(DictField, self).__init__(*args, **kwargs)
        self.child.bind(field_name='', parent=self)

    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)

    def to_internal_value(self, data):
        """
        Dicts of native values <- Dicts of primitive datatypes.
        """
        if not isinstance(data, dict):
            self.raise_error('not_a_dict', input_type=type(data).__name__)
        return {
            str(key): self.child.run_validation(value)
            for key, value in data.items()
        }

    def to_representation(self, value):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return {
            str(key): self.child.to_representation(val) if val is not None else None  # NOQA
            for key, val in value.items()
        }


class HStoreField(DictField):
    """
    HStore field for PostgreSQL.
    """
    child = CharField(allow_blank=True)


class JSONField(AbstractField):
    """
    Special kind of field which is storing data in JSON format.
    """
    default_error_messages = {
        'invalid': u"Value must be valid JSON."
    }

    def __init__(self, *args, **kwargs):
        self.binary = kwargs.pop('binary', False)
        super(JSONField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            if self.binary:
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
            else:
                json.dumps(data)
        except (TypeError, ValueError):
            self.raise_error('invalid')
        return data

    def to_representation(self, value):
        if self.binary:
            value = json.dumps(value)
            if isinstance(value, str):
                value = bytes(value.encode('utf-8'))
        return value


class ModelField(AbstractField):
    """
    A generic field that can be used against an arbitrary model field.
    This is used by `ModelSerializer` when dealing with custom model fields,
    that do not have a serializer field to be mapped to.
    """
    def __init__(self, model_field, **kwargs):
        self.model_field = model_field
        super(ModelField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        raise NotImplementedError('`to_internal_value()` must be implemented.')

    def get_attribute(self, obj):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute
        return obj

    def to_representation(self, obj):
        raise NotImplementedError('`to_representation()` must be implemented.')


class SerializerMethodField(AbstractField):
    """
    A read-only field that get its representation from calling a method on the
    parent serializer class. The method called will be of the form
    "get_{field_name}", and should take a single argument, which is the
    object being serialized. For example:

    class ExampleSerializer(ModelSerializer):
        extra_info = SerializerMethodField()
        def get_extra_info(self, obj):
            return ...  # Calculate some data to return
    """
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super(SerializerMethodField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        # In order to enforce a consistent style, we error if a redundant
        # 'method_name' argument has been used. For example:
        # my_field = serializer.CharField(source='my_field')
        default_method_name = 'get_{field_name}'.format(field_name=field_name)
        assert self.method_name != default_method_name, (
            "It is redundant to specify `%s` on SerializerMethodField '%s' in "
            "serializer '%s', because it is the same as the default method "
            "name. Remove the `method_name` argument." %
            (self.method_name, field_name, parent.__class__.__name__)
        )

        # The method name should default to `get_{field_name}`
        if self.method_name is None:
            self.method_name = default_method_name

        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value)
