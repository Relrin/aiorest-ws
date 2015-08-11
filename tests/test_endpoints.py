# -*- coding: utf -*-
import re
import unittest

from aiorest_ws.endpoints import PlainEndpoint, DynamicEndpoint
from aiorest_ws.views import MethodBasedView


class PlainEndpointTestCase(unittest.TestCase):

    def setUp(self):
        super(PlainEndpointTestCase, self).setUp()
        self.endpoint = PlainEndpoint('/api/', MethodBasedView, 'GET', None)

    def test_matched_path(self):
        matched_path = '/api/'
        self.assertEqual(self.endpoint.match(matched_path), ())

    def test_unmatched_path(self):
        unmatched_path = '/api/another'
        self.assertEqual(self.endpoint.match(unmatched_path), None)


class DynamicEndpointTestCase(unittest.TestCase):

    def setUp(self):
        super(DynamicEndpointTestCase, self).setUp()
        self.endpoint = DynamicEndpoint(
            '/api/{another}/', MethodBasedView, 'GET', None,
            re.compile("^{}$".format(r'/api/(?P<var>[^{}/]+)/'))
        )

    def test_matched_path(self):
        unmatched_path = '/api/another/'
        self.assertEqual(self.endpoint.match(unmatched_path), ('another', ))

    def test_unmatched_path(self):
        unmatched_path = '/api/another/value'
        self.assertEqual(self.endpoint.match(unmatched_path), None)
