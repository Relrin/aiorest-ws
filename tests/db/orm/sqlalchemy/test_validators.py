# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.db.orm.sqlalchemy.fields import CharField
from aiorest_ws.db.orm.sqlalchemy.validators import ORMFieldValidator, \
    UniqueORMValidator
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.test.utils import override_settings

from tests.fixtures.sqlalchemy import ENGINE, SESSION

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TestORMFieldValidator(unittest.TestCase):

    class SQLAlchemyModel(object):
        email = CharField()

        def validate_email(self, key, address):
            assert '@' in address, '@ must be in email address'
            return address

    def test_validation_passed_sucessfully(self):
        validator = ORMFieldValidator(
            self.SQLAlchemyModel.validate_email, self.SQLAlchemyModel.email,
            'email'
        )
        self.assertIsNone(validator('admin@site.com'))

    def test_validation_raises_validation_error(self):
        validator = ORMFieldValidator(
            self.SQLAlchemyModel.validate_email, self.SQLAlchemyModel.email,
            'email'
        )

        with self.assertRaises(ValidationError):
            validator('wrong email address')


class TestUniqueORMValidator(unittest.TestCase):

    class TableWithUniqueName(Base):
        __tablename__ = 'test_unique_field'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)

    @classmethod
    def setUpClass(cls):
        super(TestUniqueORMValidator, cls).setUpClass()
        Base.metadata.create_all(
            ENGINE, tables=[cls.TableWithUniqueName.__table__, ]
        )
        cls.session = SESSION()

        cls.session.add_all([
            cls.TableWithUniqueName(name='Adam'),
            cls.TableWithUniqueName(name='Bob'),
            cls.TableWithUniqueName(name='Eve'),
        ])
        cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestUniqueORMValidator, cls).tearDownClass()
        Base.metadata.remove(cls.TableWithUniqueName.__table__)

    def test_filter_queryset(self):
        validator = UniqueORMValidator(
            self.TableWithUniqueName, 'name'
        )
        result_queryset = validator.filter_queryset(
            'Bob', self.session.query(validator.model)
        )
        self.assertEqual(result_queryset.count(), 1)
        self.assertEqual(result_queryset.value('name'), 'Bob')

    def test_exclude_current_instance(self):
        validator = UniqueORMValidator(
            self.TableWithUniqueName, 'name'
        )

        validator.instance = self.session.query(validator.model)\
            .filter(self.TableWithUniqueName.name == 'Adam')\
            .first()
        queryset = self.session.query(validator.model)
        self.assertEqual(queryset.count(), 3)
        self.assertEqual(
            validator.exclude_current_instance(queryset).count(), 2
        )

    def test_exclude_current_instance_not_applied(self):
        validator = UniqueORMValidator(
            self.TableWithUniqueName, 'name'
        )

        queryset = self.session.query(validator.model)
        self.assertEqual(queryset.count(), 3)
        self.assertEqual(
            validator.exclude_current_instance(queryset).count(), 3
        )

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_validation_passed_sucessfully(self):
        validator = UniqueORMValidator(
            self.TableWithUniqueName, 'name'
        )
        self.assertIsNone(validator('John'))

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_validation_raises_validation_error(self):
        validator = UniqueORMValidator(
            self.TableWithUniqueName, 'name'
        )

        with self.assertRaises(ValidationError):
            self.assertIsNone(validator('Eve'))
