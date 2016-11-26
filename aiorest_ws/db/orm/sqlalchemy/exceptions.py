# -*- coding: utf-8 -*-
"""
Exception classes for work with model serializers, fields and SQLAlchemy ORM.
"""
from aiorest_ws.exceptions import BaseAPIException


__all__ = ('ObjectDoesNotExist', )


class ObjectDoesNotExist(BaseAPIException):
    default_detail = "The requested object does not exist."
