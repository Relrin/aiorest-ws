# -*- coding: utf-8 -*-
from aiorest_ws.conf import settings
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.views import MethodBasedView

from app.db import User
from app.serializers import AddressSerializer, UserSerializer


class UserListView(MethodBasedView):

    def get(self, request, *args, **kwargs):
        session = settings.SQLALCHEMY_SESSION()
        users = session.query(User).all()
        return UserSerializer(users, many=True).data

    def post(self, *args, **kwargs):
        data = kwargs.get('params', None)
        if not data:
            raise ValidationError('You must provide arguments for create.')

        created_obj_data = data.get('list' , [])
        if not data:
            raise ValidationError('You must provide a list of objects.')

        serializer = UserSerializer(data=created_obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class UserView(MethodBasedView):

    def get(self, request, id, *args, **kwargs):
        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        return UserSerializer(instance).data

    def put(self, request, id, *args, **kwargs):
        validated_data = kwargs.get('params', None)
        if not validated_data:
            raise ValidationError('You must provide an updated instance.')

        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        if not instance:
            raise ValidationError('Object does not exist')

        serializer = UserSerializer(instance, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class CreateUserView(MethodBasedView):

    def post(self, request, *args, **kwargs):
        validated_data = kwargs.get('params', None)
        serializer = UserSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class AddressView(MethodBasedView):

    def get(self, request, id, *args, **kwargs):
        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        return AddressSerializer(instance).data


class CreateAddressView(MethodBasedView):

    def post(self, request, *args, **kwargs):
        validated_data = kwargs.get('params', None)
        serializer = AddressSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
