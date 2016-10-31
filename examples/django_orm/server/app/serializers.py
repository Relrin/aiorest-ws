# -*- coding: utf-8 -*-
from aiorest_ws.db.orm.django import serializers

from app.db import Manufacturer, Car


class ManufacturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer


class CarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Car
