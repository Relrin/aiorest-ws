# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.decorators import endpoint
from aiorest_ws.exceptions import NotSupportedArgumentType
from aiorest_ws.serializers import JSONSerializer


class EndpointTestCase(unittest.TestCase):

    def test_create_handler_with_str_method_name(self):
        @endpoint('/api', 'GET')
        def fake_handler(request, *args, **kwargs):
            pass

        path, handler, methods, name = fake_handler()
        self.assertEqual(methods, 'GET')

    def test_create_handler_with_list_method_name(self):
        @endpoint('/api', ['GET', 'post'])
        def fake_handler(request, *args, **kwargs):
            pass

        path, handler, methods, name = fake_handler()
        self.assertEqual(methods, ['GET', 'post'])

    def test_set_attr_for_endpoint(self):
        @endpoint('/api', ['GET', 'post'], serializers=(JSONSerializer, ))
        def fake_handler(request, *args, **kwargs):
            pass

        path, handler, methods, name = fake_handler()
        self.assertEqual(handler.serializers, (JSONSerializer, ))

    def test_create_handler_with_invalid_method_type(self):
        @endpoint('/api', None)
        def fake_handler(request, *args, **kwargs):
            pass

        self.assertRaises(NotSupportedArgumentType, fake_handler)
