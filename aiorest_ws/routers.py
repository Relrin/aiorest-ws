"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs

    For example, we can use this features something like this:

        router = RestWSRouter()
        router.add('user/info', info_handler, methods='GET')
        router.add('user/register', register_handler, methods='POST')
        router.add('user/{user_name}', user_handler, methods=['GET', 'PUT'])


    If necessary append this urls to Django instantly, we can use this:

        urlpatterns += router.get_urls()
"""
import abc
from aiohttp.web_urldispatcher import UrlDispatcher

from exceptions import NotSupportedArgumentType


__all__ = ('DjangoRouterMixin', 'RestWSRouter')


class DjangoRouterMixin(metaclass=abc.ABCMeta):

    """
        Mixin for compatibility with Django URLs
    """
    @abc.abstractmethod
    def get_urls(self):
        """
            Returns list of urlpatterns, which can be added to Django URLs
        """
        pass


class RestWSRouter(UrlDispatcher):

    """
        Default router class, used for working with REST over WebSockets
    """

    def add(self, path, handler, methods, base_name=None):
        """
            Add new endpoint to server router

            Args:
                path - URL, which used to get access to API
                handler - callable function, which used for processing request
                methods - list of supported
                base_name - the base to use for the URL names that are created
        """
        if isinstance(methods, list):
            for method in methods:
                self.add_route(method, path, handler, name=base_name)
        if isinstance(methods, str):
            self.add_route(methods, path, handler, name=base_name)
        else:
            raise NotSupportedArgumentType(
                "Argument `methods` doesn't support `{0}`"
                "type.".format(type(methods))
            )

    # add there support class-based handlers
    # def add_class_handler(self, path, handler, base_name=None):
    # ...
