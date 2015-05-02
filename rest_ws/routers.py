"""
    This modules provide a functions and classes, which every developer
    can used for determine URL for their APIs

    For example, we can use this features something like this:

        router = WSDefaultRouter()
        router.add('user/info', methods='GET')
        router.add('user/register', methods='POST')
        router.add('user/{user_name}', methods=['GET', 'PUT'])


    If necessary append this urls to Django instantly, we can use this:

        urlpatters += router.get_urls()
"""

from aiohttp.web_urldispatcher import UrlDispatcher

# TODO: make class-based handlers

class WSDefaultRouter(UrlDispatcher):

    def add(self, path, handler, methods, base_name=None):
        if isinstance(methods, str):
            methods_list = []
            methods_list.append(methods)
            methods = methods_list

        for method in methods:
            self.add_route(method, path, handler, name=base_name)
