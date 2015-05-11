"""
    Classes and function for creating and starting web server
"""
import asyncio
from aiohttp import web


__all__ = ('init_server', 'deinit_server', 'run_server')


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
    app['sockets'] = []
    handler = app.make_handler()
    srv = yield from loop.create_server(handler, str(ip), int(port))
    print("Server started at http://{0}:{1}".format(ip, port))
    return app, srv, handler


@asyncio.coroutine
def deinit_server(app, server, handler):
    """
        Deinitialize instance of web server
    """
    for ws in app['sockets']:
        ws.close()
    app['sockets'].clear()
    yield from asyncio.sleep(0.1)
    server.close()
    yield from handler.finish_connections()
    yield from server.wait_closed()


def run_server(ip='127.0.0.1', port=8080, router=None):
    """
        Create and start web server with some IP and PORT

        Args:
            ip - used IP for server
            port - listened port
            router - instance of RestWSRouter
    """
    loop = asyncio.get_event_loop()
    server_instance = init_server(loop, ip, port, router)
    app, srv, handler = loop.run_until_complete(server_instance)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(deinit_server(app, srv, handler))
