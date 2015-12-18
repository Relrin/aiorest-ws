.. _aiorest-ws-request:

Factories and protocols
=======================

.. currentmodule:: aiorest_ws.request

This documentation page contains information about :class:`RequestHandlerProtocol`
and :class:`RequestHandlerFactory`, which provide mechanisms for transferring data
through WebSockets, and their processing.

RequestHandler protocol
-----------------------

:class:`RequestHandlerProtocol` instance, created for every client connection.
The instance of this class (which based on the Authobahn.ws implementation)
processing client request asynchronously. This means that the protocol never
waits for an event, but responds to events when they arrived from the network.

Base algorithm for the default implementation, described by the next
scheme:

1) Get a message (which can be JSON or base64 string) from the client.

2) Decode message and wrap him into :class:`Request` instance.

3) Process request through invoke routers ``process_request`` method.

4) Get response data from :class:`Response` instance and encode message.

5) Send result data (in the same form, which had taken at the 1st step) to the client.


Also what necessary to know, when you're working with this protocol:

1) Protocols can retrieve the message, why a connection was terminated.

2) You can create multiple connections to a server.

RequestHandler factory
----------------------

:class:`RequestHandlerFactory` is a class, which instantiates client connections.

.. note::

    Persistent configuration information is not saved in the instantiated
    protocol. For such cases kept data in a factory classes, databases, etc.

This factory also provide a access for the client handlers (:class:`RequestHandlerProtocol`
instances) to the general router, which used for processing users requests.

If necessary provide any access to databases, cache storages or whatever you want,
strongly recommend to use properties. For example it can be something like that:

.. code-block:: python

    from aiorest_ws.request import RequestHandlerFactory

    class CustomHandlerFactory(RequestHandlerFactory):
    """Factory, which also provide access to the cookies."""
    def __init__(self, *args, **kwargs):
        super(CustomHandlerFactory, self).__init__(*args, **kwargs)
        self._cookies = kwargs.get('cookies_dump', {})

    @property
    def cookies(self):
        return self._cookies

For more information about factories with WebSockets support, overriding behaviour of
aiorest-ws :class:`RequestHandlerFactory` factory (which rely onto Authobahn.ws
implementation) look into `Autobahn.ws documentation <http://autobahn.ws/python/websocket/programming.html>`_.
