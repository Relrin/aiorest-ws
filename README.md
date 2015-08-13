# aiorest-ws [![Build Status](https://travis-ci.org/Relrin/aiorest-ws.svg)](https://travis-ci.org/Relrin/aiorest-ws) [![Coverage Status](https://coveralls.io/repos/Relrin/aiorest-ws/badge.svg?branch=master&service=github)](https://coveralls.io/github/Relrin/aiorest-ws?branch=master)
REST framework with WebSockets support

This library represents as a flexible toolkit for building Web APIs, which using WebSockets and asyncio package.

Requirements
-----
- Python 3.4+
- Autobahn.ws
- asyncio

License
-----
This library published under BSD license. For more details read [LICENSE](https://github.com/Relrin/aiorest-ws/blob/master/LICENSE) file.

Contributing
-----
Read [CONTRIBUTING](https://github.com/Relrin/aiorest-ws/blob/master/CONTRIBUTING.md) file for more information.

Roadmap (by priority) to releases:
-----
v1.0:
- [x] JSON/XML serializers
- [x] Routing
- [x] Views (function and method-based)
- [ ] Authentication
- [ ] Documentation over all code (~70-80% done)

v1.1:
- Settings file for overriding behavior of serializers, routers, etc
- Compatible with Django and SQLAlchemy ORMs
- Filters support over querysets

v1.2:
- Improve scalability of aiorest-ws (balancer instance)
- Notification support

v1.3:
- Web browsable API (similar on swagger?)

Getting started
---------------
#### Client (JavaScript)
```javascript
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
```

#### Client (Python)
```python
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
```

#### Server
```python
from aiorest_ws.app import Application
from aiorest_ws.routers import RestWSRouter
from aiorest_ws.views import MethodBasedView

class HelloWorld(MethodBasedView):
    def get(self, request, *args, **kwargs):
        return "Hello, world!"

router = RestWSRouter()
router.register('/hello', HelloWorld, 'GET')


if __name__ == '__main__':
    app = Application()
    app.run(host='127.0.0.1', port=8080, router=router)
```

Also you can look more examples [there](https://github.com/Relrin/aiorest-ws/tree/master/examples).

Running server with SSL
-----

Aiorest-ws framework support running server with SSL. Just append ```certificate``` and ```key``` options to the ```Application``` constructor:

```python
# WebSockets will be available on wss://127.0.0.1:8080/api
app = Application(certificate='path/to/my.crt', key='path/to/my.key')
app.run(host='127.0.0.1', port=8080, path='api', router=router)
```

If you don't have any certificates and keys, but want to run server with SSL, then generate self-signed certificate via OpenSSL:

```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt
openssl x509 -in server.crt -out server.pem
```
