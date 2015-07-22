# -*- coding: utf-8 -*-
"""
    Decorators and wrappers, used for routing issues.
"""
__all__ = ('endpoint', )

from .validators import MethodValidator
from .views import MethodBasedView


def endpoint(path, methods, name=None):
    """Decorator function, which turn handler into MethodBasedView class."""
    def endpoint_decorator(func):
        def wrapper(*args, **kwargs):
            class FunctionView(MethodBasedView):
                pass
            view = FunctionView

            supported_methods = methods
            method_validator = MethodValidator()
            method_validator.validate(supported_methods)

            if type(supported_methods) is str:
                supported_methods = [supported_methods, ]

            for method in supported_methods:
                setattr(view, method.lower(), func)
            return path, view, methods, name
        return wrapper
    return endpoint_decorator
