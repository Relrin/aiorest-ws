# -*- coding: utf-8 -*-
"""
    User abstractions for authentication.
"""
from aiorest_ws.auth.user.utils import generate_password_hash

__all__ = ('AbstractUser', 'User', )


class AbstractUser(object):
    """Abstract class, which describe generic user."""
    def __init__(self, *args, **kwargs):
        super(AbstractUser, self).__init__()
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self._change_user_credentials(*args, **kwargs)

    def _change_user_credentials(self, *args, **kwargs):
        """Change user credentials, based on the passed args and kwargs."""
        self._is_active = kwargs.get('is_active', True)
        self._is_superuser = kwargs.get('is_superuser', False)
        self._is_staff = kwargs.get('is_staff', False)
        self._is_user = kwargs.get('is_user', False)

        if any([self._is_superuser, self._is_staff, self._is_user]):
            self._is_anonymous = False
        else:
            self._is_anonymous = True

    def get_fullname(self):
        """Get fullname of user."""
        return u"{0} {1}".format(self.first_name, self.last_name).strip()

    @property
    def is_active(self):
        """Get is_active status of user."""
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        """Set is_active status of user.

        :param is_active: boolean value of is_active.
        """
        self._is_active = is_active

    @property
    def is_superuser(self):
        """Get is_superuser status of user."""
        return self._is_superuser

    @property
    def is_staff(self):
        """Get is_staff status of user."""
        return self._is_staff

    @property
    def is_user(self):
        """Get is_user status of user."""
        return self._is_user

    @property
    def is_anonymous(self):
        """Get is_anonymous status of user."""
        return self._is_anonymous

    def is_authenticated(self):
        """Check that this user is authenticated."""
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
        """Get users ID."""
        return self._id

    @property
    def username(self):
        """Get username."""
        return self._username

    @username.setter
    def username(self, username):
        """Set username.

        :param username: new username as a string.
        """
        self._username = username

    @property
    def password(self):
        """Get password."""
        return self._password

    @password.setter
    def password(self, password):
        """Set new password for user.

        :param password: password as a string.
        """
        self._password = generate_password_hash(password)

    @property
    def email(self):
        """Get email."""
        return self._email

    @email.setter
    def email(self, email):
        """Set email for user.

        :param email: email as a string.
        """
        self._email = email

    @property
    def permissions(self):
        """Get list of permissions."""
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        """Set permissions for user.

        :param permissions: list of permissions.
        """
        self._permissions = permissions

    def check_password(self, password):
        """Check for a valid password has taken.

        :param password: password as a string.
        """
        return self.password == generate_password_hash(password)

    def has_permission(self, obj=None):
        """Check that user have a some permission.

        :param obj: permissions object derived from the AbstractPermission.
        """
        if self.is_active:
            return obj in self.permissions
        else:
            return False
