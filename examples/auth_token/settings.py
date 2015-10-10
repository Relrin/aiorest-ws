# -*- coding: utf-8 -*-
# store User and Token tables in the memory
DATABASES = {
    'default': {
        'backend': 'aiorest_ws.db.backends.sqlite3',
        'name': ':memory:'
    }
}
