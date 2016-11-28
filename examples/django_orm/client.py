# -*- coding: utf-8 -*-
import asyncio
import json

from hashlib import sha256
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory


def hash_password(password):
    return sha256(password.encode('utf-8')).hexdigest()


class HelloClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        # Create new manufacturer
        request = {
            'method': 'POST',
            'url': '/manufacturer/',
            'event_name': 'create-manufacturer',
            'args': {
                "name": 'Ford'
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get information about Audi
        request = {
            'method': 'GET',
            'url': '/manufacturer/Audi/',
            'event_name': 'get-manufacturer-detail'
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get cars list
        request = {
            'method': 'GET',
            'url': '/cars/',
            'event_name': 'get-cars-list'
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Create new car
        request = {
            'method': 'POST',
            'url': '/cars/',
            'event_name': 'create-car',
            'args': {
                'name': 'M5',
                'manufacturer': 2
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Trying to create new car with same info, but we have taken an error
        self.sendMessage(json.dumps(request).encode('utf8'))

        # # Update existing object
        request = {
            'method': 'PUT',
            'url': '/cars/Q5/',
            'event_name': 'partial-update-car',
            'args': {
                'name': 'Q7'
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get the list of manufacturers
        request = {
            'method': 'GET',
            'url': '/manufacturer/',
            'event_name': 'get-manufacturer-list',
            'args': {}
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Update manufacturer
        request = {
            'method': 'PUT',
            'url': '/manufacturer/Audi/',
            'event_name': 'update-manufacturer',
            'args': {
                'name': 'Not Audi'
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get car by name
        request = {
            'method': 'GET',
            'url': '/cars/TT/',
            'event_name': 'get-car-detail',
            'args': {}
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

    def onMessage(self, payload, isBinary):
        print("Result: {0}".format(payload.decode('utf8')))


if __name__ == '__main__':
    factory = WebSocketClientFactory("ws://localhost:8080")
    factory.protocol = HelloClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 8080)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
