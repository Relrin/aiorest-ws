# -*- coding: utf-8 -*-
import tempfile
import unittest

from aiorest_ws.db.backends.sqlite3.constants import IN_MEMORY
from aiorest_ws.db.backends.sqlite3.managers import SQLiteManager


SQL_CREATE_USER_TABLE = """
    CREATE TABLE IF NOT EXISTS test_user_table
    (id INTEGER PRIMARY KEY NOT NULL,
     username CHAR(255) NOT NULL
    );
"""
SQL_USER_ADD = """
    INSERT INTO test_user_table (`username`)
    VALUES (?);
"""
SQL_USER_GET = """
    SELECT `id`, `username`
    FROM test_user_table
    WHERE username=?;
"""


class SQLiteManagerTestCase(unittest.TestCase):

    def setUp(self):
        super(SQLiteManagerTestCase, self).setUp()
        self.manager = SQLiteManager(name=IN_MEMORY)

    def test_execute_sql(self):
        self.manager.execute_sql(SQL_CREATE_USER_TABLE)

    def test_execute_sql_and_fetchone(self):
        username = 'test_user'
        self.manager.execute_sql(SQL_CREATE_USER_TABLE)
        self.manager.execute_sql(SQL_USER_ADD, (username, ))
        row = self.manager.execute_sql_and_fetchone(SQL_USER_GET, (username, ))
        self.assertEqual(row, (1, username))

    def test_execute_sql_from_file(self):
        self.manager.execute_sql(SQL_CREATE_USER_TABLE)
        with tempfile.NamedTemporaryFile() as tmpfile:
            file_sql = bytes("""
                INSERT INTO test_user_table (`username`)
                VALUES ('test_user');
            """, encoding='utf-8')
            tmpfile.write(file_sql)
            self.manager.execute_sql_from_file(tmpfile.name)

    def test_execute_script(self):
        self.manager.execute_sql(SQL_CREATE_USER_TABLE)
        self.manager.execute_script("""
            INSERT INTO test_user_table (`username`)
            VALUES ('test_user');
        """)
