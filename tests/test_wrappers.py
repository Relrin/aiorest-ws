# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.wrappers import Request, Response
from aiorest_ws.exceptions import NotSupportedArgumentType


class RequestTestCase(unittest.TestCase):

    def test_init_failed(self):
        self.assertRaises(NotSupportedArgumentType, Request, None)

    def test_method_property(self):
        request = Request({})
        self.assertEqual(request.method, None)

    def test_method_property_2(self):
        request = Request({'method': None})
        self.assertEqual(request.method, None)

    def test_method_property_3(self):
        request = Request({'method': 'get'})
        self.assertEqual(request.method, 'get')

    def test_url_property(self):
        request = Request({})
        self.assertEqual(request.url, None)

    def test_url_property_2(self):
        request = Request({'url': None})
        self.assertEqual(request.url, None)

    def test_url_property_3(self):
        request = Request({'url': '/api'})
        self.assertEqual(request.url, '/api')

    def test_args_property(self):
        request = Request({})
        self.assertEqual(request.args, {})

    def test_args_property_2(self):
        request = Request({'args': None})
        self.assertEqual(request.args, None)

    def test_args_property_3(self):
        request = Request({'args': {'key': 'value'}})
        self.assertEqual(request.args, {'key': 'value'})

    def test_token_property(self):
        request = Request({})
        self.assertEqual(request.token, None)

    def test_token_property_2(self):
        request = Request({'token': None})
        self.assertEqual(request.token, None)

    def test_token_property_3(self):
        request = Request({'token': 'secret_token'})
        self.assertEqual(request.token, 'secret_token')

    def test_to_representation(self):
        request = Request({})
        self.assertEqual(
            request.to_representation(),
            {'method': None, 'url': None}
        )

    def test_to_representation_2(self):
        request = Request({'url' : '/api'})
        self.assertEqual(
            request.to_representation(),
            {'method': None, 'url': '/api'}
        )

    def test_to_representation_3(self):
        request = Request({'method': 'GET'})
        self.assertEqual(
            request.to_representation(),
            {'method': 'GET', 'url': None}
        )

    def test_to_representation_4(self):
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

    def test_content_getter_2(self):
        response = Response()
        response._content = data = {'key': 'value'}
        self.assertEqual(response.content, data)

    def test_content_setter(self):
        response = Response()
        self.assertEqual(response.content, {})

    def test_content_setter_2(self):
        response = Response()
        response.content = data = {'details': 'some error'}
        self.assertEqual(response._content, data)

    def test_content_setter_3(self):
        response = Response()
        response.content = data = {'key': 'value'}
        self.assertEqual(response._content['data'], data)

    def test_content_setter_4(self):
        response = Response()
        response.content = data = [1, 2, 3, 4, 5]
        self.assertEqual(response._content['data'], data)

    def test_append_request(self):
        request = Request({'url': '/api', 'method': 'GET'})
        response = Response()
        response.append_request(request)
        self.assertEqual(
            response.content['request'], request.to_representation()
        )
