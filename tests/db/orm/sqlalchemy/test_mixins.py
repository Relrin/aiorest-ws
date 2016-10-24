# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.db.orm.sqlalchemy.mixins import ORMSessionMixin, \
    SQLAlchemyMixin
from aiorest_ws.test.utils import override_settings

from tests.fixtures.sqlalchemy import ENGINE, SESSION

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query


Base = declarative_base()


class TestORMSessionMixin(unittest.TestCase):
    settings = {'SQLALCHEMY_SESSION': SESSION}

    class TableForORMSessionMixin(Base):
        __tablename__ = 'test_orm_session_mixin'
        id = Column(Integer, primary_key=True)

    @classmethod
    def setUpClass(cls):
        super(TestORMSessionMixin, cls).setUpClass()
        cls._cls_overridden_context = override_settings(**cls.settings)
        cls._cls_overridden_context.enable()
        Base.metadata.create_all(
            ENGINE, tables=[cls.TableForORMSessionMixin.__table__, ]
        )
        cls.session = SESSION()

    @classmethod
    def tearDownClass(cls):
        super(TestORMSessionMixin, cls).tearDownClass()
        cls._cls_overridden_context.disable()
        Base.metadata.remove(cls.TableForORMSessionMixin.__table__)

    def test_get_session(self):
        mixin = ORMSessionMixin()
        self.assertIsInstance(mixin._get_session(), Session)

    def test_get_queryset_returns_new_queryset_with_session(self):
        mixin = ORMSessionMixin()
        mixin.queryset = Query(self.TableForORMSessionMixin)
        queryset = mixin.get_queryset()
        self.assertNotEqual(mixin.queryset.session, self.session)
        self.assertEqual(mixin.queryset, queryset)

    def test_get_queryset_returns_has_closed_session_and_returns_new_qs(self):
        mixin = ORMSessionMixin()
        mixin.queryset = self.session.query(self.TableForORMSessionMixin)
        queryset = mixin.get_queryset()
        self.assertNotEqual(mixin.queryset.session, self.session)
        self.assertEqual(mixin.queryset, queryset)


class TestSQLAlchemyMixin(unittest.TestCase):
    settings = {'SQLALCHEMY_SESSION': SESSION}

    class TableForSQLAlchemyMixin(Base):
        __tablename__ = 'test_sqlalchemy_orm_mixin'
        id = Column(Integer, primary_key=True)
        login = Column(String, nullable=False)

    @classmethod
    def setUpClass(cls):
        super(TestSQLAlchemyMixin, cls).setUpClass()
        cls._cls_overridden_context = override_settings(**cls.settings)
        cls._cls_overridden_context.enable()
        Base.metadata.create_all(
            ENGINE, tables=[cls.TableForSQLAlchemyMixin.__table__, ]
        )
        cls.session = SESSION()
        cls.session.add_all([cls.TableForSQLAlchemyMixin(login='user'), ])
        cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestSQLAlchemyMixin, cls).tearDownClass()
        cls._cls_overridden_context.disable()
        Base.metadata.remove(cls.TableForSQLAlchemyMixin.__table__)

    def test_get_filter_args(self):
        mixin = SQLAlchemyMixin()
        query = Query(self.TableForSQLAlchemyMixin)
        filter_arguments = list(mixin._get_filter_args(query, {'id': 1}))
        self.assertEqual(len(filter_arguments), 1)
        self.assertEqual(
            filter_arguments[0].__str__(),
            (self.TableForSQLAlchemyMixin.id == 1).__str__()
        )

    def test_get_object_pk(self):
        mixin = SQLAlchemyMixin()
        obj = self.session.query(self.TableForSQLAlchemyMixin) \
                          .filter(self.TableForSQLAlchemyMixin.id == 1) \
                          .first()
        self.assertEqual(mixin._get_object_pk(obj), 1)
