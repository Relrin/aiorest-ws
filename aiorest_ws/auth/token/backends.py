# -*- coding: utf-8 -*-
"""
    Storage backends for save/get credentials.
"""
from aiorest_ws.auth.token.utils import SQL_CREATE_TOKEN_TABLE, \
    SQL_TOKEN_GET, SQL_TOKEN_GET_BY_TOKEN_USERNAME, SQL_TOKEN_ADD, \
    TOKEN_MODEL_FIELDS
from aiorest_ws.conf import settings
from aiorest_ws.db.backends.sqlite3.constants import IN_MEMORY
from aiorest_ws.db.backends.sqlite3.managers import SQLiteManager
from aiorest_ws.db.utils import convert_db_row_to_dict
from aiorest_ws.storages.backends import BaseStorageBackend

__all__ = ('InMemoryTokenBackend', )


class InMemoryTokenBackend(BaseStorageBackend):
    """In memory backend (based on SQLite) for token."""

    def __init__(self):
        super(InMemoryTokenBackend, self).__init__()
        if settings.DATABASES:
            self.db_manager = settings.DATABASES['default']['manager']
        else:
            self.db_manager = SQLiteManager(name=IN_MEMORY)
        self.__create_models()

    def __create_models(self):
        self.db_manager.execute_script(SQL_CREATE_TOKEN_TABLE)

    def get(self, token):
        """Get token from the storage.

        :param token: token as string.
        """
        args = (token, )
        row = self.db_manager.execute_sql_and_fetchone(SQL_TOKEN_GET, args)
        if row:
            token_object = convert_db_row_to_dict(row, TOKEN_MODEL_FIELDS)
        else:
            token_object = {}
        return token_object

    def get_token_by_username(self, token_name, username):
        """Get token from the storage by token_name and username.

        :param token: token as string.
        """
        args = (token_name, username)
        row = self.db_manager.execute_sql_and_fetchone(
            SQL_TOKEN_GET_BY_TOKEN_USERNAME, args
        )
        if row:
            token_object = convert_db_row_to_dict(row, TOKEN_MODEL_FIELDS)
        else:
            token_object = {}
        return token_object

    def save(self, token_name, token, expired=None, user_id=None):
        """Save token in the storage.

        :param user: instance of User class.
        :param token: token as string.
        """
        args = (token_name, token, expired, user_id)
        self.db_manager.execute_sql(SQL_TOKEN_ADD, args)
