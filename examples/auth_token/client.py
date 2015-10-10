# -*- coding: utf-8 -*-
import asyncio
import json

from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory


class AuthAPIClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        # create user
        request = {
            'method': 'POST', 'url': '/auth/user/create',
            'args': {
                'username': 'admin',
                'password': '123456',
                'is_superuser': True, 'is_staff': False, 'is_user': False
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

        # take there message, that this user already created
        self.sendMessage(json.dumps(request).encode('utf8'))

        # log in
        request = {
            'method': 'POST',
            'url': '/auth/login',
            'args': {
                'username': 'admin',
                'password': '123456',
            }
        }
        self.sendMessage(json.dumps(request).encode('utf8'))

    def onMessage(self, payload, isBinary):
        message = json.loads(payload.decode('utf8'))
        print("Result: {0}".format(message))
        if 'request' in message and message['request']['url'] == "/auth/login":
            # log out
            request = {
                'method': 'POST',
                'url': '/auth/logout',
                'token': message['data']['token']
            }
            self.sendMessage(json.dumps(request).encode('utf8'))


if __name__ == '__main__':
    factory = WebSocketClientFactory("ws://localhost:8080", debug=False)
    factory.protocol = AuthAPIClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 8080)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
