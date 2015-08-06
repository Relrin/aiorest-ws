# -*- coding: utf-8 -*-
import unittest

from fixtures.fakes import FakeGetView

from aiorest_ws.exceptions import NotSpecifiedHandler, NotSpecifiedMethodName, \
    IncorrectMethodNameType, InvalidSerializer
from aiorest_ws.serializers import JSONSerializer
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
        request = Request({})
        self.assertRaises(NotSpecifiedMethodName, self.view.dispatch, request)

        request = Request({'method': ['POST', ]})
        self.assertRaises(IncorrectMethodNameType, self.view.dispatch,
                          request)

        request = Request({'method': 'POST'})
        self.view.methods = ['GET', ]
        self.assertRaises(NotSpecifiedHandler, self.view.dispatch, request)

        request = Request({'method': 'GET'})
        self.assertEqual(self.view.dispatch(request), 'fake')

    def test_get_serializer(self):
        format = None
        self.view.serializers = ()
        self.assertIsInstance(self.view.get_serializer(format),
                              JSONSerializer)

        self.view.serializers = 'JSONSerializer'
        self.assertRaises(InvalidSerializer, self.view.get_serializer, format)

        format = 'json'
        self.view.serializers = (JSONSerializer, )
        self.assertIsInstance(self.view.get_serializer(format),
                              JSONSerializer)

        format = 'xml'
        self.assertIsInstance(self.view.get_serializer(format),
                              JSONSerializer)
