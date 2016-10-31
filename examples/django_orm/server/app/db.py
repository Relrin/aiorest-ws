# -*- coding: utf-8 -*-
from django.db import models


class Manufacturer(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'django_orm_example'

    def __str__(self):
        return '<Manufacturer(%d: %s)>' % (self.id, self.name)


class Car(models.Model):
    name = models.CharField(max_length=30, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, related_name='cars')

    class Meta:
        app_label = 'django_orm_example'

    def __str__(self):
        return '<Car(%d: %s, %s)>' % (self.id, self.name, self.manufacturer)
