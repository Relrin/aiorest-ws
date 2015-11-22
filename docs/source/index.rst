.. aiorest-ws documentation master file, created by
   sphinx-quickstart on Wed Oct 21 22:56:10 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiorest-ws
==========

.. _GitHub: https://github.com/Relrin/aiorest-ws

This library represents as a flexible toolkit for building Web APIs, which
based on the Autobahn.ws and asyncio packages. Use the opportunities of
WebSockets for communication between clients and servers, build APIs like in
popular frameworks (Django REST, Flask, etc.) with enough simplicity,
flexibility and transparency. Develop with a pleasure!

Features
--------

- Routing
- Views (function and method-based)
- Authentication (using JSON Web Token)
- Customizing behaviour of your application through settings file
- Compressing messages for minimize of transmitted traffic (if your browser support)
- SSL support

Library installation
--------------------

Use PIP for install this library:

.. code-block:: bash

   $ pip install aiorest-ws

Getting started
---------------

Client example (JavaScript):

.. code-block:: javascript

    var ws = null;
    var isopen = false;

    window.onload = function()
    {
      ws = new WebSocket("ws://127.0.0.1:8080");
      ws.onopen = function() {
        console.log("Connected!");
        isopen = true;
      };

      ws.onmessage = function(e) {
        console.log("Result: " +  e.data);
      };

      ws.onclose = function(e) {
        console.log("Connection closed.");
        ws = null;
        isopen = false;
      }
    };

    function sendOnStaticURL() {
      if (isopen) {
        ws.send(JSON.stringify({'method': 'GET', 'url': '/hello'}));
      } else {
        console.log("Connection not opened.")
      }
    }

Client example (Python):

.. code-block:: python

    import asyncio
    import json

    from autobahn.asyncio.websocket import WebSocketClientProtocol, \
        WebSocketClientFactory


    class HelloClientProtocol(WebSocketClientProtocol):

        def onOpen(self):
            request = {'method': 'GET', 'url': '/hello'}
            self.sendMessage(json.dumps(request).encode('utf8'))

        def onMessage(self, payload, isBinary):
            message = payload.decode('utf8')
            print(message)


    if __name__ == '__main__':
        factory = WebSocketClientFactory("ws://localhost:8080", debug=False)
        factory.protocol = HelloClientProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, '127.0.0.1', 8080)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()

Server example:

.. code-block:: python

    from aiorest_ws.app import Application
    from aiorest_ws.routers import SimpleRouter
    from aiorest_ws.views import MethodBasedView

    class HelloWorld(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return "Hello, world!"

    router = SimpleRouter()
    router.register('/hello', HelloWorld, 'GET')


    if __name__ == '__main__':
        app = Application()
        app.run(host='127.0.0.1', port=8080, router=router)


Source code
-----------

The project is hosted on GitHub_

Please feel free to open an issue on the `bug tracker
<https://github.com/Relrin/aiorest-ws/issues>`_ if you have found a bug
or have some suggestions to improve the library.
The library uses `Travis <https://travis-ci.org/Relrin/aiorest-ws>`_ for
Continuous Integration.

Dependencies
------------

- Python 3.4.0+
- Autobahn.ws 0.10.0+

Contributing
------------

Please read the `guideline for contributors <https://github.com/Relrin/aiorest-ws/blob/master/CONTRIBUTING.md>`_
before making a Pull Request.

Authors and License
-------------------

The aiorest-ws package is written by Valeryi Savich.

It's **BSD** licensed and freely available. For more details read `license <https://github.com/Relrin/aiorest-ws/blob/master/LICENSE>`_ file.

Contents:
---------

.. toctree::
   :maxdepth: 2

   auth
   app
   request
   routing
   wrappers
   views
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
