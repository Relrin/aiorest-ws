# -*- coding: utf-8 -*-
"""
    Permission classes for authentication.
"""
from aiorest_ws.abstract import AbstractPermission

__all__ = ('IsAuthenticated', )


class IsAuthenticated(AbstractPermission):
    """Permissions used for checking authenticated users."""
    @staticmethod
    def check(request, handler):
        """Check permission method.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        return request.user and request.user.is_authenticated()
