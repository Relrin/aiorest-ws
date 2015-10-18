# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.auth.user.abstractions import AbstractUser, User
from aiorest_ws.auth.user.utils import generate_password_hash


class AbstractUserTestCase(unittest.TestCase):

    def test_get_fullname(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertEqual(user.get_fullname(), 'test user')

    def test_get_fullname_for_anonymous(self):
        user = AbstractUser()
        self.assertEqual(user.get_fullname(), '')

    def test_change_user_credentials_1(self):
        user = AbstractUser()
        self.assertTrue(user.is_anonymous)

    def test_change_user_credentials_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_anonymous)

    def test_create_superuser(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_superuser': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_user)
        self.assertFalse(user.is_anonymous)

    def test_create_staff(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_staff': True
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_user)
        self.assertFalse(user.is_anonymous)

    def test_create_user(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_user)
        self.assertFalse(user.is_anonymous)

    def test_create_anonymous(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_user)
        self.assertTrue(user.is_anonymous)

    def test_is_active_getter_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_superuser': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_superuser)

    def test_is_active_getter_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_super': False
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_superuser)

    def test_is_active_setter(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)

        self.assertTrue(user.is_active)
        user.is_active = False
        self.assertFalse(user.is_active)

    def test_is_superuser_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_superuser': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_superuser)

    def test_is_superuser_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_superuser': False
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_superuser)

    def test_is_staff_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_staff': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_staff)

    def test_is_staff_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_staff': False
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_staff)

    def test_is_user_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_user)

    def test_is_user_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': False
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_user)

    def test_is_anonymous_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_anonymous)

    def test_is_anonymous_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_anonymous)

    def test_is_authenticated_1(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_superuser': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_authenticated())

    def test_is_authenticated_2(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_staff': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_authenticated())

    def test_is_authenticated_3(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True
        }
        user = AbstractUser(**user_data)
        self.assertTrue(user.is_authenticated())

    def test_is_authenticated_4(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        user = AbstractUser(**user_data)
        self.assertFalse(user.is_authenticated())


class UserTestCase(unittest.TestCase):

    def test_id_getter_1(self):
        user_data = {'id': 1}
        user = User(**user_data)
        self.assertEqual(user.id, 1)

    def test_id_getter_2(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.id, None)

    def test_username_getter_1(self):
        user_data = {'username': 'admin'}
        user = User(**user_data)
        self.assertEqual(user.username, 'admin')

    def test_username_getter_2(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.username, '')

    def test_username_setter(self):
        user_data = {'username': 'admin'}
        user = User(**user_data)
        user.username = 'new_admin'
        self.assertEqual(user.username, 'new_admin')

    def test_password_getter_1(self):
        password_hash = generate_password_hash('123456')
        user_data = {'password': password_hash}
        user = User(**user_data)
        self.assertEqual(user.password, password_hash)

    def test_password_getter_2(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.password, '')

    def test_password_setter(self):
        old_password_hash = generate_password_hash('123456')
        user_data = {'password': old_password_hash}
        user = User(**user_data)
        self.assertEqual(user.password, old_password_hash)
        new_password_hash = generate_password_hash('new_pass')
        user.password = 'new_pass'
        self.assertEqual(user.password, new_password_hash)

    def test_email_getter_1(self):
        user_data = {'email': 'admin@site.com'}
        user = User(**user_data)
        self.assertEqual(user.email, 'admin@site.com')

    def test_email_getter_2(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.email, '')

    def test_email_setter(self):
        old_email = 'admin@site.com'
        user_data = {'email': old_email}
        user = User(**user_data)
        self.assertEqual(user.email, old_email)
        new_email = 'admin@testsite.com'
        user.email = new_email
        self.assertEqual(user.email, new_email)
        self.assertEqual(user.email, new_email)

    def test_permissions_getter_1(self):
        class CanViewAdmin(object):
            pass

        permissions = [CanViewAdmin, ]
        user_data = {'permissions': permissions}
        user = User(**user_data)
        self.assertEqual(user.permissions, permissions)

    def test_permissions_getter_2(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.permissions, [])

    def test_permissions_setter_1(self):
        user_data = {}
        user = User(**user_data)
        self.assertEqual(user.permissions, [])

        class CanEditUser(object):
            pass

        permissions = [CanEditUser, ]
        user.permissions = permissions
        self.assertEqual(user.permissions, permissions)

    def test_check_valid_password(self):
        password = '123456'
        password_hash = generate_password_hash(password)
        user_data = {'password': password_hash}
        user = User(**user_data)
        self.assertTrue(user.check_password(password))

    def test_check_invalid_password(self):
        password = '123456'
        password_hash = generate_password_hash(password)
        user_data = {'password': password_hash}
        user = User(**user_data)
        self.assertFalse(user.check_password('password'))

    def test_has_permission(self):
        class DeleteAdminPermission(object):
            pass

        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_user': True,
            'password': generate_password_hash('123456'),
            'permissions': [DeleteAdminPermission, ]
        }
        user = User(**user_data)
        self.assertTrue(user.has_permission(DeleteAdminPermission))

    def test_has_permission_for_inactive_user(self):
        class ViewAdminSitePermission(object):
            pass

        user_data = {
            'first_name': 'test',
            'last_name': 'user',
            'is_active': False,
            'is_user': True,
            'password': generate_password_hash('123456'),
            'permissions': [ViewAdminSitePermission, ]
        }
        user = User(**user_data)
        self.assertFalse(user.has_permission(ViewAdminSitePermission))
