# -*- coding: utf-8 -*-
from django.db import models

from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.django.serializers import ModelSerializer
from aiorest_ws.db.orm.django.validators import qs_filter, qs_exists, \
    UniqueValidator


from tests.db.orm.django.base import DjangoUnitTest


class TestQuerysetFunctions(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30)

        class Meta:
            app_label = 'test_django_queryset_functions'

        def __str__(self):
            return '<User(%s)>' % self.name

    apps = ('test_django_queryset_functions',)
    models = (User, )

    @classmethod
    def setUpClass(cls):
        super(TestQuerysetFunctions, cls).setUpClass()
        cls.User.objects.create(name='admin')

    def test_qs_exists_returns_true(self):
        queryset = self.User.objects.filter(name='admin')
        self.assertTrue(qs_exists(queryset))

    def test_qs_exists_returns_false(self):
        queryset = self.User.objects.filter(name='nonexistent_user')
        self.assertFalse(qs_exists(queryset))

    def test_qs_exists_returns_false_for_invalid_type(self):

        class InvalidType(object):

            def exists(self):
                raise TypeError()

        obj = InvalidType()
        self.assertFalse(qs_exists(obj))

    def test_qs_filter_returns_object(self):
        user = self.User.objects.get(name='admin')
        queryset = self.User.objects.all()
        result = qs_filter(queryset, name='admin')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], user)

    def test_qs_filter_returns_none_for_invalid_queryset(self):

        class InvalidQueryset(object):

            none_method_is_called = False

            def filter(self, **kwargs):
                raise ValueError()

            def none(self):
                self.none_method_is_called = True
                return None

        obj = InvalidQueryset()
        self.assertIsNone(qs_filter(obj))
        self.assertTrue(obj.none_method_is_called)


class TestUniqueValidator(DjangoUnitTest):

    class User(models.Model):
        name = models.CharField(max_length=30, unique=True)

        class Meta:
            app_label = 'test_django_unique_validator'

        def __str__(self):
            return '<User(%s)>' % self.name

    apps = ('test_django_queryset_functions', )
    models = (User, )

    @classmethod
    def setUpClass(cls):
        super(TestUniqueValidator, cls).setUpClass()
        cls.User.objects.create(name='admin')
        cls.User.objects.create(name='manager')
        cls.User.objects.create(name='author')

        class UserSerializer(ModelSerializer):

            class Meta:
                model = cls.User

        cls.user_serializer = UserSerializer

    def test_set_context(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        self.assertEqual(validator.field_name, 'name')
        self.assertIsNone(validator.instance)

    def test_filter_queryset(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        filtered_queryset = validator.filter_queryset('admin', queryset)
        self.assertEqual(len(filtered_queryset), 1)
        self.assertIsInstance(filtered_queryset[0], self.User)
        self.assertEqual(filtered_queryset[0].name, 'admin')

    def test_filter_queryset_returns_empty_queryset(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        filtered_queryset = validator.filter_queryset('anonymous', queryset)
        self.assertEqual(len(filtered_queryset), 0)

    def test_exclude_current_instance_returns_queryset(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        self.assertEqual(
            validator.exclude_current_instance(queryset),
            queryset
        )

    def test_exclude_current_instance_returns_queryset_with_exclude(self):
        admin = self.User.objects.get(name='admin')
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        serializer.fields['name'].parent.instance = admin
        validator.set_context(serializer.fields['name'])
        filtered_queryset = validator.exclude_current_instance(queryset)
        self.assertNotIn(queryset, filtered_queryset)

    def test_call_passed_successfully(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        self.assertIsNone(validator('unnamed'))

    def test_call_raises_validation_error(self):
        queryset = self.User.objects.all()
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        self.assertRaises(ValidationError, validator, 'admin')

    def test_repr(self):
        queryset = self.User.objects.all().order_by('id')
        serializer = self.user_serializer()
        validator = UniqueValidator(queryset)
        validator.set_context(serializer.fields['name'])
        self.assertEqual(
            validator.__repr__(),
            "'<UniqueValidator(queryset=<QuerySet [<User: <User(admin)>>, "
            "<User: <User(manager)>>, <User: <User(author)>>]>)>'"
        )
