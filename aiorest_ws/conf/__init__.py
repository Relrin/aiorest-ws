# -*- coding: utf-8 -*-
"""
    Module for initialize "global" settings and make it available from any
    part of future application.

    First of all, values will be read from user defined settings file, when
    path to him is specified at AIOREST_SETTINGS_MODULE environment variable.
    Any other settings, which not specified/defined by the user, will be taken
    from the default aiorest_ws.conf.settings module.
"""
__all__ = ('ENVIRONMENT_VARIABLE', 'Settings', 'settings', )

import importlib
import os

from aiorest_ws.conf import global_settings


ENVIRONMENT_VARIABLE = "AIORESTWS_SETTINGS_MODULE"


class Settings(object):
    """Settings class of application."""
    def __init__(self):
        # parse default settings and append to object
        self._setup(global_settings)

        # after that take the user defined settings and make merge
        user_settings = os.environ.get(ENVIRONMENT_VARIABLE, None)
        if user_settings:
            user_settings = importlib.import_module(user_settings)
            self._setup(user_settings)

        self._create_database_managers()

    def _setup(self, settings):
        for setting in dir(settings):
            if setting.isupper():
                setattr(self, setting, getattr(settings, setting))

    def _create_database_managers(self):
        for name, db_settings in self.DATABASES.items():
            backend = db_settings['backend']

            init_kwargs = ('name', 'user', 'password', 'host', 'port')
            kwargs = {
                key: db_settings[key]
                for key in db_settings if key in init_kwargs
            }

            managers_module = importlib.import_module(backend + '.managers')
            manager_cls = db_settings.get('manager') or 'SQLiteManager'
            # user defined manager_cls as string means that necessary to
            # extract class and create one instance of this
            if type(manager_cls) is str:
                manager_instance = getattr(
                    managers_module, manager_cls
                )(**kwargs)
            # in any other cases in can be already instantiated manager
            else:
                manager_instance = manager_cls
            db_settings['manager'] = manager_instance


settings = Settings()
