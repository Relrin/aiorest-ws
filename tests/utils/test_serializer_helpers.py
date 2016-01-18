# -*- coding: utf-8 -*-
import inspect
import unittest

from aiorest_ws.utils.serializer_helpers import ReturnList, ReturnDict, \
    BoundField, NestedBoundField, BindingDict


class FakeField(object):
    field_name = "pk"

    def __init__(self, field, value, errors, prefix=""):
        self.field = field
        self.value = value
        self.errors = errors
        self.prefix = prefix

    def bind(self, field_name, parent):
        self.field_name = field_name
        self.parent = parent


class FakeSerializer(object):
    field_name = "fake serializer"
    fields = {"pk": FakeField(int, 'value', {"key": "error"}, prefix='none')}


class FakeNestedSerializer(object):
    field_name = "fake nested serializer"
    fields = {"item": FakeSerializer()}


class TestReturnDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestReturnDict, cls).setUpClass()
        cls.instance = ReturnDict({"test": "value"}, serializer=object())

    def test_copy(self):
        self.assertEqual(self.instance, self.instance.copy())

    def test_repr(self):
        self.assertEqual(
            self.instance.__repr__(), {"test": "value"}.__repr__()
        )

    def test_reduce(self):
        self.assertEqual(
            self.instance.__reduce__(), (dict, ({'test': 'value'},))
        )


class TestReturnList(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestReturnList, cls).setUpClass()
        cls.instance = ReturnList(["test", "value"], serializer=object())

    def test_repr(self):
        self.assertEqual(
            self.instance.__repr__(), ["test", "value"].__repr__()
        )

    def test_reduce(self):
        self.assertEqual(
            self.instance.__reduce__(), (list, (["test", "value"],))
        )


class TestBoundField(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBoundField, cls).setUpClass()
        cls.instance = BoundField(
            FakeField, 'value', 'some error', prefix='none'
        )

    def test_proxy_class(self):
        self.assertEqual(self.instance._proxy_class, list.__class__)

    def test_repr(self):
        self.assertEqual(
            self.instance.__repr__(),
            u"<%s value=%s errors=%s>" % (
                self.instance.__class__.__name__, self.instance.value,
                self.instance.errors
            )
        )

    def test_as_form_field(self):
        bound_field = self.instance.as_form_field()
        self.assertEqual(bound_field._field, self.instance._field)
        self.assertEqual(bound_field.value, self.instance.value)
        self.assertEqual(bound_field.errors, self.instance.errors)
        self.assertEqual(bound_field._prefix, self.instance._prefix)

    def test_as_form_field_with_none_value(self):
        instance = BoundField(
            self.instance._field, None, {"key": "error"}, prefix='none'
        )

        bound_field = instance.as_form_field()
        self.assertEqual(bound_field._field, instance._field)
        self.assertEqual(bound_field.value, '')
        self.assertEqual(bound_field.errors, instance.errors)
        self.assertEqual(bound_field._prefix, instance._prefix)

    def test_as_form_field_with_false_value(self):
        instance = BoundField(
            self.instance._field, False, {"key": "error"}, prefix='none'
        )

        bound_field = instance.as_form_field()
        self.assertEqual(bound_field._field, instance._field)
        self.assertEqual(bound_field.value, '')
        self.assertEqual(bound_field.errors, instance.errors)
        self.assertEqual(bound_field._prefix, instance._prefix)


class TestNestedBoundField(unittest.TestCase):

    def test_init(self):
        instance = NestedBoundField(
            FakeField, "value", {"key": "error"}, prefix='none'
        )
        self.assertEqual(instance._field, instance._field)
        self.assertEqual(instance.value, "value")
        self.assertEqual(instance.errors, instance.errors)
        self.assertEqual(instance._prefix, instance._prefix)

    def test_init_with_none(self):
        instance = NestedBoundField(
            FakeField, None, 'some error', prefix='none'
        )
        self.assertEqual(instance._field, instance._field)
        self.assertEqual(instance.value, {})
        self.assertEqual(instance.errors, instance.errors)
        self.assertEqual(instance._prefix, instance._prefix)

    def test_init_with_empty_string(self):
        instance = NestedBoundField(
            FakeField, {"key": "value"}, {}, prefix='none'
        )
        self.assertEqual(instance._field, instance._field)
        self.assertEqual(instance.value, instance.value)
        self.assertEqual(instance.errors, instance.errors)
        self.assertEqual(instance._prefix, instance._prefix)

    def test_iter(self):
        instance = NestedBoundField(
            FakeSerializer, {}, {"pk": "error"}, prefix='none'
        )
        checked_data = set([field.field_name for field in instance])
        self.assertEqual(checked_data, {FakeField.field_name})

    def test_getitem_returns_nested_bound_field(self):
        instance = NestedBoundField(
            FakeNestedSerializer, '', {}, prefix='none'
        )
        nested_field = instance['item']
        self.assertIsInstance(nested_field, NestedBoundField)

    def test_getitem_returns_bound_field(self):
        instance = NestedBoundField(FakeSerializer, {}, {}, prefix='none')
        nested_field = instance['pk']
        self.assertIsInstance(nested_field, BoundField)

    def test_as_form_field(self):
        instance = NestedBoundField(
            FakeSerializer, {}, {}, prefix='none'
        )
        nested_bound_field = instance.as_form_field()
        self.assertEqual(nested_bound_field._field, instance._field)
        self.assertEqual(nested_bound_field.value, {})
        self.assertEqual(nested_bound_field.errors, instance.errors)
        self.assertEqual(nested_bound_field._prefix, instance._prefix)

    def test_as_form_field_with_list_value(self):
        instance = NestedBoundField(
            FakeSerializer, {"list": []}, {}, prefix='none'
        )

        nested_bound_field = instance.as_form_field()
        self.assertEqual(nested_bound_field._field, instance._field)
        self.assertEqual(nested_bound_field.value, instance.value)
        self.assertEqual(nested_bound_field.errors, instance.errors)
        self.assertEqual(nested_bound_field._prefix, instance._prefix)

    def test_as_form_field_with_list_dict(self):
        instance = NestedBoundField(
            FakeSerializer, {"dict": {}}, {}, prefix='none'
        )

        nested_bound_field = instance.as_form_field()
        self.assertEqual(nested_bound_field._field, instance._field)
        self.assertEqual(nested_bound_field.value, instance.value)
        self.assertEqual(nested_bound_field.errors, instance.errors)
        self.assertEqual(nested_bound_field._prefix, instance._prefix)

    def test_as_form_field_with_none_field_value(self):
        instance = NestedBoundField(
            FakeSerializer, {"item": None}, {}, prefix='none'
        )

        nested_bound_field = instance.as_form_field()
        self.assertEqual(nested_bound_field._field, instance._field)
        self.assertEqual(nested_bound_field.value, {"item": ''})
        self.assertEqual(nested_bound_field.errors, instance.errors)
        self.assertEqual(nested_bound_field._prefix, instance._prefix)

    def test_as_form_field_with_false_field_value(self):
        instance = NestedBoundField(
            FakeSerializer, {"item": False}, {}, prefix='none'
        )

        nested_bound_field = instance.as_form_field()
        self.assertEqual(nested_bound_field._field, instance._field)
        self.assertEqual(nested_bound_field.value, {"item": ''})
        self.assertEqual(nested_bound_field.errors, instance.errors)
        self.assertEqual(nested_bound_field._prefix, instance._prefix)


class TestBindingDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBindingDict, cls).setUpClass()
        cls.instance = BindingDict(serializer=object())

    def test_set_item(self):
        self.instance['pk'] = FakeField(int, {}, {}, prefix='none')
        self.assertIn('pk', self.instance.fields)

    def test_get_item(self):
        field = FakeField(int, {}, {}, prefix='none')
        self.instance['pk'] = field
        self.assertIn('pk', self.instance.fields)
        self.assertEqual(self.instance['pk'], field)

    def test_delete_item(self):
        self.instance['pk'] = FakeField(int, {}, {}, prefix='none')
        del self.instance['pk']
        self.assertNotIn('pk', self.instance.fields)

    def test_iter(self):
        self.instance['pk'] = FakeField(int, {}, {}, prefix='none')
        self.assertTrue(inspect.isgenerator(iter(self.instance)))

    def test_len(self):
        self.instance['pk'] = FakeField(int, {}, {}, prefix='none')
        self.assertEqual(len(self.instance), len(self.instance.fields))

    def test_repr(self):
        self.instance['pk'] = FakeField(int, {}, {}, prefix='none')
        self.assertEqual(
            self.instance.__repr__(), dict.__repr__(self.instance.fields)
        )
