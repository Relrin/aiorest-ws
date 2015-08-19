# -*- coding: utf-8 -*-
from aiorest_ws.app import Application
from aiorest_ws.command_line import CommandLine
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.views import MethodBasedView


class HelloWorld(MethodBasedView):
    def get(self, request, *args, **kwargs):
        return "Hello, username!"


class HelloWorldCustom(MethodBasedView):
    def get(self, request, user, id, *args, **kwargs):
        return "Hello, {0} with ID={1}".format(user, id)


class CalculateSum(MethodBasedView):
    def get(self, request, *args, **kwargs):
        try:
            digits = kwargs['params']['digits']
        except KeyError:
            digits = [0, ]
        return {"sum": sum(digits)}


router = SimpleRouter()
router.register('/hello', HelloWorld, 'GET')
router.register('/hello/{user}/{id}', HelloWorldCustom, 'GET')
router.register('/calc/sum', CalculateSum, 'GET')


if __name__ == '__main__':
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()

    app = Application()
    app.run(host=args.ip, port=args.port, router=router)
