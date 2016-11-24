# -*- coding: utf-8 -*-
from django.db import models

from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.relations import PKOnlyObject
from aiorest_ws.db.orm.django.relations import ManyRelatedField, \
    RelatedField, PrimaryKeyRelatedField, HyperlinkedRelatedField, \
    SlugRelatedField
from aiorest_ws.db.orm.relations import RelatedField as BaseRelatedField
from aiorest_ws.parsers import URLParser
from aiorest_ws.urls.base import set_urlconf

from tests.fixtures.fakes import FakeView
from tests.db.orm.django.base import DjangoUnitTest


class TestManyRelatedField(DjangoUnitTest):

    class FakeRelatedField(BaseRelatedField):

        def get_queryset(self):
            return []

        def to_representation(self, value):
            return value

    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_many_related_field'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_many_related_field'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_many_related_field.Publisher",
            related_name='books', null=True
        )
        authors = models.ManyToManyField(
            "test_django_many_related_field.Author",
            related_name='books',
        )

        class Meta:
            app_label = 'test_django_many_related_field'

    apps = ('test_django_many_related_field', )
    models = (Author, Publisher, Book)

    def test_many_related_field_with_fk_field(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('publisher', None)

        publisher = self.Publisher.objects.create(name='publisher')
        book = self.Book.objects.create(name="aiorest-ws", publisher=publisher)
        self.assertEqual(instance.get_attribute(book), publisher)

    def test_many_related_field_with_m2m_field(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('books', None)

        author = self.Author.objects.create(name='admin')
        book = self.Book.objects.create(name="aiorest-ws")
        book.authors.add(author)
        book.save()
        queryset = instance.get_attribute(author)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset.first(), book)

    def test_many_related_field_with_not_saved_object(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('books', None)

        author = self.Author(name='admin')
        self.assertEqual(instance.get_attribute(author), [])


class TestRelatedField(DjangoUnitTest):

    class RelatedWithOptimization(RelatedField):

        def use_pk_only_optimization(self):
            return self.source_attrs[-1] in ('id', 'pk')

        def to_representation(self, value):
            return value.__class__.__name__

    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_related_field'

        def __str__(self):
            return str(self.id)

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_related_field'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_related_field.Publisher",
            related_name='books', null=True
        )
        authors = models.ManyToManyField(
            "test_django_related_field.Author",
            related_name='books',
        )

        class Meta:
            app_label = 'test_django_related_field'

        def get_pk(self):
            return self

    apps = ('test_django_related_field',)
    models = (Author, Publisher, Book)

    @classmethod
    def setUpClass(cls):
        super(TestRelatedField, cls).setUpClass()
        cls.author = cls.Author.objects.create(name='admin')
        cls.publisher = cls.Publisher.objects.create(name='publisher')
        cls.book = cls.Book.objects.create(name="aiorest-ws")
        cls.book.publisher = cls.publisher
        cls.book.authors.add(cls.author)
        cls.book.save()

    def test_get_queryset_returns_passed_object(self):
        instance = RelatedField(queryset=self.author)
        instance.bind('user', self)

        self.assertEqual(instance.get_queryset(), self.author)

    def test_get_queryset_returns_objects_from_relation(self):
        queryset = self.Author.objects.all()
        instance = RelatedField(queryset=queryset)
        instance.bind('user', self)

        self.assertEqual(list(instance.get_queryset()), list(queryset))

    def test_get_attribute_returns_attribute(self):
        instance = RelatedField(read_only=True)
        instance.bind('publisher', self)

        self.assertEqual(
            instance.get_attribute(self.book),
            self.book.publisher
        )

    def test_get_attribute_returns_pk_object(self):
        instance = self.RelatedWithOptimization(read_only=True)
        instance.bind('publisher.id', self)

        relation_object = instance.get_attribute(self.book)
        self.assertIsInstance(relation_object, PKOnlyObject)
        self.assertEqual(relation_object.pk, self.book.publisher.id)

    def test_get_attribute_returns_pk_object_with_callable_value(self):

        class CustomRelatedField(RelatedField):

            def use_pk_only_optimization(self):
                return True

        instance = CustomRelatedField(read_only=True)
        instance.bind('books.first.get_pk', self)

        relation_object = instance.get_attribute(self.author)
        self.assertIsInstance(relation_object, PKOnlyObject)
        self.assertEqual(relation_object.pk, self.book.pk)

    def test_get_attribute_raises_attribute_error_for_callable_value(self):
        instance = self.RelatedWithOptimization(read_only=True)
        instance.bind('books.first.some_attr.pk', self)

        self.assertRaises(AttributeError, instance.get_attribute, self.author)

    def test_get_attribute_raises_attribute_error(self):
        instance = RelatedField(read_only=True)
        instance.bind('author.wrong_attribute', self)

        self.assertRaises(AttributeError, instance.get_attribute, self.author)

    def test_get_choices(self):
        queryset = self.Author.objects.all()
        instance = self.RelatedWithOptimization(queryset=queryset)
        self.assertEqual(instance.get_choices(), {'Author': '1'})

    def test_get_choices_returns_empty_dict(self):
        instance = RelatedField(read_only=True)
        self.assertEqual(instance.get_choices(), {})

    def test_get_choices_with_cutoff(self):
        queryset = self.Author.objects.all()
        instance = self.RelatedWithOptimization(queryset=queryset)
        self.assertEqual(instance.get_choices(cutoff=1), {'Author': '1'})

    def test_choices(self):
        queryset = self.Author.objects.all()
        instance = self.RelatedWithOptimization(queryset=queryset)
        self.assertEqual(instance.choices, {'Author': '1'})

    def test_grouped_choices(self):
        queryset = self.Author.objects.all()
        instance = self.RelatedWithOptimization(queryset=queryset)
        self.assertEqual(instance.grouped_choices, {'Author': '1'})

    def test_display_value(self):
        instance = RelatedField(read_only=True)
        self.assertEqual(
            instance.display_value(self.author),
            str(self.author.id)
        )


class TestPrimaryKeyRelatedField(DjangoUnitTest):

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_primary_key_related_field'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_primary_key_related_field.Publisher",
            related_name='book', null=True
        )

        class Meta:
            app_label = 'test_django_primary_key_related_field'

    apps = ('test_django_primary_key_related_field',)
    models = (Publisher, Book)

    @classmethod
    def setUpClass(cls):
        super(TestPrimaryKeyRelatedField, cls).setUpClass()
        cls.publisher = cls.Publisher.objects.create(name='publisher')
        cls.book = cls.Book.objects.create(name="test book")
        cls.book.publisher = cls.publisher
        cls.book.save()

    def test_to_internal_value(self):
        instance = PrimaryKeyRelatedField(queryset=self.Book.objects.all())
        self.assertEqual(
            instance.to_internal_value(self.book.id),
            self.book
        )

    def test_to_internal_value_with_specified_pk_field(self):

        class FakePkField(object):

            def to_internal_value(self, data):
                return data['id']

        instance = PrimaryKeyRelatedField(
            queryset=self.Publisher.objects.all(), pk_field=FakePkField()
        )
        self.assertEqual(
            instance.to_internal_value({'id': self.publisher.id}),
            self.publisher
        )

    def test_to_internal_value_raises_object_does_not_exist_error(self):
        instance = PrimaryKeyRelatedField(queryset=self.Book.objects.all())
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, -1
        )

    def test_to_internal_value_raises_value_error(self):
        instance = PrimaryKeyRelatedField(queryset=self.Book.objects.all())
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, {'id': ""}
        )

    def test_to_internal_value_raises_type_error(self):
        instance = PrimaryKeyRelatedField(queryset=self.Book.objects.all())
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, {'id': self.book.id}
        )

    def test_to_representation(self):
        instance = PrimaryKeyRelatedField(queryset=self.Book.objects.all())
        self.assertEqual(
            instance.to_representation(self.book),
            self.book.pk
        )

    def test_to_representation_with_with_specified_pk_field(self):

        class FakePkField(object):

            def to_representation(self, value):
                return value

        instance = PrimaryKeyRelatedField(
            queryset=self.Publisher.objects.all(), pk_field=FakePkField()
        )
        self.assertEqual(
            instance.to_representation(self.publisher),
            self.publisher.pk
        )


class TestHyperlinkedRelatedField(DjangoUnitTest):

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_hyperlinked_related_field'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_hyperlinked_related_field.Publisher",
            related_name='book', null=True
        )

        class Meta:
            app_label = 'test_django_hyperlinked_related_field'

    apps = ('test_django_hyperlinked_related_field',)
    models = (Publisher, Book)

    @classmethod
    def setUpClass(cls):
        super(TestHyperlinkedRelatedField, cls).setUpClass()
        cls.publisher = cls.Publisher.objects.create(name='publisher')
        cls.book = cls.Book.objects.create(name="test book")
        cls.book.publisher = cls.publisher
        cls.book.save()

        url_parser = URLParser()
        cls.data = {
            'urls': [
                url_parser.define_route(
                    '/book/{pk}/', FakeView, ['GET', ], name='book-detail'
                ),
            ]
        }
        set_urlconf(cls.data)

    def test_use_pk_only_optimization_returns_true(self):
        instance = HyperlinkedRelatedField(view_name='book-detail')
        self.assertTrue(instance.use_pk_only_optimization())

    def test_use_pk_only_optimization_returns_false(self):
        class CustomHyperlinkedRelatedField(HyperlinkedRelatedField):
            lookup_field = 'name'

        instance = CustomHyperlinkedRelatedField(view_name='book-detail')
        self.assertFalse(instance.use_pk_only_optimization())

    def test_get_object(self):
        instance = HyperlinkedRelatedField(
            view_name='book-detail', queryset=self.Book.objects.all()
        )
        self.assertEqual(
            instance.get_object('book-detail', [], {'pk': self.book.id}),
            self.book
        )

    def test_get_object_raises_object_does_not_exists_error(self):
        instance = HyperlinkedRelatedField(
            view_name='book-detail', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.get_object, 'book-detail', [], {'pk': -1},
        )

    def test_get_object_raises_improperly_configured_error(self):
        instance = HyperlinkedRelatedField(
            view_name='book-detail', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ImproperlyConfigured,
            instance.get_object, 'book-detail', [], {'id': self.book.id},
        )

    def test_get_object_raises_type_error(self):
        instance = HyperlinkedRelatedField(
            view_name='book-detail', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.get_object, 'book-detail', [], {'pk': {}},
        )

    def test_get_object_raises_value_error(self):
        instance = HyperlinkedRelatedField(
            view_name='book-detail', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.get_object, 'book-detail', [], {'pk': ""},
        )

    def test_is_saved_in_database_returns_true(self):
        instance = HyperlinkedRelatedField(view_name='book-detail')
        self.assertTrue(instance.is_saved_in_database(self.book))

    def test_is_saved_in_database_returns_false(self):
        obj = self.Book(name='not_saved_object')
        instance = HyperlinkedRelatedField(view_name='book-detail')
        self.assertFalse(instance.is_saved_in_database(obj))

    def test_get_lookup_value_returns_single_primary_key(self):
        instance = HyperlinkedRelatedField(view_name='book-detail')
        self.assertEqual(
            instance.get_lookup_value(self.book),
            (self.book.pk, )
        )

    def test_get_lookup_value_returns_сomposity_primary_key(self):
        class FakeBookObject(object):
            pk = (1, 2)

        obj = FakeBookObject()
        instance = HyperlinkedRelatedField(view_name='book-detail')
        self.assertEqual(instance.get_lookup_value(obj), obj.pk)


class TestSlugRelatedField(DjangoUnitTest):

    class Book(models.Model):
        name = models.CharField(max_length=30, unique=True)

        class Meta:
            app_label = 'test_django_slug_related_field'

    apps = ('test_django_slug_related_field', )
    models = (Book, )

    @classmethod
    def setUpClass(cls):
        super(TestSlugRelatedField, cls).setUpClass()
        cls.book = cls.Book.objects.create(name='test_book')

    def test_to_internal_value_returns_object(self):
        instance = SlugRelatedField(
            slug_field='name', queryset=self.Book.objects.all()
        )
        self.assertEqual(
            instance.to_internal_value(self.book.name),
            self.book
        )

    def test_to_internal_value_raises_object_does_not_exist_error(self):
        instance = SlugRelatedField(
            slug_field='name', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, "not_exists_book"
        )

    def test_to_internal_value_raises_value_error(self):
        instance = SlugRelatedField(
            slug_field='id', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, ""
        )

    def test_to_internal_value_raises_type_error(self):
        instance = SlugRelatedField(
            slug_field='id', queryset=self.Book.objects.all()
        )
        self.assertRaises(
            ValidationError,
            instance.to_internal_value, {}
        )

    def test_to_representation(self):
        instance = SlugRelatedField(
            slug_field='name', queryset=self.Book.objects.all()
        )
        self.assertEqual(
            instance.to_representation(self.book),
            self.book.name
        )
