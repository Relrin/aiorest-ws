# -*- coding: utf-8 -*-
"""
    Permission classes for authentication.
"""
__all__ = ('IsAuthenticated', )

from aiorest_ws.abstract import AbstractPermission


class IsAuthenticated(AbstractPermission):
    """Permissions used for checking authenticated users."""
    @staticmethod
    def check(request, handler):
        """Check permission method.

        :param request: instance of Request class.
        :param handler: view, invoked later for the request.
        """
        return request.user and request.user.is_authenticated()
