# -*- coding: utf-8 -*-
import sys
from os import path

from django import setup as django_setup
from django.conf import settings as django_settings

from aiorest_ws.conf import settings


sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))
django_settings.configure(
    DATABASES=settings.DATABASES,
    INSTALLED_APPS=settings.INSTALLED_APPS
)
django_setup()

