.. _aiorest-ws-routing:

Routing
=======

.. currentmodule:: aiorest_ws.routers

Register endpoints
------------------

The basic implementation :class:`SimpleRouter` have support to register
endpoints with function or method-based views.

Example of using for the endpoint with method-based view:

.. code-block:: python

    from aiorest_ws.routers import SimpleRouter
    from aiorest_ws.views import MethodBasedView

    class MethodView(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return "aiorest-ws is awesome!"

    router = SimpleRouter()
    router.register('/test_view', MethodView, 'GET')

and the same, but with function-based view:

.. code-block:: python

    from aiorest_ws.decorators import endpoint
    from aiorest_ws.routers import SimpleRouter

    @endpoint(path='/test_view', methods='GET')
    def function_based_view(request, *args, **kwargs):
        return "aiorest-ws is awesome!"

    router = SimpleRouter()
    router.register(function_based_view)

Request processing
------------------

When client send a request to the our API, he will have
processed by the following algorithm:

1. Get the URL from request
2. Search handler by received URL
3. If handler was found, do the next steps:

   3.1. Make pre-processing of request, via invoke middlewares

   3.2. Search suitable serializer for generating response

   3.3. Processing request by calling specified method from the view

4. Serialize response
5. Return response

Merge endpoint lists
--------------------

In situations, when you separate functionality of your application on a parts,
can be useful to union endpoints into one router, which will have been used for
processing client requests further.

:class:`SimpleRouter` have ``include`` method, which provide a mechanism, which copy endpoints
from another router into himself.

Example of using:

.. code-block:: python


    # hello_routing.py

    from aiorest_ws.routers import SimpleRouter
    from aiorest_ws.views import MethodBasedView

    class HelloWorld(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return "Hello from hello_routing.py!"

    hello_router = SimpleRouter()
    hello_router.register('/hello_module/hello', HelloWorld, 'GET')

    # main_routing.py

    from hello_routing import hello_router

    from aiorest_ws.routers import SimpleRouter
    from aiorest_ws.views import MethodBasedView

    class HelloWorld(MethodBasedView):
        def get(self, request, *args, **kwargs):
            return return "Hello, world!"

    main_router = SimpleRouter()
    main_router.register('/hello', HelloWorld, 'GET')
    # after this line of code main_router will be contains 2 endpoints
    main_router.include(hello_router)
