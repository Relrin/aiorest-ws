# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.wrappers import Request, Response


class RequestTestCase(unittest.TestCase):

    def test_method_property(self):
        request = Request({})
        self.assertEqual(request.method, None)

        request = Request({'method': None})
        self.assertEqual(request.method, None)

        request = Request({'method': 'get'})
        self.assertEqual(request.method, 'get')

    def test_url_property(self):
        request = Request({})
        self.assertEqual(request.url, None)

        request = Request({'url': None})
        self.assertEqual(request.url, None)

        request = Request({'url': '/api'})
        self.assertEqual(request.url, '/api')

    def test_args_property(self):
        request = Request({})
        self.assertEqual(request.args, {})

        request = Request({'args': None})
        self.assertEqual(request.args, None)

        request = Request({'args': {'key': 'value'}})
        self.assertEqual(request.args, {'key': 'value'})

    def test_token_property(self):
        request = Request({})
        self.assertEqual(request.token, None)

        request = Request({'token': None})
        self.assertEqual(request.token, None)

        request = Request({'token': 'secret_token'})
        self.assertEqual(request.token, 'secret_token')

    def test_to_representation(self):
        request = Request({})
        self.assertEqual(
            request.to_representation(),
            {'method': None, 'url': None}
        )

        request = Request({'url' : '/api'})
        self.assertEqual(
            request.to_representation(),
            {'method': None, 'url': '/api'}
        )

        request = Request({'method': 'GET'})
        self.assertEqual(
            request.to_representation(),
            {'method': 'GET', 'url': None}
        )

        request = Request({'url': '/api', 'method': 'GET'})
        self.assertEqual(
            request.to_representation(),
            {'method': 'GET', 'url': '/api', }
        )


class ResponseTestCase(unittest.TestCase):

    def test_init(self):
        response = Response()
        self.assertEqual(response._content, {})

    def test_content_getter(self):
        response = Response()
        self.assertEqual(response.content, {})

        response._content = data = {'key': 'value'}
        self.assertEqual(response.content, data)

    def test_content_setter(self):
        response = Response()
        self.assertEqual(response.content, {})

        response.content = data = {'details': 'some error'}
        self.assertEqual(response._content, data)

        response.content = data = {'key': 'value'}
        self.assertEqual(response._content['data'], data)

        response.content = data = [1, 2, 3, 4, 5]
        self.assertEqual(response._content['data'], data)

    def test_append_request(self):
        request = Request({'url': '/api', 'method': 'GET'})
        response = Response()
        response.append_request(request)
        self.assertEqual(
            response.content['request'], request.to_representation()
        )
