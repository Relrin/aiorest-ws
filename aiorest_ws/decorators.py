# -*- coding: utf-8 -*-
"""
    Decorators and wrappers, used for routing issues.
"""
from aiorest_ws.validators import MethodValidator
from aiorest_ws.views import MethodBasedView

__all__ = ('endpoint', )


def endpoint(path, methods, name=None, **attrs):
    """Decorator function, which turn handler into MethodBasedView class.

    :param path: URL, used for get access to APIs.
    :param methods: acceptable method name or list of methods.
    :param name: short name of endpoint.
    :param attrs: any other attributes, which must be initialized.
    """
    def endpoint_decorator(func):
        def wrapper():
            class FunctionView(MethodBasedView):
                def handler(self, request, *args, **kwargs):
                    return func(request, *args, **kwargs)

            view = FunctionView

            supported_methods = methods
            method_validator = MethodValidator()
            method_validator.validate(supported_methods)

            if type(supported_methods) is str:
                supported_methods = [supported_methods, ]

            for method in supported_methods:
                setattr(view, method.lower(), view.handler)

            for attr in attrs:
                setattr(view, str(attr).lower(), attrs[attr])

            return path, view, methods, name
        return wrapper
    return endpoint_decorator
