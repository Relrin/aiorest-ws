# -*- coding: utf-8 -*-
import asyncio
import json

from random import randint
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory


class HelloClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        # hello username
        request = {'method': 'GET',
                   'url': '/hello/'}
        self.sendMessage(json.dumps(request).encode('utf8'))

        # hello endpoint with arg in URL path (`user` and random digit)
        for _ in range(0, 10):
            user_id = str(randint(1, 100))
            request = {'method': 'GET',
                       'url': '/hello/user/' + user_id}
            self.sendMessage(json.dumps(request).encode('utf8'))

        # send request and parameters are separately
        digits = [randint(1, 10) for _ in range(3)]
        print("calculate sum for {}".format(digits))
        request = {'method': 'GET',
                   'url': '/calc/sum',
                   'args': {'digits': digits}}
        self.sendMessage(json.dumps(request).encode('utf8'))

    def onMessage(self, payload, isBinary):
        print("Result: {0}".format(payload.decode('utf8')))


if __name__ == '__main__':
    factory = WebSocketClientFactory("ws://localhost:8080", debug=False)
    factory.protocol = HelloClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 8080)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
