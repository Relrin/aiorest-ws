# -*- coding: utf-8 -*-

USE_ORM_ENGINE = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
INSTALLED_APPS = ("app", )
