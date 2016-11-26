# -*- coding: utf-8 -*-
"""
Universal validators for ORM fields, which applied before commit into DB.

This gives us better separation of concerns, allows us to use single-step
object creation, and makes it possible to switch between using the implicit
`ModelSerializer` class and an equivalent explicit `Serializer` class.
"""
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.representation import smart_repr

__all__ = (
    'BaseValidator', 'MaxValueValidator', 'MinValueValidator',
    'MaxLengthValidator', 'MinLengthValidator', 'EnumValidator',
    'BaseUniqueFieldValidator',
)


class BaseValidator(object):
    message = None
    code = None

    def __init__(self, *args, **kwargs):
        """
        Constructor for BaseValidator.

        :param message: string, which used as a message, when validation
        has fault.
        :param code: error code
        """
        self.message = kwargs.get('message', self.message)
        self.code = kwargs.get('code', self.code)

    def __call__(self, value):
        raise NotImplementedError('`__call__(self, value)` method must '
                                  'be implemented.')

    def __eq__(self, other):
        return (
            isinstance(other, BaseValidator) and
            (self.message == other.message) and
            (self.code == other.code)
        )


class MaxValueValidator(BaseValidator):
    """
    Validator for checking maximal value of input number.
    """
    message = u"Ensure this value is less than or equal to {max_value}."

    def __init__(self, max_value, *args, **kwargs):
        super(MaxValueValidator, self).__init__(*args, **kwargs)
        self.max_value = max_value
        if self.max_value is None:
            raise ValueError('Attribute `max_value` can not be NoneType.')

    def __call__(self, value):
        if value > self.max_value:
            message = self.message.format(max_value=self.max_value)
            raise ValidationError(message)


class MinValueValidator(BaseValidator):
    """
    Validator for checking minimal value of input number.
    """
    message = u"Ensure this value is greater than or equal to {min_value}."

    def __init__(self, min_value, *args, **kwargs):
        super(MinValueValidator, self).__init__(*args, **kwargs)
        self.min_value = min_value
        if self.min_value is None:
            raise ValueError('Attribute `min_value` can not be NoneType.')

    def __call__(self, value):
        if value < self.min_value:
            message = self.message.format(min_value=self.min_value)
            raise ValidationError(message)


class MaxLengthValidator(BaseValidator):
    """
    Validator for checking maximum length of input string.
    """
    message = u"Ensure that this value has no more {max_length} characters."

    def __init__(self, max_length, *args, **kwargs):
        super(MaxLengthValidator, self).__init__(*args, **kwargs)
        self.max_length = max_length
        if self.max_length and self.max_length < 0:
            raise ValueError('Attribute `max_length` can take only positive '
                             'numbers.')

    def __call__(self, value):
        if self.max_length and len(value) > self.max_length:
            message = self.message.format(max_length=self.max_length)
            raise ValidationError(message)


class MinLengthValidator(BaseValidator):
    """
    Validator for checking minimum length of input string.
    """
    message = u"Ensure that this value has minimum {min_length} characters."

    def __init__(self, min_length, *args, **kwargs):
        super(MinLengthValidator, self).__init__(*args, **kwargs)
        self.min_length = min_length
        if self.min_length and self.min_length < 0:
            raise ValueError('Attribute `min_length` can take only positive '
                             'numbers.')

    def __call__(self, value):
        if self.min_length and len(value) < self.min_length:
            message = self.message.format(min_length=self.min_length)
            raise ValidationError(message)


class EnumValidator(BaseValidator):
    """
    Validator for checking input keys of passed Enum.
    """
    message = u"Ensure that passed value is one of the allowable: {key_list}."

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        super(EnumValidator, self).__init__(*args, **kwargs)

    @property
    def keys(self):
        return [member for member in self.enum.__members__]

    def is_enum_key(self, value):
        return value in self.keys

    def __call__(self, value):
        if not self.is_enum_key(value):
            message = self.message.format(key_list=self.keys)
            raise ValidationError(message)


class BaseUniqueFieldValidator(BaseValidator):
    """
    Validator that corresponds to `unique=True` on a model field.
    Should be applied to an individual field on the serializer.
    """
    message = u"This field must be unique."

    def __init__(self, queryset, message=None):
        super(BaseUniqueFieldValidator, self).__init__(message=self.message)
        self.queryset = queryset
        self.serializer_field = None
        self.message = message or self.message

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.field_name = serializer_field.source_attrs[0]
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer_field.parent, 'instance', None)

    def filter_queryset(self, value, queryset):
        raise NotImplementedError('`filter_queryset()` must be implemented.')

    def exclude_current_instance(self, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict.
        """
        raise NotImplementedError('`exclude_current_instance()` must be '
                                  'implemented.')

    def __call__(self, attrs):
        raise NotImplementedError('`__call__` must be implemented.')

    def __repr__(self):
        return "<%s(queryset=%s)>" % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        )
