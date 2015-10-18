# -*- coding: utf-8 -*-
DATABASES = {
    'default': {
        'backend': 'aiorest_ws.db.backends.sqlite3',
        'name': ':memory:'
    }
}
