# -*- coding: utf -*-
import json
import unittest

from base64 import b64encode

from aiorest_ws.routers import SimpleRouter
from aiorest_ws.request import RequestHandlerFactory, RequestHandlerProtocol


class RequestHandlerProtocolTestCase(unittest.TestCase):

    def setUp(self):
        super(RequestHandlerProtocolTestCase, self).setUp()
        self.protocol = RequestHandlerProtocol()

    def test_encode_message(self):
        message = json.dumps({'key': 'value'}).encode('utf-8')
        self.assertEqual(self.protocol._encode_message(message), message)

        self.assertEqual(
            self.protocol._encode_message(message, isBinary=True),
            b64encode(message)
        )

    def test_decode_message(self):
        data = {'url': '/api'}
        message = json.dumps(data).encode('utf-8')
        request = self.protocol._decode_message(message)
        self.assertEqual({'url': request.url}, data)

    def test_decode_message_binary(self):
        data = {'url': '/api'}
        message = json.dumps(data).encode('utf-8')
        message = b64encode(message)
        request = self.protocol._decode_message(message, isBinary=True)
        self.assertEqual({'url': request.url}, data)


class RequestHandlerFactoryTestCase(unittest.TestCase):

    def setUp(self):
        super(RequestHandlerFactoryTestCase, self).setUp()
        self.factory = RequestHandlerFactory()

    def test_router_getter(self):
        self.assertEqual(self.factory.router, self.factory._router)

    def test_router_setter(self):
        class ImplementedRouter(SimpleRouter):
            pass

        self.factory.router = ImplementedRouter()
        self.assertIsInstance(self.factory.router, ImplementedRouter)

    def test_router_setter_with_invalid_router_class(self):
        class InvalidRouter(object):
            pass

        self.assertRaises(TypeError, self.factory.router, InvalidRouter())
