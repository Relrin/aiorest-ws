# -*- coding: utf-8 -*-
"""
Module which provide classes and function for related and nested field.

NOTE: Don't forget to override `to_internal_value()`, `to_representation()`
and other specific methods for all specified classes for you own purposes.

For your own ORM support necessary to implement classes accordingly to the
next inheritance tree (don't look onto the classes, which aren't inherited
as on the picture):

    AbstractField
    ├─ ManyRelatedField
    └─ RelatedField
       ├─ StringRelatedField
       ├─ PrimaryKeyRelatedField
       ├─ HyperlinkedRelatedField
       │  └─ HyperlinkedIdentityField
       └─ SlugRelatedField  # Inherit from it, if your ORM provide slug field
"""
import collections
from urllib.parse import urlparse

from aiorest_ws.conf import settings
from aiorest_ws.db.orm.abstract import AbstractField, empty
from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.urls.exceptions import NoReverseMatch, NoMatch
from aiorest_ws.urls.utils import reverse, resolve
from aiorest_ws.utils.fields import method_overridden

__all__ = (
    'MANY_RELATION_KWARGS', 'Hyperlink', 'PKOnlyObject', 'RelatedField',
    'ManyRelatedField', 'StringRelatedField', 'PrimaryKeyRelatedField',
    'HyperlinkedRelatedField', 'HyperlinkedIdentityField', 'SlugRelatedField'
)

# We assume that 'validators' are intended for the child serializer,
# rather than the parent serializer
MANY_RELATION_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty'
)


class Hyperlink(str):
    """
    A string like object that additionally has an associated name.
    We use this for hyperlinked URLs that may render as a named link
    in some contexts, or render as a plain URL in others.
    """
    is_hyperlink = True

    def __new__(self, url, name):
        ret = str.__new__(self, url)
        ret.name = name
        return ret

    def __getnewargs__(self):
        return str(self), self.name


class PKOnlyObject(object):
    """
    This is a mock object, used for when we only need the pk of the object
    instance, but still want to return an object with a .pk attribute,
    in order to keep the same interface as a regular model instance.
    """
    def __init__(self, pk):
        self.pk = pk


class RelatedField(AbstractField):
    queryset = None
    many_related_field = None

    def __init__(self, **kwargs):
        self.queryset = kwargs.pop('queryset', self.queryset)

        field_is_read_only = kwargs.get('read_only', None)
        if not method_overridden('get_queryset', RelatedField, self):
            assert self.queryset is not None or field_is_read_only, (
                'Relational field must provide a `queryset` argument, '
                'override `get_queryset`, or set read_only=`True`.'
            )
        assert not (self.queryset is not None and field_is_read_only), (
            'Relational fields should not provide a `queryset` argument, '
            'when setting read_only=`True`.'
        )
        kwargs.pop('many', None)
        kwargs.pop('allow_empty', None)
        super(RelatedField, self).__init__(**kwargs)

    def __new__(cls, *args, **kwargs):
        # We override this method in order to automagically create
        # `ManyRelatedField` classes instead when `many=True` is set
        if kwargs.pop('many', False):
            return cls.many_init(*args, **kwargs)
        return super(RelatedField, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method handles creating a parent `ManyRelatedField` instance
        when the `many=True` keyword argument is passed.
        Typically you won't need to override this method.
        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:

        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomManyRelatedField(*args, **kwargs)
        """
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return cls.many_related_field(**list_kwargs)

    def run_validation(self, data=empty):
        # We force empty strings to None values for relational fields.
        if data == '':
            data = None
        return super(RelatedField, self).run_validation(data)

    def get_queryset(self):
        raise NotImplementedError('`get_queryset()` must be implemented.')

    def use_pk_only_optimization(self):
        return False

    def get_attribute(self, instance):
        raise NotImplementedError('`get_attribute()` must be implemented.')

    @property
    def choices(self):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        return collections.OrderedDict([
            (str(self.to_representation(item)), self.display_value(item))
            for item in queryset
        ])

    @property
    def grouped_choices(self):
        return self.choices

    def display_value(self, instance):
        return str(instance)


class ManyRelatedField(AbstractField):
    """
    Relationships with `many=True` transparently get coerced into instead being
    a ManyRelatedField with a child relationship.
    The `ManyRelatedField` class is responsible for handling iterating through
    the values and passing each one to the child relationship.
    This class is treated as private API.
    You shouldn't generally need to be using this class directly yourself,
    and should instead simply set 'many=True' on the relationship.
    """
    initial = []
    default_error_messages = {
        'not_a_list': u'Expected a list of items but got type "{input_type}".',
        'empty': u'This list may not be empty.'
    }

    def __init__(self, child_relation=None, *args, **kwargs):
        self.child_relation = child_relation
        self.allow_empty = kwargs.pop('allow_empty', True)
        assert child_relation is not None, '`child_relation` is a required ' \
                                           'argument.'
        super(ManyRelatedField, self).__init__(*args, **kwargs)
        self.child_relation.bind(field_name='', parent=self)

    @property
    def choices(self):
        return self.child_relation.choices

    @property
    def grouped_choices(self):
        return self.choices

    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)

    def get_attribute(self, instance):
        raise NotImplementedError('`get_attribute()` must be implemented.')

    def to_internal_value(self, data):
        if isinstance(data, type('')) or not hasattr(data, '__iter__'):
            self.raise_error('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            self.raise_error('empty')

        return [
            self.child_relation.to_internal_value(item)
            for item in data
        ]

    def to_representation(self, iterable):
        return [
            self.child_relation.to_representation(value)
            for value in iterable
        ]


class StringRelatedField(object):
    """
    A read only field that represents its targets using their plain
    string representation.
    """
    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super(StringRelatedField, self).__init__(**kwargs)

    def to_representation(self, value):
        return str(value)


class PrimaryKeyRelatedField(object):
    default_error_messages = {
        'required': u'This field is required.',
        'does_not_exist': u'Invalid pk "{pk_value}" - object does not exist.',
        'incorrect_type': u'Incorrect type. Expected pk value, received '
                          u'{data_type}.',
    }

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        super(PrimaryKeyRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return True


class HyperlinkedRelatedField(object):
    lookup_field = None
    view_name = None

    default_error_messages = {
        'required': u'This field is required.',
        'no_match': u'Invalid hyperlink - No URL match.',
        'no_primary_key': u'For every instance necessary to specify '
                          u'`{url_field}` field.',
        'does_not_exist': u'Invalid hyperlink - Object does not exist.',
        'incorrect_type': u'Incorrect type. Expected URL string, '
                          u'received {data_type}.',
    }

    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            self.view_name = view_name
        assert self.view_name is not None, 'The `view_name` argument ' \
                                           'is required.'
        self.lookup_field = kwargs.pop('lookup_field', self.lookup_field)
        self.lookup_url_kwarg = kwargs.pop(
            'lookup_url_kwarg', self.lookup_field
        )
        self.format = kwargs.pop('format', None)

        # We include this simply for dependency injection in tests.
        # We can't add it as a class attributes or it would expect an
        # implicit `self` argument to be passed.
        # Set the `reverse` attribute of this class
        self.reverse = reverse

        super(HyperlinkedRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        # Must return boolean value for equal operation between
        # self.lookup_field attribute and defined model PK.
        # For example, for Django Framework it can be:
        # return self.lookup_field == 'pk'
        raise NotImplementedError("`use_pk_only_optimization()` must be "
                                  "implemented.")

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Return the object corresponding to a matched URL.
        Takes the matched URL conf arguments, and should return an
        object instance, or raise exception for a not existing object.
        """
        raise NotImplementedError('`get_object()` must be implemented.')

    def is_saved_in_database(self, obj):
        """
        Return the boolean value, which let us to understand whether saved
        object in a database or not.
        """
        raise NotImplementedError('`is_saved_in_database()` must be '
                                  'implemented.')

    def get_lookup_value(self, obj):
        """
        Return a tuple of object lookup values, which are will be using for
        reverse operation.
        """
        raise NotImplementedError('`get_lookup_value()` must be implemented.')

    def get_url(self, obj, view_name):
        """
        Given an object, return the URL that hyperlinks to the object.
        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL
        if not self.is_saved_in_database(obj):
            return None

        # If have taken `context` and set `relative=True`, then necessary to
        # generate relative URL
        relative = self.context.get('relative', False)

        args = tuple(map(str, self.get_lookup_value(obj)))
        return self.reverse(view_name, args=args, relative=relative)

    def get_name(self, obj):
        return str(obj)

    def to_internal_value(self, data):
        url_field_name = settings.REST_CONFIG['URL_FIELD_NAME']

        try:
            url = urlparse(data[url_field_name]).path
        except KeyError:
            self.raise_error('no_primary_key', url_field=url_field_name)
        except (AttributeError, TypeError):
            self.raise_error('incorrect_type', data_type=type(data).__name__)

        if not url.startswith('/'):
            url = '/' + url
        if not url.endswith('/'):
            url += '/'

        try:
            match = resolve(url)
        except NoMatch:
            self.raise_error('no_match')

        return self.get_object(match.view_name, match.args, match.kwargs)

    def to_representation(self, value):
        # Return the hyperlink, or error if incorrectly configured
        try:
            url = self.get_url(value, self.view_name)
        except NoReverseMatch:
            msg = (
                'Could not resolve URL for hyperlinked relationship using '
                'view name "%s". You may have failed to include the related '
                'model in your API, or incorrectly configured the '
                '`lookup_field` attribute on this field.'
            )
            if value in ('', None):
                value_string = {'': 'the empty string', None: 'None'}[value]
                msg += (
                    " WARNING: The value of the field on the model instance "
                    "was %s, which may be why it didn't match any "
                    "entries in your URL conf." % value_string
                )
            raise ImproperlyConfigured(msg % self.view_name)

        if url is None:
            return None

        name = self.get_name(value)
        return Hyperlink(url, name)


class HyperlinkedIdentityField(object):
    """
    A read-only field that represents the identity URL for an object, itself.
    This is in contrast to `HyperlinkedRelatedField` which represents the
    URL of relationships to other objects.
    """
    def __init__(self, view_name=None, **kwargs):
        assert view_name is not None, 'The `view_name` argument is required.'
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super(HyperlinkedIdentityField, self).__init__(view_name, **kwargs)

    def use_pk_only_optimization(self):
        # We have the complete object instance already. We don't need
        # to run the 'only get the pk for this relationship' code
        return False


class SlugRelatedField(object):
    """
    A read-write field that represents the target of the relationship
    by a unique 'slug' attribute.
    """
    default_error_messages = {
        'does_not_exist': u'Object with {slug_name}={value} does not exist.',
        'invalid': u'Invalid value.',
    }

    def __init__(self, slug_field=None, **kwargs):
        assert slug_field is not None, 'The `slug_field` argument is required.'
        self.slug_field = slug_field
        super(SlugRelatedField, self).__init__(**kwargs)
