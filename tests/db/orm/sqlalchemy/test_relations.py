# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm.relations import RelatedField as BaseRelatedField, \
    PKOnlyObject
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.sqlalchemy.relations import ManyRelatedField, \
    RelatedField, PrimaryKeyRelatedField, HyperlinkedRelatedField
from aiorest_ws.db.orm.sqlalchemy.fields import IntegerField, DictField
from aiorest_ws.parsers import URLParser
from aiorest_ws.test.utils import override_settings
from aiorest_ws.urls.base import set_urlconf

from tests.fixtures.fakes import FakeView
from tests.fixtures.sqlalchemy import SESSION, ENGINE

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class TestManyRelatedField(unittest.TestCase):

    class FakeRelatedField(BaseRelatedField):

        def get_queryset(self):
            return []

        def to_representation(self, value):
            return value

    class TestManyRelatedFieldUserModel(Base):
        __tablename__ = 'test_many_relations_field_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        addresses = relationship(
            "TestManyRelatedFieldAddressModel", back_populates="user"
        )

    class TestManyRelatedFieldAddressModel(Base):
        __tablename__ = 'test_many_relations_field_addresses_model'
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey('test_many_relations_field_users_model.id')
        )
        user = relationship(
            "TestManyRelatedFieldUserModel", back_populates="addresses"
        )

    tables = [
        TestManyRelatedFieldUserModel.__table__,
        TestManyRelatedFieldAddressModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestManyRelatedField, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestManyRelatedField, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_attribute_returns_relation(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('addresses', self)

        session = SESSION()

        user = self.TestManyRelatedFieldUserModel(name='admin')
        address = self.TestManyRelatedFieldAddressModel(
            email_address='admin@email.com'
        )
        user.addresses.append(address)
        session.add(user)
        session.add(address)
        session.commit()
        self.assertEqual(instance.get_attribute(user), [address])

        session.close()

    def test_get_attribute_returns_empty_list_for_transient_object(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('addresses', self)

        transient_user = self.TestManyRelatedFieldUserModel(name='admin')
        self.assertEqual(instance.get_attribute(transient_user), [])

    def test_get_attribute_returns_empty_list_for_pending_object(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('addresses', self)

        session = SESSION()

        pending_user = self.TestManyRelatedFieldUserModel(name='admin')
        session.add(pending_user)
        self.assertEqual(instance.get_attribute(pending_user), [])

        session.close()

    def test_deepcopy_field(self):
        child_instance = self.FakeRelatedField(read_only=True)
        instance = ManyRelatedField(child_relation=child_instance)
        instance.bind('addresses', self)

        instance_copy = instance.__deepcopy__(None)
        self.assertNotEqual(instance, instance_copy)
        self.assertEqual(
            instance.child_relation,
            instance_copy.child_relation
        )


class TestRelatedField(unittest.TestCase):

    class RelatedWithOptimization(RelatedField):

        def use_pk_only_optimization(self):
            return self.source_attrs[-1] in ('id', 'pk')

    class TestRelatedFieldUserModel(Base):
        __tablename__ = 'test_relation_field_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        addresses = relationship(
            "TestRelatedFieldAddressModel", back_populates="user"
        )

    class TestRelatedFieldAddressModel(Base):
        __tablename__ = 'test_relation_field_addresses_model'
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey('test_relation_field_users_model.id')
        )
        user = relationship(
            "TestRelatedFieldUserModel", back_populates="addresses"
        )

    tables = [
        TestRelatedFieldUserModel.__table__,
        TestRelatedFieldAddressModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestRelatedField, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

        session = SESSION()
        user = cls.TestRelatedFieldUserModel(name='admin')
        address = cls.TestRelatedFieldAddressModel(
            email_address='admin@email.com'
        )
        user.addresses.append(address)
        session.add(user)
        session.add(address)
        session.commit()
        session.close()

    @classmethod
    def tearDownClass(cls):
        super(TestRelatedField, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_attribute_returns_attribute(self):
        instance = RelatedField(read_only=True)
        instance.bind('user', self)
        session = SESSION()

        address = session.query(self.TestRelatedFieldAddressModel)\
                         .filter_by(email_address='admin@email.com')\
                         .first()
        self.assertEqual(instance.get_attribute(address), address.user)

        session.close()

    def test_get_attribute_returns_pk_only_object(self):
        instance = self.RelatedWithOptimization(read_only=True)
        instance.bind('user.id', self)

        session = SESSION()

        address = session.query(self.TestRelatedFieldAddressModel) \
                         .filter_by(email_address='admin@email.com') \
                         .first()
        relation_object = instance.get_attribute(address)
        self.assertIsInstance(relation_object, PKOnlyObject)
        self.assertEqual(relation_object.pk, address.user.id)

        session.close()

    def test_get_attribute_returns_raises_attribute_error(self):
        instance = self.RelatedWithOptimization(read_only=True)
        instance.bind('user.pk', self)

        session = SESSION()

        address = session.query(self.TestRelatedFieldAddressModel) \
            .filter_by(email_address='admin@email.com') \
            .first()
        self.assertRaises(AttributeError, instance.get_attribute, address)

        session.close()

    def test_deepcopy_field(self):
        instance = RelatedField(read_only=True)

        instance_copy = instance.__deepcopy__(None)
        self.assertNotEqual(instance, instance_copy)


class TestPrimaryKeyRelatedField(unittest.TestCase):

    class TestPrimaryKeyRelatedFieldUserModel(Base):
        __tablename__ = 'test_pk_related_field_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        addresses = relationship(
            "TestPrimaryKeyRelatedFieldAddressModel", back_populates="user"
        )

    class TestPrimaryKeyRelatedFieldAddressModel(Base):
        __tablename__ = 'test_pk_related_field_addresses_model'
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey('test_pk_related_field_users_model.id')
        )
        user = relationship(
            "TestPrimaryKeyRelatedFieldUserModel", back_populates="addresses"
        )

    tables = [
        TestPrimaryKeyRelatedFieldUserModel.__table__,
        TestPrimaryKeyRelatedFieldAddressModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestPrimaryKeyRelatedField, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

        session = SESSION()
        user = cls.TestPrimaryKeyRelatedFieldUserModel(name='admin')
        address = cls.TestPrimaryKeyRelatedFieldAddressModel(
            email_address='admin@email.com'
        )
        user.addresses.append(address)
        session.add(user)
        session.add(address)
        session.commit()
        session.close()

    @classmethod
    def tearDownClass(cls):
        super(TestPrimaryKeyRelatedField, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_internal_value_returns_object(self):
        session = SESSION()
        user = session.query(self.TestPrimaryKeyRelatedFieldUserModel) \
                      .filter_by(name='admin').first()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(queryset=queryset)

        relation_object = instance.to_internal_value({'id': user.id})
        self.assertIsInstance(
            relation_object,
            self.TestPrimaryKeyRelatedFieldUserModel
        )
        self.assertEqual(relation_object.id, user.id)

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_internal_value_returns_object_via_pk_field_attribute(self):
        session = SESSION()
        user = session.query(self.TestPrimaryKeyRelatedFieldUserModel) \
            .filter_by(name='admin').first()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(
            queryset=queryset, pk_field=DictField()
        )

        relation_object = instance.to_internal_value({'id': user.id})
        self.assertIsInstance(
            relation_object,
            self.TestPrimaryKeyRelatedFieldUserModel
        )
        self.assertEqual(relation_object.id, user.id)

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_internal_value_raises_validation_exc_for_invalid_pk(self):
        session = SESSION()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(queryset=queryset)

        self.assertRaises(
            ValidationError,
            instance.to_internal_value,
            {'id': -1}
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_internal_value_raises_validation_error_for_a_wrong_type(self):
        session = SESSION()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(queryset=queryset)

        self.assertRaises(
            ValidationError,
            instance.to_internal_value,
            None
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_representation_returns_object_pk(self):
        session = SESSION()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(queryset=queryset)

        user = session.query(self.TestPrimaryKeyRelatedFieldUserModel) \
                      .filter_by(name='admin').first()
        self.assertEqual(instance.to_representation(user), user.id)

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_to_representation_returns_object_primary_key_via_pk_field(self):
        session = SESSION()
        queryset = session.query(self.TestPrimaryKeyRelatedFieldUserModel)
        instance = PrimaryKeyRelatedField(
            queryset=queryset, pk_field=IntegerField()
        )

        user = session.query(self.TestPrimaryKeyRelatedFieldUserModel) \
            .filter_by(name='admin').first()
        self.assertEqual(instance.to_representation(user), user.id)

        session.close()


class TestHyperlinkedRelatedField(unittest.TestCase):

    class TestHyperlinkedRelatedFieldUserModel(Base):
        __tablename__ = 'test_hyperlink_related_field_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        addresses = relationship(
            "TestHyperlinkedRelatedFieldAddressModel", back_populates="user"
        )

    class TestHyperlinkedRelatedFieldAddressModel(Base):
        __tablename__ = 'test_hyperlink_related_field_addresses_model'
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey('test_hyperlink_related_field_users_model.id')
        )
        user = relationship(
            "TestHyperlinkedRelatedFieldUserModel", back_populates="addresses"
        )

    class TestHyperlinkedRelatedFieldCompositePkModel(Base):
        __tablename__ = 'test_hyperlink_related_field_with_composite_pk_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), primary_key=True)

    tables = [
        TestHyperlinkedRelatedFieldUserModel.__table__,
        TestHyperlinkedRelatedFieldAddressModel.__table__,
        TestHyperlinkedRelatedFieldCompositePkModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestHyperlinkedRelatedField, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

        session = SESSION()
        user = cls.TestHyperlinkedRelatedFieldUserModel(name='admin')
        address = cls.TestHyperlinkedRelatedFieldAddressModel(
            email_address='admin@email.com'
        )
        user_composite_pk = cls.TestHyperlinkedRelatedFieldCompositePkModel(
            id=1, name='test_user'
        )
        user.addresses.append(address)
        session.add(user)
        session.add(address)
        session.add(user_composite_pk)
        session.commit()
        session.close()

        url_parser = URLParser()
        cls.data = {
            'urls': [
                url_parser.define_route(
                    '/user/{pk}/', FakeView, ['GET', ], name='user-detail'
                ),
            ]
        }
        set_urlconf(cls.data)

    @classmethod
    def tearDownClass(cls):
        super(TestHyperlinkedRelatedField, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_use_pk_only_optimization_returns_true(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')
        self.assertTrue(instance.use_pk_only_optimization())

    def test_use_pk_only_optimization_returns_false(self):
        class CustomHyperlinkedRelatedField(HyperlinkedRelatedField):
            lookup_field = 'name'

        instance = CustomHyperlinkedRelatedField(view_name='user-detail')
        self.assertFalse(instance.use_pk_only_optimization())

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_object_returns_object_from_database(self):
        session = SESSION()
        queryset = session.query(self.TestHyperlinkedRelatedFieldUserModel)
        instance = HyperlinkedRelatedField(
            view_name='user-detail', queryset=queryset
        )

        user = session.query(self.TestHyperlinkedRelatedFieldUserModel) \
            .filter_by(name='admin').first()

        obj = instance.get_object('user-detail', [], {'id': user.id})
        self.assertIsInstance(obj, self.TestHyperlinkedRelatedFieldUserModel)
        self.assertEqual(obj.id, user.id)

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_object_raises_validation_error_for_object_not_found(self):
        session = SESSION()
        queryset = session.query(self.TestHyperlinkedRelatedFieldUserModel)
        instance = HyperlinkedRelatedField(
            view_name='user-detail', queryset=queryset
        )

        self.assertRaises(
            ValidationError,
            instance.get_object,
            'user-detail', [], {'id': -1}
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_object_raises_improperly_configured_exception(self):
        session = SESSION()
        queryset = session.query(self.TestHyperlinkedRelatedFieldUserModel)
        instance = HyperlinkedRelatedField(
            view_name='user-detail', queryset=queryset
        )

        self.assertRaises(
            ImproperlyConfigured,
            instance.get_object,
            'user-detail', [], {}
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_object_raises_validation_error_for_a_wrong_type(self):
        session = SESSION()
        queryset = session.query(self.TestHyperlinkedRelatedFieldUserModel)
        instance = HyperlinkedRelatedField(
            view_name='user-detail', queryset=queryset
        )

        self.assertRaises(
            ValidationError,
            instance.get_object,
            'user-detail', [], {'invalid view_kwarg type', }
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_is_saved_in_database_returs_true(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')
        session = SESSION()

        user = session.query(self.TestHyperlinkedRelatedFieldUserModel) \
                      .filter_by(name='admin').first()
        self.assertTrue(instance.is_saved_in_database(user))

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_is_saved_in_database_returs_false_for_transient_object(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')

        user = self.TestHyperlinkedRelatedFieldUserModel(name='test_admin')
        self.assertFalse(instance.is_saved_in_database(user))

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_is_saved_in_database_returs_false_for_pending_object(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')
        session = SESSION()

        user = self.TestHyperlinkedRelatedFieldUserModel(name='test_admin')
        session.add(user)
        self.assertFalse(instance.is_saved_in_database(user))

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_lookup_value_returns_tuple_for_objects_single_pk(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')
        session = SESSION()

        user = session.query(self.TestHyperlinkedRelatedFieldUserModel) \
                      .filter_by(name='admin').first()
        self.assertEqual(
            instance.get_lookup_value(user),
            (user.id, )
        )

        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_lookup_value_returns_tuple_for_objects_composite_pk(self):
        instance = HyperlinkedRelatedField(view_name='user-detail')
        session = SESSION()

        user = session\
            .query(self.TestHyperlinkedRelatedFieldCompositePkModel) \
            .filter_by(id=1, name='test_user').first()
        self.assertEqual(
            set(instance.get_lookup_value(user)),
            {user.id, user.name}
        )

        session.close()
