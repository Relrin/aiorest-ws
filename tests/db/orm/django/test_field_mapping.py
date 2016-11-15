# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import BaseValidator, DecimalValidator, \
    MinLengthValidator, MaxLengthValidator, MinValueValidator, \
    MaxValueValidator, URLValidator, validate_email, validate_slug, \
    validate_ipv46_address

from aiorest_ws.db.orm.django.field_mapping import get_detail_view_name, \
    get_field_kwargs, get_relation_kwargs, get_nested_relation_kwargs, \
    get_url_kwargs
from aiorest_ws.db.orm.django.validators import UniqueValidator
from aiorest_ws.utils.structures import RelationInfo

from tests.db.orm.django.base import DjangoUnitTest


class TestGetDetailViewNameFunction(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_detail_view_name_function'

    apps = ('test_django_get_detail_view_name_function', )
    models = (User, )

    def test_get_detail_view_name(self):
        self.assertEqual(get_detail_view_name(self.User), 'user-detail')


class CustomValidator(BaseValidator):
    pass


class TestGetFieldKwargsFunction(DjangoUnitTest):

    class TestModel(models.Model):
        FOUNDER = 'FR'
        MANAGER = 'MR'
        WORKER = 'WR'
        POSITION = (
            (FOUNDER, 'Founder'),
            (MANAGER, 'Manager'),
            (WORKER, 'Worker'),
        )

        first_name = models.CharField(max_length=30)
        middle_name = models.CharField(
            max_length=30, verbose_name='middle_name'
        )
        last_name = models.CharField(
            max_length=30, help_text='last_name help text'
        )
        salary = models.DecimalField(max_digits=5)
        bonus_salary = models.DecimalField(decimal_places=2)
        has_car = models.NullBooleanField()
        phone = models.CharField(max_length=30, null=True)
        additional_info = models.CharField(max_length=30, blank=True)
        photos = models.FilePathField(path='/home/images')
        photos_with_match = models.FilePathField(
            path='/home/images', match='img.*\.txt$'
        )
        photos_with_recursive = models.FilePathField(
            path='/home/images', recursive=True
        )
        photos_without_allow_files = models.FilePathField(
            path='/home/images', allow_files=False
        )
        photos_with_allow_folders = models.FilePathField(
            path='/home/images', allow_folders=True
        )
        position = models.CharField(
            max_length=2, choices=POSITION, default=WORKER,
        )
        rate = models.DecimalField(
            max_digits=5, validators=[CustomValidator(100), ]
        )
        min_rate = models.IntegerField(
            validators=[MinValueValidator(0), CustomValidator(100)]
        )
        max_rate = models.IntegerField(
            validators=[MaxValueValidator(100), CustomValidator(100)]
        )
        about = models.CharField(
            max_length=255,
            validators=[MaxLengthValidator(200), CustomValidator(200)]
        )
        cover_letter = models.CharField(
            max_length=255,
            validators=[MinLengthValidator(100), CustomValidator(100)]
        )
        url = models.URLField(
            validators=[CustomValidator('http://test-website.com'), ]
        )
        email = models.EmailField(
            validators=[CustomValidator('test_email@gmail.com'), ]
        )
        slug = models.SlugField(
            validators=[CustomValidator('test-param'), ]
        )
        ip_address = models.GenericIPAddressField(
            validators=[CustomValidator('127.0.0.1'), ]
        )

        class Meta:
            app_label = 'test_django_get_detail_view_name_function'

    apps = ('test_django_get_detail_view_name_function', )
    models = (TestModel, )

    def test_get_field_kwargs_for_char_field(self):
        field = self.TestModel._meta.get_field('first_name')
        kwargs = get_field_kwargs('first_name', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 30)

    def test_get_field_kwargs_for_char_field_with_verbose_name(self):
        field = self.TestModel._meta.get_field('middle_name')
        kwargs = get_field_kwargs('middle_name', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 30)
        self.assertEqual(kwargs['label'], 'Middle_name')

    def test_get_field_kwargs_for_char_field_with_help_text(self):
        field = self.TestModel._meta.get_field('last_name')
        kwargs = get_field_kwargs('last_name', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 30)
        self.assertEqual(kwargs['help_text'], 'last_name help text')

    def test_get_field_kwargs_for_decimal_field_with_max_digits(self):
        field = self.TestModel._meta.get_field('salary')
        kwargs = get_field_kwargs('salary', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_digits'], 5)

    def test_get_field_kwargs_for_decimal_field_with_decimal_places(self):
        field = self.TestModel._meta.get_field('bonus_salary')
        kwargs = get_field_kwargs('bonus_salary', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['decimal_places'], 2)

    def test_get_field_kwargs_for_auto_field_as_readonly(self):
        field = self.TestModel._meta.get_field('id')
        kwargs = get_field_kwargs('id', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertTrue(kwargs['read_only'])

    def test_get_field_kwargs_for_nullable_boolean_field(self):
        field = self.TestModel._meta.get_field('has_car')
        kwargs = get_field_kwargs('has_car', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertFalse(kwargs['required'])

    def test_get_field_kwargs_for_nullable_field(self):
        field = self.TestModel._meta.get_field('phone')
        kwargs = get_field_kwargs('phone', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 30)
        self.assertFalse(kwargs['required'])
        self.assertTrue(kwargs['allow_null'])

    def test_get_field_kwargs_for_blank_field(self):
        field = self.TestModel._meta.get_field('additional_info')
        kwargs = get_field_kwargs('additional_info', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 30)
        self.assertFalse(kwargs['required'])
        self.assertTrue(kwargs['allow_blank'])

    def test_get_field_kwargs_for_filepath_field(self):
        field = self.TestModel._meta.get_field('photos')
        kwargs = get_field_kwargs('photos', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['path'], '/home/images')

    def test_get_field_kwargs_for_filepath_field_with_match(self):
        field = self.TestModel._meta.get_field('photos_with_match')
        kwargs = get_field_kwargs('photos_with_match', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['path'], '/home/images')
        self.assertEqual(kwargs['match'], 'img.*\.txt$')

    def test_get_field_kwargs_for_filepath_field_with_recursive(self):
        field = self.TestModel._meta.get_field('photos_with_recursive')
        kwargs = get_field_kwargs('photos_with_recursive', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['path'], '/home/images')
        self.assertTrue(kwargs['recursive'])

    def test_get_field_kwargs_for_filepath_field_without_allow_files(self):
        field = self.TestModel._meta.get_field('photos_without_allow_files')
        kwargs = get_field_kwargs('photos_without_allow_files', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['path'], '/home/images')
        self.assertFalse(kwargs['allow_files'])

    def test_get_field_kwargs_for_filepath_field_with_allow_folders(self):
        field = self.TestModel._meta.get_field('photos_with_allow_folders')
        kwargs = get_field_kwargs('photos_with_allow_folders', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['path'], '/home/images')
        self.assertTrue(kwargs['allow_folders'])

    def test_get_field_kwargs_for_field_with_choices(self):
        field = self.TestModel._meta.get_field('position')
        kwargs = get_field_kwargs('position', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['choices'], self.TestModel.POSITION)

    def test_get_field_kwargs_for_decimal_field_with_validator(self):
        field = self.TestModel._meta.get_field('rate')
        kwargs = get_field_kwargs('rate', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, DecimalValidator)
            ]
        )

    def test_get_field_kwargs_for_char_field_with_max_length_validator(self):
        field = self.TestModel._meta.get_field('about')
        kwargs = get_field_kwargs('about', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 255)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, MaxLengthValidator)
            ]
        )

    def test_get_field_kwargs_for_char_field_with_min_length_validator(self):
        field = self.TestModel._meta.get_field('cover_letter')
        kwargs = get_field_kwargs('cover_letter', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_length'], 255)
        self.assertEqual(kwargs['min_length'], 100)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, (MinLengthValidator, MaxLengthValidator))  # NOQA
            ]
        )

    def test_get_field_kwargs_for_char_field_with_max_value_validator(self):
        field = self.TestModel._meta.get_field('max_rate')
        kwargs = get_field_kwargs('max_rate', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['max_value'], 100)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, (MinValueValidator, MaxValueValidator))  # NOQA
                ]
        )

    def test_get_field_kwargs_for_char_field_with_min_value_validator(self):
        field = self.TestModel._meta.get_field('min_rate')
        kwargs = get_field_kwargs('min_rate', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(kwargs['min_value'], 0)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, (MinValueValidator, MaxValueValidator))  # NOQA
            ]
        )

    def test_get_field_kwargs_for_url_field_with_validator(self):
        field = self.TestModel._meta.get_field('url')
        kwargs = get_field_kwargs('url', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if not isinstance(validator, (URLValidator, MaxLengthValidator))  # NOQA
            ]
        )

    def test_get_field_kwargs_for_email_field_with_validator(self):
        field = self.TestModel._meta.get_field('email')
        kwargs = get_field_kwargs('email', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if validator is not validate_email and
                not isinstance(validator, MaxLengthValidator)
            ]
        )

    def test_get_field_kwargs_for_slug_field_with_validator(self):
        field = self.TestModel._meta.get_field('slug')
        kwargs = get_field_kwargs('slug', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if validator is not validate_slug and
                not isinstance(validator, MaxLengthValidator)
            ]
        )

    def test_get_field_kwargs_for_ip_address_field_with_validator(self):
        field = self.TestModel._meta.get_field('ip_address')
        kwargs = get_field_kwargs('ip_address', field)
        self.assertEqual(kwargs['model_field'], field)
        self.assertEqual(
            kwargs['validators'],
            [
                validator for validator in list(field.validators)
                if validator is not validate_ipv46_address and
                not isinstance(validator, MaxLengthValidator)
            ]
        )


class TestGetRelationKwargsFunction(DjangoUnitTest):

    class Author(models.Model):
        id = models.IntegerField(primary_key=True, editable=False)
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_relation_kwargs_function'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_relation_kwargs_function'

    class PublisherAddress(models.Model):
        publisher = models.ForeignKey(
            "test_django_get_relation_kwargs_function.Publisher",
            related_name='address', null=True, blank=True, default=None,
            validators=[CustomValidator(None), ]
        )
        street = models.CharField(max_length=255)
        apartments = models.CharField(max_length=255)
        phone = models.CharField(max_length=255)

        class Meta:
            app_label = 'test_django_get_relation_kwargs_function'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_get_relation_kwargs_function.Publisher",
            related_name='books', unique=True
        )
        authors = models.ManyToManyField(
            "test_django_get_relation_kwargs_function.Author",
            help_text="authors of the book"
        )

        class Meta:
            app_label = 'test_django_get_relation_kwargs_function'

    apps = ('test_django_get_relation_kwargs_function', )
    models = (Author, Publisher, PublisherAddress, Book)

    def test_get_relation_kwargs_for_nullable_fk_field_with_validators(self):
        model_field = self.PublisherAddress._meta.get_field('publisher')
        relation_info = RelationInfo(
            model_field=model_field,
            related_model=self.PublisherAddress,
            to_many=True,
            to_field=self.Publisher._meta.get_field('id'),
            has_through_model=False
        )
        self.assertEqual(
            get_relation_kwargs('publisher', relation_info),
            {
                'allow_null': True,
                'label': 'Publisher',
                'many': True,
                'queryset': self.PublisherAddress._default_manager,
                'required': False,
                'to_field': self.Publisher._meta.get_field('id'),
                'validators': model_field.validators,
                'view_name': 'publisheraddress-detail'
            }
        )

    def test_get_relation_kwargs_for_unique_fk_field_(self):
        relation_info = RelationInfo(
            model_field=self.Book._meta.get_field('publisher'),
            related_model=self.Book,
            to_many=True,
            to_field=self.Publisher._meta.get_field('id'),
            has_through_model=False
        )
        kwargs = get_relation_kwargs('publisher', relation_info)
        validators = kwargs.pop('validators')
        self.assertEqual(
            kwargs,
            {
                'allow_empty': False,
                'label': 'Publisher',
                'many': True,
                'queryset': self.Book._default_manager,
                'to_field': self.Publisher._meta.get_field('id'),
                'view_name': 'book-detail'
            }
        )
        self.assertEqual(len(validators), 1)
        self.assertIsInstance(validators[0], UniqueValidator)
        self.assertEqual(
            validators[0].queryset,
            self.Book._default_manager
        )

    def test_get_relation_kwargs_for_m2m_field(self):
        relation_info = RelationInfo(
            model_field=self.Book._meta.get_field('authors'),
            related_model=self.Book,
            to_many=True,
            to_field=self.Author._meta.get_field('id'),
            has_through_model=True
        )
        self.assertEqual(
            get_relation_kwargs('authors', relation_info),
            {
                'label': 'Authors',
                'many': True,
                'read_only': True,
                'to_field': self.Author._meta.get_field('id'),
                'view_name': 'book-detail',
                'help_text': 'authors of the book'
            }
        )

    def test_get_relation_kwargs_for_reverse_m2m_field(self):
        relation_info = RelationInfo(
            model_field=self.Author._meta.get_field('id'),
            related_model=self.Author,
            to_many=True,
            to_field=self.Book._meta.get_field('id'),
            has_through_model=True
        )
        self.assertEqual(
            get_relation_kwargs('id', relation_info),
            {
                'label': 'Id',
                'many': True,
                'read_only': True,
                'to_field': self.Book._meta.get_field('id'),
                'view_name': 'author-detail'
            }
        )


class TestGetNestedRelationKwargsFunction(DjangoUnitTest):

    class Author(models.Model):
        id = models.IntegerField(primary_key=True, editable=False)
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_nested_relation_kwargs_function'

    class Publisher(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_nested_relation_kwargs_function'

    class PublisherAddress(models.Model):
        street = models.CharField(max_length=255)
        apartments = models.CharField(max_length=255)
        phone = models.CharField(max_length=255)
        publisher = models.OneToOneField(
            "test_django_get_nested_relation_kwargs_function.Publisher"
        )

        class Meta:
            app_label = 'test_django_get_nested_relation_kwargs_function'

    class Book(models.Model):
        name = models.CharField(max_length=30)
        publisher = models.ForeignKey(
            "test_django_get_nested_relation_kwargs_function.Publisher",
            related_name='books'
        )
        authors = models.ManyToManyField(
            "test_django_get_nested_relation_kwargs_function.Author",
        )

        class Meta:
            app_label = 'test_django_get_nested_relation_kwargs_function'

    apps = ('test_django_get_nested_relation_kwargs_function', )
    models = (Author, Publisher, PublisherAddress, Book)

    def test_get_nested_relation_kwargs_for_one_to_one_field(self):
        relation_info = RelationInfo(
            model_field=self.PublisherAddress._meta.get_field('publisher'),
            related_model=self.PublisherAddress,
            to_many=False,
            to_field=self.Publisher._meta.get_field('id'),
            has_through_model=False
        )
        self.assertEqual(
            get_nested_relation_kwargs(relation_info),
            {'read_only': True}
        )

    def test_get_nested_relation_kwargs_for_fk_field(self):
        relation_info = RelationInfo(
            model_field=self.Book._meta.get_field('publisher'),
            related_model=self.Book,
            to_many=True,
            to_field=self.Publisher._meta.get_field('id'),
            has_through_model=False
        )
        self.assertEqual(
            get_nested_relation_kwargs(relation_info),
            {
                'read_only': True,
                'many': True
            }
        )

    def test_get_nested_relation_kwargs_for_m2m_field(self):
        relation_info = RelationInfo(
            model_field=self.Author._meta.get_field('id'),
            related_model=self.Author,
            to_many=True,
            to_field=self.Book._meta.get_field('id'),
            has_through_model=True
        )
        self.assertEqual(
            get_nested_relation_kwargs(relation_info),
            {
                'read_only': True,
                'many': True
            }
        )


class TestGetUrlKwargsFunction(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_get_url_kwargs_function'

    apps = ('test_django_get_url_kwargs_function', )
    models = (User, )

    def test_get_url_kwargs(self):
        self.assertEqual(
            get_url_kwargs(self.User),
            {'view_name': 'user-detail'}
        )
