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
        # Create new address
        request = {
            'method': 'POST',
            'url': '/address/',
            'event_name': 'create-address',
            'args': {
                "email_address":'some_address@google.com'
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get existing user
        request = {
            'method': 'GET',
            'url': '/user/5/',
            'event_name': 'get-user-detail'
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Get users list
        request = {
            'method': 'GET',
            'url': '/user/list/',
            'event_name': 'get-user-list'
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Create new user with address
        request = {
            'method': 'POST',
            'url': '/user/',
            'event_name': 'create-user',
            'args': {
                'name': 'Neyton',
                'fullname': 'Neyton Drake',
                'password': hash_password('123456'),
                'addresses': [{"id": 1}, ]
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Trying to create new user with same info, but we have taken an error
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Update existing object
        request = {
            'method': 'PUT',
            'url': '/user/6/',
            'event_name': 'partial-update-user',
            'args': {
                'fullname': 'Definitely not Neyton Drake',
                'addresses': [{"id": 1}, {"id": 2}]
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # Create few user for a one request
        request = {
            'method': 'POST',
            'url': '/user/list/',
            'event_name': 'create-user-list',
            'args': {
                'list': [
                    {
                        'name': 'User 1',
                        'fullname': 'User #1',
                        'password': hash_password('1q2w3e'),
                        'addresses': [{"id": 1}, ]
                    },
                    {
                        'name': 'User 2',
                        'fullname': 'User #2',
                        'password': hash_password('qwerty'),
                        'addresses': [{"id": 2}, ]
                    },
                ]
            }
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
