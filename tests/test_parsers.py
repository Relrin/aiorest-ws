# -*- coding: utf-8 -*-
import unittest

from fixtures.fakes import FakeGetView

from aiorest_ws.endpoints import PlainEndpoint, DynamicEndpoint
from aiorest_ws.exceptions import EndpointValueError
from aiorest_ws.parsers import URLParser


class URLParserTestCase(unittest.TestCase):

    def setUp(self):
        super(URLParserTestCase, self).setUp()
        self.parser = URLParser()

    def test_parse_static_url(self):
        route = self.parser.define_route('/api', FakeGetView, 'GET')
        self.assertIsInstance(route, PlainEndpoint)

    def test_parse_dynamic_url(self):
        route = self.parser.define_route('/api/{users}', FakeGetView, 'GET')
        self.assertIsInstance(route, DynamicEndpoint)

    def test_parse_invalid_url_1(self):
        self.assertRaises(
            EndpointValueError,
            self.parser.define_route, '/api/{users', FakeGetView, 'GET'
        )

    def test_parse_invalid_url_2(self):
        self.assertRaises(
            EndpointValueError,
            self.parser.define_route,
            '/api/{users{}}', FakeGetView, 'GET'
        )

    def test_parse_invalid_url_3(self):
        self.assertRaises(
            EndpointValueError,
            self.parser.define_route,
            '/api/{users{}', FakeGetView, 'GET'
        )

    def test_parse_invalid_url_4(self):
        self.assertRaises(
            EndpointValueError,
            self.parser.define_route,
            '/api/{users"}', FakeGetView, 'GET'
        )

    def test_parse_invalid_url_5(self):
        self.assertRaises(
            EndpointValueError,
            self.parser.define_route,
            r"/api/{users+++}", FakeGetView, 'GET'
        )
