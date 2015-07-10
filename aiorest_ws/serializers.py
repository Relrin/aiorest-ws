# -*- coding: utf-8 -*-
"""
    Serializers for generated responses by the server.
"""
__all__ = ('BaseSerializer', 'JSONSerializer', 'XMLSerializer', )

from exceptions import NotImplementedMethod


class BaseSerializer(object):

    media_type = None
    format = None
    charset = 'utf-8'

    def serialize(self, data):
        """Serialize input data into another format.

        :param data: dictionary object.
        """
        raise NotImplementedMethod(u"Error occurred in not implemented "
                                   u"method of serializer.")


class JSONSerializer(BaseSerializer):

    media_type = 'application/json'
    format = 'json'
    # don't set a charset because JSON is a binary encoding, that can be
    # encoded as utf-8, utf-16 or utf-32.
    # for more details see: http://www.ietf.org/rfc/rfc4627.txt
    # and Armin Ronacher's article http://goo.gl/MExCKv
    charset = None
    # TODO: override serialize() method


class XMLSerializer(BaseSerializer):

    media_type = 'application/xml'
    format = 'xml'
    # TODO: override serialize() method
