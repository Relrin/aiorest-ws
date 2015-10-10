# -*- coding: utf-8 -*-
"""
    Exceptions for user management.
"""
__all__ = (
    'RequiredModelFieldsNotDefined', 'SearchCriteriaRequired',
    'NotEnoughArguments'
)

from aiorest_ws.exceptions import BaseAPIException


class RequiredModelFieldsNotDefined(BaseAPIException):
    default_detail = u"Required fields aren't defined."


class SearchCriteriaRequired(BaseAPIException):
    default_detail = u"Criteria for WHEN statement not defined."


class NotEnoughArguments(BaseAPIException):
    default_detail = u"Necessary specify at least one field to update."
