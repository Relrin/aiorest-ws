# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import BaseAPIException
from aiorest_ws.wrappers import Request, Response


class RequestTestCase(unittest.TestCase):

    def test_init_with_patching(self):
        options = {'token': 'base64token'}
        request = Request(**options)
        self.assertEqual(request.token, 'base64token')

    def test_method_property(self):
        options = {}
        request = Request(**options)
        self.assertEqual(request.method, None)

    def test_method_property_with_none_value(self):
        options = {'method': None}
        request = Request(**options)
        self.assertEqual(request.method, None)

    def test_method_property_with_specified_dictionary(self):
        options = {'method': 'get'}
        request = Request(**options)
        self.assertEqual(request.method, 'get')

    def test_url_property(self):
        options = {}
        request = Request(**options)
        self.assertEqual(request.url, None)

    def test_url_property_with_none_value(self):
        options = {'url': None}
        request = Request(**options)
        self.assertEqual(request.url, None)

    def test_url_property_with_specified_dictionary(self):
        options = {'url': '/api'}
        request = Request(**options)
        self.assertEqual(request.url, '/api')

    def test_args_property_with_empty_dict(self):
        options = {}
        request = Request(**options)
        self.assertEqual(request.args, {})

    def test_args_property_with_none_value(self):
        options = {'args': None}
        request = Request(**options)
        self.assertEqual(request.args, None)

    def test_args_property_with_specified_dictionary(self):
        options = {'args': {'key': 'value'}}
        request = Request(**options)
        self.assertEqual(request.args, {'key': 'value'})

    def test_data_property_by_default(self):
        request = Request()
        self.assertEqual(request.data, None)

    def test_data_property_with_empty_dictionary(self):
        options = {'data': {}}
        request = Request(**options)
        self.assertEqual(request.data, {})

    def test_data_property_with_specified_dictionary(self):
        options = {'data': {'user': 'admin', 'password': 'mysecretpassword'}}
        request = Request(**options)
        self.assertEqual(request.data, options['data'])

    def test_data_property_with_list(self):
        options = {'data': [{'pk': 1}, {'pk': 2}, {'pk': 3}]}
        request = Request(**options)
        self.assertEqual(request.data, options['data'])

    def test_to_representation_with_empty_dictionary(self):
        options = {}
        request = Request(**options)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_with_specified_url_argument(self):
        options = {'url': '/api'}
        request = Request(**options)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_with_specified_method_argument(self):
        options = {'method': 'GET'}
        request = Request(**options)
        self.assertEqual(request.to_representation(), {'event_name': None})

    def test_to_representation_with_specified_url_and_method_argument(self):
        options = {'url': '/api', 'method': 'GET', 'event_name': 'test-event'}
        request = Request(**options)
        self.assertEqual(
            request.to_representation(), {'event_name': options['event_name']}
        )

    def test_get_argument(self):
        options = {'args': {'param': 'test'}}
        request = Request(**options)
        self.assertEqual(request.get_argument('param'), 'test')

    def test_get_argument_with_unfilled_dict(self):
        options = {'args': {}}
        request = Request(**options)
        self.assertIsNone(request.get_argument('param'), None)

    def test_get_argument_with_unfilled_dict_2(self):
        options = {}
        request = Request(**options)
        self.assertIsNone(request.get_argument('param'))


class ResponseTestCase(unittest.TestCase):

    def test_init(self):
        response = Response()
        self.assertEqual(response._content, {})

    def test_content_getter_with_empty_dictionary(self):
        response = Response()
        self.assertEqual(response.content, {})

    def test_content_getter_with_specified_dictionary(self):
        response = Response()
        response._content = options = {'key': 'value'}
        self.assertEqual(response.content, options)

    def test_content_setter_with_empty_dictionary(self):
        response = Response()
        self.assertEqual(response.content, {})

    def test_content_setter_with_specified_dictionary(self):
        response = Response()
        response.content = options = {'detail': 'my description'}
        self.assertEqual(response._content['data'], options)

    def test_content_setter_with_specified_dictionary_2(self):
        response = Response()
        response.content = options = {'key': 'value'}
        self.assertEqual(response._content['data'], options)

    def test_content_setter_with_specified_list(self):
        response = Response()
        response.content = options = [1, 2, 3, 4, 5]
        self.assertEqual(response._content['data'], options)

    def test_wrap_exception(self):
        exception = BaseAPIException()
        response = Response()
        response.wrap_exception(exception)
        self.assertIn('detail', response._content)
        self.assertEqual(response._content['detail'], exception.detail)

    def test_append_request(self):
        options = {'url': '/api', 'method': 'GET', 'event_name': 'test-event'}
        request = Request(**options)
        response = Response()
        response.append_request(request)
        self.assertEqual(response.content['event_name'], request.event_name)

    def test_append_request_with_undefined_event_name(self):
        options = {'url': '/api', 'method': 'GET'}
        request = Request(**options)
        response = Response()
        response.append_request(request)
        self.assertEqual(response.content['event_name'], request.event_name)
