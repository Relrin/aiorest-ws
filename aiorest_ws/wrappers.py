# -*- coding: utf-8 -*-
"""
    Wrappers, similar on HTTP requests/responses.
"""
__all__ = ('Request', 'Response', )

from aiorest_ws.utils.modify import add_property


class Request(object):

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__()
        self._method = kwargs.pop('method', None)
        self._url = kwargs.pop('url', None)
        self._args = kwargs.pop('args', {})

        for key in kwargs.keys():
            add_property(self, key, kwargs[key])

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def args(self):
        return self._args

    def to_representation(self):
        return {'method': self.method, 'url': self.url}

    def get_argument(self, name):
        """Extracting argument from the request.

        :param name: name of extracted argument in dictionary.
        """
        argument = None
        if self.args:
            argument = self.args.get(name, None)
        return argument


class Response(object):

    def __init__(self):
        super(Response, self).__init__()
        self._content = {}

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content['data'] = value

    def wrap_exception(self, exception):
        self._content = {'detail': exception.detail}

    def append_request(self, request):
        self._content.update({'request': request.to_representation()})
