# -*- coding: utf-8 -*-
"""
List, model and hyperlinked serializer classes for Django ORM.

As you can see there, we are inherited from all base classes and implement
logic according to the work of SQLAlchemy ORM. For the most situations using
ModelSerializer class will be enough.
"""
import traceback

from aiorest_ws.conf import settings
from aiorest_ws.db.orm.abstract import empty
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.serializers import \
    ListSerializer as BaseListSerializer, \
    ModelSerializer as BaseModelSerializer, HyperlinkedModelSerializerMixin, \
    raise_errors_on_nested_writes
from aiorest_ws.db.orm.django import model_meta
from aiorest_ws.db.orm.django.compat import postgres_fields, \
    JSONField as ModelJSONField
from aiorest_ws.db.orm.django.field_mapping import get_field_kwargs, \
    get_nested_relation_kwargs, get_relation_kwargs, get_url_kwargs
from aiorest_ws.utils.field_mapping import ClassLookupDict

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.db.models import DurationField as ModelDurationField
from django.db.models.fields import Field as DjangoModelField
from django.db.models.fields import FieldDoesNotExist
from django.utils import timezone

from aiorest_ws.db.orm.django.fields import *  # NOQA
from aiorest_ws.db.orm.django.relations import *  # NOQA

__all__ = (
    'get_validation_error_detail', 'ListSerializer', 'ModelSerializer',
    'HyperlinkedModelSerializer',
)


def get_validation_error_detail(exc):
    assert isinstance(exc, (ValidationError, DjangoValidationError))

    if isinstance(exc, DjangoValidationError):
        # Normally you should raise `serializers.ValidationError`
        # inside your codebase, but we handle Django's validation
        # exception class as well for simpler compat.
        # Eg. Calling Model.clean() explicitly inside Serializer.validate()
        return {settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: exc.args}
    elif isinstance(exc.detail, dict):
        # If errors may be a dict we use the standard {key: list of values}.
        # Here we ensure that all the values are *lists* of errors.
        return {
            key: value if isinstance(value, (list, dict)) else [value]
            for key, value in exc.detail.items()
        }
    elif isinstance(exc.detail, list):
        # Errors raised as a list are non-field errors.
        return {settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: exc.detail}
    # Errors raised as a string are non-field errors.
    return {settings.REST_CONFIG['NON_FIELD_ERRORS_KEY']: [exc.detail]}


class ListSerializer(BaseListSerializer):

    def run_validation(self, data=empty):
        """
            We override the default `run_validation`, because the validation
            performed by validators and the `.validate()` method should
            be coerced into an error dictionary with a 'non_fields_error' key.
            """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'  # NOQA
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=get_validation_error_detail(exc))

        return value


class ModelSerializer(BaseModelSerializer):
    """
    Base serializer for Django models.

    This class automatically generate "scheme" for further serializing and
    de-serializing data, according to used model, which is specified by user.
    For indicated fields by programmer, ModelSerializer will not apply "scheme
    construction rule". They are will have skipped while processing. Otherwise,
    for every field which is not pre-defined by user, will be found the most
    suitable and compatible field class.
    """
    serializer_field_mapping = {
        models.AutoField: IntegerField,
        models.BigIntegerField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.CommaSeparatedIntegerField: CharField,
        models.DateField: DateField,
        models.DateTimeField: DateTimeField,
        models.DecimalField: DecimalField,
        models.EmailField: EmailField,
        models.Field: ModelField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: ImageField,
        models.IntegerField: IntegerField,
        models.NullBooleanField: NullBooleanField,
        models.PositiveIntegerField: IntegerField,
        models.PositiveSmallIntegerField: IntegerField,
        models.SlugField: SlugField,
        models.SmallIntegerField: IntegerField,
        models.TextField: CharField,
        models.TimeField: TimeField,
        models.URLField: URLField,
        models.GenericIPAddressField: IPAddressField,
        models.FilePathField: FilePathField,
    }
    if ModelDurationField is not None:
        serializer_field_mapping[ModelDurationField] = DurationField
    if ModelJSONField is not None:
        serializer_field_mapping[ModelJSONField] = JSONField
    serializer_related_field = PrimaryKeyRelatedField
    serializer_related_to_field = SlugRelatedField
    serializer_url_field = HyperlinkedIdentityField
    serializer_choice_field = ChoiceField
    default_list_serializer = ListSerializer

    def is_abstract_model(self, model):
        """
        Check the passed model is abstract.
        """
        return model_meta.is_abstract_model(model)

    def get_field_info(self, model):
        """
        Get metadata about field in the passed model.
        """
        return model_meta.get_field_info(model)

    # Default `create` and `update` behavior...
    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.add(*value)
            instance.save()

        return instance

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def run_validation(self, data=empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        for field in self.fields.values():
            for validator in field.validators:
                if hasattr(validator, 'set_context'):
                    validator.set_context(field)

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() should return the ' \
                                      'validated data'
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=get_validation_error_detail(exc))

        return value

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [model_info.pk.name] +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.forward_relations.keys())
        )

    def _get_unique_constraint_names(self, model, model_fields, field_names):
        """
        Return a set of field names, for each column unique constraint.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        unique_constraint_names = set()

        for model_field in model_fields.values():
            # Include each of the `unique_for_*` field names
            unique_constraint_names |= {
                model_field.unique_for_date, model_field.unique_for_month,
                model_field.unique_for_year
            }

        unique_constraint_names -= {None}
        return unique_constraint_names

    def _get_unique_together_constraints(self, model, model_fields, field_names):  # NOQA
        """
        Return a set of field names for a multiple unique constraints.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        unique_constraint_names = set()

        for parent_class in [model] + list(model._meta.parents.keys()):
            for unique_together_list in parent_class._meta.unique_together:
                if set(field_names).issuperset(set(unique_together_list)):
                    unique_constraint_names |= set(unique_together_list)

        return unique_constraint_names

    def _get_unique_field(self, model, unique_field_name):
        """
        Return a field by his name from a model.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        return model._meta.get_field(unique_field_name)

    def _get_default_field_value(self, unique_constraint_field):
        """
        Return a default value for a passed field.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        default = empty

        if getattr(unique_constraint_field, 'auto_now_add', None):
            default = CreateOnlyDefault(timezone.now)
        elif getattr(unique_constraint_field, 'auto_now', None):
            default = timezone.now
        elif unique_constraint_field.has_default():
            default = unique_constraint_field.default

        return default

    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Create regular model fields.
        """
        if field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            return self.build_standard_field(field_name, model_field)

        elif field_name in info.relations:
            relation_info = info.relations[field_name]
            if not nested_depth:
                return self.build_relational_field(field_name, relation_info)
            else:
                return self.build_nested_field(
                    field_name, relation_info, nested_depth
                )

        elif hasattr(model_class, field_name):
            return self.build_property_field(field_name, model_class)

        elif field_name == self.url_field_name:
            return self.build_url_field(field_name, model_class)

        return self.build_unknown_field(field_name, model_class)

    def build_standard_field(self, *args, **kwargs):
        """
        Create regular model fields.
        """
        field_name, model_field = args
        field_mapping = ClassLookupDict(self.serializer_field_mapping)

        field_class = field_mapping[model_field]
        field_kwargs = get_field_kwargs(field_name, model_field)

        if 'choices' in field_kwargs:
            # Fields with choices get coerced into `ChoiceField`
            # instead of using their regular typed field
            field_class = self.serializer_choice_field
            # Some model fields may introduce kwargs that would not be valid
            # for the choice field. We need to strip these out
            valid_kwargs = {
                'read_only', 'write_only',
                'required', 'default', 'initial', 'source',
                'label', 'help_text', 'style',
                'error_messages', 'validators', 'allow_null', 'allow_blank',
                'choices'
            }
            for key in list(field_kwargs.keys()):
                if key not in valid_kwargs:
                    field_kwargs.pop(key)

        if not issubclass(field_class, ModelField):
            # `model_field` is only valid for the fallback case of
            # `ModelField`, which is used when no other typed field
            # matched to the model field
            field_kwargs.pop('model_field', None)

        if not issubclass(field_class, CharField) and not issubclass(field_class, ChoiceField):  # NOQA
            # `allow_blank` is only valid for textual fields
            field_kwargs.pop('allow_blank', None)

        if postgres_fields and isinstance(model_field, postgres_fields.ArrayField):  # NOQA
            # Populate the `child` argument on `ListField` instances generated
            # for the PostgreSQL specific `ArrayField`
            child_model_field = model_field.base_field
            child_field_class, child_field_kwargs = self.build_standard_field(
                'child', child_model_field
            )
            field_kwargs['child'] = child_field_class(**child_field_kwargs)

        return field_class, field_kwargs

    def build_relational_field(self, *args, **kwargs):
        """
        Create fields for forward and reverse relationships.
        """
        field_name, relation_info = args
        field_class = self.serializer_related_field
        field_kwargs = get_relation_kwargs(field_name, relation_info)

        to_field = field_kwargs.pop('to_field', None)
        if to_field and not relation_info.related_model._meta.get_field(to_field).primary_key:  # NOQA
            field_kwargs['slug_field'] = to_field
            field_class = self.serializer_related_to_field

        # `view_name` is only valid for hyperlinked relationships
        if not issubclass(field_class, HyperlinkedRelatedField):
            field_kwargs.pop('view_name', None)

        return field_class, field_kwargs

    def build_nested_field(self, *args, **kwargs):
        """
        Create nested fields for forward and reverse relationships.
        """
        field_name, relation_info, nested_depth = args

        class NestedSerializer(ModelSerializer):

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    def build_property_field(self, *args, **kwargs):
        """
        Create a read only field for model methods and properties.
        """
        field_class = ReadOnlyField
        field_kwargs = {}

        return field_class, field_kwargs

    def build_url_field(self, field_name, model_class):
        """
        Create a field representing the object's own URL.
        """
        field_class = self.serializer_url_field
        field_kwargs = get_url_kwargs(model_class)

        return field_class, field_kwargs

    def _bind_field(self, model, source, model_fields):
        """
        Bind passed field to model serializer.
        Used internally by `_get_model_fields`.
        """
        try:
            field = model._meta.get_field(source)
            if isinstance(field, DjangoModelField):
                model_fields[source] = field
        except FieldDoesNotExist:
            pass


class HyperlinkedModelSerializer(HyperlinkedModelSerializerMixin,
                                 ModelSerializer):
    """
    A type of `ModelSerializer` that uses hyperlinked relationships instead
    of primary key relationships. Specifically:

    * A 'url' field is included instead of the 'id' field.
    * Relationships to other instances are hyperlinks, instead of primary keys.
    """
    serializer_related_field = HyperlinkedRelatedField

    def build_nested_field(self, field_name, relation_info, nested_depth):

        class NestedSerializer(HyperlinkedModelSerializer):

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
