# -*- coding: utf-8 -*-
"""
Base exception classes for serialize and validation actions.
"""
from aiorest_ws.exceptions import BaseAPIException, SerializerError
from aiorest_ws.utils.encoding import force_text_recursive

__all__ = ('ModelSerializerError', 'ValidationError', )


class ModelSerializerError(SerializerError):
    default_detail = u"Error has occurred inside model serializer class."


class ValidationError(BaseAPIException):
    default_detail = u"Validation error has occurred at validation process."

    def __init__(self, detail):
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail, ]
        self.detail = force_text_recursive(detail)

    def __str__(self):
        return str(self.detail)
