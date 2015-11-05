# -*- coding: utf-8 -*-
"""
    Classes and function for creating and processing requests from user.
"""
import asyncio
import json
from base64 import b64encode, b64decode

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from aiorest_ws.abstract import AbstractRouter
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.validators import check_and_set_subclass
from aiorest_ws.wrappers import Request

__all__ = ('RequestHandlerProtocol', 'RequestHandlerFactory', )


class RequestHandlerProtocol(WebSocketServerProtocol):
    """REST WebSocket protocol instance, creating for every client connection.
    This protocol describe how to process network events (users requests to
    APIs) asynchronously.
    """
    def _decode_message(self, payload, isBinary=False):
        """Decoding input message to Request object.

        :param payload: input message.
        :param isBinary: boolean value, means that received data had a binary
                         format.
        """
        # message was taken in base64
        if isBinary:
            payload = b64decode(payload)
        input_data = json.loads(payload.decode('utf-8'))
        return Request(**input_data)

    def _encode_message(self, response, isBinary=False):
        """Encoding output message.

        :param response: output message.
        :param isBinary: boolean value, means that received data had a binary
                         format.
        """
        # encode additionally to base64 if necessary
        if isBinary:
            response = b64encode(response)
        return response

    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        """Handler, called for every message which was sent from the some user.

        :param payload: input message.
        :param isBinary: boolean value, means that received data had a binary
                         format.
        """
        request = self._decode_message(payload, isBinary)
        response = self.factory.router.process_request(request)
        out_payload = self._encode_message(response, isBinary)
        self.sendMessage(out_payload, isBinary=isBinary)


class RequestHandlerFactory(WebSocketServerFactory):
    """REST WebSocket server factory, which instantiates client connections.

    NOTE: Persistent configuration information is not saved in the instantiated
    protocol. For such cases kept data in a Factory classes, databases, etc.
    """
    def __init__(self, *args, **kwargs):
        super(RequestHandlerFactory, self).__init__(*args, **kwargs)
        self._router = kwargs.get('router', SimpleRouter(*args, **kwargs))

    @property
    def router(self):
        """Get router instance."""
        return self._router

    @router.setter
    def router(self, router):
        """Set router instance.

        :param router: instance of class, which derived from AbstractRouter.
        """
        if router:
            check_and_set_subclass(self, '_router', router, AbstractRouter)
