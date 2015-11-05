# -*- coding: utf-8 -*-
"""
    Functions and decorators used for modify classes on the fly.
"""
__all__ = ('add_property', )


def add_property(instance, field_name, value):
    """Append property to the current instance of class.

    :param instance: modified object.
    :param field_name: attribute name in class.
    :param value: value, which used for initialize the field_name.
    """
    cls = type(instance)
    protected_field_name = '_{0}'.format(field_name)
    property_func = lambda self: getattr(self, protected_field_name)
    setattr(instance, protected_field_name, value)
    setattr(cls, field_name, property(property_func))
