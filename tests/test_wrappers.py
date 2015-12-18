# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import BaseAPIException
from aiorest_ws.wrappers import Request, Response


class RequestTestCase(unittest.TestCase):

    def test_init_with_patching(self):
        data = {'token': 'base64token'}
        request = Request(**data)
        self.assertEqual(request.token, 'base64token')

    def test_method_property(self):
        data = {}
        request = Request(**data)
        self.assertEqual(request.method, None)

    def test_method_property_2(self):
        data = {'method': None}
        request = Request(**data)
        self.assertEqual(request.method, None)

    def test_method_property_3(self):
        data = {'method': 'get'}
        request = Request(**data)
        self.assertEqual(request.method, 'get')

    def test_url_property(self):
        data = {}
        request = Request(**data)
        self.assertEqual(request.url, None)

    def test_url_property_2(self):
        data = {'url': None}
        request = Request(**data)
        self.assertEqual(request.url, None)

    def test_url_property_3(self):
        data = {'url': '/api'}
        request = Request(**data)
        self.assertEqual(request.url, '/api')

    def test_args_property(self):
        data = {}
        request = Request(**data)
        self.assertEqual(request.args, {})

    def test_args_property_2(self):
        data = {'args': None}
        request = Request(**data)
        self.assertEqual(request.args, None)

    def test_args_property_3(self):
        data = {'args': {'key': 'value'}}
        request = Request(**data)
        self.assertEqual(request.args, {'key': 'value'})

    def test_to_representation(self):
        data = {}
        request = Request(**data)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_2(self):
        data = {'url': '/api'}
        request = Request(**data)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_3(self):
        data = {'method': 'GET'}
        request = Request(**data)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_4(self):
        data = {'url': '/api', 'method': 'GET', 'event_name': 'test-event'}
        request = Request(**data)
        self.assertEqual(
            request.to_representation(), {'event_name': data['event_name']}
        )

    def test_get_argument(self):
        data = {'args': {'param': 'test'}}
        request = Request(**data)
        self.assertEqual(request.get_argument('param'), 'test')

    def test_get_argument_with_unfilled_dict(self):
        data = {'args': {}}
        request = Request(**data)
        self.assertIsNone(request.get_argument('param'), None)

    def test_get_argument_with_unfilled_dict_2(self):
        data = {}
        request = Request(**data)
        self.assertIsNone(request.get_argument('param'))


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
        response.content = data = {'detail': 'my description'}
        self.assertEqual(response._content['data'], data)

    def test_content_setter_3(self):
        response = Response()
        response.content = data = {'key': 'value'}
        self.assertEqual(response._content['data'], data)

    def test_content_setter_4(self):
        response = Response()
        response.content = data = [1, 2, 3, 4, 5]
        self.assertEqual(response._content['data'], data)

    def test_wrap_exception(self):
        exception = BaseAPIException()
        response = Response()
        response.wrap_exception(exception)
        self.assertIn('detail', response._content)
        self.assertEqual(response._content['detail'], exception.detail)

    def test_append_request(self):
        data = {'url': '/api', 'method': 'GET', 'event_name': 'test-event'}
        request = Request(**data)
        response = Response()
        response.append_request(request)
        self.assertEqual(response.content['event_name'], request.event_name)

    def test_append_request_with_undefined_event_name(self):
        data = {'url': '/api', 'method': 'GET'}
        request = Request(**data)
        response = Response()
        response.append_request(request)
        self.assertEqual(response.content['event_name'], request.event_name)
