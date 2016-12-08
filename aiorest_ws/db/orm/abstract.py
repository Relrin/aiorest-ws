# -*- coding: utf-8 -*-
"""
Base serialize classes for support serialize any ORM objects.

All this classes are based on serializers from Django REST framework. Original
code published under BSD license. For more details look into AUTHORS file.
"""
import copy
from abc import abstractmethod

from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.fields import get_attribute
from aiorest_ws.utils.functional import cached_property

__all__ = (
    'ERROR_MESSAGE_NOT_FOUND', 'SkipField', 'empty', 'AbstractSerializer',
    'AbstractField',
)

ERROR_MESSAGE_NOT_FOUND = (
    u'Key `{key}` not found in the `error_messages` dictionary.'
)


class empty(object):
    """
    This class is wrapper, which used to understand, passed to validators
    `empty` value or not.
    It is required, because we can take collisions in situations, when
    user passed `None` value to some function, which means that necessary
    to set `None` value for field of model.
    """
    pass


class SkipField(Exception):
    """
    This class used in situations, when necessary to skip specified field. For
    example, it can be partial updates.
    """
    pass


class AbstractSerializer(object):
    """
    Base abstract class for serialize ORM object to dictionary object.

    This class provide few methods, which will be helpful when implementing
    custom serializers for concrete ORM engine.
    """
    _creation_counter = 0
    default_error_messages = {
        'required': u"This field is required.",
        'null': u"This field doesn't accept null values."
    }
    default_validators = []
    initial = None

    def __init__(self, read_only=False, write_only=False, required=None,
                 default=empty, initial=empty, source=None, label=None,
                 error_messages=None, validators=None, allow_null=False):
        self._creation_counter = AbstractField._creation_counter
        AbstractField._creation_counter += 1

        self.read_only = read_only
        self.write_only = write_only
        self.required = required
        self.default = default
        self.source = source
        self.initial = self.initial if (initial is empty) else initial
        self.label = label
        self.allow_null = allow_null

        # Set `required` by default to `True` value, unless specified
        if self.required is None:
            self.required = self.default is empty and not self.read_only

        # Make a copy of validators for concrete field
        if validators is not None:
            self._validators = validators[:]

        # These attributes using in set up of `bind()` method, when field
        # is bonded with model serializer
        self.field_name = None
        self.parent = None

        # Build dictionary with errors, which based on the
        # `default_error_messages` attribute of every class in hierarchy
        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def __new__(cls, *args, **kwargs):
        """
        When a field is instantiated, we store the arguments that were used,
        so that we can present a helpful representation of the object.
        """
        instance = super(AbstractSerializer, cls).__new__(cls)
        instance._args = args
        instance._kwargs = kwargs
        return instance

    def __deepcopy__(self, memo):
        """
        When cloning fields we instantiate using the arguments it was
        originally created with, rather than copying the complete state.
        """
        args = copy.deepcopy(self._args)
        kwargs = dict(self._kwargs)
        validators = kwargs.pop('validators', None)
        kwargs = copy.deepcopy(kwargs)
        if validators is not None:
            kwargs['validators'] = validators
        return self.__class__(*args, **kwargs)

    def bind(self, field_name, parent):
        """
        Initializes the field name and parent for the field instance.
        Called when a field is added to the parent serializer instance.

        :param field_name: string, which describe field name of model.
        :param parent: object, which store this instance of class.
        """
        self.field_name = field_name
        self.parent = parent

        # `self.label` should default to being based on the field name
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()

        # `self.source` field using for getting value from object of ORM model
        if self.source is None:
            self.source = field_name

        # `self.source_attrs` is a list of attributes that need to be looked
        # up when serializing the instance, or populating the validated data
        if self.source == '*':
            self.source_attrs = []
        else:
            self.source_attrs = self.source.split('.')

    @cached_property
    def root(self):
        """
        Returns the top-level serializer for this field.
        """
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @cached_property
    def context(self):
        """
        Returns the context as passed to the root serializer on initialization.
        """
        return getattr(self.root, '_context', {})

    @property
    def validators(self):
        """
        Return list of used validators for specified field.
        """
        if not hasattr(self, '_validators'):
            self._validators = self.get_validators()
        return self._validators

    @validators.setter
    def validators(self, validators):
        """
        Setter for validator attribute.

        :param validators: list of validators, which necessary to use.
        """
        self._validators = validators

    @abstractmethod
    def get_default(self):
        """
        Returns the default value when validating data not specified.
        """
        pass

    @abstractmethod
    def get_value(self, dictionary):
        """
        Returns the value from passed incoming data (dictionary object), which
        will be validated and converted to a native value.

        :param dictionary: dictionary, which represented as serialized object.
        """
        pass

    @abstractmethod
    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.

        :param instance: object, from which value will have taken.
        """
        pass

    @abstractmethod
    def to_internal_value(self, data):
        """
        Convert primitive data to native value.

        :param data: object, which necessary to convert to native value.
        """
        pass

    @abstractmethod
    def to_representation(self, value):
        """
        Convert the native value into primitive data.

        :param value: object, which necessary to convert into primitive data.
        """
        pass

    def get_validators(self):
        """
        Return a list copy of validators for current field.
        """
        return self.default_validators[:]

    def get_initial(self):
        """
        Return a value to use when the field is being returned as a primitive
        value, without any object instance.
        """
        return self.initial

    def validate_empty_values(self, data):
        """
        Validate empty values, and either:
        * Raise `ValidationError`, indicating invalid data.
        * Raise `SkipField`, indicating that the field should be ignored for
          partial object update.
        * Return (True, data), indicating an empty value and not necessary
          to apply any further validation.
        * Return (False, data), indicating a result, when have taken data
          must be validated in future.

        :param data: object, required for processing.
        """
        if self.read_only:
            return True, self.get_default()

        if data is empty:
            if getattr(self.root, 'partial', False):
                raise SkipField()
            if self.required:
                self.raise_error('required')
            return True, self.get_default()

        if data is None:
            if not self.allow_null:
                self.raise_error('null')
            return True, None

        return False, data

    def run_validators(self, value):
        """
        Check the given value through all validators for the specified field.

        :param value: value, required for processing.
        """
        errors = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as exc:
                errors.extend(exc.detail)
        if errors:
            raise ValidationError(errors)

    def run_validation(self, data=empty):
        """
        Validate a simple representation and return the internal value.
        The provided data may be `empty` if no representation was included
        in the input.

        :param data: object, which necessary to validate.
        """
        is_empty_value, data = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)
        self.run_validators(value)
        return value

    def raise_error(self, key, **kwargs):
        """
        Helper function, that raise validation error with taken message.

        :param key: key for dictionary, by which selected concrete message.
        :param kwargs: dictionary object, which store additional arguments.
        """
        try:
            msg = self.error_messages[key]
        except KeyError:
            msg = ERROR_MESSAGE_NOT_FOUND.format(key=key)
            raise AssertionError(msg)
        message = msg.format(**kwargs)
        raise ValidationError(message)


class AbstractField(AbstractSerializer):
    """
    Base abstract class for model field classes.
    """
    def get_default(self):
        """
        Return the default value to use when validating data if no input
        is provided for this field.

        If a default has not been set for this field then this will simply
        return `empty`, indicating that no value should be set in the validated
        data for this field.
        """
        if self.default is empty:
            raise SkipField()
        return self.default

    def get_value(self, dictionary):
        """
        Returns the value from passed incoming data (dictionary object), which
        will be validated and converted to a native value.

        :param dictionary: dictionary, which represented as serialized object.
        """
        return dictionary.get(self.field_name, empty)

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.

        :param instance: object, from which value will have taken.
        """
        try:
            return get_attribute(instance, self.source_attrs)
        except (KeyError, AttributeError) as exc:
            if not self.required and self.default is empty:
                raise SkipField()
            msg = (
                'Got {exc_type} when attempting to get a value for field '
                '`{field}` on serializer `{serializer}`.\nThe serializer '
                'field might be named incorrectly and not match '
                'any attribute or key on the `{instance}` instance.\n'
                'Original exception text was: {exc}.'.format(
                    exc_type=type(exc).__name__,
                    field=self.field_name,
                    serializer=self.parent.__class__.__name__,
                    instance=instance.__class__.__name__,
                    exc=exc
                )
            )
            raise type(exc)(msg)

    def to_internal_value(self, data):
        """
        Convert primitive data to native value.

        :param value: object, which necessary to convert to native value.
        """
        raise NotImplementedError(
            '{cls}.to_internal_value() must be implemented.'.format(
                cls=self.__class__.__name__
            )
        )

    def to_representation(self, value):
        """
        Convert the native value into primitive data.

        :param value: object, which necessary to convert into primitive data.
        """
        raise NotImplementedError(
            '{cls}.to_representation() must be implemented for field '
            '{field_name}. If you do not need to support write operations '
            'you are able to use subclass `ReadOnlyField` instead.'.format(
                cls=self.__class__.__name__,
                field_name=self.field_name,
            )
        )
