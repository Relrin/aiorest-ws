# -*- coding: utf -*-
import re
import unittest

from aiorest_ws.endpoints import PlainEndpoint, DynamicEndpoint
from aiorest_ws.views import MethodBasedView


class PlainEndpointTestCase(unittest.TestCase):

    def test_match(self):
        endpoint = PlainEndpoint('/api/', MethodBasedView, 'GET', None)

        matched_path = '/api/'
        self.assertEqual(endpoint.match(matched_path), ())

        unmatched_path = '/api/another'
        self.assertEqual(endpoint.match(unmatched_path), None)


class DynamicEndpointTestCase(unittest.TestCase):

    def test_match(self):
        endpoint = DynamicEndpoint(
            '/api/{another}/', MethodBasedView, 'GET', None,
            re.compile("^{}$".format(r'/api/(?P<var>[^{}/]+)/'))
        )

        unmatched_path = '/api/another/'
        self.assertEqual(endpoint.match(unmatched_path), ('another', ))

        unmatched_path = '/api/another/value'
        self.assertEqual(endpoint.match(unmatched_path), None)
