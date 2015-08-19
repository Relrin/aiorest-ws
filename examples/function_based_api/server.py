# -*- coding: utf-8 -*-
from aiorest_ws.app import Application
from aiorest_ws.command_line import CommandLine
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.decorators import endpoint


@endpoint(path='/hello', methods='GET')
def hello_world(request, *args, **kwargs):
    return "Hello, world!"


@endpoint(path='/sum/{digit_1}/{digit_2}', methods='GET')
def summ(request, digit_1, digit_2, *args, **kwargs):

    def convert_to_int(digit):
        try:
            digit = int(digit)
        except ValueError:
            digit = 0
        return digit

    digit_1 = convert_to_int(digit_1)
    digit_2 = convert_to_int(digit_2)
    return "{0} + {1} = {2}".format(digit_1, digit_2, digit_1 + digit_2)


router = SimpleRouter()
router.register_endpoint(hello_world)
router.register_endpoint(summ)


if __name__ == '__main__':
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()

    app = Application()
    app.run(ip=args.ip, port=args.port, router=router)
