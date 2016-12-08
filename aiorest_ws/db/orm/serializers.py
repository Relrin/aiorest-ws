# -*- coding: utf-8 -*-
"""
This module contains base serializer classes for ORM models/objects. They
are similar to Forms and ModelForms from Django/Flask frameworks.
"""
import copy
from inspect import isclass
from collections import OrderedDict

from aiorest_ws.conf import settings
from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm.abstract import AbstractSerializer, AbstractField, \
    empty, SkipField
from aiorest_ws.db.orm.fields import *  # NOQA
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.fields import set_value, get_attribute
from aiorest_ws.utils.functional import cached_property
from aiorest_ws.utils.representation import serializer_repr, list_repr
from aiorest_ws.utils.serializer_helpers import ReturnDict, ReturnList, \
    BoundField, BindingDict, NestedBoundField

__all__ = (
    'BaseSerializer', 'SerializerMetaclass', 'Serializer',
    'raise_errors_on_nested_writes', 'ListSerializer', 'ModelSerializer',
    'HyperlinkedModelSerializerMixin', 'LIST_SERIALIZER_KWARGS',
    'VALID_FIELD_KWARGS', 'ALL_FIELDS',
)

LIST_SERIALIZER_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'instance', 'data', 'partial', 'context', 'allow_null'
)
VALID_FIELD_KWARGS = {
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'validators',
    'allow_null', 'allow_blank', 'choices'
}
ALL_FIELDS = '__all__'


class BaseSerializer(AbstractSerializer):
    """
    The BaseSerializer class provides a minimal class which may be used
    for writing custom serializer implementations.

    Note that we strongly restrict the ordering of operations/properties
    that may be used on the serializer in order to enforce correct usage.

    In particular, if a `data=` argument is passed then:

    .is_valid() - Available.
    .initial_data - Available.
    .validated_data - Only available after calling `is_valid()`
    .errors - Only available after calling `is_valid()`
    .data - Only available after calling `is_valid()`

    If a `data=` argument is not passed then:

    .is_valid() - Not available.
    .initial_data - Not available.
    .validated_data - Not available.
    .errors - Not available.
    .data - Available.
    """
    default_list_serializer = None  # override to your ListSerializer

    def __init__(self, instance=None, data=empty, **kwargs):
        self.instance = instance
        if data is not empty:
            self.initial_data = data
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        kwargs.pop('many', None)
        super(BaseSerializer, self).__init__(**kwargs)

    def __new__(cls, *args, **kwargs):
        # We override this method in order to automatically create
        # `ListSerializer` classes instead when `many=True` is set
        if kwargs.pop('many', False):
            return cls.many_init(*args, **kwargs)
        return super(BaseSerializer, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method implements the creation of a `ListSerializer` parent
        class when `many=True` is used. You can customize it if you need to
        control which keyword arguments are passed to the parent, and which
        are passed to the child.

        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:

        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomListSerializer(*args, **kwargs)
        """
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
        }
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(
            meta, 'list_serializer_class', cls.default_list_serializer
        )
        if list_serializer_class is None:
            raise ImproperlyConfigured(
                "You must define `default_list_serializer` attribute for "
                "{cls} class before using this serializer for list of "
                "objects.".format(cls=cls)
            )
        return list_serializer_class(*args, **list_kwargs)

    @property
    def errors(self):
        if not hasattr(self, '_errors'):
            msg = 'You must call `.is_valid()` before ' \
                  'accessing `.errors`.'
            raise AssertionError(msg)
        return self._errors

    @property
    def validated_data(self):
        if not hasattr(self, '_validated_data'):
            msg = 'You must call `.is_valid()` before ' \
                  'accessing `.validated_data`.'
            raise AssertionError(msg)
        return self._validated_data

    @property
    def data(self):
        if hasattr(self, 'initial_data') and not hasattr(self, '_validated_data'):  # NOQA
            msg = (
                'When a serializer is passed a `data` keyword argument you '
                'must call `.is_valid()` before attempting to access the '
                'serialized `.data` representation.\n'
                'You should either call `.is_valid()` first, '
                'or access `.initial_data` instead.'
            )
            raise AssertionError(msg)

        if not hasattr(self, '_data'):
            if self.instance is not None and not getattr(self, '_errors', None):  # NOQA
                self._data = self.to_representation(self.instance)
            elif hasattr(self, '_validated_data') and not getattr(self, '_errors', None):  # NOQA
                self._data = self.to_representation(self.validated_data)
            else:
                self._data = self.get_initial()
        return self._data

    def to_internal_value(self, data):
        raise NotImplementedError('`to_internal_value()` must be implemented.')

    def to_representation(self, instance):
        raise NotImplementedError('`to_representation()` must be implemented.')

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` must be implemented.')

    def create(self, validated_data):
        raise NotImplementedError('`create()` must be implemented.')

    def save(self, **kwargs):
        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database "
            "then inspect 'serializer.validated_data' instead. You can also "
            "pass additional keyword arguments to 'save()' if you need to "
            "set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`. If "
            "you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, '`update()` did not return an object instance.'  # NOQA
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, '`create()` did not return an object instance.'  # NOQA

        return self.instance

    def is_valid(self, raise_exception=False):
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)


class SerializerMetaclass(type):
    """
    This metaclass sets a dictionary named `_declared_fields` on the class.
    Any instances of `Field` included as attributes on either the class
    or on any of its superclasses will be include in the `_declared_fields`
    dictionary.
    """
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        fields = [
            (field_name, attrs.pop(field_name))
            for field_name, obj in list(attrs.items())
            if isinstance(obj, (AbstractField, BaseSerializer))
        ]
        fields.sort(key=lambda x: x[1]._creation_counter)

        # If this class is subclass of another Serializer, then add that
        # Serializer's fields. Note that we loop over the bases in *reverse*.
        # This is necessary in order to maintain the correct order of fields
        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = list(base._declared_fields.items()) + fields

        return OrderedDict(fields)

    def __new__(cls, name, bases, attrs):
        attrs['_declared_fields'] = cls._get_declared_fields(bases, attrs)
        return super(SerializerMetaclass, cls).__new__(cls, name, bases, attrs)


class Serializer(BaseSerializer, metaclass=SerializerMetaclass):
    default_error_messages = {
        'invalid': u"Invalid data. Expected a dictionary, but got {datatype}."
    }

    @property
    def fields(self):
        """
        A dictionary of {field_name: field_instance}.
        """
        # `fields` is evaluated lazily. We do this to ensure that we don't
        # have issues importing modules that use ModelSerializers as fields,
        # even if app-loading stage has not yet run
        if not hasattr(self, '_fields'):
            self._fields = BindingDict(self)
            for key, value in self.get_fields().items():
                self._fields[key] = value
        return self._fields

    @cached_property
    def _writable_fields(self):
        return [
            field for field in self.fields.values()
            if (not field.read_only) or (field.default is not empty)
        ]

    @cached_property
    def _readable_fields(self):
        return [
            field for field in self.fields.values()
            if not field.write_only
        ]

    def get_fields(self):
        """
        Returns a dictionary of {field_name: field_instance}.
        """
        # Every new serializer is created with a clone of the field instances.
        # This allows users to dynamically modify the fields on a serializer
        # instance without affecting every other serializer class
        return copy.deepcopy(self._declared_fields)

    def get_validators(self):
        """
        Returns a list of validator callables.
        """
        # Used by the lazily-evaluated `validators` property
        meta = getattr(self, 'Meta', None)
        validators = getattr(meta, 'validators', None)
        return validators[:] if validators else []

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            return OrderedDict([
                (field_name, field.get_value(self.initial_data))
                for field_name, field in self.fields.items()
                if (field.get_value(self.initial_data) is not empty) and
                not field.read_only
            ])

        return OrderedDict([
            (field.field_name, field.get_initial())
            for field in self.fields.values()
            if not field.read_only
        ])

    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)

    def run_validation(self, data=empty):
        """
        Validate passed data.
        """
        raise NotImplementedError('`run_validation()` must be implemented.')

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, dict):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: [message]
            })

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(
                self, 'validate_' + field.field_name, None
            )
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is None:
                # We skip `to_representation` for `None` values so that
                # fields do not have to explicitly deal with that case
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def validate(self, attrs):
        return attrs

    def __repr__(self):
        return serializer_repr(self, indent=1)

    # The following are used for accessing `BoundField` instances on the
    # serializer, for the purposes of presenting a form-like API onto the
    # field values and field errors.

    def __iter__(self):
        for field in self.fields.values():
            yield self[field.field_name]

    def __getitem__(self, key):
        field = self.fields[key]
        value = self.data.get(key)
        error = self.errors.get(key) if hasattr(self, '_errors') else None
        if isinstance(field, Serializer):
            return NestedBoundField(field, value, error)
        return BoundField(field, value, error)

    @property
    def data(self):
        ret = super(Serializer, self).data
        return ReturnDict(ret, serializer=self)

    @property
    def errors(self):
        ret = super(Serializer, self).errors
        return ReturnDict(ret, serializer=self)


def raise_errors_on_nested_writes(method_name, serializer, validated_data):
    """
    Give explicit errors when users attempt to pass writable nested data.
    If we don't do this explicitly they'd get a less helpful error when
    calling `.save()` on the serializer.
    We don't *automatically* support these sorts of nested writes because
    there are too many ambiguities to define a default behavior.
    Eg. Suppose we have a `UserSerializer` with a nested profile. How should
    we handle the case of an update, where the `profile` relationship does
    not exist? Any of the following might be valid:
    * Raise an application error.
    * Silently ignore the nested part of the update.
    * Automatically create a profile instance.
    """

    # Ensure we don't have a writable nested field. For example:
    #
    # class UserSerializer(ModelSerializer):
    #     ...
    #     profile = ProfileSerializer()
    assert not any(
        isinstance(field, BaseSerializer) and
        (key in validated_data) and
        isinstance(validated_data[key], (list, dict))
        for key, field in serializer.fields.items()
    ), (
        'The `.{method_name}()` method does not support writable nested '
        'fields by default.\nWrite an explicit `.{method_name}()` method for '
        'serializer `{module}.{class_name}`, or set `read_only=True` on '
        'nested serializer fields.'.format(
            method_name=method_name,
            module=serializer.__class__.__module__,
            class_name=serializer.__class__.__name__
        )
    )

    # Ensure we don't have a writable dotted-source field. For example:
    #
    # class UserSerializer(ModelSerializer):
    #     ...
    #     address = serializer.CharField('profile.address')
    assert not any(
        '.' in field.source and
        (key in validated_data) and
        isinstance(validated_data[key], (list, dict))
        for key, field in serializer.fields.items()
    ), (
        'The `.{method_name}()` method does not support writable '
        'dotted-source fields by default.\nWrite an explicit `.{method_name}'
        '()` method for serializer `{module}.{class_name}`, or set '
        '`read_only=True` on dotted-source serializer fields.'.format(
            method_name=method_name,
            module=serializer.__class__.__module__,
            class_name=serializer.__class__.__name__
        )
    )


class ListSerializer(BaseSerializer):
    child = None
    many = True

    default_error_messages = {
        'not_a_list': u'Expected a list of items but got type "{input_type}".',
        'empty': u"This list may not be empty."
    }

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(self.child))
        self.allow_empty = kwargs.pop('allow_empty', True)
        assert self.child is not None, '`child` is a required argument.'
        assert not isclass(self.child), '`child` has not been instantiated.'
        super(ListSerializer, self).__init__(*args, **kwargs)
        self.child.bind(field_name='', parent=self)

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            return self.to_representation(self.initial_data)
        return []

    def get_value(self, dictionary):
        """
        Given the input dictionary, return the field value.
        """
        return dictionary.get(self.field_name, empty)

    def get_attribute(self, instance):
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

    def run_validation(self, data=empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        raise NotImplementedError('`run_validation()` must be implemented.')

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if not isinstance(data, list):
            message = self.error_messages['not_a_list'].format(
                input_type=type(data).__name__
            )
            raise ValidationError({
                settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: [message]
            })

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages['empty']
            raise ValidationError({
                settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: [message]
            })

        ret = []
        errors = []

        for item in data:
            try:
                validated = self.child.run_validation(item)
            except ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)
                errors.append({})

        if any(errors):
            raise ValidationError(errors)

        return ret

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        return [self.child.to_representation(item) for item in data]

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        raise NotImplementedError(
            "Serializers with many=True do not support multiple update by "
            "default, only multiple create. For updates it is unclear how to "
            "deal with insertions and deletions. If you need to support "
            "multiple update, use a `ListSerializer` class and override "
            "`.update()` so you can specify the behavior exactly."
        )

    def create(self, validated_data):
        return [self.child.create(attrs) for attrs in validated_data]

    def save(self, **kwargs):
        """
        Save and return a list of object instances.
        """
        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database "
            "then inspect 'serializer.validated_data' instead. You can also "
            "pass additional keyword arguments to 'save()' if you need to "
            "set extra attributes on the saved model instance. For example: "
            "'serializer.save(owner=request.user)'.'"
        )

        validated_data = [
            dict(list(attrs.items()) + list(kwargs.items()))
            for attrs in self.validated_data
        ]

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, '`update()` did not return an object instance.'  # NOQA
        else:
            self.instance = self.create(validated_data)
            assert self.instance is not None, '`create()` did not return an object instance.'  # NOQA

        return self.instance

    def __repr__(self):
        return list_repr(self, indent=1)

    @property
    def data(self):
        ret = super(ListSerializer, self).data
        return ReturnList(ret, serializer=self)

    @property
    def errors(self):
        ret = super(ListSerializer, self).errors
        if isinstance(ret, dict):
            return ReturnDict(ret, serializer=self)
        return ReturnList(ret, serializer=self)


class ModelSerializer(Serializer):
    """
    A `ModelSerializer` is just a regular `Serializer`, except that:
    * A set of default fields are automatically populated.
    * A set of default validators are automatically populated.
    * Default `.create()` and `.update()` implementations are provided.
    The process of automatically determining a set of serializer fields based
    on the model fields is reasonably complex, but you almost certainly don't
    need to dig into the implementation.
    If the `ModelSerializer` class *doesn't* generate the set of fields that
    you need you should either declare the extra/differing fields explicitly on
    the serializer class, or simply use a `Serializer` class.
    """
    serializer_field_mapping = {}  # override according with your ORM
    serializer_related_field = None  # override to your PrimaryKeyRelatedField
    serializer_related_to_field = None  # override to your SlugRelatedField
    serializer_url_field = None  # override to your HyperlinkedIdentityField
    serializer_choice_field = None  # override to your ChoiceField

    # The field name for hyperlinked identity fields. Defaults to 'url'.
    # You can modify this using the API setting.
    url_field_name = None

    def is_abstract_model(self, model):
        """
        Check the passed model is abstract.
        """
        raise NotImplementedError('`is_abstract_model()` must be implemented.')

    def get_field_info(self, model):
        """
        Get metadata about field in the passed model.
        """
        raise NotImplementedError('`get_field_info()` must be implemented.')

    # Default `create` and `update` behavior
    def create(self, validated_data):
        """
        Create object in the database, with the passed `validated_data`.
        """
        raise NotImplementedError('`create()` must be implemented.')

    def update(self, instance, validated_data):
        """
        Update existing object in database.
        """
        raise NotImplementedError('`create()` must be implemented.')

    def get_fields(self):
        """
        Return the dict of field names -> field instances that should be
        used for `self.fields` when instantiating the serializer.
        """
        if self.url_field_name is None:
            self.url_field_name = settings.REST_CONFIG['URL_FIELD_NAME']

        assert hasattr(self, 'Meta'), (
            'Class {serializer_class} missing "Meta" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )
        assert hasattr(self.Meta, 'model'), (
            'Class {serializer_class} missing "Meta.model" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )

        if self.is_abstract_model(self.Meta.model):
            raise ValueError('Cannot use ModelSerializer with Abstract Models.')  # NOQA

        declared_fields = copy.deepcopy(self._declared_fields)
        model = getattr(self.Meta, 'model')
        depth = getattr(self.Meta, 'depth', 0)

        if depth is not None:
            assert depth >= 0, "'depth' may not be negative."
            assert depth <= 10, "'depth' may not be greater than 10."

        # Retrieve metadata about fields & relationships on the model class
        info = self.get_field_info(model)
        field_names = self.get_field_names(declared_fields, info)

        # Determine any extra field arguments and hidden fields that
        # should be included
        extra_kwargs = self.get_extra_kwargs()
        extra_kwargs, hidden_fields = self.get_uniqueness_extra_kwargs(
            field_names, declared_fields, extra_kwargs
        )

        # Determine the fields that should be included on the serializer
        fields = OrderedDict()

        for field_name in field_names:
            # If the field is explicitly declared on the class then use that
            if field_name in declared_fields:
                fields[field_name] = declared_fields[field_name]
                continue

            # Determine the serializer field class and keyword arguments
            field_class, field_kwargs = self.build_field(
                field_name, info, model, depth
            )

            # Include any kwargs defined in `Meta.extra_kwargs`
            extra_field_kwargs = extra_kwargs.get(field_name, {})
            field_kwargs = self.include_extra_kwargs(
                field_kwargs, extra_field_kwargs
            )

            # Create the serializer field
            fields[field_name] = field_class(**field_kwargs)

        # Add in any hidden fields
        fields.update(hidden_fields)
        return fields

    def get_field_names(self, declared_fields, info):
        """
        Returns the list of all field names that should be created when
        instantiating this serializer class. This is based on the default
        set of fields, but also takes into account the `Meta.fields` or
        `Meta.exclude` options if they have been specified.
        """
        fields = getattr(self.Meta, 'fields', None)
        exclude = getattr(self.Meta, 'exclude', None)

        fields_are_specified = fields and fields != ALL_FIELDS
        if fields_are_specified and not isinstance(fields, (list, tuple)):
            raise TypeError(
                'The `fields` option must be a list or tuple or "__all__". '
                'Got %s.' % type(fields).__name__
            )

        if exclude and not isinstance(exclude, (list, tuple)):
            raise TypeError(
                'The `exclude` option must be a list or tuple. Got %s.' %
                type(exclude).__name__
            )

        assert not (fields and exclude), (
            "Cannot set both 'fields' and 'exclude' options on "
            "serializer {serializer_class}.".format(
                serializer_class=self.__class__.__name__
            )
        )

        if fields == ALL_FIELDS:
            fields = None

        if fields is not None:
            # Ensure that all declared fields have also been included in the
            # `Meta.fields` option

            # Do not require any fields that are declared a parent class,
            # in order to allow serializer subclasses to only include
            # a subset of fields
            required_field_names = set(declared_fields)
            for cls in self.__class__.__bases__:
                _declared_fields = getattr(cls, '_declared_fields', [])
                required_field_names -= set(_declared_fields)

            for field_name in required_field_names:
                assert field_name in fields, (
                    "The field '{field_name}' was declared on serializer "
                    "{serializer_class}, but has not been included in the "
                    "'fields' option.".format(
                        field_name=field_name,
                        serializer_class=self.__class__.__name__
                    )
                )

            return fields

        # Use the default set of field names if `Meta.fields` is not specified
        fields = self.get_default_field_names(declared_fields, info)

        if exclude is not None:
            # If `Meta.exclude` is included, then remove those fields
            for field_name in exclude:
                assert field_name in fields, (
                    "The field '{field_name}' was included on serializer "
                    "{serializer_class} in the 'exclude' option, but does "
                    "not match any model field.".format(
                        field_name=field_name,
                        serializer_class=self.__class__.__name__
                    )
                )
                fields.remove(field_name)

        return fields

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        raise NotImplementedError('`get_default_field_names()` must be '
                                  'implemented.')

    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Return a two tuple of (cls, kwargs) to build a serializer field with.
        """
        raise NotImplementedError('`build_field()` must be implemented.')

    def build_standard_field(self, *args, **kwargs):
        """
        Create regular model fields.
        """
        raise NotImplementedError('`build_standard_field()` must be '
                                  'implemented.')

    def build_relational_field(self, *args, **kwargs):
        """
        Create fields for forward and reverse relationships.
        """
        raise NotImplementedError('`build_relational_field()` must be '
                                  'implemented.')

    def build_nested_field(self, *args, **kwargs):
        """
        Create nested fields for forward and reverse relationships.
        """
        raise NotImplementedError('`build_nested_field()` must be '
                                  'implemented.')

    def build_property_field(self, *args, **kwargs):
        """
        Create a read only field for model methods and properties.
        """
        raise NotImplementedError('`build_property_field()` must be '
                                  'implemented.')

    def build_url_field(self, *args, **kwargs):
        """
        Create a field representing the object's own URL.
        """
        raise NotImplementedError('`build_url_field()` must be implemented.')

    def build_unknown_field(self, field_name, model_class):
        """
        Raise an error on any unknown fields.
        """
        raise ImproperlyConfigured(
            'Field name `%s` is not valid for model `%s`.' %
            (field_name, model_class.__name__)
        )

    def include_extra_kwargs(self, kwargs, extra_kwargs):
        """
        Include any 'extra_kwargs' that have been included for this field,
        possibly removing any incompatible existing keyword arguments.
        """
        if extra_kwargs.get('read_only', False):
            for attr in [
                'required', 'default', 'allow_blank', 'allow_null',
                'min_length', 'max_length', 'min_value', 'max_value',
                'validators', 'queryset'
            ]:
                kwargs.pop(attr, None)

        if extra_kwargs.get('default') and kwargs.get('required') is False:
            kwargs.pop('required')

        if extra_kwargs.get('read_only', kwargs.get('read_only', False)):
            # Read only fields should always omit the 'required' argument
            extra_kwargs.pop('required', None)

        kwargs.update(extra_kwargs)

        return kwargs

    def get_extra_kwargs(self):
        """
        Return a dictionary mapping field names to a dictionary of
        additional keyword arguments.
        """
        extra_kwargs = copy.deepcopy(getattr(self.Meta, 'extra_kwargs', {}))

        read_only_fields = getattr(self.Meta, 'read_only_fields', None)
        if read_only_fields is not None:
            for field_name in read_only_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs

    def get_uniqueness_extra_kwargs(self, field_names, declared_fields,
                                    extra_kwargs):
        """
        Return any additional field options that need to be included as a
        result of uniqueness constraints on the model. This is returned as
        a two-tuple of:
        ('dict of updated extra kwargs', 'mapping of hidden fields')
        """
        model = getattr(self.Meta, 'model')
        model_fields = self._get_model_fields(
            field_names, declared_fields, extra_kwargs
        )

        # Determine if we need any additional `HiddenField` or extra keyword
        # arguments to deal with `unique_for` dates that are required to
        # be in the input data in order to validate it
        unique_constraint_names = self._get_unique_constraint_names(
            model, model_fields, field_names
        )

        # Include each of "unique multiple columns" field names,
        # so long as all the field names are included on the serializer
        unique_constraint_names |= self._get_unique_together_constraints(
            model, model_fields, field_names
        )

        # Now we have all the field names that have uniqueness constraints
        # applied, we can add the extra 'required=...' or 'default=...'
        # arguments that are appropriate to these fields, or add a
        # `HiddenField` for it
        hidden_fields = {}
        uniqueness_extra_kwargs = {}

        for unique_constraint_name in unique_constraint_names:
            # Get the model field that is referred too
            unique_constraint_field = self._get_unique_field(
                model, unique_constraint_name
            )

            default = self._get_default_field_value(unique_constraint_field)

            if unique_constraint_name in model_fields:
                # The corresponding field is present in the serializer
                if default is empty:
                    field_kwargs = {'required': True}
                else:
                    field_kwargs = {'default': default}
                uniqueness_extra_kwargs[unique_constraint_name] = field_kwargs
            elif default is not empty:
                # The corresponding field is not present in the,
                # serializer. We have a default to use for it, so
                # add in a hidden field that populates it
                hidden_fields[unique_constraint_name] = HiddenField(default=default)  # NOQA

        # Update `extra_kwargs` with any new options
        for key, value in uniqueness_extra_kwargs.items():
            if key in extra_kwargs:
                extra_kwargs[key].update(value)
            else:
                extra_kwargs[key] = value

        return extra_kwargs, hidden_fields

    def _get_model_fields(self, field_names, declared_fields, extra_kwargs):
        """
        Returns all the model fields that are being mapped to by fields
        on the serializer class.
        Returned as a dict of 'model field name' -> 'model field'.
        Used internally by `get_uniqueness_field_options`.
        """
        model = getattr(self.Meta, 'model')
        model_fields = {}

        for field_name in field_names:
            if field_name in declared_fields:
                # If the field is declared on the serializer
                field = declared_fields[field_name]
                source = field.source or field_name
            else:
                try:
                    source = extra_kwargs[field_name]['source']
                except KeyError:
                    source = field_name

            if '.' in source or source == '*':
                # Model fields will always have a simple source mapping,
                # they can't be nested attribute lookups
                continue

            self._bind_field(model, source, model_fields)

        return model_fields

    def _get_unique_constraint_names(self, model, model_fields, field_names):
        """
        Return a set of field names, for each column unique constraint.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        raise NotImplementedError('`_get_unique_constraint_names()` '
                                  'must be implemented.')

    def _get_unique_together_constraints(self, model, model_fields, field_names):  # NOQA
        """
        Return a set of field names for a multiple unique constraints.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        raise NotImplementedError('`_get_unique_constraint_names()` '
                                  'must be implemented.')

    def _get_unique_field(self, model, unique_field_name):
        """
        Return a field by his name from a model.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        raise NotImplementedError('`_get_unique_field()` must be implemented.')

    def _get_default_field_value(self, unique_constraint_field):
        """
        Return a default value for a passed field.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        raise NotImplementedError('`_get_default_field_value()` '
                                  'must be implemented.')

    def _bind_field(self, model, source, model_fields):
        """
        Bind passed field to model serializer.
        Used internally by `_get_model_fields`.
        """
        raise NotImplementedError('`_bind_field()` must be implemented.')

    def get_validators(self):
        """
        Determine the set of validators to use when instantiating serializer.
        """
        meta = getattr(self, 'Meta', None)
        validators = getattr(meta, 'validators', None)
        return validators[:] if validators else []


class HyperlinkedModelSerializerMixin(object):
    """
    A type of `ModelSerializer` that uses hyperlinked relationships instead
    of primary key relationships. Specifically:
    * A 'url' field is included instead of the 'id' field.
    * Relationships to other instances are hyperlinks, instead of primary keys.
    """
    serializer_related_field = None  # override to your HyperlinkedRelatedField

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [self.url_field_name, ] +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.forward_relations.keys())
        )

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """
        raise NotImplementedError('`build_nested_field()` must be '
                                  'implemented.')
