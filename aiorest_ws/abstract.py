from abc import ABCMeta, abstractmethod


class AbstractEndpoint(metaclass=ABCMeta):

    path = None     # URL, used for get access to API
    handler = None  # class/function for processing request
    methods = []    # list of supported methods (GET, POST, etc.)
    name = None     # short name for route

    def __init__(self, path, handler, methods, name):
        self.path = path
        self.handler = handler
        if type(methods) is str:
            self.methods.append(methods)
        else:
            self.methods.extend(methods)
        self.name = name

    @abstractmethod
    def match(self, path):
        """Checking path on compatible.

        :param path: URL, which used for get access to API.
        """
        pass


class AbstractRouter(metaclass=ABCMeta):

    @abstractmethod
    def dispatch(self, request):
        """Handling received request from user.

        :param request: request from user.
        """
        pass
