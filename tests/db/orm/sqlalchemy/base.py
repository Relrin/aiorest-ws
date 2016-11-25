# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.ext.declarative import declarative_base
from tests.fixtures.sqlalchemy import ENGINE

Base = declarative_base()


class SQLAlchemyUnitTest(unittest.TestCase):

    tables = []

    @classmethod
    def setUpClass(cls):
        super(SQLAlchemyUnitTest, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(SQLAlchemyUnitTest, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)
