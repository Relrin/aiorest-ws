# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.storages.backends import BaseStorageBackend


class BaseStorageBackendTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseStorageBackendTestCase, self).setUp()
        self.backend = BaseStorageBackend()

    def test_get(self):
        self.assertEqual(self.backend.get(), None)

    def test_save(self):
        self.assertEqual(self.backend.save(), None)
