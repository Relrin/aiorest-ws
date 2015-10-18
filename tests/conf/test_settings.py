# -*- coding: utf-8 -*-
import os
import unittest

from aiorest_ws.db.backends.sqlite3.managers import SQLiteManager
from aiorest_ws.conf import Settings, ENVIRONMENT_VARIABLE


class SettingsTestCase(unittest.TestCase):

    def __set_user_settings(self, settings):
        os.environ.setdefault(ENVIRONMENT_VARIABLE, settings)

    def test_base_settings(self):
        settings = Settings()
        default_settings = [
            'DATABASES', 'DEFAULT_ENCODING', 'DEFAULT_LOGGING_SETTINGS',
            'ISO_8601', 'MIDDLEWARE_CLASSES'
        ]

        for setting_name in default_settings:
            self.assertTrue(hasattr(settings, setting_name))

    def test_setup_manager(self):
        os.environ.setdefault(
            ENVIRONMENT_VARIABLE, "tests.fixtures.example_settings"
        )
        settings = Settings()

        self.assertTrue(hasattr(settings, 'DATABASES'))
        self.assertIsInstance(settings.DATABASES['default']['manager'],
                              SQLiteManager)
