# -*- coding: utf-8 -*-
"""
Utility module for work with _urlconf variable.
"""
import re

from aiorest_ws.parsers import DYNAMIC_PARAMETER
from aiorest_ws.urls.base import get_urlconf
from aiorest_ws.urls.exceptions import NoReverseMatch, NoMatch
from aiorest_ws.utils.encoding import force_text

__all__ = (
    'RouteMatch', '_generate_url_parameters', 'reverse', 'resolve'
)


class RouteMatch(object):

    def __init__(self, view_name, args=(), kwargs={}):
        super(RouteMatch, self).__init__()
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs


def _generate_url_parameters(parameters):
    format_parameters = (
        "{}={}".format(key, value)
        for key, value in parameters.items()
    )
    return '?' + '&'.join(format_parameters)


def resolve(path, urlconf=None):
    """
    Return the endpoint corresponding to a matched URL.
    """
    if urlconf is None:
        urlconf = get_urlconf()

    # Convert absolute path to relative
    path = path.replace(urlconf['path'], '')

    # Iterate over the all endpoints
    for route in urlconf.get('urls', []):
        # Find match between endpoint and passed URL
        match = route.match(path)
        if match is not None:
            kwargs = {}
            if route._pattern:
                kwargs = route._pattern.match(path).groupdict()
            return RouteMatch(route.name, args=match, kwargs=kwargs)
    raise NoMatch()


def reverse(view_name, urlconf=None, args=[], kwargs={}, relative=False):
    """
    Generate URL to endpoint, which processing by Application instance, based
    on the `view_name` and passed arguments.

    :param view_name: view name.
    :param urlconf: urlconf instance (dictionary).
    :param args: tuple of data, which used by handler with this URL.
    :param kwargs: named arguments for the defined URL.
    :return: generated URL with the passed arguments.
    """
    if urlconf is None:
        urlconf = get_urlconf()

    root_path = ''
    api_path = ''
    try:
        # Get root path, when necessary to generate absolute URL
        root_path = '' if relative else urlconf['path'].strip('/')

        # Get path to a specific endpoint
        route = urlconf['routes'][view_name]
        api_path = route.path.strip('/')

        # Replace parameters in 'api_url' on the passed args
        dynamic_parameters = re.findall(DYNAMIC_PARAMETER, api_path)
        if len(dynamic_parameters) != len(args):
            raise ValueError(
                "Endpoint '{path}' must take {valid_count} parameters, "
                "but passed {invalid_count}.".format(
                    path=api_path,
                    valid_count=len(dynamic_parameters),
                    invalid_count=len(args)
                )
            )
        for parameter, value in zip(dynamic_parameters, args):
            api_path = api_path.replace(parameter, value)
    except KeyError:
        raise NoReverseMatch()

    url_parameters = _generate_url_parameters(kwargs) if kwargs else ""
    url = '/'.join([root_path, api_path, url_parameters])
    return force_text(url)
