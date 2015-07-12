# aiorest-ws [![Build Status](https://travis-ci.org/Relrin/aiorest-ws.svg)](https://travis-ci.org/Relrin/aiorest-ws)
[![Coverage Status](https://coveralls.io/repos/Relrin/aiorest-ws/badge.svg?branch=master&service=github)](https://coveralls.io/github/Relrin/aiorest-ws?branch=master)
REST framework with WebSockets support

This library represents as a flexible toolkit for building Web APIs, which used WebSockets and asyncio package.

Requirements
-----
- Python 3.4+
- Autobahn.ws
- asyncio

License
-----
This library published under MIT license. Feel free for using and customizing.

Roadmap (by priority) to releases:
-----
v1.0:
- JSON/XML serializers
- Routing
- Views (function and class-based)
- Authentication
- Documentation over all code

v1.1:
- Settings file for overriding behavior of serializers, routers, etc
- Compatible with Django and SQLAlchemy ORMs
- Filters support over querysets

v1.2:
- Web browsable API (similar on swagger?)
