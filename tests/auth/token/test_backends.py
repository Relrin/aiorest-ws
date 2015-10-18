# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.auth.token.backends import InMemoryTokenBackend
from aiorest_ws.auth.user.models import UserSQLiteModel
from aiorest_ws.conf import settings

from tests.fixtures.example_settings import DATABASES


class InMemoryTokenBackendTestCase(unittest.TestCase):

    def _set_user_settings(self):
        settings.DATABASES = DATABASES
        settings._create_database_managers()

    def _create_simple_user(self, user_model):
        kwargs = {
            'username': 'testuser',
            'password': '123456',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'is_superuser': False,
            'is_staff': False,
            'is_user': True,
        }
        user_model.create_user(**kwargs)
        user = user_model.get_user_by_username('testuser', with_id=True)
        return user

    def test_init_by_default(self):
        settings.DATABASES = {}
        backend = InMemoryTokenBackend()  # NOQA

    def test_init_with_user_settings(self):
        self._set_user_settings()
        backend = InMemoryTokenBackend()  # NOQA

    def test_get(self):
        self._set_user_settings()
        token_backend = InMemoryTokenBackend()
        user_model = UserSQLiteModel()
        user = self._create_simple_user(user_model)
        token_data = {
            'name': 'api',
            'token': 'my_test_token',
            'user_id': user.id
        }
        token_backend.save(
            token_data['name'],
            token_data['token'],
            user_id=token_data['user_id']
        )
        db_token = token_backend.get(token_data['token'])
        self.assertEqual(db_token['name'], token_data['name'])
        self.assertEqual(db_token['token'], token_data['token'])
        self.assertEqual(db_token['user_id'], token_data['user_id'])

    def test_get_not_existed_token(self):
        self._set_user_settings()
        backend = InMemoryTokenBackend()
        db_token = backend.get('unknown_token')
        self.assertEqual(db_token, {})

    def test_get_token_by_username(self):
        self._set_user_settings()
        token_backend = InMemoryTokenBackend()
        user_model = UserSQLiteModel()
        user = self._create_simple_user(user_model)
        token_data = {
            'name': 'api',
            'token': 'my_test_token',
            'user_id': user.id
        }
        token_backend.save(
            token_data['name'],
            token_data['token'],
            user_id=token_data['user_id']
        )
        db_token = token_backend.get_token_by_username('api', user.username)
        self.assertEqual(db_token['name'], token_data['name'])
        self.assertEqual(db_token['token'], token_data['token'])
        self.assertEqual(db_token['user_id'], token_data['user_id'])

    def test_get_token_by_not_existed_username(self):
        self._set_user_settings()
        token_backend = InMemoryTokenBackend()
        user_model = UserSQLiteModel()
        user = self._create_simple_user(user_model)
        token_backend.save('api', 'my_test_token', user_id=user.id)
        token = token_backend.get_token_by_username('unknown', user.username)
        self.assertEqual(token, {})

    def test_save(self):
        self._set_user_settings()
        token_backend = InMemoryTokenBackend()
        user_model = UserSQLiteModel()
        user = self._create_simple_user(user_model)
        token_backend.save('api', 'my_test_token', user_id=user.id)
