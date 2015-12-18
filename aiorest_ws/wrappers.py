# -*- coding: utf-8 -*-
"""
    Wrappers, similar on HTTP requests/responses.
"""
from aiorest_ws.utils.modify import add_property

__all__ = ('Request', 'Response', )


class Request(object):

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__()
        self._method = kwargs.pop('method', None)
        self._url = kwargs.pop('url', None)
        self._args = kwargs.pop('args', {})
        self._event_name = kwargs.pop('event_name', None)

        for key in kwargs.keys():
            add_property(self, key, kwargs[key])

    @property
    def method(self):
        """Get method type, which defined by the user."""
        return self._method

    @property
    def url(self):
        """Get the APIs url, from which expected response."""
        return self._url

    @property
    def args(self):
        """Get dictionary of arguments, defined by the user."""
        return self._args

    @property
    def event_name(self):
        """Get event name, which used by the client for processing response."""
        return self._event_name

    def to_representation(self):
        """Serialize request object to dictionary object."""
        return {'event_name': self.event_name}

    def get_argument(self, name):
        """Extracting argument from the request.

        :param name: name of extracted argument in dictionary.
        """
        return self.args.get(name, None) if self.args else None


class Response(object):

    def __init__(self):
        super(Response, self).__init__()
        self._content = {}

    @property
    def content(self):
        """Get content of response."""
        return self._content

    @content.setter
    def content(self, value):
        """Set content for the response."""
        self._content['data'] = value

    def wrap_exception(self, exception):
        """Set content of response, when taken exception."""
        self._content = {'detail': exception.detail}

    def append_request(self, request):
        """Add to the response object serialized request."""
        self._content.update(request.to_representation())
