.. _aiorest-ws-views:

Views
=====

.. currentmodule:: aiorest_ws.views

There you can find description about views and endpoints, which can be used
by developers for implementing APIs. By this framework supported method- and
function-based views.

Method-based views
------------------

It is mostly preferred approach to make your APIs. For using this class
enough to inherit from it and override required methods or fields. For example:

.. code-block:: python

    from aiorest_ws.views import MethodBasedView

    class HelloWorld(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return "Hello, world!"

After that implementation, register the view

.. code-block:: python

    from aiorest_ws.routers import SimpleRouter

    router = SimpleRouter()
    router.register('/hello', HelloWorld, 'GET')

Function-based views
--------------------

Also aiorest-ws support function-based views, which you can import from
``aiorest_ws.endpoints`` module. He contains special wrappers, which provide
syntactic sugar for developers. Its looks like this:

.. code-block:: python

    from aiorest_ws.decorators import endpoint

    @endpoint(path='/hello', methods='GET')
    def hello_world(request, *args, **kwargs):
        return "Hello, world!"

And don't forget to register endpoint inside some router:

.. code-block:: python

    from aiorest_ws.routers import SimpleRouter

    endpoint_router = SimpleRouter()
    endpoint_router.register_endpoint(hello_world)
