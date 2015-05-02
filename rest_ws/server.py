import asyncio
from aiohttp import web

from command_line import define, parse_command_line


@asyncio.coroutine
def init_server(loop, ip, port, router=None):
    app = web.Application(loop=loop, router=router)
    srv = yield from loop.create_server(app.make_handler(), str(ip), int(port))
    print("Server started at http://{0}:{1}".format(ip, port))
    return srv


def run_server(router=None):
    define('-ip', default='127.0.0.1', type=str, help="used ip for server",
           required=False)
    define('-port', default=8080, type=int, help="listened port for server",
           required=False)
    args = parse_command_line()
    loop = asyncio.get_event_loop()
    server_instance = init_server(loop, args.ip, args.port, router)
    loop.run_until_complete(server_instance)
    loop.run_forever()
