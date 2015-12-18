.. _aiorest-ws-wrappers:

HTTP wrappers
=============

.. currentmodule:: aiorest_ws.wrappers

On this documentation page you will find definition of classes, which used
for wrapping inner data of aiorest-ws into HTTP-like request or response
objects.

Request
-------

Properties:

- method

    Returns a method name as string, which specified by client at the request.

- url

    Returns a request URL as string of described resource which necessary to take.

- args

    Returns dictionary of arguments for request.

    For example in the "classical REST" you can send the HTTP request by
    the URL something like http://mywebsite.com/api/?name=admin&password=admin
    and a part of him, parameters, converted later to the dictionary
    ``{'name': admin, 'password': admin}``.

- event_name

    Returns event name, which defined by the client in the request.

    This string value will have appended to response and used by aiorest-ws clients
    dispatchers, when necessary to find the most suitable registered function, which
    intended for processing response.

Available methods:

- to_representation

    Returns part of request as a dictionary object. It used for serializing and
    appending ``event_name`` to the response object.

- get_argument

    As an function argument take ``name``, which necessary to extract from request.
    If this parameter not found, returns ``None``.

Response
--------

Properties:

- content

    This property return content (or result some view), which will be serialized
    later as response for client.

Available methods:

- wrap_exception

    As an argument take ``exception`` object (which inherited from
    :class:`BaseAPIException`) and set his message for ``content`` property.

- append_request

    As an argument take ``request``, which used for appending part of :class:`Request` object
    to the :class:`Response` object.
