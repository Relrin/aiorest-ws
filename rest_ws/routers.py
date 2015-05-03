"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs

    For example, we can use this features something like this:

        router = WSDefaultRouter()
        router.add('user/info', info_handler, methods='GET',)
        router.add('user/register', register_handler, methods='POST')
        router.add('user/{user_name}', user_handler, methods=['GET', 'PUT'])


    If necessary append this urls to Django instantly, we can use this:

        urlpatters += router.get_urls()
"""

from aiohttp.web_urldispatcher import UrlDispatcher

# TODO: make compability with Django routing (without using framework)


class DjangoRouterMixin(object):

    def get_urls():
        # add there some logic ...
        pass


class WSDefaultRouter(UrlDispatcher):

    def add(self, path, handler, methods, base_name=None):
        # check there, that function have WebSocketResponse() object

        if isinstance(methods, str):
            methods_list = []
            methods_list.append(methods)
            methods = methods_list

        for method in methods:
            self.add_route(method, path, handler, name=base_name)

    # add there support class-based handlers
    # def add_class_handler(self, path, handler, base_name=None):
    # ...
