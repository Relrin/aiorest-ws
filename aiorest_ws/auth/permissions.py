# -*- coding: utf-8 -*-
"""
    Permission classes for authentication.
"""
__all__ = ('IsAuthenticated', )

from aiorest_ws.abstract import AbstractPermission


class IsAuthenticated(AbstractPermission):

    @staticmethod
    def check(request, handler):
        return request.user and request.user.is_authenticated()
