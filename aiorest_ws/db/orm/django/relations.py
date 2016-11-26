# -*- coding: utf-8 -*-
"""
Module, which provide classes and function for related and nested field.
"""
from collections import OrderedDict

from aiorest_ws.db.orm import relations
from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.utils.fields import get_attribute, is_simple_callable

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.utils.encoding import smart_text


__all__ = (
    'ManyRelatedField', 'RelatedField', 'StringRelatedField',
    'PrimaryKeyRelatedField', 'HyperlinkedRelatedField',
    'HyperlinkedIdentityField', 'SlugRelatedField'
)


class ManyRelatedField(relations.ManyRelatedField):
    """
    Relationships with `many=True` transparently get coerced into instead being
    a ManyRelatedField with a child relationship.
    The `ManyRelatedField` class is responsible for handling iterating through
    the values and passing each one to the child relationship.
    This class is treated as private API.
    You shouldn't generally need to be using this class directly yourself,
    and should instead simply set 'many=True' on the relationship.
    """

    def get_attribute(self, instance):
        # Can't have any relationships if not created
        if hasattr(instance, 'pk') and instance.pk is None:
            return []

        relationship = get_attribute(instance, self.source_attrs)
        if hasattr(relationship, 'all'):
            return relationship.all()
        return relationship


class RelatedField(relations.RelatedField):
    many_related_field = ManyRelatedField

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, (QuerySet, Manager)):
            # Ensure queryset is re-evaluated whenever used.
            # Note that actually a `Manager` class may also be used as the
            # queryset argument. This occurs on ModelSerializer fields,
            # as it allows us to generate a more expressive 'repr' output
            # for the field.
            # Eg: 'MyRelationship(queryset=ExampleModel.objects.all())'
            queryset = queryset.all()
        return queryset

    def get_attribute(self, instance):
        if self.use_pk_only_optimization() and self.source_attrs:
            # Optimized case, return a mock object only containing the
            # pk attribute
            try:
                instance = get_attribute(instance, self.source_attrs[:-1])
                value = instance.serializable_value(self.source_attrs[-1])
                if is_simple_callable(value):
                    # Handle edge case where the relationship `source` argument
                    # points to a `get_relationship()` method on the model
                    value = value().pk
                return relations.PKOnlyObject(pk=value)
            except AttributeError:
                pass

        # Standard case, return the object instance.
        return get_attribute(instance, self.source_attrs)

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (self.to_representation(item), self.display_value(item))
            for item in queryset
        ])

    @property
    def choices(self):
        return self.get_choices()

    @property
    def grouped_choices(self):
        return self.choices

    def display_value(self, instance):
        return str(instance)


class StringRelatedField(relations.StringRelatedField, RelatedField):
    pass


class PrimaryKeyRelatedField(relations.PrimaryKeyRelatedField,
                             RelatedField):

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.raise_error('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.raise_error('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        return value.pk


class HyperlinkedRelatedField(relations.HyperlinkedRelatedField,
                              RelatedField):
    lookup_field = 'pk'

    def use_pk_only_optimization(self):
        return self.lookup_field == 'pk'

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Return the object corresponding to a matched URL.
        Takes the matched URL conf arguments, and should return an
        object instance, or raise an `ObjectDoesNotExist` exception.
        """
        try:
            lookup_value = view_kwargs[self.lookup_url_kwarg]
            lookup_kwargs = {self.lookup_field: lookup_value}
            return self.get_queryset().get(**lookup_kwargs)
        except ObjectDoesNotExist:
            self.raise_error('does_not_exist')
        except KeyError:
            raise ImproperlyConfigured(
                "Missing primary key in the endpoint path. For fixing it just "
                "specify for a requested endpoint URL with included "
                "`{field_name}` parameter in the path or override"
                "`lookup_url_kwarg` in the constructor for the concrete field."
                .format(field_name=self.lookup_url_kwarg)
            )
        except (TypeError, ValueError):
            self.raise_error(
                'incorrect_type', data_type=type(view_kwargs).__name__
            )

    def is_saved_in_database(self, obj):
        if not obj or not obj.pk:
            return False
        return True

    def get_lookup_value(self, obj):
        pk = getattr(obj, self.lookup_field)
        return pk if isinstance(pk, (tuple, list)) else (pk, )


class HyperlinkedIdentityField(relations.HyperlinkedIdentityField,
                               HyperlinkedRelatedField):
    pass


class SlugRelatedField(relations.SlugRelatedField, RelatedField):
    """
    A read-write field that represents the target of the relationship
    by a unique 'slug' attribute.
    """
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            self.raise_error(
                'does_not_exist', slug_name=self.slug_field,
                value=smart_text(data)
            )
        except (TypeError, ValueError):
            self.raise_error('invalid')

    def to_representation(self, obj):
        return getattr(obj, self.slug_field)
