# -*- coding: utf-8 -*-
import unittest

from io import StringIO
from aiorest_ws.utils.xmlutils import SimpleXMLGenerator


class SimpleXMLGeneratorTestCase(unittest.TestCase):

    def setUp(self):
        super(SimpleXMLGeneratorTestCase, self).setUp()
        self.render = StringIO()

    def test_parse(self):
        sxml = SimpleXMLGenerator(self.render)
        data = [{'count': 1}, [1, 2, 3], None, 'test_string']
        sxml.parse(data)
        result = self.render.getvalue()
        self.assertIn('<list-item><count>1</count></list-item>', result)
        self.assertIn('<list-item><list-item>1</list-item><list-item>'
                      '2</list-item><list-item>3</list-item></list-item>',
                      result)
        self.assertIn('<list-item></list-item>', result)
        self.assertIn('<list-item>test_string</list-item>', result)

    def test_to_str(self):
        sxml = SimpleXMLGenerator(self.render)
        self.assertEqual(sxml.to_str({'count': 1}), b"{'count': 1}")
        self.assertEqual(sxml.to_str(['1, 2, 3']), b"['1, 2, 3']")
        self.assertEqual(sxml.to_str('test_string'), b"test_string")

    def test_to_xml(self):
        sxml = SimpleXMLGenerator(self.render)
        data = [{'count': 1}, [1, 2, 3], None, 'test_string']

        sxml.startDocument()
        sxml.startElement('test', {})
        sxml.to_xml(sxml, data)
        sxml.endElement('test')
        sxml.endDocument()

        result = self.render.getvalue()
        self.assertIn('<list-item><count>1</count></list-item>', result)
        self.assertIn('<list-item><list-item>1</list-item><list-item>'
                      '2</list-item><list-item>3</list-item></list-item>',
                      result)
        self.assertIn('<list-item></list-item>', result)
        self.assertIn('<list-item>test_string</list-item>', result)
