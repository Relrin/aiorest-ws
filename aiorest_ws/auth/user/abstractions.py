# -*- coding: utf-8 -*-
"""
    User abstractions for authentication.
"""
__all__ = ('AbstractUser', 'User')

from aiorest_ws.auth.user.utils import generate_password_hash


class AbstractUser(object):
    """Abstract class, which describe generic user."""
    def __init__(self, *args, **kwargs):
        super(AbstractUser, self).__init__()
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self._change_user_credentials(*args, **kwargs)

    def _change_user_credentials(self, *args, **kwargs):
        self._is_active = kwargs.get('is_active', True)
        self._is_superuser = kwargs.get('is_superuser', False)
        self._is_staff = kwargs.get('is_staff', False)
        self._is_user = kwargs.get('is_user', False)

        if any([self._is_superuser, self._is_staff, self._is_user]):
            self._is_anonymous = False
        else:
            self._is_anonymous = True

    def get_fullname(self):
        return u"{0} {1}".format(self.first_name, self.last_name).strip()

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active

    @property
    def is_superuser(self):
        return self._is_superuser

    @property
    def is_staff(self):
        return self._is_staff

    @property
    def is_user(self):
        return self._is_user

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @property
    def is_authenticated(self):
        if self.is_anonymous:
            return False
        else:
            return True


class User(AbstractUser):
    """Default class, which describe current user."""
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._id = kwargs.get('id', None)
        self._username = kwargs.get('username', '')
        self._password = kwargs.get('password', '')
        self._email = kwargs.get('email', '')
        self._permissions = kwargs.get('permissions', [])

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def permissions(self):
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        self._permissions = permissions

    def check_password(self, password):
        return self.password == generate_password_hash(password)

    def has_permission(self, obj=None):
        if self.is_active:
            return obj in self.permissions
        else:
            return False
