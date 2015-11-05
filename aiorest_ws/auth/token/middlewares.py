# -*- coding: utf-8 -*-
"""
    Middlewares for authentication issues.
"""
from aiorest_ws.abstract import AbstractMiddleware
from aiorest_ws.auth.user.models import UserSQLiteModel
from aiorest_ws.auth.user.abstractions import User
from aiorest_ws.auth.token.backends import InMemoryTokenBackend
from aiorest_ws.auth.token.exceptions import TokenNotProvidedException
from aiorest_ws.auth.token.managers import JSONWebTokenManager
from aiorest_ws.utils.modify import add_property

__all__ = ('BaseTokenMiddleware', 'JSONWebTokenMiddleware', )


class BaseTokenMiddleware(AbstractMiddleware):
    """Base token middleware class."""

    def init_credentials(self, request):
        """Getting credentials (user, keys, tokens) from database/cache/etc.

        :param request: instance of Request class.
        """
        pass

    def authenticate(self, request, handler):
        """Authenticate user.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        pass

    def process_request(self, request, handler):
        """Processing request before calling handler.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        self.init_credentials(request)
        self.authenticate(request, handler)


class JSONWebTokenMiddleware(BaseTokenMiddleware):
    """The JSON Web Token middleware class."""
    storage_backend = InMemoryTokenBackend
    manager = JSONWebTokenManager
    user_model = UserSQLiteModel

    def __init__(self):
        super(JSONWebTokenMiddleware, self).__init__()
        self.storage_backend = self.storage_backend()
        self.user_model = self.user_model()
        self.manager = self.manager()

    def get_user_by_token(self, token):
        """Get user from the database by passed token.

        :param token: token as string.
        """
        token_data = self.storage_backend.get(token)
        if token_data:
            user = self.user_model.get_user_by_token(token_data)
        else:
            user = User()
        return user

    def init_credentials(self, request):
        """Getting credentials (user, keys, tokens) from database/cache/etc.

        :param request: instance of Request class.
        """
        token = getattr(request, 'token', None)

        if token:
            token_payload = self.manager.verify(token)
            user = self.get_user_by_token(token)
        else:
            token_payload = None
            user = User()

        add_property(request, 'user', user)
        add_property(request, 'token_payload', token_payload)

    def authenticate(self, request, view):
        """Authenticate user.

        NOTE: Authentication applied for the views, which set `auth_required`
        attribute to `True` value.

        :param request: instance of Request class.
        :param view: view, invoked later for the request.
        """
        auth_required = getattr(view, 'auth_required', False)
        permission_classes = getattr(view, 'permission_classes', ())

        if auth_required:
            if hasattr(request, 'token') and request.token:
                for permission in permission_classes:
                    permission.check(request, view)
            else:
                raise TokenNotProvidedException()
