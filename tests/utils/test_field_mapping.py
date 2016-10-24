# -*- coding: utf-8 -*-
import pytest
import unittest

from aiorest_ws.utils.field_mapping import ClassLookupDict, needs_label


class TestClassLookupDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.instance = ClassLookupDict({str: str})

    def test_get_item(self):
        self.assertEqual(self.instance["string"], str)

    def test_get_item_for_class_with_proxy(self):
        class ClassWithProxy(object):
            _proxy_class = str

        self.assertEqual(self.instance[ClassWithProxy], str)

    def test_get_item_has_failed(self):
        self.assertRaises(KeyError, self.instance.__getitem__, dict)

    def test_set_item(self):
        self.instance[float] = float
        self.assertEqual(self.instance.mapping[float], float)


@pytest.mark.parametrize("model_field_verbose_name, field_name, expected", [
    ('test_label', 'test label', True),
    ('test_label', 'custom_label', True),
    ('no need label', 'no_need_label', False),
])
def test_needs_label(model_field_verbose_name, field_name, expected):
    assert needs_label(model_field_verbose_name, field_name) == expected
