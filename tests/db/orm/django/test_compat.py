# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from aiorest_ws.db.orm.django.compat import _resolve_model, \
    get_related_model, get_remote_field, value_from_object

from tests.db.orm.django.base import DjangoUnitTest


class CustomStringField(models.CharField):
    pass


class TestDjangoCompatModule(DjangoUnitTest):

    class Manufacturer(models.Model):
        name = CustomStringField(max_length=30)

        class Meta:
            app_label = 'test_django_compat_module'

        def __str__(self):
            return '<Manufacturer(%s)>' % self.name

    class Car(models.Model):
        name = models.CharField(max_length=30)
        max_speed = models.FloatField(null=True, blank=True)
        manufacturer = models.ForeignKey(
            "test_django_compat_module.Manufacturer", related_name='cars',
            null=True, blank=True
        )

        class Meta:
            app_label = 'test_django_compat_module'

        def __str__(self):
            return '<Car(%s, %s)>' % (self.name, self.manufacturer)

    apps = ('test_django_compat_module', )
    models = (Manufacturer, Car)

    @classmethod
    def setUpClass(cls):
        super(TestDjangoCompatModule, cls).setUpClass()
        user = cls.Manufacturer.objects.create(name='TestName')
        car = cls.Car.objects.create(name='TestCar', max_speed=350)
        user.cars.add(car)
        user.save()

    def test_resolve_model_return_object(self):
        self.assertEqual(_resolve_model(self.Manufacturer), self.Manufacturer)

    def test_resolve_model_return_object_by_model_as_string(self):

        class FakeCarConfig(object):

            model_mapping = {
                'car': self.Car
            }

            def get_model(config, model_name):
                return config.model_mapping.get(model_name, None)

        patched_module = 'django.apps.apps.app_configs'
        patched_value = {'test_django_compat_module': FakeCarConfig()}
        with patch(patched_module, new=patched_value):
            value = "test_django_compat_module.car"
            self.assertEqual(_resolve_model(value), self.Car)

    def test_resolve_model_raises_improperly_configured_exception(self):

        class FakeConfig(object):

            def get_model(self, model_name):
                return None

        patched_module = 'django.apps.apps.app_configs'
        patched_value = {'invalid_app': FakeConfig()}
        with patch(patched_module, new=patched_value):
            value = "invalid_app.fake_model"
            self.assertRaises(ImproperlyConfigured, _resolve_model, value)

    def test_resolve_model_raises_value_error_exception(self):

        class NotDjangoModel(object):
            pass

        obj = NotDjangoModel()
        self.assertRaises(ValueError, _resolve_model, obj)

    def test_get_related_model(self):
        field = self.Car._meta.get_field('manufacturer')
        self.assertEqual(get_related_model(field), field.remote_field.model)

    def test_get_remote_field(self):
        field = self.Car._meta.get_field('manufacturer')
        self.assertEqual(get_remote_field(field), field.remote_field)

    def test_value_from_object(self):
        field = self.Manufacturer._meta.get_field('name')
        obj = self.Manufacturer.objects.get(name='TestName')
        self.assertEqual(value_from_object(field, obj), obj.name)
