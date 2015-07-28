# -*- coding: utf -*-
import json
import unittest

from base64 import b64encode

from aiorest_ws.routers import RestWSRouter
from aiorest_ws.server import RestWSServerFactory, RestWSServerProtocol


class RestWSServerProtocolTestCase(unittest.TestCase):

    def setUp(self):
        super(RestWSServerProtocolTestCase, self).setUp()
        self.protocol = RestWSServerProtocol()

    def test_encode_message(self):
        message = json.dumps({'key': 'value'}).encode('utf-8')
        self.assertEqual(self.protocol._encode_message(message), message)

        self.assertEqual(
            self.protocol._encode_message(message, isBinary=True),
            b64encode(message)
        )

    def test_decode_message(self):
        data = {'key': 'value'}

        message = json.dumps(data).encode('utf-8')
        self.assertEqual(
            self.protocol._decode_message(message),
            data
        )

        self.assertEqual(
            self.protocol._decode_message(b64encode(message), isBinary=True),
            data
        )


class RestWSServerFactoryTestCase(unittest.TestCase):

    def setUp(self):
        super(RestWSServerFactoryTestCase, self).setUp()
        self.factory = RestWSServerFactory()

    def test_router_getter(self):
        self.assertEqual(self.factory.router, self.factory._router)

    def test_router_setter(self):
        class InvalidRouter(object):
            pass

        class ImplementedRouter(RestWSRouter):
            pass

        self.assertRaises(TypeError, self.factory.router, InvalidRouter())

        self.factory.router = ImplementedRouter()
        self.assertIsInstance(self.factory.router, ImplementedRouter)
