# -*- coding: utf-8 -*-
"""
Serializers for generated responses by the server.
"""
import json

from io import StringIO
from aiorest_ws.conf import settings
from aiorest_ws.exceptions import SerializerError
from aiorest_ws.utils.formatting import SHORT_SEPARATORS, LONG_SEPARATORS, \
    WRONG_UNICODE_SYMBOLS
from aiorest_ws.utils.xmlutils import SimpleXMLGenerator

__all__ = ('BaseRenderer', 'JSONRenderer', 'XMLRenderer', )


class BaseRenderer(object):

    format = None
    charset = 'utf-8'

    def render(self, data):
        """
        Render input data into another format.

        :param data: dictionary object.
        """
        pass


class JSONRenderer(BaseRenderer):

    format = 'json'
    # Don't set a charset because JSON is a binary encoding, that can be
    # encoded as utf-8, utf-16 or utf-32.
    # For more details see: http://www.ietf.org/rfc/rfc4627.txt
    # and Armin Ronacher's article http://goo.gl/MExCKv
    charset = None
    ensure_ascii = not settings.UNICODE_JSON
    compact = settings.COMPACT_JSON

    def render(self, data):
        """
        Render input data into JSON.

        :param data: dictionary or list object (response).
        """
        separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS

        try:
            render = json.dumps(
                data, ensure_ascii=self.ensure_ascii, separators=separators
            )

            # Unicode symbols \u2028 and \u2029 are invisible in JSON and
            # make output are invalid. To avoid this situations, necessary
            # replace this symbols.
            # For more information read this article: http://goo.gl/ImC89E
            for wrong_symbol, expected in WRONG_UNICODE_SYMBOLS:
                render = render.replace(wrong_symbol, expected)

            render = bytes(render.encode('utf-8'))
        except Exception as exc:
            raise SerializerError(exc)
        return render


class XMLRenderer(BaseRenderer):

    format = 'xml'
    xml_generator = SimpleXMLGenerator

    def render(self, data):
        """
        Render input data into XML.

        :param data: dictionary or list object (response).
        """
        try:
            render = StringIO()
            xml = self.xml_generator(render, self.charset)
            xml.parse(data)
            render = bytes(render.getvalue().encode('utf-8'))
        except Exception as exc:
            raise SerializerError(exc)
        return render
