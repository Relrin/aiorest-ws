# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.parsers import URLParser
from aiorest_ws.urls.base import set_urlconf
from aiorest_ws.urls.utils import RouteMatch, resolve, reverse, NoMatch, \
    NoReverseMatch

from tests.fixtures.fakes import FakeView


class TestResolve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestResolve, cls).setUpClass()
        url_parser = URLParser()
        cls.data = {
            'urls': [
                url_parser.define_route(
                    '/user/list/', FakeView, ['GET', ], name='user-list'
                ),
                url_parser.define_route(
                    '/user/{pk}/', FakeView, ['GET', ]
                ),
                url_parser.define_route(
                    '/user/', FakeView, ['GET', ]
                )
            ]
        }
        set_urlconf(cls.data)

    def test_resolve_with_static_path(self):
        match = resolve('/user/')
        self.assertIsInstance(match, RouteMatch)
        self.assertIsNone(match.view_name)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})

    def test_resolve_with_static_path_and_specified_name(self):
        view_name = 'user-list'
        match = resolve('/user/list/')
        self.assertIsInstance(match, RouteMatch)
        self.assertEqual(match.view_name, view_name)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})

    def test_resolve_with_dynamic_path(self):
        match = resolve('/user/1/')
        self.assertIsInstance(match, RouteMatch)
        self.assertIsNone(match.view_name)
        self.assertEqual(match.args, ('1',))
        self.assertEqual(match.kwargs, {'pk': '1'})

    def test_resolve_raises_no_match_exception(self):
        with self.assertRaises(NoMatch):
            resolve('/user-list/')

    def test_resolve_raises_no_match_exception_for_empty_list(self):
        with self.assertRaises(NoMatch):
            resolve('/user/1/', {'urls': []})


class TestReverse(unittest.TestCase):

    def setUp(self):
        super(TestReverse, self).setUpClass()
        url_parser = URLParser()
        data = {
            'path': 'wss://127.0.0.1:8000/',
            'routes': {
                'user-detail': url_parser.define_route(
                    '/user/{pk}/', FakeView, ['GET', ], name='user-detail'
                )
            }
        }
        set_urlconf(data)

    def test_reverse_with_args(self):
        self.assertEqual(
            reverse('user-detail', args=('1',)), "wss://127.0.0.1:8000/user/1/"
        )

    def test_reverse_with_args_and_kwargs(self):
        self.assertEqual(
            reverse('user-detail', args=('1',), kwargs={"token": "123456"}),
            "wss://127.0.0.1:8000/user/1/?token=123456"
        )

    def test_reverse_raises_value_error_exception(self):
        with self.assertRaises(ValueError):
            reverse('user-detail')

    def test_reverse_raises_no_reverse_match_exceptions(self):
        set_urlconf({})
        with self.assertRaises(NoReverseMatch):
            reverse('user-detail', args=('1',))
