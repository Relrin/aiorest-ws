"""
    Classes and function for creating and starting web server
"""
import asyncio
from aiohttp import web

from command_line import define, parse_command_line


__all__ = ('init_server', 'run_server')


@asyncio.coroutine
def init_server(loop, ip, port, router=None):
    """
        Initialize instance of web server

        Args:
            ip - used IP
            port - listened port on web server
            router - instance of RestWSRouter class with user defined endpoints
    """
    app = web.Application(loop=loop, router=router)
    srv = yield from loop.create_server(app.make_handler(), str(ip), int(port))
    print("Server started at http://{0}:{1}".format(ip, port))
    return srv


def run_server(router=None):
    """
        Create and start web server with typed IP and PORT via command line

        Args:
            router - instance of RestWSRouter class with user defined endpoints
    """
    define('-ip', default='127.0.0.1', type=str, help="used ip for server")
    define('-port', default=8080, type=int, help="listened port on the server")
    args = parse_command_line()
    loop = asyncio.get_event_loop()
    server_instance = init_server(loop, args.ip, args.port, router)
    loop.run_until_complete(server_instance)
    loop.run_forever()
