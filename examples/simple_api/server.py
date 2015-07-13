from aiorest_ws.command_line import CommandLine
from aiorest_ws.routers import RestWSRouter
from aiorest_ws.server import run_server
from aiorest_ws.views import MethodBasedView


class hello_static(MethodBasedView):
    def get(self, request, *args, **kwargs):
        return "Hello, username!"


class hello_dynamic(MethodBasedView):
    def get(self, request, user, id, *args, **kwargs):
        return "Hello, {0} with ID={1}".format(user, id)


class calc_sum(MethodBasedView):
    def get(self, request, *args, **kwargs):
        try:
            digits = kwargs['params']['digits']
        except KeyError:
            digits = [0, ]
        return {"sum": sum(digits)}


router = RestWSRouter()
router.register('/hello', hello_static, 'GET')
router.register('/hello/{user}/{id}', hello_dynamic, 'GET')
router.register('/calc/sum', calc_sum, 'GET')


if __name__ == '__main__':
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()
    run_server(ip=args.ip, port=args.port, router=router)
