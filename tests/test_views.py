# -*- coding: utf-8 -*-
import unittest

from fixtures.fakes import FakeGetView

from aiorest_ws.exceptions import NotSpecifiedHandler, \
    NotSpecifiedMethodName, IncorrectMethodNameType, InvalidRenderer
from aiorest_ws.renderers import JSONRenderer
from aiorest_ws.views import View
from aiorest_ws.wrappers import Request


class ViewTestCase(unittest.TestCase):

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.view = View()

    def test_as_view(self):
        self.assertEqual(self.view.as_view('api'), None)


class MethodBaseViewTestCase(unittest.TestCase):

    def setUp(self):
        super(MethodBaseViewTestCase, self).setUp()
        self.view = FakeGetView()

    def test_dispatch(self):
        data = {}
        request = Request(**data)
        self.assertRaises(NotSpecifiedMethodName, self.view.dispatch, request)

    def test_dispatch_2(self):
        data = {'method': 'GET'}
        request = Request(**data)
        self.assertEqual(self.view.dispatch(request), 'fake')

    def test_dispatch_failed(self):
        data = {'method': ['POST', ]}
        request = Request(**data)
        self.assertRaises(IncorrectMethodNameType, self.view.dispatch,
                          request)

    def test_dispatch_failed_2(self):
        data = {'method': 'POST'}
        request = Request(**data)
        self.view.methods = ['GET', ]
        self.assertRaises(NotSpecifiedHandler, self.view.dispatch, request)

    def test_get_serializer(self):
        format = None
        self.view.renderers = ()
        self.assertIsInstance(
            self.view.get_renderer(format), JSONRenderer
        )

    def test_get_serializer_2(self):
        format = 'json'
        self.view.renderers = (JSONRenderer,)
        self.assertIsInstance(
            self.view.get_renderer(format), JSONRenderer
        )

    def test_get_serializer_3(self):
        format = 'xml'
        self.view.renderers = (JSONRenderer,)
        self.assertIsInstance(
            self.view.get_renderer(format), JSONRenderer
        )

    def test_get_serializer_failed(self):
        format = None
        self.view.renderers = 'JSONSerializer'
        self.assertRaises(InvalidRenderer, self.view.get_renderer, format)
