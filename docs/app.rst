.. _aiorest-ws-app:

Application usage
=================

.. currentmodule:: aiorest_ws.app

This module provide :class:`Application` class, which used as entry point
for your REST applications with WebSockets.


Run a instance of application
-----------------------------

Before running the server with you application necessary to satisfy few
conditions:

1. Import required modules of ``aiorest-ws`` package to write your own
handler. It can be method-based:

.. code-block:: python

    from aiorest_ws.views import MethodBasedView

    class HelloWorld(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return "Hello, world!"

or function-based view:

.. code-block:: python

    from aiorest_ws.decorators import endpoint

    @endpoint(path='/hello', methods='GET')
    def hello_world(request, *args, **kwargs):
        return "Hello, world!"

2. Add implemented endpoint to the instance of :class:`SimpleRouter` class or
derived from it. For method-based view its looks like this:

.. code-block:: python

    from aiorest_ws.routers import SimpleRouter

    router = SimpleRouter()
    router.register('/hello', HelloWorld, 'GET')

and a little bit different for a function-based approach:

.. code-block:: python

    from aiorest_ws.routers import SimpleRouter

    router = SimpleRouter()
    router.register_endpoint(hello_world)

3. Set user-defined router and start ``Application`` instance via ``run``
method:

.. code-block:: python

    # By default server listen on 127.0.0.1:8080
    app = Application()
    app.run(router=router)

Constructor arguments
---------------------

Application instance can get in the constructor the next arguments:

- factory
    Factory class, used for instantiating protocol objects. Must be inherited
    from the :class:`RequestHandlerFactory` class. Default to ``RequestHandlerFactory`` class

- protocol
    Protocol class, used for processing client requests. Must be inherited from
    the :class:`RequestHandlerProtocol` class. Default to ``RequestHandlerProtocol`` class

- certificate
    Path to SSL certificate. Default to ``None``

- key
    Path to private key of SSL certificate. Default to ``None``

- middlewares
    List of middlewares, applied for every request. Default to ``[]``

Middlewares
-----------

:class:`Application` can receive list of middlewares, which used for
pre-processing requests in the order of their appearance.

Example of using:

.. code-block:: python

    default_middlewares = (MyCustomMiddleware, )
    app = Application(middlewares=default_middlewares)
    app.run()

For more demonstrative example you can look onto `example of API with JSON WebTokens <https://github.com/Relrin/aiorest-ws/tree/master/examples/auth_token>`_

Run method
----------

.. note::

    If you want to change behaviour of ``run`` method, then focus on override
    some inner function or procedure. For example, it can be ``generate_factory``
    method, which return configured factory class.

``Run`` method its a entry point for your all applications, because it start
server on the specified ip and port. Default realization of this method can get
the next parameters:

- ip
    The hostname to listen on. Default to ``'127.0.0.1'``

- port
    The port of the webserver. Defaults to ``8080``

- path
    Path to REST APIs relatively to server. Default to ``''``

    For example if user has left ``ip``, ``port`` by default, and set ``path='api'``,
    then server REST with WebSockets will be available on the ``ws://127.0.0.1:8080/api``
    or ``wss://127.0.0.1:8080/api`` (when SSL enabled)

- debug
    If given, enable or disable debug mode. Default to ``False``

- router
    Router with registered endpoints
    Default to ``None`` (instead None object :class:`Application` using instance of :class:`SimpleRouter` class)

- compress
    Enable compressing for transmitted traffic. Default to ``False``

Running with SSL
----------------

.. warning::

    Don't use non-encrypted channels for transferring user data
    (passwords, tokens, etc.).

Aiorest-ws framework support running server with SSL. Just append ``certificate``
and ``key`` options to the :class:`Application` constructor:

.. code-block:: python

    # REST with WebSockets will be available on wss://127.0.0.1:8080
    app = Application(certificate='path/to/my.crt', key='path/to/my.key')
    app.run(host='127.0.0.1', port=8080, router=router)

In situations, when required to test your application for a work with SSL, but
certificate has expired or have not provided by the customer, you can generate
your own self-signed certificate via OpenSSL:

.. code-block:: bash

    $ openssl genrsa -out server.key 2048
    $ openssl req -new -key server.key -out server.csr
    $ openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt
    $ openssl x509 -in server.crt -out server.pem

Running with traffic compression
--------------------------------

:class:`Application` instance have support to compress all transmitted
traffic by the network. This feature was taken from Autobahn.ws implementation
(which rely onto `this <https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression-28>`_ document).

For enable this feature is enough to append ``compress`` parameter with
``True`` value to the ``run`` method:

.. code-block:: python

    app = Application()
    app.run(compress=True)
