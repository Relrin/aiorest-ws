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
        data = UserSerializer(users, many=True).data
        session.close()
        return data

    def post(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide arguments for create.')

        if not isinstance(request.data, list):
            raise ValidationError('You must provide a list of objects.')

        serializer = UserSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class UserView(MethodBasedView):

    def get(self, request, id, *args, **kwargs):
        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        data = UserSerializer(instance).data
        session.close()
        return data

    def put(self, request, id, *args, **kwargs):
        if not request.data:
            raise ValidationError('You must provide an updated instance.')

        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        if not instance:
            raise ValidationError('Object does not exist')

        serializer = UserSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        session.close()
        return data


class CreateUserView(MethodBasedView):

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class AddressView(MethodBasedView):

    def get(self, request, id, *args, **kwargs):
        session = settings.SQLALCHEMY_SESSION()
        instance = session.query(User).filter(User.id == id).first()
        data = AddressSerializer(instance).data
        session.close()
        return data


class CreateAddressView(MethodBasedView):

    def post(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
