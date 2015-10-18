# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.auth.user.exceptions import RequiredModelFieldsNotDefined, \
    SearchCriteriaRequired, NotEnoughArguments
from aiorest_ws.auth.user.models import UserSQLiteModel
from aiorest_ws.auth.user.utils import USER_MODEL_FIELDS, \
    USER_MODEL_FIELDS_WITHOUT_PK, generate_password_hash
from aiorest_ws.conf import settings

from tests.fixtures.example_settings import DATABASES


class UserSQLiteModelTestCase(unittest.TestCase):

    def _create_simple_user(self, user_model, **kwargs):
        user_data = {
            'username': kwargs.get('username', None) or 'testuser',
            'password': kwargs.get('password', None) or '123456',
            'first_name': kwargs.get('first_name', None) or 'test',
            'last_name': kwargs.get('last_name', None) or 'user',
            'is_active': kwargs.get('is_active', None) or True,
            'is_superuser': kwargs.get('is_superuser', None) or False,
            'is_staff': kwargs.get('is_staff', None) or False,
            'is_user': kwargs.get('is_user', None) or True,
        }
        user_model.create_user(**user_data)

    def test_init_with_default_settings(self):
        model = UserSQLiteModel()  # NOQA

    def test_init_with_custom_settings(self):
        settings.DATABASES = DATABASES
        settings._create_database_managers()
        model = UserSQLiteModel()  # NOQA

    def test_fields(self):
        model = UserSQLiteModel()
        self.assertEqual(model.fields, USER_MODEL_FIELDS)

    def test_fields_without_pk(self):
        model = UserSQLiteModel()
        self.assertEqual(model.fields_without_pk, USER_MODEL_FIELDS_WITHOUT_PK)

    def test_create_user(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)

    def test_create_user_without_username(self):
        model = UserSQLiteModel()
        kwargs = {
            'password': '123456',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'is_superuser': False,
            'is_staff': False,
            'is_user': True,
        }
        self.assertRaises(
            RequiredModelFieldsNotDefined, model.create_user, **kwargs
        )

    def test_create_user_without_password(self):
        model = UserSQLiteModel()
        kwargs = {
            'username': 'testuser',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'is_superuser': False,
            'is_staff': False,
            'is_user': True,
        }
        self.assertRaises(
            RequiredModelFieldsNotDefined, model.create_user, **kwargs
        )

    def test_update_user(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        update_kwargs = {
            'username': 'testuser',
            'is_superuser': True,
            'is_user': False
        }
        model.update_user(**update_kwargs)

    def test_update_user_password(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        update_kwargs = {
            'username': 'testuser',
            'password': 'testuser',
        }
        model.update_user(**update_kwargs)

    def test_search_criteria_required_in_update_user(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        update_kwargs = {
            'is_superuser': True
        }
        self.assertRaises(
            SearchCriteriaRequired, model.update_user, **update_kwargs
        )

    def test_not_enough_arguments_exception_in_update_user(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        update_kwargs = {
            'username': 'testuser'
        }
        self.assertRaises(
            NotEnoughArguments, model.update_user, **update_kwargs
        )

    @unittest.mock.patch('aiorest_ws.log.logger.error')
    def test_operational_error_in_logger_in_update_user(self, m_logger):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        update_kwargs = {
            'username': 'testuser',
            'unknown': 'field'
        }
        # there we are take the message with the text
        # "[ERROR] near "WHERE": syntax error"
        # which means that defined update under "not existed" field
        model.update_user(**update_kwargs)

    def test_get_user_by_username_with_id(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        user = model.get_user_by_username('testuser', with_id=True)
        self.assertIsNotNone(user.id)
        self.assertEquals(user.username, 'testuser')
        self.assertEquals(user.password, generate_password_hash('123456'))
        self.assertEquals(user.first_name, 'test')
        self.assertEquals(user.last_name, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_user)

    def test_get_user_by_username_without_id(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        user = model.get_user_by_username('testuser')
        self.assertIsNone(user.id)
        self.assertEquals(user.username, 'testuser')
        self.assertEquals(user.password, generate_password_hash('123456'))
        self.assertEquals(user.first_name, 'test')
        self.assertEquals(user.last_name, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_user)

    def test_get_not_existed_user_by_username(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        user = model.get_user_by_username('user')
        self.assertIsNone(user.id)
        self.assertEquals(user.username, '')
        self.assertEquals(user.password, '')
        self.assertEquals(user.first_name, '')
        self.assertEquals(user.last_name, '')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_user)
        self.assertTrue(user.is_anonymous)

    def test_get_user_by_token(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        user = model.get_user_by_username('testuser', with_id=True)
        token = {'user_id': user.id}
        user = model.get_user_by_token(token)
        self.assertIsNone(user.id)
        self.assertEquals(user.username, 'testuser')
        self.assertEquals(user.password, generate_password_hash('123456'))
        self.assertEquals(user.first_name, 'test')
        self.assertEquals(user.last_name, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_user)

    def test_get_not_existing_user_by_token(self):
        model = UserSQLiteModel()
        self._create_simple_user(model)
        token = {'user_id': 0}
        user = model.get_user_by_token(token)
        self.assertIsNone(user.id)
        self.assertEquals(user.username, '')
        self.assertEquals(user.password, '')
        self.assertEquals(user.first_name, '')
        self.assertEquals(user.last_name, '')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_user)
        self.assertTrue(user.is_anonymous)
