.. _aiorest-ws-auth:

Authentication
==============

At this section you will find description about the default user abstraction
and using JSON Web Token as a basic implementation for authentication.

User abstraction
----------------

:class:`User` class provide a very useful user abstraction, which used for
storing information about current online user. Most basic fields are defined
inside his base class – :class:`AbstractUser`.

.. note::
    At the current release :class:`User` model used with SQLite database,
    however, if necessary, you can write your own implementation for any
    other database (MySQL, PostgreSQL, Oracle, DB2, etc).

.. autoclass:: aiorest_ws.auth.user.abstractions.User
    :members:
    :inherited-members:
    :show-inheritance:

JSON Web Token (JWT)
--------------------

JSON Web Token (JWT) is an open standard (RFC 7519) that defines a compact and
self-contained way for securely transmitting information between parties as a
JSON object. This information can be verified and trusted because it is digitally
signed. JWTs can be signed using a secret (with HMAC algorithm) or a public/private
key pair using RSA. (c) jwt.io

For more details about how JSON Web Token works, his advantages and
why necessary to use it, you can read `there <http://jwt.io/introduction/>`_.

Also you can look on `example <https://github.com/Relrin/aiorest-ws/tree/master/examples/auth_token>`_
which implement simple user registration and log-in/log out mechanism with JSON Web Tokens.

At this package provided middleware and manager classes, which used for add
support JWT inside you application.

.. autoclass:: aiorest_ws.auth.token.middlewares.JSONWebTokenMiddleware
    :members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: aiorest_ws.auth.token.managers.JSONWebTokenManager
    :members:
    :inherited-members:
    :show-inheritance:



