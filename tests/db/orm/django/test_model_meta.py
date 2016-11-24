# -*- coding: utf-8 -*-
from django.db import models

from aiorest_ws.db.orm.django.model_meta import _get_pk, _get_fields, \
    _get_to_field, _get_forward_relationships, _get_reverse_relationships, \
    _merge_fields_and_pk, _merge_relationships, get_field_info, \
    is_abstract_model

from tests.db.orm.django.base import DjangoUnitTest


class TestGetPkFunction(DjangoUnitTest):

    class TableWithOnePk(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_pk_function'

    class InheritedTable(TableWithOnePk):

        class Meta:
            app_label = 'test_django_get_pk_function'

    class TableWithUniqueTogether(models.Model):
        pk_1 = models.IntegerField()
        pk_2 = models.IntegerField()

        class Meta:
            app_label = 'test_django_get_pk_function'
            # Django model still return only id/pk fields, but for the
            # insert/update operations these keys checked
            unique_together = (('pk_1', 'pk_2'), )

    apps = ('test_django_get_pk_function', )
    models = (TableWithOnePk, InheritedTable, TableWithUniqueTogether)

    def test_get_pk_returns_one_primary_key(self):
        opts = self.TableWithOnePk._meta.concrete_model._meta
        self.assertEqual(_get_pk(opts), opts.pk)

    def test_get_pk_from_inherited_table(self):
        opts = self.InheritedTable._meta.concrete_model._meta
        self.assertEqual(_get_pk(opts), opts.pk.remote_field.model._meta.pk)

    def test_get_pk_returns_primary_key_for_table_with_unique_together(self):
        opts = self.TableWithUniqueTogether._meta.concrete_model._meta
        self.assertEqual(_get_pk(opts), opts.pk)


class TestGetFieldsFunction(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_fields_function'

    class Address(models.Model):
        email = models.CharField(max_length=255)
        user = models.ForeignKey("test_django_get_fields_function.User")

        class Meta:
            app_label = 'test_django_get_fields_function'

    apps = ('test_django_get_fields_function', )
    models = (User, Address)

    def test_get_fields_returns_fields_for_simple_model(self):
        opts = self.User._meta.concrete_model._meta
        fields = _get_fields(opts)
        self.assertEqual(set(fields.keys()), {'name', })
        self.assertEqual(fields['name'], opts.get_field('name'))

    def test_get_fields_returns_fields_for_model_with_foreign_key(self):
        opts = self.Address._meta.concrete_model._meta
        fields = _get_fields(opts)
        self.assertEqual(set(fields.keys()), {'email'})
        self.assertEqual(fields['email'], opts.get_field('email'))


class TestGetToFieldFunction(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_to_field_function'

    class Address(models.Model):
        email = models.CharField(max_length=255)
        user = models.ForeignKey("test_django_get_fields_function.User")
        user_2 = models.ForeignKey(
            "test_django_get_fields_function.User", to_field='id'
        )

        class Meta:
            app_label = 'test_django_get_to_field_function'

    apps = ('test_django_get_to_field_function', )
    models = (User, Address)

    def test_get_to_field_returns_false_for_not_related_field(self):
        field = self.User._meta.get_field('name')
        self.assertFalse(_get_to_field(field))

    def test_get_to_field_returns_false_for_foreign_key_without_to_field(self):
        field = self.Address._meta.get_field('user')
        self.assertFalse(_get_to_field(field))

    def test_get_to_field_returns_true_for_foreign_key_with_to_field(self):
        field = self.Address._meta.get_field('user_2')
        self.assertTrue(_get_to_field(field))


class TestGetForwardRelationshipsFunction(DjangoUnitTest):

    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_forward_relationships_function'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_forward_relationships_function'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_get_forward_relationships_function.Publisher",
            related_name='books'
        )
        authors = models.ManyToManyField(
            "test_django_get_forward_relationships_function.Author"
        )

        class Meta:
            app_label = 'test_django_get_forward_relationships_function'

    apps = ('test_django_get_forward_relationships_function', )
    models = (Author, Publisher, Book)

    def test_get_forward_relationships_for_simple_model(self):
        opts = self.Author._meta.concrete_model._meta
        fields = _get_forward_relationships(opts)
        self.assertEqual(set(fields.keys()), set())

    def test_get_forward_relationships_for_model_with_m2m_and_fk(self):
        opts = self.Book._meta.concrete_model._meta
        fields = _get_forward_relationships(opts)
        self.assertEqual(set(fields.keys()), {'authors', 'publisher'})

        self.assertEqual(
            fields['authors'].model_field,
            opts.get_field('authors')
        )
        self.assertTrue(fields['authors'].to_many)
        self.assertFalse(fields['authors'].has_through_model)

        self.assertEqual(
            fields['publisher'].model_field,
            opts.get_field('publisher')
        )
        self.assertFalse(fields['publisher'].to_many)
        self.assertFalse(fields['publisher'].has_through_model)


class TestMergeFieldsAndPkFunction(DjangoUnitTest):

    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_merge_fields_and_pk_function'

    apps = ('test_django_merge_fields_and_pk_function', )
    models = (Author, )

    def test_merge_fields_and_pk(self):
        opts = self.Author._meta.concrete_model._meta
        pk = _get_pk(opts)
        fields = _get_fields(opts)
        result = _merge_fields_and_pk(pk, fields)
        self.assertEqual(set(result.keys()), {'pk', 'id', 'name'})


class TestMergeRelationsFunction(DjangoUnitTest):
    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_merge_relationships_function'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_merge_relationships_function'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_merge_relationships_function.Publisher",
            related_name='books'
        )
        authors = models.ManyToManyField(
            "test_django_merge_relationships_function.Author"
        )

        class Meta:
            app_label = 'test_django_merge_relationships_function'

    apps = ('test_django_merge_relationships_function', )
    models = (Author, Publisher, Book)

    def test_merge_relationships(self):
        opts = self.Book._meta.concrete_model._meta
        forward_relations = _get_forward_relationships(opts)
        reverse_relations = _get_reverse_relationships(opts)
        result = _merge_relationships(forward_relations, reverse_relations)
        self.assertEqual(set(result.keys()), {'authors', 'publisher'})


class TestGetFieldInfoFunction(DjangoUnitTest):
    class Author(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_field_info_function'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_field_info_function'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_get_field_info_function.Publisher",
            related_name='books'
        )
        authors = models.ManyToManyField(
            "test_django_get_field_info_function.Author"
        )

        class Meta:
            app_label = 'test_django_get_field_info_function'

    apps = ('test_django_get_field_info_function', )
    models = (Author, Publisher, Book)

    def test_merge_relationships_for_model(self):
        field_info = get_field_info(self.Author)
        self.assertEqual(field_info.pk.name, 'id')
        self.assertEqual(set(field_info.fields.keys()), {'name', })
        self.assertEqual(set(field_info.forward_relations.keys()), set())
        self.assertEqual(set(field_info.reverse_relations.keys()), set())
        self.assertEqual(
            set(field_info.fields_and_pk.keys()),
            {'id', 'name', 'pk'}
        )
        self.assertEqual(set(field_info.relations.keys()), set())

    def test_merge_relationships_for_model_with_m2m_and_pk(self):
        field_info = get_field_info(self.Book)
        self.assertEqual(field_info.pk.name, 'id')
        self.assertEqual(set(field_info.fields.keys()), {'name', })
        self.assertEqual(
            set(field_info.forward_relations.keys()),
            {'authors', 'publisher'}
        )
        self.assertEqual(set(field_info.reverse_relations.keys()), set())
        self.assertEqual(
            set(field_info.fields_and_pk.keys()),
            {'id', 'name', 'pk'}
        )
        self.assertEqual(
            set(field_info.relations.keys()),
            {'authors', 'publisher'}
        )


class TestIsAbstractModelFunction(DjangoUnitTest):

    class AbstractModel(models.Model):

        class Meta:
            abstract = True

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_is_abstract_model_function'

    apps = ('test_django_is_abstract_model_function', )
    models = (User, )

    def test_is_abstract_model_returns_true_for_abstract_model(self):
        self.assertTrue(is_abstract_model(self.AbstractModel))

    def test_is_abstract_model_returns_false_for_real_model(self):
        self.assertFalse(is_abstract_model(self.User))
