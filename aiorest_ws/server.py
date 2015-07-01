# -*- coding: utf-8 -*-
"""
    Classes and function for creating and starting web server
"""
import asyncio
import json
from base64 import b64encode, b64decode
from time import gmtime, strftime

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from __init__ import __version__

__all__ = ('RestWSServer', 'run_server', )


class RestWSServer(WebSocketServerProtocol):

    router = None

    @classmethod
    def setRouter(cls, router):
        cls.router = router

    def _decode_message(self, payload, isBinary):
        # message in base64
        if isBinary:
            payload = b64decode(payload)
        input_data = payload.decode('utf8')
        return json.loads(input_data)

    def _encode_message(self, response, isBinary):
        output_data = json.dumps(response)
        output_data = output_data.encode('utf8')
        # convert to base64 if necessary
        if isBinary:
            output_data = b64encode(output_data)
        return output_data

    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        request = self._decode_message(payload, isBinary)
        response = self.router.dispatch(request)
        out_payload = self._encode_message(response, isBinary)
        self.sendMessage(out_payload, isBinary=isBinary)


def run_server(ip='127.0.0.1', port=8080, server=RestWSServer, router=None,
               cert=None, key=None, debug=False):
    """
        Create and start web server with some IP and PORT

        Args:
            ip - used IP for server
            port - listened port
            server - class inherited from WebSocketServerProtocol
            router - instance of RestWSRouter
            cert - path to certificate
            key - key for certificate
            debug - output all debug information
    """
    if cert and key:
        url = "wss://{0}:{1}".format(ip, port)
    else:
        url = "ws://{0}:{1}".format(ip, port)

    if router:
        server.setRouter(router)

    factory = WebSocketServerFactory(url, debug=debug)
    factory.protocol = server

    # TODO: Add there SSL support

    loop = asyncio.get_event_loop()
    server_coroutine = loop.create_server(factory, ip, port)
    server = loop.run_until_complete(server_coroutine)

    print(strftime("%d %b, %Y - %X", gmtime()))
    print("aiorest-ws version {0}".format(__version__))
    print("Server started at {0}".format(url))
    print("Quit the server with CONTROL-C.")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
