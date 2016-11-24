# -*- coding: utf-8 -*-
import unittest
import uuid

from django.db import models
from django.core.validators import BaseValidator as DjangoBaseValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm.abstract import empty
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.serializers import Serializer
from aiorest_ws.db.orm.django import fields
from aiorest_ws.db.orm.django.serializers import ListSerializer, \
    ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField, \
    get_validation_error_detail
from aiorest_ws.db.orm.validators import BaseValidator

from tests.db.orm.django.base import DjangoUnitTest


class TestGetValidationErrorDetailFunction(unittest.TestCase):

    def test_function_raises_assert_error_for_invalid_exception_type(self):
        exc = ValueError()
        self.assertRaises(AssertionError, get_validation_error_detail, exc)

    def test_function_returns_dict_for_django_validation_error(self):
        message = '@ must be in email address'
        exc = DjangoValidationError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertEqual(detail['non_field_errors'][0], message)

    def test_function_returns_dict_for_exception_with_message_as_dict(self):
        message = {'email': '@ must be in email address'}
        exc = ValidationError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('email', detail.keys())
        self.assertEqual(detail['email'][0], message['email'])

    def test_function_returns_dict_for_exception_with_message_as_list(self):
        message = ['@ must be in email address', ]
        exc = ValidationError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertIsInstance(detail['non_field_errors'], list)
        self.assertEqual(len(detail['non_field_errors']), 1)
        self.assertEqual(detail['non_field_errors'], message)

    def test_function_returns_dict_for_exception_with_message_as_string(self):
        message = '@ must be in email address'
        exc = ValidationError('expected message')
        exc.detail = message  # someone patched object
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertIsInstance(detail['non_field_errors'], list)
        self.assertEqual(len(detail['non_field_errors']), 1)
        self.assertEqual(detail['non_field_errors'][0], message)


class TestListSerializer(unittest.TestCase):

    class FakeSerializer(Serializer):
        default_list_serializer = ListSerializer
        pk = fields.IntegerField()

        def run_validation(self, data=empty):
            return self.to_internal_value(data)

    def test_run_validation_returns_value(self):
        instance = self.FakeSerializer(many=True)
        self.assertEqual(
            instance.run_validation([{'pk': 1}, ]),
            [{'pk': 1}, ]
        )

    def test_run_validation_returns_value_for_empty_value(self):
        instance = self.FakeSerializer(many=True, allow_null=True)
        self.assertEqual(instance.run_validation(None), None)

    def test_run_validation_raises_validation_error(self):

        class NegativePkValidator(DjangoBaseValidator):

            def __call__(self, data):
                for obj in data:
                    if obj['pk'] < 0:
                        raise ValidationError("PKs can't be negative.")

        class CustomListSerializer(ListSerializer):
            validators = [NegativePkValidator(10), ]

        class InvalidFakeSerializer(self.FakeSerializer):

            class Meta:
                list_serializer_class = CustomListSerializer

        instance = InvalidFakeSerializer(many=True)
        self.assertRaises(
            ValidationError,
            instance.run_validation,
            [{'pk': -1}, ]
        )

    def test_run_validation_raises_assertion_error_for_none_value(self):

        class CustomListSerializer(ListSerializer):
            def validate(self, data):
                return None  # suppose, that something happens wrong

        class InvalidFakeSerializer(self.FakeSerializer):
            class Meta:
                list_serializer_class = CustomListSerializer

        instance = InvalidFakeSerializer(many=True)
        self.assertRaises(
            AssertionError,
            instance.run_validation,
            [{'pk': 1}, ]
        )


class TestModelSerializer(DjangoUnitTest):

    class Author(models.Model):
        name = models.CharField(max_length=100, unique=True)

        class Meta:
            app_label = 'test_django_model_serializer'

    class Course(models.Model):
        ACTIVE = 0
        INACTIVE = 1
        STATUS_CHOICES = (
            (ACTIVE, 'active'),
            (INACTIVE, 'inactive')
        )
        author = models.CharField(max_length=100)
        name = models.CharField(max_length=100, unique_for_date="created_at")
        created_at = models.DateTimeField(auto_now_add=True)
        modified_at = models.DateTimeField(auto_now=True)
        lecturer = models.CharField(
            max_length=100, default=None, null=True, blank=True
        )
        status = models.IntegerField(
            choices=STATUS_CHOICES, default=ACTIVE, null=True, blank=True
        )

        @property
        def course_info(self):
            return "<Course #{} by {}>".format(self.name, self.author)

        class Meta:
            app_label = 'test_django_model_serializer'
            unique_together = (('author', 'name'), )

    class Publisher(models.Model):
        name = models.CharField(max_length=100)
        profit = models.IntegerField(null=True)

        class Meta:
            app_label = 'test_django_model_serializer'

    class PublisherAddress(models.Model):
        street = models.CharField(max_length=255)
        apartments = models.CharField(max_length=255)
        phone = models.CharField(max_length=255, null=True)
        publisher = models.ForeignKey(
            "test_django_model_serializer.Publisher",
            null=True, related_name='publisher_address'
        )

        class Meta:
            app_label = 'test_django_model_serializer'

    class Book(models.Model):
        name = models.CharField(max_length=100)
        publishers = models.ManyToManyField(
            "test_django_model_serializer.Publisher", related_name='books',
        )

        class Meta:
            app_label = 'test_django_model_serializer'

    apps = ('test_django_model_serializer', )
    models = (Author, Course, Publisher, PublisherAddress, Book)

    def test_create(self):

        class PublisherSerializer(ModelSerializer):

            class Meta:
                model = self.Publisher

        data = {'name': 'publisher_{}'.format(uuid.uuid4())}
        instance = PublisherSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.data)
        publisher = self.Publisher.objects.get(name=data['name'])

        self.assertIsInstance(publisher, self.Publisher)
        self.assertEqual(publisher.name, data['name'])

        publisher.delete()

    def test_create_object_with_fk(self):

        class PublisherAddressSerializer(ModelSerializer):

            class Meta:
                model = self.PublisherAddress

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)

        data = {
            'street': 'some street',
            'apartments': 'some apartments',
            'phone': '123-456-789',
            'publisher': publisher.pk
        }
        instance = PublisherAddressSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        publisher_address = self.PublisherAddress.objects.get(
            apartments=data['apartments'], street=data['street'],
            phone=data['phone']
        )

        self.assertIsInstance(publisher_address, self.PublisherAddress)
        self.assertEqual(publisher_address.street, data['street'])
        self.assertEqual(publisher_address.apartments, data['apartments'])
        self.assertEqual(publisher_address.phone, data['phone'])
        self.assertEqual(publisher_address.publisher.pk, publisher.pk)

        publisher_address.delete()
        publisher.delete()

    def test_create_object_with_m2m(self):

        class BookSerializer(ModelSerializer):

            class Meta:
                model = self.Book

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)
        data = {
            'name': 'book_{}'.format(uuid.uuid4()),
            'publishers': [publisher.pk, ]
        }
        instance = BookSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        book = self.Book.objects.get(name=data['name'])
        publisher.refresh_from_db()

        self.assertIsInstance(book, self.Book)
        self.assertEqual(book.name, data['name'])
        self.assertEqual(
            set(publisher.books.all().values_list('pk', flat=True)),
            {book.pk, }
        )

        book.delete()
        publisher.delete()

    def test_create_raises_type_error(self):
        class BookSerializer(ModelSerializer):
            class Meta:
                model = self.Book

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)
        data = {
            'name': 'book_{}'.format(uuid.uuid4()),
            'publishers': [publisher.pk, ]
        }
        instance = BookSerializer(data=data)
        instance.is_valid(raise_exception=True)

        data['profit'] = "not_a_number"
        self.assertRaises(TypeError, instance.create, data)

        publisher.delete()

    def test_update(self):

        class PublisherAddressSerializer(ModelSerializer):

            class Meta:
                model = self.PublisherAddress

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)

        data = {
            'street': 'some street',
            'apartments': 'some apartments',
            'phone': '123-456-789',
            'publisher': publisher.pk
        }
        instance = PublisherAddressSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        publisher_address = self.PublisherAddress.objects.get(
            apartments=data['apartments'], street=data['street'],
            phone=data['phone']
        )

        self.assertIsInstance(publisher_address, self.PublisherAddress)
        self.assertEqual(publisher_address.street, data['street'])
        self.assertEqual(publisher_address.apartments, data['apartments'])
        self.assertEqual(publisher_address.phone, data['phone'])
        self.assertEqual(publisher_address.publisher.pk, publisher.pk)

        data = {
            'street': 'new some street',
            'apartments': 'new some apartments',
            'phone': '123-456-789-000',
        }
        instance = PublisherAddressSerializer(
            publisher_address, data=data, partial=True
        )
        instance.is_valid(raise_exception=True)
        updated_publisher_address = instance.save()
        self.assertEqual(updated_publisher_address.street, data['street'])
        self.assertEqual(
            updated_publisher_address.apartments,
            data['apartments']
        )
        self.assertEqual(updated_publisher_address.phone, data['phone'])
        self.assertEqual(updated_publisher_address.publisher.pk, publisher.pk)

        publisher_address.delete()
        publisher.delete()

    def test_update_with_relations(self):

        class PublisherAddressSerializer(ModelSerializer):
            class Meta:
                model = self.PublisherAddress

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)

        data = {
            'street': 'some street',
            'apartments': 'some apartments',
            'phone': '123-456-789',
        }
        instance = PublisherAddressSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        publisher_address = self.PublisherAddress.objects.get(
            apartments=data['apartments'], street=data['street'],
            phone=data['phone']
        )

        self.assertIsInstance(publisher_address, self.PublisherAddress)
        self.assertEqual(publisher_address.street, data['street'])
        self.assertEqual(publisher_address.apartments, data['apartments'])
        self.assertEqual(publisher_address.phone, data['phone'])
        self.assertIsNone(publisher_address.publisher)

        data = {
            'street': 'new some street {}'.format(uuid.uuid4()),
            'apartments': 'new some apartments',
            'phone': '123-456-789-000',
            'publisher': publisher.pk
        }
        instance = PublisherAddressSerializer(
            publisher_address, data=data, partial=True
        )
        instance.is_valid(raise_exception=True)
        updated_publisher_address = instance.save()
        self.assertEqual(updated_publisher_address.street, data['street'])
        self.assertEqual(
            updated_publisher_address.apartments,
            data['apartments']
        )
        self.assertEqual(updated_publisher_address.phone, data['phone'])
        self.assertEqual(updated_publisher_address.publisher.pk, publisher.pk)

        publisher_address.delete()
        publisher.delete()

    def test_update_return_updated_object_after_deletion(self):

        class PublisherAddressSerializer(ModelSerializer):

            class Meta:
                model = self.PublisherAddress

        publisher_name = 'publisher_{}'.format(uuid.uuid4())
        publisher = self.Publisher.objects.create(name=publisher_name)

        data = {
            'street': 'new some street {}'.format(uuid.uuid4()),
            'apartments': 'some apartments',
            'phone': '123-456-789',
        }
        instance = PublisherAddressSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        publisher_address = self.PublisherAddress.objects.get(
            apartments=data['apartments'], street=data['street'],
            phone=data['phone']
        )

        self.assertIsInstance(publisher_address, self.PublisherAddress)
        self.assertEqual(publisher_address.street, data['street'])
        self.assertEqual(publisher_address.apartments, data['apartments'])
        self.assertEqual(publisher_address.phone, data['phone'])
        self.assertIsNone(publisher_address.publisher)

        update_data = {'publisher': publisher.pk}
        instance = PublisherAddressSerializer(
            publisher_address, data=update_data, partial=True
        )
        instance.is_valid(raise_exception=True)
        publisher_address.delete()
        instance.save()

        new_publisher_address = self.PublisherAddress.objects.get(
            apartments=data['apartments'], street=data['street'],
            phone=data['phone']
        )
        self.assertEqual(publisher_address.pk, new_publisher_address.pk)
        self.assertEqual(publisher_address.street, data['street'])
        self.assertEqual(publisher_address.apartments, data['apartments'])
        self.assertEqual(publisher_address.phone, data['phone'])
        self.assertEqual(publisher_address.publisher.pk, publisher.pk)

        new_publisher_address.delete()
        publisher.delete()

    def test_run_validation(self):

        class AuthorSerializer(ModelSerializer):

            class Meta:
                model = self.Author

        data = {'name': 'Author #{}'.format(uuid.uuid4())}
        instance = AuthorSerializer(data=data)

        self.assertEqual(instance.run_validation(data), data)

    def test_run_validation_returns_empty_value(self):

        class BookSerializer(ModelSerializer):

            class Meta:
                model = self.Book

        instance = BookSerializer(allow_null=True)

        self.assertIsNone(instance.run_validation(None))

    def test_run_validation_raises_error_for_assert(self):

        class AuthorSerializer(ModelSerializer):

            class Meta:
                model = self.Author

            def validate(self, data):
                return None  # suppose, that something happens wrong

        data = {'name': 'Author #{}'.format(uuid.uuid4())}
        instance = AuthorSerializer(data=data)

        self.assertRaises(AssertionError, instance.run_validation, data)

    def test_run_validation_raises_error_for_validation_error(self):

        class AuthorNameValidator(BaseValidator):

            def __call__(self, data):
                if data['name'] == 'test':
                    raise ValidationError("Invalid author name.")

        class AuthorSerializer(ModelSerializer):

            class Meta:
                model = self.Author
                validators = [AuthorNameValidator(), ]

        data = {'name': 'test'}
        instance = AuthorSerializer(data=data)

        self.assertRaises(ValidationError, instance.run_validation, data)

    def test_get_unique_constraint_names(self):

        class CourseSerializer(ModelSerializer):

            class Meta:
                model = self.Course

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)
        info = instance.get_field_info(instance.Meta.model)
        field_names = instance.get_field_names(instance._declared_fields, info)
        extra_kwargs = instance.get_uniqueness_extra_kwargs(
            field_names, instance._declared_fields, instance.get_extra_kwargs()
        )[0]
        model_fields = instance._get_model_fields(
            field_names, instance._declared_fields, extra_kwargs
        )

        self.assertEqual(
            instance._get_unique_constraint_names(
                instance.Meta.model, model_fields, field_names
            ),
            {'created_at', }
        )

    def test_get_unique_together_constraints(self):

        class CourseSerializer(ModelSerializer):

            class Meta:
                model = self.Course

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)
        info = instance.get_field_info(instance.Meta.model)
        field_names = instance.get_field_names(instance._declared_fields, info)
        extra_kwargs = instance.get_uniqueness_extra_kwargs(
            field_names, instance._declared_fields, instance.get_extra_kwargs()
        )[0]
        model_fields = instance._get_model_fields(
            field_names, instance._declared_fields, extra_kwargs
        )

        self.assertEqual(
            instance._get_unique_together_constraints(
                instance.Meta.model, model_fields, field_names
            ),
            {'name', 'author'}
        )

    def test_get_unique_field(self):

        class CourseSerializer(ModelSerializer):

            class Meta:
                model = self.Course

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)

        self.assertEqual(
            instance._get_unique_field(self.Course, 'created_at'),
            self.Course._meta.get_field('created_at')
        )

    def test_get_default_field_value(self):

        class CourseSerializer(ModelSerializer):

            class Meta:
                model = self.Course

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)

        name_field = self.Course._meta.get_field('name')
        created_at_field = self.Course._meta.get_field('created_at')
        modified_at_field = self.Course._meta.get_field('modified_at')
        lecturer_field = self.Course._meta.get_field('lecturer')
        self.assertEqual(
            instance._get_default_field_value(name_field),
            empty
        )
        self.assertEqual(
            instance._get_default_field_value(created_at_field).default,
            timezone.now
        )
        self.assertEqual(
            instance._get_default_field_value(modified_at_field),
            timezone.now
        )
        self.assertEqual(
            instance._get_default_field_value(lecturer_field),
            lecturer_field.default
        )

    def test_build_standard_field_for_choices(self):

        class CourseSerializer(ModelSerializer):
            class Meta:
                model = self.Course

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)

        self.assertIn('status', instance.fields.keys())
        self.assertIsInstance(
            instance.fields['status'], fields.ChoiceField
        )
        self.assertEqual(
            instance.fields['status']._kwargs,
            {
                'allow_null': True,
                'choices': self.Course.STATUS_CHOICES,
                'required': False
            }
        )

    def test_build_nested_field(self):

        class PublisherAddressSerializer(ModelSerializer):

            class Meta:
                model = self.PublisherAddress
                depth = 1

        data = {
            'street': 'new some street {}'.format(uuid.uuid4()),
            'apartments': 'some apartments',
            'phone': '123-456-789',
        }
        instance = PublisherAddressSerializer(data=data)

        publisher_serializer = instance.fields['publisher']
        self.assertIsInstance(publisher_serializer, ModelSerializer)
        self.assertEqual(
            publisher_serializer.__class__.__name__,
            "NestedSerializer"
        )

    def test_build_property_field(self):

        class CourseSerializer(ModelSerializer):

            class Meta:
                model = self.Course
                fields = ('name', 'author', 'lecturer', 'course_info')

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)

        self.assertIsInstance(
            instance.fields['course_info'],
            fields.ReadOnlyField
        )

    def test_build_url_field(self):

        class CourseSerializer(HyperlinkedModelSerializer):

            class Meta:
                model = self.Course
                fields = ('url', 'name', 'author', 'lecturer')
                extra_kwargs = {'url': {'view_name': 'courses'}}

        data = {
            'author': 'user #{}'.format(uuid.uuid4()),
            'name': 'name #{}'.format(uuid.uuid4()),
            'lecturer': 'unknown lecturer',
        }
        instance = CourseSerializer(data=data)

        url_serializer = instance.fields['url']
        self.assertIsInstance(url_serializer, HyperlinkedIdentityField)
        self.assertEqual(
            url_serializer.__class__.__name__,
            "HyperlinkedIdentityField"
        )

    def test_build_unknown_field(self):

        class AuthorSerializer(ModelSerializer):

            class Meta:
                model = self.Author
                fields = ('name', 'invalid_field')

        data = {'name': 'unknown author'}
        instance = AuthorSerializer(data=data)

        with self.assertRaises(ImproperlyConfigured):
            serializer_fields = instance.fields  # NOQA


class TestHyperlinkModelSerializer(DjangoUnitTest):

    class Publisher(models.Model):
        name = models.CharField(max_length=100)
        profit = models.IntegerField(null=True)

        class Meta:
            app_label = 'test_django_hyperlink_model_serializer'

    class PublisherAddress(models.Model):
        street = models.CharField(max_length=255)
        apartments = models.CharField(max_length=255)
        phone = models.CharField(max_length=255, null=True)
        publisher = models.ForeignKey(
            "test_django_hyperlink_model_serializer.Publisher",
            null=True, related_name='publisher_address'
        )

        class Meta:
            app_label = 'test_django_hyperlink_model_serializer'

    apps = ('test_django_hyperlink_model_serializer', )
    models = (Publisher, PublisherAddress, )

    def test_build_nested_field(self):

        class PublisherAddresskSerializer(HyperlinkedModelSerializer):

            class Meta:
                model = self.PublisherAddress
                depth = 1
                fields = ('url', 'street', 'apartments', 'phone', 'publisher')
                extra_kwargs = {'url': {'view_name': 'books'}}

        data = {
            'street': 'new some street {}'.format(uuid.uuid4()),
            'apartments': 'some apartments',
            'phone': '123-456-789',
        }
        instance = PublisherAddresskSerializer(data=data)

        publisher_serializer = instance.fields['publisher']
        self.assertIsInstance(publisher_serializer, HyperlinkedModelSerializer)
        self.assertEqual(
            publisher_serializer.__class__.__name__,
            "NestedSerializer"
        )
