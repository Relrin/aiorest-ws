# -*- coding: utf-8 -*-
"""
List, model and hyperlinked serializer classes for SQLAlchemy ORM.

As you can see there, we are inherited from all base classes and implement
logic according to the work of SQLAlchemy ORM. For the most situations using
ModelSerializer class will be enough.
"""
from aiorest_ws.conf import settings
from aiorest_ws.db.orm.abstract import empty
from aiorest_ws.db.orm.serializers import \
    ListSerializer as BaseListSerializer, \
    ModelSerializer as BaseModelSerializer, HyperlinkedModelSerializerMixin, \
    raise_errors_on_nested_writes
from aiorest_ws.db.orm.sqlalchemy import model_meta
from aiorest_ws.db.orm.sqlalchemy.field_mapping import get_field_kwargs, \
    get_relation_kwargs, get_nested_relation_kwargs, get_url_kwargs
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.utils.field_mapping import ClassLookupDict

from sqlalchemy import types, Column
from sqlalchemy.sql.schema import ColumnCollectionConstraint
from sqlalchemy.orm.interfaces import MANYTOMANY, MANYTOONE, ONETOMANY
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.dialects import postgresql

from aiorest_ws.db.orm.sqlalchemy.fields import *  # NOQA
from aiorest_ws.db.orm.sqlalchemy.relations import *  # NOQA

__all__ = (
    'get_validation_error_detail', 'ListSerializer', 'ModelSerializer',
    'HyperlinkedModelSerializer',
)


def get_validation_error_detail(exc):
    assert isinstance(exc, (ValidationError, AssertionError))

    if isinstance(exc, AssertionError):
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
        except (ValidationError, AssertionError) as exc:
            raise ValidationError(detail=get_validation_error_detail(exc))

        return value


class ModelSerializer(BaseModelSerializer):
    """
    Base serializer for SQLAlchemy models.

    This class automatically generate "scheme" for further serializing and
    de-serializing data, according to used model, which is specified by user.
    For indicated fields by programmer, ModelSerializer will not apply "scheme
    construction rule". They are will have skipped while processing. Otherwise,
    for every field which is not pre-defined by user, will be found the most
    suitable and compatible field class.
    """
    serializer_field_mapping = {
        # Generic types
        types.BigInteger: BigIntegerField,
        types.Binary: LargeBinaryField,
        types.Boolean: BooleanField,
        types.Date: DateField,
        types.DateTime: DateTimeField,
        types.Enum: EnumField,
        types.Float: FloatField,
        types.Integer: IntegerField,
        types.Interval: IntervalField,
        types.LargeBinary: LargeBinaryField,
        types.MatchType: BooleanField,
        types.Numeric: DecimalField,
        types.PickleType: PickleField,
        types.SmallInteger: SmallIntegerField,
        types.String: CharField,
        types.Text: CharField,
        types.Time: TimeField,
        types.Unicode: CharField,
        types.UnicodeText: CharField,
        # SQL standard and multiple vendor types
        types.BIGINT: BigIntegerField,
        types.BLOB: LargeBinaryField,
        types.BOOLEAN: BooleanField,
        types.CHAR: CharField,
        types.CLOB: CharField,
        types.DATE: DateField,
        types.DATETIME: DateTimeField,
        types.DECIMAL: DecimalField,
        types.FLOAT: FloatField,
        types.INT: IntegerField,
        types.INTEGER: IntegerField,
        types.NCHAR: CharField,
        types.NVARCHAR: CharField,
        types.NUMERIC: DecimalField,
        types.REAL: FloatField,
        types.SMALLINT: SmallIntegerField,
        types.TEXT: CharField,
        types.TIMESTAMP: DateTimeField,
        types.VARBINARY: LargeBinaryField,
        types.VARCHAR: CharField,
        # Special SQLAlchemy types
        postgresql.ARRAY: ListField,
        postgresql.HSTORE: HStoreField,
        # For any other field types (include custom)
        types.TypeEngine: ModelField
    }
    serializer_related_field = PrimaryKeyRelatedField
    serializer_related_to_field = None
    serializer_url_field = HyperlinkedIdentityField
    serializer_choice_field = EnumField
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

    # Default `create` and `update` behavior
    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            instance = ExampleModel(**validated_data)
            session.add(instance)
            session.commit()
            return object_to_dict(instance)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel(**validated_data)
            instance.example_relationship = example_relationship
            session.add(instance)
            session.commit()
            return object_to_dict(instance)

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model
        # Remove relationship instances from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved
        relations = model_meta.get_relations_data(ModelClass, validated_data)

        session = settings.SQLALCHEMY_SESSION(expire_on_commit=False)
        try:
            instance = ModelClass(**validated_data)
            # After creating instance of ModelClass, just append all data,
            # which are removed earlier
            if relations:
                session.enable_relationship_loading(instance)
                for field_name, value in relations.items():
                    setattr(instance, field_name, value)

            session.add(instance)
            session.commit()
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)
        finally:
            session.close()

        return instance

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        ModelClass = self.Meta.model
        relations = model_meta.get_relations_data(ModelClass, validated_data)

        # Generate filter for getting existing object once more. Earlier,
        # We generate query to the database, because we can get relationship
        # objects, which attached to the existing object. But can't use this
        # instance further. To avoid issues with it, just get object once more
        filter_args = (
            getattr(ModelClass, field) == getattr(instance, field)
            for field in model_meta.model_pk(ModelClass)
        )

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with
        session = settings.SQLALCHEMY_SESSION(expire_on_commit=False)
        try:
            instance = session.query(ModelClass).filter(*filter_args).first()
            if not instance:
                raise ValidationError("Object does not exist.")

            for field_name, value in validated_data.items():
                setattr(instance, field_name, value)

            # Update relation objects
            if relations:
                session.enable_relationship_loading(instance)
                for field_name, value in relations.items():
                    setattr(instance, field_name, [])
                    session.refresh(instance)

                    if value:
                        setattr(instance, field_name, value)

            session.commit()
        finally:
            session.close()

        return instance

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'  # NOQA
        except (ValidationError, AssertionError) as exc:
            raise ValidationError(detail=get_validation_error_detail(exc))

        return value

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return list(set(
            list(dict(model_info.pk)) +
            list(declared_fields.keys()) +
            list(model_info.fields.keys()) +
            list(model_info.forward_relations.keys())
        ))

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
        unique_constraint_names = set()

        # Iterate over all model field and include every field, which
        # marked have value `True` for `unique` attribute
        for field_name in model_fields.keys():
            column = getattr(model, field_name)
            unique_constraint_names |= {
                column.name
                for column in column.property.columns
                if column.unique
            }

        unique_constraint_names -= {None}
        return unique_constraint_names

    def _get_unique_together_constraints(self, model, model_fields, field_names):  # NOQA
        """
        Return a set of field names for a multiple unique constraints.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        unique_constraint_names = set()

        # Scan tables for passed model and include every unique field
        # as at the previous sub-step. Also, there we try to find special
        # unique constrains (e.g. CheckConstraint, ForeignKeyConstraint,
        # PrimaryKeyConstraint, UniqueConstraint)
        for constraint in model.__table__.constraints:
            if isinstance(constraint, ColumnCollectionConstraint):
                unique_constraint_names |= set(constraint.columns.keys())

        return unique_constraint_names

    def _get_unique_field(self, model, unique_field_name):
        """
        Return a field by his name from a model.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        return model.__mapper__.columns[unique_field_name]

    def _get_default_field_value(self, unique_constraint_field):
        """
        Return a default value for a passed field.
        Used internally by `get_uniqueness_extra_kwargs`.
        """
        default = empty

        if unique_constraint_field.default:
            default = unique_constraint_field.default
        elif unique_constraint_field.onupdate:
            default = unique_constraint_field.onupdate

        return default

    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Create regular model fields.
        """
        if field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            return self.build_standard_field(field_name, model_field, model_class)  # NOQA

        elif field_name in info.relations:
            relation_info = info.relations[field_name]
            if not nested_depth:
                return self.build_relational_field(field_name, relation_info)
            else:
                return self.build_nested_field(field_name, relation_info, nested_depth)  # NOQA

        elif hasattr(model_class, field_name):
            return self.build_property_field(field_name, model_class)

        elif field_name == self.url_field_name:
            return self.build_url_field(field_name, model_class)

        return self.build_unknown_field(field_name, model_class)

    def build_standard_field(self, *args, **kwargs):
        """
        Create regular model fields.
        """
        field_name, model_field, model_class = args
        field_mapping = ClassLookupDict(self.serializer_field_mapping)

        field_class = field_mapping[model_field.type]
        field_kwargs = get_field_kwargs(field_name, model_field, model_class)

        if 'choices' in field_kwargs:
            # Fields with choices get coerced into `ChoiceField`
            # instead of using their regular typed field
            field_class = self.serializer_choice_field
            # Some model fields may introduce kwargs that would not be valid
            # for the choice field. We need to strip these out.
            # Eg. Column('race', Enum('one', 'two', 'three'))
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

        if not issubclass(field_class, CharField) and \
                not issubclass(field_class, EnumField):
            # `allow_blank` is only valid for textual fields
            field_kwargs.pop('allow_blank', None)

        if isinstance(model_field.type, postgresql.ARRAY):
            # Populate the `child` argument on `ListField` instances generated
            # for the PostgreSQL specific `ArrayField`
            child_field_name = '%s.%s' % (field_name, 'child')
            child_model_field = model_field.type.item_type
            # Because our model_field, which passed to the build_standard_field
            # function is a Column, then wrap this sub-field and invoke this
            # method one more time
            child_field_class, child_field_kwargs = self.build_standard_field(
                child_field_name, Column(child_model_field), model_class
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

        relation_type = relation_info.model_field.direction
        if relation_type in (MANYTOMANY, MANYTOONE, ONETOMANY):
            field_kwargs['many'] = True

        # `to_field` is only valid for slug fields, which aren't
        # supported by SQLAlchemy ORM by default
        field_kwargs.pop('to_field', None)

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
        try:
            column = getattr(model, source, None)
            if column and isinstance(column.property, ColumnProperty):
                model_fields[source] = type(column.property.columns[0].type)
        except (AttributeError, IndexError):
            pass


class HyperlinkedModelSerializer(HyperlinkedModelSerializerMixin,
                                 ModelSerializer):
    serializer_related_field = HyperlinkedRelatedField

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """
        class NestedSerializer(HyperlinkedModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
