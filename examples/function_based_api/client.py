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

        # sum endpoint with arg in URL path (two random digits)
        for _ in range(0, 10):
            digit_1 = str(randint(1, 100))
            digit_2 = str(randint(1, 100))
            request = {'method': 'GET',
                       'url': '/sum/{0}/{1}'.format(digit_1, digit_2)}
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
