# -*- coding: utf-8 -*-
"""
    This module implements the central application object.
"""
import asyncio
import ssl
from time import gmtime, strftime

from aiorest_ws.__init__ import __version__
from aiorest_ws.request import RequestHandlerFactory, RequestHandlerProtocol
from aiorest_ws.validators import check_and_set_subclass
from aiorest_ws.utils.websocket import deflate_offer_accept as accept

__all__ = ('Application', )


class Application(object):
    """Main application of aiorest-ws framework."""

    _factory = RequestHandlerFactory
    _protocol = RequestHandlerProtocol
    _certificate = None
    _key = None
    _middlewares = []

    def __init__(self, *args, **options):
        """Initialization of Application instance."""
        super(Application, self).__init__()
        self.factory = options.get('factory')
        self.protocol = options.get('protocol')
        self.certificate = options.get('certificate')
        self.key = options.get('key')

        middleware_classes = options.get('middlewares', ())
        for middleware in middleware_classes:
            self._middlewares.append(middleware())

    @property
    def factory(self):
        """Get factory class."""
        return self._factory

    @factory.setter
    def factory(self, factory):
        """Set factory class.

        :param factory: subclass of RequestHandlerFactory.
        """
        if factory:
            check_and_set_subclass(self, '_factory', factory,
                                   RequestHandlerFactory)

    @property
    def middlewares(self):
        """Get list of used middlewares."""
        return self._middlewares

    @property
    def protocol(self):
        """Get protocol class."""
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """Set protocol class.

        :param factory: subclass of RequestHandlerProtocol.
        """
        if protocol:
            check_and_set_subclass(self, '_protocol', protocol,
                                   RequestHandlerProtocol)

    @property
    def certificate(self):
        """Get filepath to certificate."""
        return self._certificate

    @certificate.setter
    def certificate(self, certificate):
        """Setter for certificate.

        :param certificate: path to certificate file.
        """
        self._certificate = certificate

    @property
    def key(self):
        """Get private key for certificate."""
        return self._key

    @key.setter
    def key(self, key):
        """Set private key for certificate.

        :param key: private key for certificate.
        """
        self._key = key

    @property
    def url(self):
        """Get url to WebSocket REST API."""
        if self.isSecure:
            url = "wss://{0}:{1}/{2}"
        else:
            url = "ws://{0}:{1}/{2}"
        return url

    @property
    def isSecure(self):
        """Property, which help us to understand, use SSL or not."""
        return self.certificate and self.key

    def _get_ssl_context(self):
        """Generating SSL context for asyncio loop."""
        if self.isSecure:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ssl_context.load_cert_chain(self.certificate, self.key)
        else:
            ssl_context = None
        return ssl_context

    def _init_factory(self, url, **options):
        """Create a factory instance."""
        debug = options.get('debug', False)

        factory = self.factory(url, debug=debug)
        factory.protocol = self.protocol
        return factory

    def _enable_compressing(self, factory, **options):
        """Set compression message for factory, if defined."""
        compress = options.get('compress', False)

        if compress:
            factory.setProtocolOptions(perMessageCompressionAccept=accept)

    def _set_factory_router(self, factory, **options):
        """Set users router for factory, if defined."""
        router = options.get('router', None)
        assert router, "Argument `router` must be defined for Application."

        factory.router = router
        factory.router._middlewares = self.middlewares

    def generate_factory(self, url, **options):
        """Create and initialize factory instance."""
        factory = self._init_factory(url, **options)
        self._enable_compressing(factory, **options)
        self._set_factory_router(factory, **options)
        return factory

    def generate_url(self, host, port, path=''):
        """Generate URL to application."""
        return self.url.format(host, port, path)

    def run(self, **options):
        """Create and start web server with some IP and PORT.

        :param options: parameters, which can be used for configuration
                        of the Application.
        """
        host = options.get('host', '127.0.0.1')
        port = options.get('port', 8080)
        path = options.get('path', '')
        url = self.generate_url(host, port, path)

        factory = self.generate_factory(url, **options)
        ssl_context = self._get_ssl_context()

        loop = asyncio.get_event_loop()
        server_coroutine = loop.create_server(
            factory, host, port, ssl=ssl_context
        )
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
