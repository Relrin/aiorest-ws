# -*- coding: utf-8 -*-
"""
Module for initialize "global" settings and make it available from any part
of future application.

First of all, values will be read from user defined settings file, when path to
him is specified at AIOREST_SETTINGS_MODULE environment variable. Any other
settings, which not specified/defined by the user, will be taken from the
default aiorest_ws.conf.settings module.
"""
import importlib
import os

from aiorest_ws.conf import global_settings

__all__ = (
    'ENVIRONMENT_VARIABLE', 'Settings', 'UserSettingsHolder', 'settings',
)

ENVIRONMENT_VARIABLE = "AIORESTWS_SETTINGS_MODULE"


class Settings(object):
    """
    Settings class of application.
    """
    def __init__(self):
        super(Settings, self).__init__()

        # Parse default settings and append to object
        self._setup(global_settings)

        # After that take the user defined settings and make merge
        user_settings = os.environ.get(ENVIRONMENT_VARIABLE, None)
        if user_settings:
            user_settings = importlib.import_module(user_settings)
            self._setup(user_settings)

        self._create_database_managers()

    def _setup(self, settings):
        for setting in dir(settings):
            if setting.isupper():
                setattr(self, setting, getattr(settings, setting))

        self._wrapped = self

    def _create_database_managers(self):
        if not self.USE_ORM_ENGINE:

            for name, db_settings in self.DATABASES.items():
                backend = db_settings['backend']

                init_kwargs = ('name', 'user', 'password', 'host', 'port')
                kwargs = {
                    key: db_settings[key]
                    for key in db_settings if key in init_kwargs
                }
                managers_module = importlib.import_module(
                    backend + '.managers'
                )
                manager_cls = db_settings.get('manager') or 'SQLiteManager'
                # User defined manager_cls as string means that necessary to
                # extract class and create one instance of this
                if type(manager_cls) is str:
                    manager_instance = getattr(
                        managers_module, manager_cls
                    )(**kwargs)
                # In any other cases in can be already instantiated manager
                else:
                    manager_instance = manager_cls
                db_settings['manager'] = manager_instance


class UserSettingsHolder(Settings):
    """
    Holder for user configured settings.
    """
    # SETTINGS_MODULE doesn't make much sense in the manually configured
    # (standalone) case
    SETTINGS_MODULE = None

    def __init__(self, default_settings):
        """
        Requests for configuration variables not in this class are satisfied
        from the module specified in default_settings (if possible).
        """
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super(UserSettingsHolder, self).__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super(UserSettingsHolder, self).__delattr__(name)

    def __dir__(self):
        return sorted(
            s for s in list(self.__dict__) + dir(self.default_settings)
            if s not in self._deleted
        )

    def is_overridden(self, setting):
        deleted = (setting in self._deleted)
        set_locally = (setting in self.__dict__)
        set_on_default = getattr(
            self.default_settings, 'is_overridden', lambda s: False
        )(setting)
        return (deleted or set_locally or set_on_default)

    def __repr__(self):
        return '<%(cls)s>' % {
            'cls': self.__class__.__name__,
        }


settings = Settings()
