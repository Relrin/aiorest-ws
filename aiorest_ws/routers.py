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

from .abstract import AbstractEndpoint, AbstractRouter
from .exceptions import BaseAPIException, EndpointValueError, \
    NotSpecifiedHandler, NotSpecifiedURL
from .serializers import JSONSerializer
from .parsers import URLParser
from .validators import RouteArgumentsValidator
from .wrappers import Response


class RestWSRouter(AbstractRouter):
    """Default router class, used for working with REST over WebSockets."""
    args_validator = RouteArgumentsValidator()
    url_parser = URLParser()

    def __init__(self):
        super(RestWSRouter, self).__init__()
        self._urls = []
        self._routes = {}

    def _correct_path(self, path):
        """Convert path to valid value.

        :param path: URL, which used to get access to API.
        """
        path = path.strip()
        if not path.endswith('/'):
            path = path + '/'
        return path

    def register(self, path, handler, methods, name=None):
        """Add new endpoint to server router.

        :param path: URL, which used to get access to API.
        :param handler: inherited class from the MethodBasedView, which used
                        for processing request.
        :param methods: list of available for user methods or string with
                        concrete method name.
        :param name: the base to use for the URL names that are created.
        """
        path = self._correct_path(path)
        self.args_validator.validate(path, handler, methods, name)

        route = self.url_parser.define_route(path, handler, methods, name)
        self._register_url(route)

    def register_endpoint(self, endpoint):
        """Add new endpoint to server router.

        :param endpoint: function with @endpoint decorator, which used for
                         processing request.
        """
        path, handler, methods, name = endpoint()
        self.register(path, handler, methods, name)

    def extract_url(self, request):
        """Extracting URL parameter for request.

        :param request: request from the user.
        """
        if not request.url:
            raise NotSpecifiedURL()
        return self._correct_path(request.url)

    def search_handler(self, request, url):
        """Searching handler by URL.

        :param request: request from user.
        :param url: path to the registered endpoint.
        """
        args = ()
        kwargs = {}
        handler = None
        for route in self._urls:
            match = route.match(url)
            if match is not None:
                handler = route.handler()
                args = match
                params = request.args
                if params:
                    kwargs.update({'params': params})
                break
        return handler, args, kwargs

    def process_request(self, request):
        """Handle received request from user.

        :param request: request from user.
        """
        response = Response()

        try:
            url = self.extract_url(request)
            handler, args, kwargs = self.search_handler(request, url)

            # invoke handler for request
            if handler:
                # search serializer for response
                format = self.get_argument(request, 'format')
                serializer = handler.get_serializer(format, *args, **kwargs)

                response.content = handler.dispatch(request, *args, **kwargs)
                response.append_request(request)
            else:
                raise NotSpecifiedHandler()
        except BaseAPIException as exc:
            response.content = {'details': exc.detail}
            serializer = JSONSerializer()

        return serializer.serialize(response.content)

    def get_argument(self, request, name):
        """Extracting argument from the request.

        :param request: request, passed from a dispatcher
        :param name: name of extracted argument in dictionary.
        """
        argument = None
        if request.args:
            argument = request.args.get(name, None)
        return argument

    def _register_url(self, route):
        """Register new endpoint.

        :param route: instance of class, inherited from AbstractEndpoint.
        """
        if not issubclass(type(route), (AbstractEndpoint, )):
            raise TypeError(u"Custom route must be inherited from the "
                            u"AbstractEndpoint class.")

        name = route.name
        if name is not None:
            if name in self._routes.keys():
                raise EndpointValueError(
                    'Duplicate {}, already handled by {}'
                    .format(name, self._routes[name]))
            else:
                self._routes[name] = route
        self._urls.append(route)

    def include(self, router):
        """Appending endpoints from another router to self.

        :param router: instance of subclass, derived from AbstractRouter
        """
        if not issubclass(type(router), (RestWSRouter, )):
            raise TypeError(u"Passed router must be inherited from the "
                            u"RestWSRouter class.")
        self._urls.extend(router._urls)
        self._routes.update(router._routes)
