# -*- coding: utf-8 -*-
import os
os.environ.setdefault("AIORESTWS_SETTINGS_MODULE", "settings")

from aiorest_ws.auth.token.managers import JSONWebTokenManager
from aiorest_ws.auth.token.backends import InMemoryTokenBackend
from aiorest_ws.auth.token.middlewares import JSONWebTokenMiddleware
from aiorest_ws.auth.user.models import UserSQLiteModel
from aiorest_ws.app import Application
from aiorest_ws.command_line import CommandLine
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.views import MethodBasedView


class RegisterUser(MethodBasedView):
    user_manager = UserSQLiteModel()

    def post(self, request, *args, **kwargs):
        user = self.user_manager.get_user_by_username(request.args['username'])
        # only anonymous doesn't have username
        if user.is_authenticated:
            message = "User already created."
        else:
            self.user_manager.create_user(**request.args)
            message = "User created successfully."
        return message


class LogIn(MethodBasedView):
    token_manager = JSONWebTokenManager()
    token_backend = InMemoryTokenBackend()
    user_manager = UserSQLiteModel()

    def get_or_create_token(self, user, *args, **kwargs):

        def get_token(user):
            return self.token_backend.get_token_by_username(
                'admin', username=user.username
            )

        def create_token(user, *args, **kwargs):
            jwt_kwargs = {
                "iss": "aiorest-ws",
                "exp": 60,
                "name": kwargs.get('username'),
                "authorized": True,
                "token_name": "admin"
            }
            kwargs.update(jwt_kwargs)
            api_token = self.token_manager.generate({}, **kwargs)
            self.token_backend.save('admin', api_token, user_id=user.id)
            return api_token

        return get_token(user) or create_token(user, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.user_manager.get_user_by_username(
            request.args['username'], with_id=True
        )
        if user.is_authenticated:
            api_token = self.get_or_create_token(user, *args, **kwargs)
        else:
            api_token = None
        return {'token': api_token}


class LogOut(MethodBasedView):
    auth_required = True

    def post(self, request, *args, **kwargs):
        return "Successful log out."


router = SimpleRouter()
router.register('/auth/user/create', RegisterUser, 'POST')
router.register('/auth/login', LogIn, 'POST')
router.register('/auth/logout', LogOut, 'POST')


if __name__ == '__main__':
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()

    app = Application(middlewares=(JSONWebTokenMiddleware, ))
    app.run(host=args.ip, port=args.port, router=router)
