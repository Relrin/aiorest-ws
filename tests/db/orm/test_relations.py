# -*- coding: utf-8 -*-
import collections
import unittest

from aiorest_ws.db.orm.abstract import empty, SkipField
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.fields import AbstractField
from aiorest_ws.db.orm.relations import Hyperlink, PKOnlyObject, \
    RelatedField, ManyRelatedField, StringRelatedField, \
    PrimaryKeyRelatedField, HyperlinkedRelatedField, \
    HyperlinkedIdentityField, SlugRelatedField
from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.urls.base import set_urlconf

from fixtures.fakes import FakeView


class TestHyperlink(unittest.TestCase):

    def test_new_constructor(self):
        url = 'wss://127.0.0.1:8080/api/user/1'
        name = 'user-detail'
        instance = Hyperlink(url, name)

        self.assertIsInstance(instance, str)
        self.assertEqual(instance, url)
        self.assertEqual(instance.name, name)
        self.assertTrue(instance.is_hyperlink)

    def test_getnewargs(self):
        url = 'wss://127.0.0.1:8080/api/user/1'
        name = 'user-detail'
        instance = Hyperlink(url, name)

        self.assertEqual(
            instance.__getnewargs__(),
            (str(instance), instance.name)
        )


class TestPKOnlyObject(unittest.TestCase):

    def test_init(self):
        instance = PKOnlyObject(1)
        self.assertEqual(instance.pk, 1)


class TestRelatedField(unittest.TestCase):

    def test_init_raises_assertion_error_for_not_specified_queryset(self):

        with self.assertRaises(AssertionError):
            RelatedField()

    def test_init_raises_assertion_error_for_read_only_field(self):

        with self.assertRaises(AssertionError):
            RelatedField(read_only=False)

    def test_init_raises_assertion_error_for_qs_and_read_only_field(self):

        class CustomQueryset(object):
            pass

        class FakeRelatedField(RelatedField):
            queryset = CustomQueryset()

            def get_queryset(self):
                pass

        with self.assertRaises(AssertionError):
            FakeRelatedField(read_only=True)

    def test_init_many(self):

        class FakeRelatedField(RelatedField):
            many_related_field = ManyRelatedField

        instance = FakeRelatedField(many=True, read_only=True)
        self.assertIsInstance(instance, FakeRelatedField.many_related_field)

    def test_run_validation(self):
        instance = RelatedField(read_only=True)

        with self.assertRaises(SkipField):
            value = object()
            instance.run_validation(value)

    def test_run_validation_raises_skip_field_exception_for_empty_value(self):
        instance = RelatedField(read_only=True)

        with self.assertRaises(SkipField):
            instance.run_validation(empty)

    def test_run_validation_raises_skip_field_exception_for_empty_string(self):
        instance = RelatedField(read_only=True)

        with self.assertRaises(SkipField):
            instance.run_validation('')

    def test_get_queryset_raises_not_implemented_error(self):
        instance = RelatedField(read_only=True)

        with self.assertRaises(NotImplementedError):
            instance.get_queryset()

    def test_use_pk_only_optimization_returns_False(self):
        instance = RelatedField(read_only=True)
        self.assertFalse(instance.use_pk_only_optimization())

    def test_get_attribute_raises_not_implemented_error(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

        obj = FakeObject(10)

        instance = RelatedField(read_only=True)
        instance.bind('pk', None)

        with self.assertRaises(NotImplementedError):
            self.assertEqual(instance.get_attribute(obj), obj.pk)

    def test_choices_property_returns_empty_dict(self):

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return None

        instance = FakeRelatedField(read_only=True)
        self.assertEqual(instance.choices, {})

    def test_choices_property_returns_ordered_dict(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return [FakeObject(1), FakeObject(2), FakeObject(3)]

            def to_representation(self, value):
                return value

        instance = FakeRelatedField(read_only=True)
        self.assertEqual(
            instance.choices,
            collections.OrderedDict([('1', '1'), ('2', '2'), ('3', '3')])
        )

    def test_grouped_choices_property_returns_empty_dict(self):

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return None

        instance = FakeRelatedField(read_only=True)
        self.assertEqual(instance.grouped_choices, {})

    def test_grouped_choices_property_returns_ordered_dict(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return [FakeObject(1), FakeObject(2), FakeObject(3)]

            def to_representation(self, value):
                return value

        instance = FakeRelatedField(read_only=True)
        self.assertEqual(
            instance.grouped_choices,
            collections.OrderedDict([('1', '1'), ('2', '2'), ('3', '3')])
        )

    def test_display_value(self):

        class FakeObject(object):
            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        class FakeRelatedField(RelatedField):

            def to_representation(self, value):
                return value

        obj = FakeObject(10)
        instance = FakeRelatedField(read_only=True)
        self.assertEqual(instance.display_value(obj), '10')


class TestManyRelatedField(unittest.TestCase):

    def test_init_raises_assertion_error_for_missed_child_argument(self):

        with self.assertRaises(AssertionError):
            ManyRelatedField()

    def test_choices(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return [FakeObject(1), FakeObject(2), FakeObject(3)]

            def to_representation(self, value):
                return value

        child_instance = FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        self.assertEqual(
            instance.choices,
            collections.OrderedDict([('1', '1'), ('2', '2'), ('3', '3')])
        )

    def test_grouped_choices(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        class FakeRelatedField(RelatedField):

            def get_queryset(self):
                return [FakeObject(1), FakeObject(2), FakeObject(3)]

            def to_representation(self, value):
                return value

        child_instance = FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        self.assertEqual(
            instance.grouped_choices,
            collections.OrderedDict([('1', '1'), ('2', '2'), ('3', '3')])
        )

    def test_get_value(self):
        child_instance = RelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('pk_list', None)
        self.assertEqual(
            instance.get_value({'pk_list': [1, 2, 3]}),
            [1, 2, 3]
        )

    def test_get_value_returns_empty_value(self):
        child_instance = RelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('pk_list', None)
        self.assertEqual(
            instance.get_value({'pks': [1, 2, 3]}),
            empty
        )

    def test_get_attribute_raises_not_implemented_error(self):

        class FakeObject(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return str(self.pk)

        child_instance = RelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)

        with self.assertRaises(NotImplementedError):
            instance.get_attribute(FakeObject(10))

    def test_to_internal_value(self):

        class FakeRelatedField(RelatedField):

            def to_internal_value(self, data):
                return data

        child_instance = FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        data = [{'pk': 1}, {'pk': 2}, {'pk': 3}]
        self.assertEqual(instance.to_internal_value(data), data)

    def test_to_internal_value_raises_error_for_not_a_list_argument(self):
        child_instance = RelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)

        with self.assertRaises(ValidationError):
            instance.to_internal_value(object())

    def test_to_internal_value_raises_error_for_empty_value(self):
        child_instance = RelatedField(read_only=True)
        instance = ManyRelatedField(
            child_relation=child_instance, allow_empty=False
        )

        with self.assertRaises(ValidationError):
            instance.to_internal_value([])

    def test_to_representation(self):

        class FakeRelatedField(RelatedField):

            def to_representation(self, value):
                return value

        child_instance = FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        data = [{'pk': 1}, {'pk': 2}, {'pk': 3}]
        self.assertEqual(instance.to_representation(data), data)


class TestStringRelatedField(unittest.TestCase):

    class CustomStringRelatedField(StringRelatedField, RelatedField):
        pass

    def test_string_related_field_is_read_only(self):
        instance = self.CustomStringRelatedField()
        self.assertTrue(instance.read_only)

    def test_to_representation(self):
        instance = self.CustomStringRelatedField()
        self.assertEqual(
            instance.to_representation('value'),
            'value'
        )


class TestPrimaryKeyRelatedField(unittest.TestCase):

    class CustomPrimaryKeyRelatedField(PrimaryKeyRelatedField, RelatedField):
        pass

    def test_pk_field_attribute_is_none_by_default(self):
        instance = self.CustomPrimaryKeyRelatedField(read_only=True)
        self.assertIsNone(instance.pk_field)

    def test_pk_field_attribute_is_true(self):
        instance = self.CustomPrimaryKeyRelatedField(
            pk_field=True, read_only=True
        )
        self.assertTrue(instance.pk_field)

    def test_use_pk_only_optimization_returns_true(self):
        instance = self.CustomPrimaryKeyRelatedField(read_only=True)
        self.assertTrue(instance.use_pk_only_optimization())


class TestHyperlinkedRelatedField(unittest.TestCase):

    class CustomHyperlinkedRelatedField(HyperlinkedRelatedField, RelatedField):
        pass

    def test_init_raises_assertion_error_for_missed_view_name(self):

        with self.assertRaises(AssertionError):
            self.CustomHyperlinkedRelatedField(read_only=True)

    def test_init_with_specified_view_name_argument(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )
        self.assertIsNotNone(instance.view_name)
        self.assertEqual(instance.view_name, 'test_view')

    def test_use_pk_only_optimization_raises_not_implemented_error(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        with self.assertRaises(NotImplementedError):
            instance.use_pk_only_optimization()

    def test_get_object_raises_not_implemented_error(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        with self.assertRaises(NotImplementedError):
            instance.get_object('test_view', (), {})

    def test_is_saved_in_database_raises_not_implemented_error(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        with self.assertRaises(NotImplementedError):
            instance.is_saved_in_database(object())

    def test_get_lookup_value_raises_not_implemented_error(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        with self.assertRaises(NotImplementedError):
            instance.get_lookup_value(object())

    def test_get_url_returns_none(self):

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return False

        instance = FakeHyperlinkField('test_view', read_only=True)
        self.assertIsNone(instance.get_url(object(), 'test_view'))

    def test_get_url_returns_url_to_an_object(self):

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return True

            def get_lookup_value(self, obj):
                return (1, )

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        self.assertEqual(
            instance.get_url(object(), 'test_view'),
            'wss://127.0.0.1:8000/test_view/1/'
        )

    def test_get_name(self):
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )
        self.assertEqual(instance.get_name('api_name'), 'api_name')

    def test_to_internal_value(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def get_object(self, view_name, view_args, view_kwargs):
                return FakeModel(1)

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        data = {'url': 'wss://127.0.0.1:8000/test_view/1/'}
        obj = instance.to_internal_value(data)
        self.assertIsInstance(obj, FakeModel)
        self.assertEqual(obj.pk, 1)

    def test_to_internal_value_raises_error_with_fixing_url(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def get_object(self, view_name, view_args, view_kwargs):
                return FakeModel(1)

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        data = {'url': 'test_view/1'}
        obj = instance.to_internal_value(data)
        self.assertIsInstance(obj, FakeModel)
        self.assertEqual(obj.pk, 1)

    def test_to_internal_value_raises_error_for_no_primary_key(self):
        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        data = {'wrong_url_name': 'wss://127.0.0.1:8000/test_view/1/'}
        with self.assertRaises(ValidationError):
            instance.to_internal_value(data)

    def test_to_internal_value_raises_error_for_incorrect_type(self):
        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000/',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        with self.assertRaises(ValidationError):
            instance.to_internal_value('not a dict')

    def test_to_internal_value_raises_error_for_no_match(self):
        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = self.CustomHyperlinkedRelatedField(
            'test_view', read_only=True
        )

        data = {'url': 'wss://127.0.0.1:8000/wrong_view/1/'}
        with self.assertRaises(ValidationError):
            instance.to_internal_value(data)

    def test_to_representation(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return "object.pk={}".format(self.pk)

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return True

            def get_lookup_value(self, obj):
                return (1, )

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        hyperlink_object = instance.to_representation(FakeModel(1))
        self.assertEqual(
            hyperlink_object,
            'wss://127.0.0.1:8000/test_view/1/'
        )
        self.assertEqual(hyperlink_object.name, 'object.pk=1')

    def test_to_representation_returns_relative_url(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return "object.pk={}".format(self.pk)

        class FakeModelSerializer(object):

            parent = None
            _context = {'relative': True}

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return True

            def get_lookup_value(self, obj):
                return (1, )

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)
        instance.bind('pk', FakeModelSerializer())

        hyperlink_object = instance.to_representation(FakeModel(1))
        self.assertEqual(hyperlink_object, '/test_view/1/')
        self.assertEqual(hyperlink_object.name, 'object.pk=1')

    def test_to_representation_returns_none(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return "object.pk={}".format(self.pk)

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return False

            def get_lookup_value(self, obj):
                return (1, )

        router = SimpleRouter()
        router.register('/test_view/{pk}', FakeView, 'GET', name='test_view')
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        self.assertIsNone(instance.to_representation(FakeModel(1)))

    def test_to_representation_raises_improperly_configured(self):

        class FakeModel(object):

            def __init__(self, pk):
                self.pk = pk

            def __str__(self):
                return "object.pk={}".format(self.pk)

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return True

            def get_lookup_value(self, obj):
                return ()

        router = SimpleRouter()
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        with self.assertRaises(ImproperlyConfigured):
            instance.to_representation(FakeModel(1))

    def test_to_representation_raises_exception_for_empty_string(self):

        class FakeHyperlinkField(self.CustomHyperlinkedRelatedField):

            def is_saved_in_database(self, obj):
                return True

            def get_lookup_value(self, obj):
                return ()

        router = SimpleRouter()
        url_configuration = {
            'path': 'wss://127.0.0.1:8000',
            'urls': router._urls,
            'routes': router._routes
        }
        set_urlconf(url_configuration)
        instance = FakeHyperlinkField('test_view', read_only=True)

        with self.assertRaises(ImproperlyConfigured):
            instance.to_representation('')


class TestHyperlinkedIdentityField(unittest.TestCase):

    class CustomHyperlinkedIdentityField(HyperlinkedIdentityField,
                                         HyperlinkedRelatedField,
                                         RelatedField):
        pass

    def test_init(self):
        instance = self.CustomHyperlinkedIdentityField('test_view')
        self.assertEqual(instance.view_name, 'test_view')
        self.assertTrue(instance.read_only)

    def test_init_raises_assertion_error_for_not_specified_view_name(self):

        with self.assertRaises(AssertionError):
            self.CustomHyperlinkedIdentityField()

    def test_use_pk_only_optimization_returns_false(self):
        instance = self.CustomHyperlinkedIdentityField('test_view')
        self.assertFalse(instance.use_pk_only_optimization())


class TestSlugRelatedField(unittest.TestCase):

    class CustomSlugField(SlugRelatedField, RelatedField):
        pass

    class FakeSlugField(AbstractField):
        pass

    def test_init(self):
        instance = self.CustomSlugField(self.FakeSlugField, read_only=True)
        self.assertEqual(instance.slug_field, self.FakeSlugField)

    def test_init_raises_assertion_error_for_not_specified_slug_field(self):

        with self.assertRaises(AssertionError):
            self.CustomSlugField(read_only=True)
