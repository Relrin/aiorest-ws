# -*- coding: utf-8 -*-
import json
import unittest

from fixtures.fakes import InvalidEndpoint, FakeView, FakeGetView, FakeEndpoint

from aiorest_ws.decorators import endpoint
from aiorest_ws.endpoints import PlainEndpoint
from aiorest_ws.exceptions import EndpointValueError, NotSpecifiedURL
from aiorest_ws.routers import RestWSRouter
from aiorest_ws.views import MethodBasedView
from aiorest_ws.wrappers import Request


class RestWSRouterTestCase(unittest.TestCase):

    def setUp(self):
        super(RestWSRouterTestCase, self).setUp()
        self.router = RestWSRouter()

    def test_correct_path(self):
        broken_path = 'api'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

        broken_path = ' api  '
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

        correct_path = 'api/'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, correct_path)

    def test_get_argument(self):
        request = Request({'args': {'param': 'test'}})
        self.assertEqual(self.router.get_argument(request, 'param'), 'test')

        request = Request({'args': {}})
        self.assertIsNone(self.router.get_argument(request, 'param'), None)

        request = Request({})
        self.assertIsNone(self.router.get_argument(request, 'param'))

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
        request = Request({})
        self.assertRaises(NotSpecifiedURL, self.router.extract_url, request)

        request = Request({'url': '/api'})
        self.assertEqual(self.router.extract_url(request), '/api/')

        request = Request({'url': '/api/'})
        self.assertEqual(self.router.extract_url(request), '/api/')

    def test_search_handler(self):
        self.router.register('/api/', FakeView, 'GET')
        self.router.register('/api/{version}/', FakeView, 'GET')

        request = Request({})
        url = '/api/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {})

        request = Request({})
        url = '/api/v1/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v1',))
        self.assertEqual(kwargs, {})

        request = Request({'args': {'format': 'json'}})
        url = '/api/v2/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v2',))
        self.assertEqual(kwargs, {'params': {'format': 'json'}})

    def test_dispatch(self):
        self.router.register('/api/get/', FakeGetView, 'GET')

        decoded_json = {'method': 'GET', 'url': '/api/get/'}
        request = Request(decoded_json)
        response = json.loads(self.router.dispatch(request).decode('utf-8'))
        self.assertIn('data', response.keys())
        self.assertEqual(response['data'], 'fake')
        self.assertEqual(
            response['request'],
            {'method': 'GET', 'url': '/api/get/'}
        )

        decoded_json = {'method': 'GET', 'url': '/api/get/',
                        'args': {'format': 'xml'}}
        request = Request(decoded_json)
        response = json.loads(self.router.dispatch(request).decode('utf-8'))
        self.assertIn('data', response.keys())
        self.assertEqual(response['data'], 'fake')
        self.assertEqual(
            response['request'],
            {'method': 'GET', 'url': '/api/get/'}
        )

        decoded_json = {'method': 'GET', 'url': '/api/invalid/'}
        request = Request(decoded_json)
        response = json.loads(self.router.dispatch(request).decode('utf-8'))
        self.assertIn('details', response.keys())
        self.assertEqual(
            response['details'],
            "For URL, typed in request, handler not specified."
        )
        self.assertNotIn('request', response.keys())

        decoded_json = {'method': 'GET'}
        request = Request(decoded_json)
        response = json.loads(self.router.dispatch(request).decode('utf-8'))
        self.assertIn('details', response.keys())
        self.assertEqual(
            response['details'],
            "In query not specified `url` argument."
        )
        self.assertNotIn('request', response.keys())

    def test_dispatch_wrapped_function(self):
        @endpoint('/api', 'GET')
        def fake_handler(request, *args, **kwargs):
            return "fake"

        self.router.register_endpoint(fake_handler)
        decoded_json = {'url': '/api', 'method': 'GET'}
        request = Request(decoded_json)
        response = json.loads(self.router.dispatch(request).decode('utf-8'))
        self.assertIn('data', response.keys())
        self.assertEqual(response['data'], 'fake')
        self.assertEqual(response['request'], decoded_json)

    def test_register_url(self):
        endpoint = InvalidEndpoint
        self.assertRaises(TypeError, self.router._register_url, endpoint)

        endpoint = FakeEndpoint('/api/', None, 'GET', 'good')
        self.router._register_url(endpoint)
        self.assertRaises(EndpointValueError, self.router._register_url,
                          endpoint)

        endpoint.name = None
        self.router._register_url(endpoint)

    def test_include(self):
        class AnotherRouter(RestWSRouter):
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
