# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.auth.exceptions import PermissionDeniedException
from aiorest_ws.auth.permissions import AbstractPermission, IsAuthenticated
from aiorest_ws.auth.token.exceptions import TokenNotProvidedException
from aiorest_ws.auth.token.middlewares import BaseTokenMiddleware, \
    JSONWebTokenMiddleware
from aiorest_ws.auth.user.abstractions import User
from aiorest_ws.conf import settings
from aiorest_ws.views import MethodBasedView
from aiorest_ws.wrappers import Request
from aiorest_ws.utils.modify import add_property

from tests.fixtures.fakes import FakeGetView
from tests.fixtures.example_settings import DATABASES


class BaseTokenMiddlewareTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.middleware = BaseTokenMiddleware()

    def test_init_credentials(self):
        request = Request()
        self.assertIsNone(self.middleware.init_credentials(request))

    def test_authenticate(self):
        request = Request()
        handler = FakeGetView()
        self.assertIsNone(self.middleware.authenticate(request, handler))

    def test_process_request(self):
        request = Request()
        handler = FakeGetView()
        self.assertIsNone(self.middleware.process_request(request, handler))


class JSONWebTokenMiddlewareTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings.DATABASES = DATABASES
        settings._create_database_managers()
        cls.middleware = JSONWebTokenMiddleware()

    def _create_simple_user(self, user_model, **kwargs):
        username = kwargs.get('username', None) or 'testuser'
        user_data = {
            'username': username,
            'password': kwargs.get('password', None) or '123456',
            'first_name': kwargs.get('first_name', None) or 'test',
            'last_name': kwargs.get('last_name', None) or 'user',
            'is_active': kwargs.get('is_active', None) or True,
            'is_superuser': kwargs.get('is_superuser', None) or False,
            'is_staff': kwargs.get('is_staff', None) or False,
            'is_user': kwargs.get('is_user', None) or True,
        }
        user_model.create_user(**user_data)
        user = user_model.get_user_by_username(username, with_id=True)
        return user

    def test_get_user_by_token(self):
        user = self._create_simple_user(self.middleware.user_model)
        token_data = {
            'name': 'api',
            'token': 'my_test_token',
            'user_id': user.id
        }
        self.middleware.storage_backend.save(
            token_data['name'],
            token_data['token'],
            user_id=token_data['user_id']
        )
        user = self.middleware.get_user_by_token(token_data['token'])
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_user)

    def test_get_anonymous_user_by_not_existed_token(self):
        user = self.middleware.get_user_by_token('unknown')
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_anonymous)

    def test_init_credentials(self):
        user = self._create_simple_user(self.middleware.user_model)
        token_data = {'key': 'value'}
        raw_token = self.middleware.manager.generate(token_data)
        init_data = {
            'name': 'api',
            'token': raw_token,
            'user_id': user.id
        }
        self.middleware.storage_backend.save(
            init_data['name'],
            init_data['token'],
            user_id=init_data['user_id']
        )

        request = Request()
        add_property(request, 'token', raw_token)
        self.middleware.init_credentials(request)
        self.assertIsInstance(request.user, User)
        self.assertTrue(request.user.is_user)
        self.assertIsNotNone(request.token_payload)

    def test_init_credentials_without_token(self):
        request = Request()
        self.middleware.init_credentials(request)
        self.assertIsInstance(request.user, User)
        self.assertTrue(request.user.is_anonymous)
        self.assertIsNone(request.token_payload)

    def test_authenticate(self):
        class TestView(MethodBasedView):
            auth_required = True

        user = User(is_user=True)
        token_data = {'key': 'value'}
        raw_token = self.middleware.manager.generate(token_data)

        request = Request()
        add_property(request, 'user', user)
        add_property(request, 'token', raw_token)
        view = TestView()
        self.assertIsNone(self.middleware.authenticate(request, view))

    def test_authenticate_with_permissions(self):
        class ViewWithIsAuthenticatedPermission(MethodBasedView):
            auth_required = True
            permission_classes = (IsAuthenticated, )

        user = User(is_user=True)
        token_data = {'key': 'value'}
        raw_token = self.middleware.manager.generate(token_data)

        request = Request()
        add_property(request, 'user', user)
        add_property(request, 'token', raw_token)
        view = ViewWithIsAuthenticatedPermission()
        self.assertIsNone(self.middleware.authenticate(request, view))

    def test_authenticate_with_permissions_and_raise_exception(self):
        class CustomPermission(AbstractPermission):
            @staticmethod
            def check(request, handler):
                raise PermissionDeniedException

        class ViewWithPermissions(MethodBasedView):
            auth_required = True
            permission_classes = (CustomPermission, )

        user = User(is_user=True)
        token_data = {'key': 'value'}
        raw_token = self.middleware.manager.generate(token_data)

        request = Request()
        add_property(request, 'user', user)
        add_property(request, 'token', raw_token)
        view = ViewWithPermissions()
        self.assertRaises(
            PermissionDeniedException,
            self.middleware.authenticate, request, view
        )

    def test_authenticate_for_view_without_auth_required_pass(self):
        class TestView(MethodBasedView):
            pass

        request = Request()
        view = TestView()
        self.assertIsNone(self.middleware.authenticate(request, view))

    def test_raised_token_not_provided_exception_in_authenticate(self):
        class ViewWithTokenCheck(MethodBasedView):
            auth_required = True

        request = Request()
        view = ViewWithTokenCheck()
        self.assertRaises(
            TokenNotProvidedException,
            self.middleware.authenticate, request, view
        )
