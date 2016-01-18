# -*- coding: utf-8 -*-
import os


def get_module_content(filename):
    with open(filename, 'r') as module:
        return module.read()


if __name__ == __name__:
    os.environ.setdefault("AIORESTWS_SETTINGS_MODULE", "settings")
    exec(get_module_content('./create_db.py'))
    exec(get_module_content('./server.py'))
