# -*- coding: utf-8 -*-
"""
    Manager classes and functions, which help for work with databases via SQL.
"""
__all__ = ('SQLiteManager', )

import sqlite3


class SQLiteManager(object):

    def __init__(self, *args, **kwargs):
        super(SQLiteManager, self).__init__()
        db_path = kwargs.get('name')
        self.connection = sqlite3.connect(db_path)

    def execute_sql(self, sql, parameters=()):
        """Executes a SQL statement.

        :param sql: SQL statement as string.
        :param parameters: tuple with arguments.
        """
        return self.connection.execute(sql, parameters)

    def execute_sql_and_fetchone(self, sql, parameters=()):
        """Executes a SQL statement with fetching one row from result.

        :param sql: SQL statement as string.
        :param parameters: tuple with arguments.
        """
        return self.execute_sql(sql, parameters).fetchone()

    def execute_sql_from_file(self, filepath):
        """Executes a SQL statement, which was taken from the file.

        :param filepath: path to file.
        """
        with open(filepath, 'r') as f:
            sql = f.read()
            result = self.connection.executescript(sql)
        return result

    def execute_script(self, sql):
        """Execute a SQL statement. This method recommended to use, when
        required to execute few SQL queries independent and in parallel.

        :param sql: SQL statement as string.
        """
        return self.connection.executescript(sql)
