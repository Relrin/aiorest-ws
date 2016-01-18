# -*- coding: utf-8 -*-
from app.db import User, Address
from aiorest_ws.db.orm.sqlalchemy import serializers

from sqlalchemy.orm import Query


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('id', 'email_address')


class UserSerializer(serializers.ModelSerializer):
    addresses = serializers.PrimaryKeyRelatedField(
        queryset=Query(Address), many=True, required=False,
    )

    class Meta:
        model = User
