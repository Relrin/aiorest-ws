# -*- coding: utf-8 -*-
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.views import MethodBasedView

from django.core.exceptions import ObjectDoesNotExist

from app.db import Manufacturer, Car
from app.serializers import ManufacturerSerializer, CarSerializer


class ManufacturerListView(MethodBasedView):

    def get(self, request, *args, **kwargs):
        instances = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(instances, many=True)
        return serializer.data

    def post(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide arguments for create.')

        serializer = ManufacturerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class ManufacturerView(MethodBasedView):

    def get_manufacturer(self, name):
        try:
            manufacturer = Manufacturer.objects.get(name__iexact=name)
        except ObjectDoesNotExist:
            raise ValidationError("The requested object does not exist")

        return manufacturer

    def get(self, request, name, *args, **kwargs):
        manufacturer = self.get_manufacturer(name)
        serializer = ManufacturerSerializer(manufacturer)
        return serializer.data

    def put(self, request, name, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide arguments for create.')

        instance = self.get_manufacturer(name)
        serializer = ManufacturerSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class CarListView(MethodBasedView):

    def get(self, request, *args, **kwargs):
        data = Car.objects.all()
        serializer = CarSerializer(data, many=True)
        return serializer.data

    def post(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide arguments for create.')

        serializer = CarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class CarView(MethodBasedView):

    def get_car(self, name):
        try:
            car = Car.objects.get(name__iexact=name)
        except ObjectDoesNotExist:
            raise ValidationError("The requested object does not exist")

        return car

    def get(self, request, name, *args, **kwargs):
        instance = self.get_car(name)
        serializer = CarSerializer(instance)
        return serializer.data

    def put(self, request, name, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide data for update.')

        instance = self.get_car(name)
        serializer = CarSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
