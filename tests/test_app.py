# -*- coding: utf-8 -*-
import ssl
import unittest

from aiorest_ws.app import Application
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.request import RequestHandlerFactory, RequestHandlerProtocol
from aiorest_ws.utils.websocket import deflate_offer_accept as accept

from tests.fixtures.fakes import FakeTokenMiddleware


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.app = Application()

    def test_factory_getter(self):
        self.assertEqual(self.app.factory, self.app._factory)

    def test_factory_setter_1(self):
        self.app.factory = RequestHandlerFactory
        self.assertEqual(type(self.app.factory), type(self.app._factory))

    def test_factory_setter_2(self):
        with self.assertRaises(TypeError):
            self.app.factory = u'NotFactory'

    def test_middleware_getter_1(self):
        self.assertEqual(self.app.middlewares, [])

    def test_middleware_getter_2(self):
        self.app = Application(middlewares=(FakeTokenMiddleware, ))
        self.assertEqual(len(self.app.middlewares), 1)
        self.assertIsInstance(self.app.middlewares[0], FakeTokenMiddleware)

    def test_protocol_getter(self):
        self.assertEqual(self.app.protocol, self.app._protocol)

    def test_protocol_setter_1(self):
        self.app.protocol = RequestHandlerProtocol
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

    def test_url(self):
        self.app.certificate = self.app.key = None
        self.assertTrue(self.app.url, u'ws://{0}:{1}')

    def test_url_2(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = None
        self.assertTrue(self.app.url, u'ws://{0}:{1}')

    def test_url_3(self):
        self.app.certificate = None
        self.app.key = u'web/keys/server.key'
        self.assertTrue(self.app.url, u'ws://{0}:{1}')

    def test_url_4(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'
        self.assertTrue(self.app.url, u'wss://{0}:{1}')

    def test_isSecure(self):
        self.app.certificate = self.app.key = None
        self.assertFalse(self.app.isSecure)

    def test_isSecure_2(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = None
        self.assertFalse(self.app.isSecure)

    def test_isSecure_3(self):
        self.app.certificate = None
        self.app.key = u'web/keys/server.key'
        self.assertFalse(self.app.isSecure)

    def test_isSecure_4(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'
        self.assertTrue(self.app.isSecure)

    def test_get_ssl_context(self):
        self.app.certificate = self.app.key = None
        ssl_context = self.app._get_ssl_context()
        self.assertIsNone(ssl_context)

    def test_get_ssl_context_2(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = None
        ssl_context = self.app._get_ssl_context()
        self.assertIsNone(ssl_context)

    def test_get_ssl_context_3(self):
        self.app.certificate = None
        self.app.key = u'web/keys/server.key'
        ssl_context = self.app._get_ssl_context()
        self.assertIsNone(ssl_context)

    def test_get_ssl_context_4(self):
        self.app.certificate = u'./tests/keys/server.crt'
        self.app.key = u'./tests/keys/server.key'
        ssl_context = self.app._get_ssl_context()
        self.assertIsInstance(ssl_context, ssl.SSLContext)

    def test_init_factory(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app._init_factory(url)
        self.assertFalse(factory.debug)
        self.assertEqual(factory.protocol, RequestHandlerProtocol)

    def test_init_factory_2(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {'debug': False}
        factory = self.app._init_factory(url, **options)
        self.assertFalse(factory.debug)
        self.assertEqual(factory.protocol, RequestHandlerProtocol)

    def test_init_factory_3(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {'debug': True}
        factory = self.app._init_factory(url, **options)
        self.assertTrue(factory.debug)
        self.assertEqual(factory.protocol, RequestHandlerProtocol)

    def test_enable_compressing(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {}
        factory = self.app._init_factory(url)
        self.app._enable_compressing(factory, **options)
        self.assertTrue(callable(factory.perMessageCompressionAccept))
        self.assertIsNone(factory.perMessageCompressionAccept('not_used_arg'))

    def test_enable_compressing_2(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {'compress': False}
        factory = self.app._init_factory(url)
        self.app._enable_compressing(factory, **options)
        self.assertTrue(callable(factory.perMessageCompressionAccept))
        self.assertIsNone(factory.perMessageCompressionAccept('not_used_arg'))

    def test_enable_compressing_3(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {'compress': True}
        factory = self.app._init_factory(url)
        self.app._enable_compressing(factory, **options)
        self.assertTrue(callable(factory.perMessageCompressionAccept))
        self.assertEqual(factory.perMessageCompressionAccept, accept)

    def test_factory_router_not_defined(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        options = {}
        factory = self.app._init_factory(url)
        with self.assertRaises(AssertionError):
            self.app._set_factory_router(factory, **options)

    def test_set_factory_router(self):
        class CustomRouter(SimpleRouter):
            pass

        url = self.app.generate_url('127.0.0.1', 8080)
        options = {'router': CustomRouter()}
        factory = self.app._init_factory(url)
        self.app._set_factory_router(factory, **options)
        self.assertIsInstance(factory.router, CustomRouter)

    def test_generate_factory(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.generate_factory(
            url, debug=True, router=SimpleRouter()
        )
        self.assertTrue(factory.debug)
        self.assertIsInstance(factory.router, SimpleRouter)

    def test_generate_factory_2(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.generate_factory(url, router=SimpleRouter())
        self.assertFalse(factory.debug)
        self.assertIsInstance(factory.router, SimpleRouter)

    def test_generate_factory_3(self):
        url = self.app.generate_url('127.0.0.1', 8080)
        factory = self.app.generate_factory(
            url, router=SimpleRouter(), compress=True
        )
        self.assertFalse(factory.debug)
        self.assertIsInstance(factory.router, SimpleRouter)
        self.assertEqual(factory.perMessageCompressionAccept, accept)

    def test_generate_url(self):
        host, ip = u'127.0.0.1', 8080
        self.assertEqual(
            self.app.generate_url(host, ip),
            u'ws://{0}:{1}/'.format(host, ip)
        )

    def test_generate_url_2(self):
        host, ip, path = u'127.0.0.1', 8080, ''
        self.assertEqual(
            self.app.generate_url(host, ip, path),
            u'ws://{0}:{1}/'.format(host, ip, path)
        )

    def test_generate_url_3(self):
        host, ip, path = u'127.0.0.1', 8080, 'ssl'
        self.assertEqual(
            self.app.generate_url(host, ip, path),
            u'ws://{0}:{1}/{2}'.format(host, ip, path)
        )

    def test_generate_url_4(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'

        host, ip = u'127.0.0.1', 8080
        self.assertEqual(
            self.app.generate_url(host, ip),
            u'wss://{0}:{1}/'.format(host, ip)
        )

    def test_generate_url_5(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'

        host, ip, path = u'127.0.0.1', 8080, ''
        self.assertEqual(
            self.app.generate_url(host, ip, path),
            u'wss://{0}:{1}/'.format(host, ip, path)
        )

    def test_generate_url_6(self):
        self.app.certificate = u'web/keys/server.crt'
        self.app.key = u'web/keys/server.key'

        host, ip, path = u'127.0.0.1', 8080, 'ssl'
        self.assertEqual(
            self.app.generate_url(host, ip, path),
            u'wss://{0}:{1}/{2}'.format(host, ip, path)
        )
