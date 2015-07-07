# -*- coding: utf-8 -*-
"""
    Classes and function for creating and starting web server.

    :copyright: (c) 2015 by Savich Valeryi.
    :license: MIT, see LICENSE for more details.
"""
import asyncio
import json
from base64 import b64encode, b64decode
from time import gmtime, strftime

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from __init__ import __version__
from routers import RestWSRouter

__all__ = ('RestWSServer', 'run_server', )


class RestWSServer(WebSocketServerProtocol):
    """REST WebSocket server instance."""
    router = RestWSRouter()

    @classmethod
    def setRouter(cls, router):
        """Set users router by default for the server instance.

        :param router: user-defined router.
        """
        if not issubclass(router, RestWSRouter):
            raise TypeError('Custom router class must be inherited from '
                            'RestWSRouter class.')
        cls.router = router

    def _decode_message(self, payload, isBinary=False):
        """Decoding input message to JSON or base64 object.

        :param payload: input message.
        :param isBinary: boolean value, means that received data had a binary
                         format.
        """
        # message in base64
        if isBinary:
            payload = b64decode(payload)
        input_data = payload.decode('utf8')
        return json.loads(input_data)

    def _encode_message(self, response, isBinary=False):
        """Encoding output message to JSON or base64 object.

        :param response: output message.
        :param isBinary: boolean value, means that received data had a binary
                         format.
        """
        output_data = response.encode('utf8')
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
    """Create and start web server with some IP and PORT.

    :param ip: used IP for server.
    :param port: listened port.
    :param server: class inherited from WebSocketServerProtocol.
    :param router: instance of RestWSRouter.
    :param cert: path to certificate.
    :param key: private key for certificate.
    :param debug: output all debug information.
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
    # TODO: Add compressing messages

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
