# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.app import Application
from aiorest_ws.routers import RestWSRouter
from aiorest_ws.server import RestWSServerFactory, RestWSServerProtocol
from aiorest_ws.utils.websocket import deflate_offer_accept as accept


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.app = Application()

    def test_factory_getter(self):
        self.assertEqual(self.app.factory, self.app._factory)

    def test_factory_setter_1(self):
        self.app.factory = RestWSServerFactory
        self.assertEqual(type(self.app.factory), type(self.app._factory))

    def test_factory_setter_2(self):
        with self.assertRaises(TypeError):
            self.app.factory = u'NotFactory'

    def test_protocol_getter(self):
        self.assertEqual(self.app.protocol, self.app._protocol)

    def test_protocol_setter_1(self):
        self.app.protocol = RestWSServerProtocol
        self.assertEqual(type(self.app.protocol), type(self.app._protocol))

    def test_protocol_setter_2(self):
        with self.assertRaises(TypeError):
            self.app.protocol = u'NotProtocol'

    def test_certificate_getter(self):
        self.assertEqual(self.app.certificate, self.app._certificate)

    def test_certificate_setter(self):
        certificate_path = u'web/keys/server.crt'
        self.app.certificate = certificate_path
        self.assertEqual(self.app.certificate, certificate_path)

    def test_key_getter(self):
        self.assertEqual(self.app.key, self.app._key)

    def test_key_setter(self):
        key_path = u'web/keys/server.key'
        self.app.key = key_path
        self.assertEqual(self.app.key, key_path)

    def test_url_1(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'
        self.assertTrue(self.app.url, u'wss://{0}:{1}')

    def test_url_2(self):
        self.assertTrue(self.app.url, u'ws://{0}:{1}')

    def test_create_factory_1(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.create_factory(url, debug=True)
        self.assertTrue(factory.debug)
        self.assertIsInstance(factory.router, RestWSRouter)

    def test_create_factory_2(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.create_factory(url, router=RestWSRouter())
        self.assertFalse(factory.debug)
        self.assertIsInstance(factory.router, RestWSRouter)

    def test_create_factory_3(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.create_factory(url, router=RestWSRouter(),
                                          compress=True)
        self.assertFalse(factory.debug)
        self.assertIsInstance(factory.router, RestWSRouter)
        self.assertEqual(factory.perMessageCompressionAccept, accept)

    def test_generate_url_1(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'

        host, ip = u'127.0.0.1', 8080
        self.assertEqual(
            self.app.generate_url(host, ip), u'wss://{0}:{1}'.format(host, ip)
        )

    def test_generate_url_2(self):
        host, ip = u'127.0.0.1', 8080
        self.assertEqual(
            self.app.generate_url(host, ip), u'ws://{0}:{1}'.format(host, ip)
        )
