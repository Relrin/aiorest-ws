# -*- coding: utf-8 -*-
from aiorest_ws.app import Application
from aiorest_ws.command_line import CommandLine
from aiorest_ws.routers import SimpleRouter

from app.urls import router

main_router = SimpleRouter()
main_router.include(router)


if __name__ == '__main__':
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()

    app = Application()
    app.run(host=args.ip, port=args.port, router=main_router)
