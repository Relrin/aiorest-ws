# -*- coding: utf-8 -*-
"""
    This module implements the central application object.
"""
__all__ = ('Application', )

import asyncio
import ssl

from time import gmtime, strftime

from .__init__ import __version__
from .server import RestWSServerFactory, RestWSServerProtocol
from .validators import check_and_set_subclass
from .utils.websocket import deflate_offer_accept as accept


class Application(object):
    """Main application of aiorest-ws framework."""

    _factory = RestWSServerFactory
    _protocol = RestWSServerProtocol
    _certificate = None
    _key = None

    def __init__(self, *args, **options):
        """Initialization of Application instance."""
        super(Application, self).__init__()
        self.factory = options.get('factory')
        self.protocol = options.get('protocol')
        self.certificate = options.get('certificate')
        self.key = options.get('key')

    @property
    def factory(self):
        return self._factory

    @factory.setter
    def factory(self, factory):
        if factory:
            check_and_set_subclass(self, '_factory', factory,
                                   RestWSServerFactory)

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        if protocol:
            check_and_set_subclass(self, '_protocol', protocol,
                                   RestWSServerProtocol)

    @property
    def certificate(self):
        return self._certificate

    @certificate.setter
    def certificate(self, certificate):
        self._certificate = certificate

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def url(self):
        if self.isSecure:
            url = "wss://{0}:{1}/{2}"
        else:
            url = "ws://{0}:{1}/{2}"
        return url

    @property
    def isSecure(self):
        """Property, which help us to understand, using SSL or not."""
        if self.certificate and self.key:
            isSecure = True
        else:
            isSecure = False
        return isSecure

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
        router = options.get('router')

        if router:
            factory.router = router

    def _allow_hixie76(self, factory):
        """Allow using hixie-76 if supported.

        For more details check the link below:
        https://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
        """
        factory.setProtocolOptions(allowHixie76=True)

    def generate_factory(self, url, **options):
        """Create and initialize factory instance."""
        factory = self._init_factory(url, **options)
        self._enable_compressing(factory, **options)
        self._set_factory_router(factory, **options)
        self._allow_hixie76(factory)
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
        server_coroutine = loop.create_server(factory, host, port,
                                              ssl=ssl_context)
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
