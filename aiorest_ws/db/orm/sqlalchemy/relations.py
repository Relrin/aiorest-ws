# -*- coding: utf-8 -*-
"""
Module, which provide classes and function for related and nested field.
"""
from copy import copy

from aiorest_ws.db.orm import relations
from aiorest_ws.db.orm.sqlalchemy.mixins import ORMSessionMixin, \
    SQLAlchemyMixin
from aiorest_ws.db.orm.sqlalchemy.exceptions import ObjectDoesNotExist
from aiorest_ws.db.orm.relations import PKOnlyObject
from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.utils.fields import get_attribute

__all__ = (
    'ManyRelatedField', 'RelatedField', 'StringRelatedField',
    'PrimaryKeyRelatedField', 'HyperlinkedRelatedField',
    'HyperlinkedIdentityField'
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
        object_state = instance._sa_instance_state
        if object_state.transient or object_state.pending:
            return []

        return get_attribute(instance, self.source_attrs)

    def __deepcopy__(self, memo):
        # Avoid to deepcopy instance attributes. Because some SQLAlchemy
        # objects (e.g. Query) doesn't override __deepcopy__ methods, it leads
        # to some errors in runtime (e.g. maximum recursion limit)
        return copy(self)


class RelatedField(ORMSessionMixin, relations.RelatedField):
    many_related_field = ManyRelatedField

    def __deepcopy__(self, memo):
        # Avoid to deepcopy instance attributes. Because some SQLAlchemy
        # objects (e.g. Query) doesn't override __deepcopy__ methods, it leads
        # to some errors in runtime (e.g. maximum recursion limit)
        return copy(self)

    def get_attribute(self, instance):
        if self.use_pk_only_optimization() and self.source_attrs:
            # Optimized case, return a mock object only containing the
            # pk attribute
            try:
                instance = get_attribute(instance, self.source_attrs[:-1])
                value = getattr(instance, self.source_attrs[-1])
                return PKOnlyObject(pk=value)
            except AttributeError:
                pass

        # Standard case, return the object instance
        return get_attribute(instance, self.source_attrs)


class StringRelatedField(relations.StringRelatedField, RelatedField):
    pass


class PrimaryKeyRelatedField(relations.PrimaryKeyRelatedField,
                             SQLAlchemyMixin, RelatedField):

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)

        query = self.get_queryset()
        try:
            filter_args = self._get_filter_args(query, data)
            obj = query.filter(*filter_args).first()
            if not obj:
                raise ObjectDoesNotExist()
            return obj
        except ObjectDoesNotExist:
            self.raise_error('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.raise_error('incorrect_type', data_type=type(data).__name__)
        finally:
            query.session.close()

    def to_representation(self, value):
        object_pk = self._get_object_pk(value)
        if self.pk_field is not None:
            return self.pk_field.to_representation(object_pk)
        return object_pk


class HyperlinkedRelatedField(relations.HyperlinkedRelatedField,
                              SQLAlchemyMixin, RelatedField):
    lookup_field = 'id'  # or `pk`

    def use_pk_only_optimization(self):
        return self.lookup_field in ('id', 'pk')

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Return the object corresponding to a matched URL.
        Takes the matched URL conf arguments, and should return an
        object instance, or raise an `ObjectDoesNotExist` exception.
        """
        query = self.get_queryset()
        try:
            lookup_value = view_kwargs[self.lookup_url_kwarg]
            lookup_kwargs = {self.lookup_field: lookup_value}
            filter_args = self._get_filter_args(query, lookup_kwargs)
            obj = query.filter(*filter_args).first()
            if not obj:
                raise ObjectDoesNotExist()
            return obj
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
        finally:
            query.session.close()

    def is_saved_in_database(self, obj):
        """
        Return the boolean value, which let us to understand whether saved
        object in a database or not.
        """
        object_state = obj._sa_instance_state
        if object_state.transient or object_state.pending:
            return False
        return True

    def get_lookup_value(self, obj):
        """
        Return a tuple of object lookup values, which are will be using for
        reverse operation.
        """
        object_pk = self._get_object_pk(obj)
        if isinstance(object_pk, dict):
            return object_pk.values()
        return object_pk,


class HyperlinkedIdentityField(relations.HyperlinkedIdentityField,
                               HyperlinkedRelatedField):
    pass
