# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.db.orm.sqlalchemy.model_meta import _get_pk, _get_fields, \
    _get_relations, _get_to_field, _get_forward_relationships, \
    _get_reverse_relationships, _merge_fields_and_pk, _merge_relationships, \
    get_field_info, is_abstract_model, get_relations_data, model_pk

from tests.fixtures.sqlalchemy import ENGINE

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Table, \
    DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.interfaces import ONETOMANY


Base = declarative_base()


class TestGetPkFunction(unittest.TestCase):

    class TestGetPkWithSinglePkModel(Base):
        __tablename__ = 'test_get_pk_with_single_pk_model'
        id = Column(Integer, primary_key=True)

    class TestGetPkWithCompositePkModel(Base):
        __tablename__ = 'test_get_pk_with_composite_pk_model'
        id = Column(Integer, primary_key=True)
        username = Column(String(50), primary_key=True)

    tables = [
        TestGetPkWithSinglePkModel.__table__,
        TestGetPkWithCompositePkModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetPkFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetPkFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_single_pk_from_model(self):
        mapper = self.TestGetPkWithSinglePkModel.__mapper__

        self.assertEqual(
            _get_pk(mapper),
            [(column.name, column) for column in mapper.primary_key]
        )

    def test_get_composite_pk_from_model(self):
        mapper = self.TestGetPkWithCompositePkModel.__mapper__

        self.assertEqual(
            _get_pk(mapper),
            [(column.name, column) for column in mapper.primary_key]
        )


class TestGetFieldsFunction(unittest.TestCase):

    class TestGetFieldsFunctionModel(Base):
        __tablename__ = 'test_get_fields_function_model'
        id = Column(Integer, primary_key=True)
        username = Column(String(50))
        address = Column(String(50), nullable=True)
        email = Column(String(50), unique=True)
        gender = Column(Enum(*('male', 'female')))

    tables = [
        TestGetFieldsFunctionModel.__table__,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetFieldsFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetFieldsFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_fields_from_model(self):
        mapper = self.TestGetFieldsFunctionModel.__mapper__

        self.assertEqual(
            set(_get_fields(mapper).keys()),
            {'id', 'username', 'address', 'email', 'gender'}
        )


class TestGetRelationsFunction(unittest.TestCase):

    class TestGetRelationsParentModel(Base):
        __tablename__ = 'test_get_relations_parent_model'
        id = Column(Integer, primary_key=True)
        children = relationship("TestGetRelationsChildModel")

    class TestGetRelationsChildModel(Base):
        __tablename__ = 'test_get_relations_child_model'
        id = Column(Integer, primary_key=True)
        parent_id = Column(
            Integer, ForeignKey('test_get_relations_parent_model.id')
        )
        parent = relationship("TestGetRelationsParentModel")

    tables = [
        TestGetRelationsParentModel.__table__,
        TestGetRelationsChildModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetRelationsFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetRelationsFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_relations(self):
        mapper = self.TestGetRelationsParentModel.__mapper__

        self.assertEqual(
            set([field for field, _ in _get_relations(mapper, ONETOMANY)]),
            {'children', }
        )


class TestGetToFieldFunction(unittest.TestCase):

    class TestGetToFieldParentModel(Base):
        __tablename__ = 'test_get_to_field_parent_model'
        id = Column(Integer, primary_key=True)
        children = relationship(
            "TestGetToFieldChildModel", back_populates="parent"
        )

    class TestGetToFieldChildModel(Base):
        __tablename__ = 'test_get_to_field_child_model'
        id = Column(Integer, primary_key=True)
        parent_id = Column(
            Integer, ForeignKey('test_get_to_field_parent_model.id')
        )
        parent = relationship(
            "TestGetToFieldParentModel", back_populates="children"
        )

    tables = [
        TestGetToFieldParentModel.__table__,
        TestGetToFieldChildModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetToFieldFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetToFieldFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_to_field(self):
        mapper = self.TestGetToFieldParentModel.__mapper__
        relation_field = mapper.relationships.items()[0][1]

        self.assertEqual(_get_to_field(relation_field).name, 'parent_id')

    def test_get_to_field_returns_none(self):
        mapper = self.TestGetToFieldChildModel.__mapper__
        non_relation_field = mapper.columns['id']

        self.assertIsNone(_get_to_field(non_relation_field))


class TestGetForwardRelationsFunction(unittest.TestCase):

    class TestGetForwardRelationsParentModel(Base):
        __tablename__ = 'test_forward_rel_parent_model'
        id = Column(Integer, primary_key=True)
        children = relationship(
            "TestGetForwardRelationsChildModel", back_populates="parent"
        )

    class TestGetForwardRelationsChildModel(Base):
        __tablename__ = 'test_forward_rel_child_model'
        id = Column(Integer, primary_key=True)
        parent_id = Column(
            Integer, ForeignKey('test_forward_rel_parent_model.id')
        )
        parent = relationship(
            "TestGetForwardRelationsParentModel", back_populates="children"
        )

    tables = [
        TestGetForwardRelationsParentModel.__table__,
        TestGetForwardRelationsChildModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetForwardRelationsFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetForwardRelationsFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_forward_relations(self):
        mapper = self.TestGetForwardRelationsParentModel.__mapper__

        self.assertEqual(
            set(_get_forward_relationships(mapper).keys()),
            {'children', }
        )


test_get_reverse_relations_association_table = Table(
    'test_get_reverse_relations_association_table', Base.metadata,
    Column(
        'left_id', Integer,
        ForeignKey('test_get_reverse_relations_left_model.id')
    ),
    Column(
        'right_id', Integer,
        ForeignKey('test_get_reverse_relations_right_model.id')
    )
)


class TestGetReverseRelationsFunction(unittest.TestCase):

    class TestGetReverseRelationsFkParentModel(Base):
        __tablename__ = 'test_get_reverse_relations_fk_parent_model'
        id = Column(Integer, primary_key=True)
        child_id = Column(
            Integer,
            ForeignKey('test_get_reverse_relations_fk_child_model.id')
        )
        child = relationship(
            "TestGetReverseRelationsFkChildModel", back_populates="parents"
        )

    class TestGetReverseRelationsFkChildModel(Base):
        __tablename__ = 'test_get_reverse_relations_fk_child_model'
        id = Column(Integer, primary_key=True)
        parents = relationship(
            "TestGetReverseRelationsFkParentModel", back_populates="child"
        )

    class TestGetReverseRelationsParentModel(Base):
        __tablename__ = 'test_get_reverse_relations_left_model'
        id = Column(Integer, primary_key=True)
        children = relationship(
            "TestGetReverseRelationsChildModel",
            secondary=test_get_reverse_relations_association_table,
            back_populates="parents"
        )

    class TestGetReverseRelationsChildModel(Base):
        __tablename__ = 'test_get_reverse_relations_right_model'
        id = Column(Integer, primary_key=True)
        parents = relationship(
            "TestGetReverseRelationsParentModel",
            secondary=test_get_reverse_relations_association_table,
            back_populates="children"
        )

    tables = [
        TestGetReverseRelationsFkParentModel.__table__,
        TestGetReverseRelationsFkChildModel.__table__,
        test_get_reverse_relations_association_table,
        TestGetReverseRelationsParentModel.__table__,
        TestGetReverseRelationsChildModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetReverseRelationsFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetReverseRelationsFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_reverse_relations_for_many_to_one(self):
        mapper = self.TestGetReverseRelationsFkParentModel.__mapper__

        self.assertEqual(
            set(_get_reverse_relationships(mapper).keys()),
            {'child', }
        )

    def test_get_reverse_relations_for_many_to_many(self):
        mapper = self.TestGetReverseRelationsParentModel.__mapper__

        self.assertEqual(
            set(_get_reverse_relationships(mapper).keys()),
            {'children', }
        )


class TestMergeFieldAndPkFunction(unittest.TestCase):

    class TestMergeFieldAndPkModel(Base):
        __tablename__ = 'test_merge_fields_and_pk_model'
        id = Column(Integer, primary_key=True)
        username = Column(String(50))
        address = Column(String(50), nullable=True)
        email = Column(String(50), unique=True)

    @classmethod
    def setUpClass(cls):
        super(TestMergeFieldAndPkFunction, cls).setUpClass()
        Base.metadata.create_all(
            ENGINE, tables=[cls.TestMergeFieldAndPkModel.__table__, ]
        )

    @classmethod
    def tearDownClass(cls):
        super(TestMergeFieldAndPkFunction, cls).tearDownClass()
        Base.metadata.remove(cls.TestMergeFieldAndPkModel.__table__)

    def test_merge_field_and_pk(self):
        mapper = self.TestMergeFieldAndPkModel.__mapper__
        pk = _get_pk(mapper)
        fields = _get_fields(mapper)

        self.assertEqual(
            set(_merge_fields_and_pk(pk, fields).keys()),
            {'id', 'username', 'address', 'email'}
        )


test_merge_function_m2m_file_server_model = Table(
    'test_merge_function_m2m_file_server_model', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column(
        'file_id', Integer,
        ForeignKey('test_merge_relations_file_model.id')
    ),
    Column(
        'fileserver_id', Integer,
        ForeignKey('test_merge_relations_fileserver_model.id')
    )
)


class TestMergeRelationsFunction(unittest.TestCase):

    class TestMergeRelationsCatalogModel(Base):
        __tablename__ = 'test_merge_relations_catalog_model'
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False, unique=True)
        file_id = relationship("TestMergeRelationsFileModel")

    class TestMergeRelationsFileModel(Base):
        __tablename__ = 'test_merge_relations_file_model'
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        catalog_id = Column(
            Integer,
            ForeignKey("test_merge_relations_catalog_model.id")
        )
        server_id = relationship(
            "TestMergeRelationsFileServerModel",
            secondary=test_merge_function_m2m_file_server_model
        )
        link_id = relationship("TestMergeRelationsLinkModel")

    class TestMergeRelationsFileServerModel(Base):
        __tablename__ = 'test_merge_relations_fileserver_model'
        id = Column(Integer, primary_key=True)
        ip = Column(String, nullable=False)
        port = Column(Integer, nullable=False)
        status = Column(String)
        last_online = Column(DateTime)

    class TestMergeRelationsLinkModel(Base):
        __tablename__ = 'test_merge_relations_link_model'
        id = Column(Integer, primary_key=True)
        url = Column(String(255), nullable=False, unique=True)
        expire_date = Column(DateTime, nullable=False)
        key = Column(String(255), nullable=False)
        description = Column(String, nullable=True)
        file_id = Column(
            Integer,
            ForeignKey('test_merge_relations_file_model.id')
        )

    tables = [
        TestMergeRelationsCatalogModel.__table__,
        TestMergeRelationsFileModel.__table__,
        TestMergeRelationsFileServerModel.__table__,
        TestMergeRelationsLinkModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestMergeRelationsFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestMergeRelationsFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_merge_relations(self):
        mapper = self.TestMergeRelationsFileModel.__mapper__
        forward_relations = _get_forward_relationships(mapper)
        reverse_relations = _get_reverse_relationships(mapper)

        relations = _merge_relationships(forward_relations, reverse_relations)
        self.assertEqual(
            set(relations.keys()),
            {'link_id', 'server_id'}
        )


class TestFieldInfoFunction(unittest.TestCase):

    class TestFieldInfoParentModel(Base):
        __tablename__ = 'test_field_info_parent_model'
        id = Column(Integer, primary_key=True)
        children = relationship(
            "TestFieldInfoChildModel", back_populates="parent"
        )

    class TestFieldInfoChildModel(Base):
        __tablename__ = 'test_field_info_child_model'
        id = Column(Integer, primary_key=True)
        parent_id = Column(
            Integer, ForeignKey('test_field_info_parent_model.id')
        )
        parent = relationship(
            "TestFieldInfoParentModel", back_populates="children"
        )

    tables = [
        TestFieldInfoParentModel.__table__,
        TestFieldInfoChildModel.__table__,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestFieldInfoFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestFieldInfoFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_field_info(self):
        self.assertEqual(
            set(get_field_info(self.TestFieldInfoParentModel)._fields),
            {'pk', 'fields', 'forward_relations', 'reverse_relations',
             'fields_and_pk', 'relations'}
        )


class TestIsAbstractModelFunction(unittest.TestCase):

    class TestIsAbstractModel(Base):
        __tablename__ = 'test_is_abstract_model'
        __abstract__ = True
        id = Column(Integer, primary_key=True)

    class TestIsNotAbstractModel(Base):
        __tablename__ = 'test_is_not_abstract_model'
        id = Column(Integer, primary_key=True)

    tables = [
        TestIsNotAbstractModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestIsAbstractModelFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestIsAbstractModelFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_is_abstract_model_returns_true(self):
        self.assertTrue(is_abstract_model(self.TestIsAbstractModel))

    def test_is_abstract_model_return_false(self):
        self.assertFalse(is_abstract_model(self.TestIsNotAbstractModel))


class TestGetRelationsDataFunction(unittest.TestCase):

    class TestGetRelationsDataUserModel(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        fullname = Column(String(50), default='Unknown')
        password = Column(String(12))
        addresses = relationship(
            "TestGetRelationsDataAddressModel", back_populates="user"
        )

    class TestGetRelationsDataAddressModel(Base):
        __tablename__ = 'addresses'
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(Integer, ForeignKey('users.id'))
        user = relationship(
            "TestGetRelationsDataUserModel", back_populates="addresses"
        )

    tables = [
        TestGetRelationsDataUserModel.__table__,
        TestGetRelationsDataAddressModel.__table__,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestGetRelationsDataFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestGetRelationsDataFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_get_relations_data_returns_empty_dict(self):
        data = {
            "id": 1,
            "name": "admin",
            "fullname": "Nayton Drake",
            "password": "mysupersecretpassword",
        }

        self.assertEqual(
            get_relations_data(self.TestGetRelationsDataUserModel, data),
            {}
        )

    def test_get_relations_data_returns_filled_dict(self):
        data = {
            "id": 1,
            "name": "admin",
            "fullname": "Nayton Drake",
            "password": "mysupersecretpassword",
            "addresses": [1, 2, 3]  # some presumable IDs
        }

        self.assertEqual(
            get_relations_data(self.TestGetRelationsDataUserModel, data),
            {"addresses": [1, 2, 3]}
        )


class TestModelPkFunction(unittest.TestCase):

    class TestModelPkWithSinglePkModel(Base):
        __tablename__ = 'test_model_pk_with_single_pk_model'
        id = Column(Integer, primary_key=True)

    class TestModelPkWithCompositePkModel(Base):
        __tablename__ = 'test_model_pk_with_composite_pk_model'
        id = Column(Integer, primary_key=True)
        username = Column(String(50), primary_key=True)

    tables = [
        TestModelPkWithSinglePkModel.__table__,
        TestModelPkWithCompositePkModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestModelPkFunction, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestModelPkFunction, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_model_pk_from_model_with_one_pk(self):
        self.assertEqual(
            set(model_pk(self.TestModelPkWithSinglePkModel)),
            {'id', }
        )

    def test_model_pk_from_model_with_composite_pk(self):
        self.assertEqual(
            set(model_pk(self.TestModelPkWithCompositePkModel)),
            {'id', 'username'}
        )
