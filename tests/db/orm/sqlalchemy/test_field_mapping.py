# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.db.orm.sqlalchemy.field_mapping import get_detail_view_name, \
    get_field_kwargs, get_relation_kwargs, get_nested_relation_kwargs
from aiorest_ws.utils.structures import RelationInfo

from tests.fixtures.sqlalchemy import ENGINE, SESSION

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

Base = declarative_base()


# Only for the TestGetRelationKwargs test cases

class FakeFieldArgument(object):

        def __init__(self, field_name):
            self.arg = field_name


class FakeModelField(object):

    def __init__(self, field_name, sqlalchemy_field):
        self.argument = FakeFieldArgument(field_name)
        self.field = sqlalchemy_field


class TestGetDetailViewName(unittest.TestCase):

    def test_get_detail_view_name(self):

        class TestModel(object):
            __tablename__ = 'my_test_model'

        self.assertEqual(
            get_detail_view_name(TestModel),
            'my_test_model-detail'
        )


class TestGetFieldKwargs(unittest.TestCase):

    class TestGetFieldKwargsModel(Base):
        __tablename__ = 'test_get_field_kwargs'
        id = Column(Integer, primary_key=True)
        username = Column(String(50))
        address = Column(String(50), nullable=True)
        email = Column(String(50), unique=True)
        gender = Column(Enum(*('male', 'female')))

        @validates('email')
        def validate_email(self, key, address):
            assert '@' in address, '@ must be in email address'
            return address

    @classmethod
    def setUpClass(cls):
        super(TestGetFieldKwargs, cls).setUpClass()
        Base.metadata.create_all(
            ENGINE, tables=[cls.TestGetFieldKwargsModel.__table__, ]
        )
        session = SESSION()
        session.add_all([
            cls.TestGetFieldKwargsModel(
                username='Adam',
                address='UK, London',
                email='adam@mail.com',
                gender='male'
            ),
            cls.TestGetFieldKwargsModel(
                username='Bob',
                address='USA, CA, San Francisco',
                email='bob@mail.com',
                gender='male'
            ),
            cls.TestGetFieldKwargsModel(
                username='Alexandra',
                address=None,
                email='alexandra@mail.com',
                gender='female'
            ),
        ])
        session.commit()

    @classmethod
    def tearDownClass(cls):
        super(TestGetFieldKwargs, cls).tearDownClass()
        Base.metadata.remove(cls.TestGetFieldKwargsModel.__table__)

    def test_get_field_kwargs_for_primary_key_field(self):
        field_kwargs = get_field_kwargs(
            'id', self.TestGetFieldKwargsModel.id, self.TestGetFieldKwargsModel
        )

        self.assertEqual(
            set(field_kwargs.keys()),
            set(['model_field', 'read_only'])
        )
        self.assertTrue(field_kwargs['read_only'])
        self.assertEqual(
            field_kwargs['model_field'],
            self.TestGetFieldKwargsModel.id
        )

    def test_get_field_kwargs_for_nullable_field(self):
        field_kwargs = get_field_kwargs(
            'address', self.TestGetFieldKwargsModel.address,
            self.TestGetFieldKwargsModel
        )

        self.assertEqual(
            set(field_kwargs.keys()),
            set([
                'model_field', 'required', 'allow_blank', 'allow_null',
                'max_length'
            ])
        )
        self.assertTrue(field_kwargs['allow_blank'])
        self.assertTrue(field_kwargs['allow_null'])
        self.assertFalse(field_kwargs['required'])
        self.assertEqual(field_kwargs['max_length'], 50)
        self.assertEqual(
            field_kwargs['model_field'],
            self.TestGetFieldKwargsModel.address
        )

    def test_get_field_kwargs_for_unique_and_validated_field(self):
        field_kwargs = get_field_kwargs(
            'email', self.TestGetFieldKwargsModel.email,
            self.TestGetFieldKwargsModel
        )

        self.assertEqual(
            set(field_kwargs.keys()),
            set([
                'model_field', 'required', 'allow_blank', 'allow_null',
                'validators', 'max_length'
            ])
        )
        self.assertTrue(field_kwargs['allow_blank'])
        self.assertTrue(field_kwargs['allow_null'])
        self.assertFalse(field_kwargs['required'])
        self.assertEqual(field_kwargs['max_length'], 50)
        self.assertEqual(
            field_kwargs['model_field'],
            self.TestGetFieldKwargsModel.email
        )
        self.assertIn('validators', field_kwargs.keys())

    def test_get_field_kwargs_for_enum_field(self):
        field_kwargs = get_field_kwargs(
            'gender', self.TestGetFieldKwargsModel.gender,
            self.TestGetFieldKwargsModel
        )

        self.assertEqual(
            set(field_kwargs.keys()),
            set([
                'model_field', 'required', 'allow_blank', 'allow_null',
                'choices'
            ])
        )
        self.assertTrue(field_kwargs['allow_blank'])
        self.assertTrue(field_kwargs['allow_null'])
        self.assertFalse(field_kwargs['required'])
        self.assertEqual(
            field_kwargs['model_field'],
            self.TestGetFieldKwargsModel.gender
        )
        self.assertEqual(field_kwargs['choices'], ('male', 'female'))


class TestGetRelationKwargs(unittest.TestCase):

    class FakeProductModel(object):
        __tablename__ = 'product'
        id = FakeModelField('id', Column(Integer))
        name = FakeModelField('name', Column(String(50)))
        orders = FakeModelField(
            'orders', Column(ForeignKey('m2m_product_order.id'))
        )

    class FakeOrderModel(object):
        __tablename__ = 'order'
        id = FakeModelField('id', Column(Integer))
        comment = FakeModelField('comment', Column(String(50)))
        product = FakeModelField(
            'products', Column(ForeignKey('m2m_product_order.id'))
        )

    class FakeM2MProductOrderModel(object):
        __tablename__ = 'm2m_product_order'
        id = FakeModelField('id', Column(Integer))
        order_id = FakeModelField(
            'order_id', Column(ForeignKey('order.id'))
        )
        product_id = FakeModelField(
            'product_id', Column(ForeignKey('product.id'))
        )

    def test_get_relation_kwargs_for_foreign_key(self):
        relation_info = RelationInfo(
            model_field=self.FakeM2MProductOrderModel.product_id,
            related_model=self.FakeProductModel,
            to_many=False,
            to_field=self.FakeProductModel.id.field,
            has_through_model=False
        )
        self.assertEqual(
            get_relation_kwargs('product_id', relation_info),
            {
                'label': 'Product_id',
                'queryset': self.FakeProductModel,
                'to_field': self.FakeProductModel.id.field,
                'view_name': 'product-detail'
            }
        )

    def test_get_relation_kwargs_for_m2m_field(self):
        relation_info = RelationInfo(
            model_field=self.FakeProductModel.orders,
            related_model=self.FakeProductModel,
            to_many=True,
            to_field=self.FakeM2MProductOrderModel.order_id.field,
            has_through_model=True
        )
        self.assertEqual(
            get_relation_kwargs('orders', relation_info),
            {
                'many': True, 'read_only': True,
                'to_field': self.FakeM2MProductOrderModel.order_id.field,
                'view_name': 'product-detail'
            }
        )


class TestGetNestedRelationKwargs(unittest.TestCase):

    class FakeUserModel(object):
        __tablename__ = 'user'
        id = int
        name = str
        addresses = list
        birthday_place = int

    class FakeAddressModel(object):
        __tablename__ = 'address'
        id = int
        city = str

    def test_get_nested_relation_kwargs_default(self):
        relation_info = RelationInfo(
            model_field=Column('birthday_place', Integer),
            related_model=self.FakeUserModel,
            to_many=False,
            to_field=Column('address', Integer),
            has_through_model=False
        )
        self.assertEqual(
            get_nested_relation_kwargs(relation_info),
            {'read_only': True}
        )

    def test_get_nested_relation_kwargs_for_list_field(self):
        relation_info = RelationInfo(
            model_field=Column('addresses', Integer),
            related_model=self.FakeUserModel,
            to_many=True,
            to_field=Column('id', ForeignKey('FakeAddressModel.id')),
            has_through_model=True
        )
        self.assertEqual(
            get_nested_relation_kwargs(relation_info),
            {'read_only': True, 'many': True}
        )
