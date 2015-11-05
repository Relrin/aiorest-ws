# -*- coding: utf-8 -*-
"""
    XML classes and functions, used for serializing and de-serializing.
"""
from xml.sax.saxutils import XMLGenerator

__all__ = ('SimpleXMLGenerator', )


class SimpleXMLGenerator(XMLGenerator):
    """XML generator for input data."""
    root_name = 'root'
    item_tag_name = 'list-item'

    def __init__(self, stream, encoding='utf-8'):
        super(SimpleXMLGenerator, self).__init__(stream, encoding=encoding)

    def parse(self, data):
        """Convert data to XML.

        :param data: input data.
        """
        self.startDocument()
        self.startElement(self.root_name, {})
        self.to_xml(self, data)
        self.endElement(self.root_name)
        self.endDocument()

    def to_str(self, value):
        """Encode value for the string.

        :param value: value, which will have converted to the string.
        """
        return str(value).encode(self._encoding)

    def to_xml(self, xml, data):
        """Convert Python object to XML.

        :param xml: XML object.
        :param data: Python's object, which will have been converted.
        """
        if isinstance(data, (list, tuple)):
            for item in data:
                self.startElement(self.item_tag_name, {})
                self.to_xml(xml, item)
                self.endElement(self.item_tag_name)
        elif isinstance(data, dict):
            for key, value in data.items():
                xml.startElement(key, {})
                self.to_xml(xml, value)
                xml.endElement(key)
        elif data is None:
            pass
        else:
            xml.characters(self.to_str(data))
