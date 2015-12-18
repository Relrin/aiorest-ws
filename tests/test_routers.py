# -*- coding: utf-8 -*-
import json
import unittest
import unittest.mock

from fixtures.fakes import InvalidEndpoint, FakeView, FakeGetView, \
    FakeEndpoint, FakeTokenMiddleware, FakeTokenMiddlewareWithExc

from aiorest_ws.decorators import endpoint
from aiorest_ws.endpoints import PlainEndpoint
from aiorest_ws.exceptions import EndpointValueError, NotSpecifiedURL
from aiorest_ws.routers import SimpleRouter
from aiorest_ws.views import MethodBasedView
from aiorest_ws.wrappers import Request


class RestWSRouterTestCase(unittest.TestCase):

    def setUp(self):
        super(RestWSRouterTestCase, self).setUp()
        self.router = SimpleRouter()

    def test_correct_path(self):
        broken_path = 'api'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

    def test_correct_path_2(self):
        broken_path = ' api  '
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

    def test_correct_path_3(self):
        broken_path = 'api'
        correct_path = 'api/'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, correct_path)

    def test_register(self):
        self.router.register('/api', FakeView, 'GET')
        self.assertEqual(FakeView, self.router._urls[0].handler)

    def test_register_with_list_methods(self):
        self.router.register('/api', FakeView, ['GET', 'POST', ])
        self.assertEqual(FakeView, self.router._urls[0].handler)

    def test_register_endpoint(self):
        @endpoint(path='/api', methods='GET')
        def fake_handler(request, *args, **kwargs):
            pass

        self.router.register_endpoint(fake_handler)
        assert issubclass(self.router._urls[0].handler, MethodBasedView)

    def test_extract_url(self):
        data = {}
        request = Request(**data)
        self.assertRaises(NotSpecifiedURL, self.router.extract_url, request)

    def test_extract_url_2(self):
        data = {'url': '/api'}
        request = Request(**data)
        self.assertEqual(self.router.extract_url(request), '/api/')

    def test_extract_url_3(self):
        data = {'url': '/api/'}
        request = Request(**data)
        self.assertEqual(self.router.extract_url(request), '/api/')

    def test_search_handler_with_plain_endpoint(self):
        self.router.register('/api/', FakeView, 'GET')

        data = {}
        request = Request(**data)
        url = '/api/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {})

    def test_search_handler_with_dynamic_endpoint(self):
        self.router.register('/api/{version}/', FakeView, 'GET')

        data = {}
        request = Request(**data)
        url = '/api/v1/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v1',))
        self.assertEqual(kwargs, {})

    def test_search_handler_with_dynamic_endpoint_2(self):
        self.router.register('/api/{version}/', FakeView, 'GET')

        data = {'args': {'format': 'json'}}
        request = Request(**data)
        url = '/api/v2/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v2',))
        self.assertEqual(kwargs, {'params': {'format': 'json'}})

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    def test_process_request(self, log_info):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET', 'url': '/api/get/'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('data', json_response.keys())
        self.assertEqual(json_response['data'], 'fake')
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    def test_process_request_with_defined_args(self, log_info):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {
            'method': 'GET', 'url': '/api/get/',
            'args': {'format': 'xml'}
        }
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('data', json_response.keys())
        self.assertEqual(json_response['data'], 'fake')
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    def test_process_request_with_defined_args_and_event_name(self, log_info):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {
            'method': 'GET', 'url': '/api/get/',
            'args': {'format': 'xml'}, 'event_name': 'test'
        }
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('data', json_response.keys())
        self.assertEqual(json_response['data'], 'fake')
        self.assertIn('event_name', json_response)
        self.assertEqual(
            json_response['event_name'], decoded_json['event_name']
        )

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    @unittest.mock.patch('aiorest_ws.log.logger.exception')
    def test_process_request_by_invalid_url(self, log_info, log_exc):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET', 'url': '/api/invalid/'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('detail', json_response.keys())
        self.assertEqual(
            json_response['detail'],
            "For URL, typed in request, handler not specified."
        )
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    @unittest.mock.patch('aiorest_ws.log.logger.exception')
    def test_process_request_without_url(self, log_info, log_exc):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('detail', json_response.keys())
        self.assertEqual(
            json_response['detail'],
            "In query not specified `url` argument."
        )
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    def test_process_request_with_middleware(self, log_info):
        self.router._middlewares = [FakeTokenMiddleware(), ]
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET', 'url': '/api/get/'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('data', json_response.keys())
        self.assertEqual(json_response['data'], 'fake')
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    @unittest.mock.patch('aiorest_ws.log.logger.exception')
    def test_process_request_with_failed_middleware(self, log_info, log_exc):
        self.router._middlewares = [FakeTokenMiddlewareWithExc(), ]
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET', 'url': '/api/get/'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('detail', json_response.keys())
        self.assertNotIn('data', json_response.keys())

    @unittest.mock.patch('aiorest_ws.log.logger.info')
    def test_process_request_wrapped_function(self, log_info):
        @endpoint('/api', 'GET')
        def fake_handler(request, *args, **kwargs):
            return "fake"

        self.router.register_endpoint(fake_handler)

        decoded_json = {'url': '/api', 'method': 'GET'}
        request = Request(**decoded_json)
        response = self.router.process_request(request).decode('utf-8')
        json_response = json.loads(response)
        self.assertIn('data', json_response.keys())
        self.assertEqual(json_response['data'], 'fake')
        self.assertIn('event_name', json_response)
        self.assertIsNone(json_response['event_name'])

    def test_register_url(self):
        endpoint = FakeEndpoint('/api/', None, 'GET', 'good')
        self.router._register_url(endpoint)
        self.assertRaises(EndpointValueError, self.router._register_url,
                          endpoint)

    def test_register_url_without_endpoint_name(self):
        endpoint = FakeEndpoint('/api/', None, 'GET', None)
        self.router._register_url(endpoint)

    def test_register_url_failed(self):
        endpoint = InvalidEndpoint
        self.assertRaises(TypeError, self.router._register_url, endpoint)

    def test_include(self):
        class AnotherRouter(SimpleRouter):
            pass

        another_router = AnotherRouter()
        another_router.register('/api', FakeView, 'GET', name='test_api')

        self.assertEqual(len(self.router._urls), 0)
        self.assertEqual(len(self.router._routes), 0)

        self.router.include(another_router)

        self.assertEqual(len(self.router._urls), 1)
        self.assertEqual(len(self.router._routes), 1)
        self.assertEqual(type(self.router._urls[0]), PlainEndpoint)
        self.assertEqual(type(self.router._routes['test_api']), PlainEndpoint)

    def test_include_fail(self):
        another_router = None
        self.assertRaises(TypeError, self.router.include, another_router)
