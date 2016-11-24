# -*- coding: utf-8 -*-
import unittest

from django.apps import apps
from django.db import connections


class DjangoUnitTest(unittest.TestCase):

    models = []
    apps = ()

    @classmethod
    def setUpClass(cls):
        super(DjangoUnitTest, cls).setUpClass()
        if apps:
            apps.populate(cls.apps)

        conn = connections['default']
        with conn.schema_editor() as editor:
            for model in cls.models:
                editor.create_model(model)

    @classmethod
    def tearDownClass(cls):
        super(DjangoUnitTest, cls).tearDownClass()

        conn = connections['default']
        with conn.schema_editor() as editor:
            for model in cls.models:
                editor.delete_model(model)
