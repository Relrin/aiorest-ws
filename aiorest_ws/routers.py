# -*- coding: utf-8 -*-
"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs.

    For example, we can use this features something like this:

        router = RestWSRouter()
        router.add('user/info', info_handler, methods='GET')
        router.add('user/register', register_handler, methods='POST')
        router.add('user/{user_name}', user_handler, methods=['GET', 'PUT'])
"""
__all__ = ('RestWSRouter', )


class RestWSRouter(object):
    """
        Default router class, used for working with REST over WebSockets
    """
    def add(self, path, handler, methods, base_name=None):
        """
            Add new endpoint to server router

            Args:
                path - URL, which used to get access to API
                handler - callable function, which used for processing request
                methods - list of supported HTTP methods
                base_name - the base to use for the URL names that are created
        """
        pass

    def dispatch(self):
        pass
