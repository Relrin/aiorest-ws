# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict

from aiorest_ws.utils.fields import is_simple_callable, method_overridden, \
    get_attribute, set_value, to_choices_dict, flatten_choices_dict


class FakeClass(object):
    attr = 'value'

    def get_object(self):
        return self

    @staticmethod
    def get_true():
        return True

    def base_method(self):
        raise NotImplementedError()

    def attribute_error(self):
        raise AttributeError()

    def key_error(self):
        raise KeyError()


class DerivedFakeClass(FakeClass):

    def base_method(self):
        return self.attr


@pytest.mark.parametrize("value, expected", [
    (FakeClass(), False),
    (FakeClass().get_object, True),
    (FakeClass.get_true, True),
])
def test_is_simple_callable(value, expected):
    assert is_simple_callable(value) == expected


@pytest.mark.parametrize("method_name, cls, instance, expected", [
    ('base_method', FakeClass, FakeClass(), False),
    ('base_method', FakeClass, DerivedFakeClass(), True),
])
def test_method_overridden(method_name, cls, instance, expected):
    assert method_overridden(method_name, cls, instance) == expected


@pytest.mark.parametrize("instance, attrs, expected", [
    (None, ['key', ], None),
    ('test', [], 'test'),
    ({'key': 'value'}, ['key', ], 'value'),
    ({'key': {'key2': 'value'}}, ['key', 'key2'], 'value'),
    (FakeClass, ['attr', ], 'value'),
    (FakeClass, ['get_true', ], True),
])
def test_get_attribute(instance, attrs, expected):
    assert get_attribute(instance, attrs) == expected


@pytest.mark.parametrize("instance, attrs, exc_cls", [
    (FakeClass(), ['attribute_error', ], ValueError),
    (FakeClass(), ['key_error', ], ValueError),
])
def test_get_attribute_failed(instance, attrs, exc_cls):
    with pytest.raises(exc_cls):
        get_attribute(instance, attrs)


@pytest.mark.parametrize("dictionary, keys, value, expected", [
    ({'a': 1}, [], {'b': 2}, {'a': 1, 'b': 2}),
    ({'a': 1}, ['x'], 2, {'a': 1, 'x': 2}),
    ({'a': 1}, ['x', 'y'], 2, {'a': 1, 'x': {'y': 2}})
])
def test_set_value(dictionary, keys, value, expected):
    set_value(dictionary, keys, value)
    assert dictionary == expected


@pytest.mark.parametrize("value, expected", [
    ([1, 2, 3], {1: 1, 2: 2, 3: 3}),
    ([(1, '1st'), (2, '2nd')], {1: '1st', 2: '2nd'}),
    ([('Group', ((1, '1'), 2))],
     OrderedDict([('Group', OrderedDict([(1, '1'), (2, 2)]))])
     ),
])
def test_to_choices_dict(value, expected):
    assert to_choices_dict(value) == expected


@pytest.mark.parametrize("value, expected", [
    ({1: '1st', 2: '2nd'}, {1: '1st', 2: '2nd'}),
    ({'Key': {1: '1st', 2: '2nd'}}, {1: '1st', 2: '2nd'}),
])
def test_flatten_choices_dict(value, expected):
    assert flatten_choices_dict(value) == expected
