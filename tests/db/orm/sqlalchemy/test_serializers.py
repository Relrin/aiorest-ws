# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import ImproperlyConfigured
from aiorest_ws.db.orm.validators import BaseValidator
from aiorest_ws.db.orm.abstract import empty
from aiorest_ws.db.orm.exceptions import ValidationError
from aiorest_ws.db.orm.sqlalchemy.relations import ManyRelatedField, \
    HyperlinkedIdentityField
from aiorest_ws.db.orm.serializers import Serializer
from aiorest_ws.db.orm.sqlalchemy.serializers import ListSerializer, \
    ModelSerializer, HyperlinkedModelSerializer, get_validation_error_detail
from aiorest_ws.db.orm.sqlalchemy import fields, serializers
from aiorest_ws.test.utils import override_settings

from tests.fixtures.sqlalchemy import SESSION, ENGINE

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Query


Base = declarative_base()


class TestGetValidationErrorDetailFunction(unittest.TestCase):

    def test_function_raises_assert_error_for_invalid_exception_type(self):
        exc = ValueError()
        self.assertRaises(AssertionError, get_validation_error_detail, exc)

    def test_function_returns_dict_for_assertion_error(self):
        message = '@ must be in email address'
        exc = AssertionError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertEqual(detail['non_field_errors'][0], message)

    def test_function_returns_dict_for_exception_with_message_as_dict(self):
        message = {'email': '@ must be in email address'}
        exc = ValidationError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('email', detail.keys())
        self.assertEqual(detail['email'][0], message['email'])

    def test_function_returns_dict_for_exception_with_message_as_list(self):
        message = ['@ must be in email address', ]
        exc = ValidationError(message)
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertIsInstance(detail['non_field_errors'], list)
        self.assertEqual(len(detail['non_field_errors']), 1)
        self.assertEqual(detail['non_field_errors'], message)

    def test_function_returns_dict_for_exception_with_message_as_string(self):
        message = '@ must be in email address'
        exc = ValidationError('expected message')
        exc.detail = message  # someone patched object
        detail = get_validation_error_detail(exc)

        self.assertIsInstance(detail, dict)
        self.assertIn('non_field_errors', detail.keys())
        self.assertIsInstance(detail['non_field_errors'], list)
        self.assertEqual(len(detail['non_field_errors']), 1)
        self.assertEqual(detail['non_field_errors'][0], message)


class TestListSerializer(unittest.TestCase):

    class FakeSerializer(Serializer):
        default_list_serializer = ListSerializer
        pk = fields.IntegerField()

        def run_validation(self, data=empty):
            return self.to_internal_value(data)

    def test_run_validation_returns_value(self):
        instance = self.FakeSerializer(many=True)
        self.assertEqual(
            instance.run_validation([{'pk': 1}, ]),
            [{'pk': 1}, ]
        )

    def test_run_validation_returns_value_for_empty_value(self):
        instance = self.FakeSerializer(many=True, allow_null=True)
        self.assertEqual(instance.run_validation(None), None)

    def test_run_validation_raises_validation_error(self):

        class NegativePkValidator(BaseValidator):

            def __call__(self, data):
                for obj in data:
                    if obj['pk'] < 0:
                        raise ValidationError("PKs can't be negative.")

        class CustomListSerializer(ListSerializer):
            validators = [NegativePkValidator(), ]

        class InvalidFakeSerializer(self.FakeSerializer):

            class Meta:
                list_serializer_class = CustomListSerializer

        instance = InvalidFakeSerializer(many=True)
        self.assertRaises(
            ValidationError,
            instance.run_validation,
            [{'pk': -1}, ]
        )

    def test_run_validation_raises_validation_error_for_value_assert(self):

        class CustomListSerializer(ListSerializer):

            def validate(self, data):
                return None  # suppose, that something happens wrong

        class InvalidFakeSerializer(self.FakeSerializer):
            class Meta:
                list_serializer_class = CustomListSerializer

        instance = InvalidFakeSerializer(many=True)
        self.assertRaises(
            ValidationError,
            instance.run_validation,
            [{'pk': 1}, ]
        )


class TestModelSerializer(unittest.TestCase):

    class TestModelSerializerUserModel(Base):
        __tablename__ = 'test_model_serializer_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        gender = Column(Enum(*('male', 'female')), nullable=True)
        addresses = relationship(
            "TestModelSerializerAddressModel", back_populates="user"
        )

        @property
        def user_info(self):
            return "<User ({}, {})>".format(self.name, self.gender)

    class TestModelSerializerAddressModel(Base):
        __tablename__ = 'test_model_serializer_addresses_model'
        id = Column(Integer, primary_key=True)
        email = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey('test_model_serializer_users_model.id')
        )
        user = relationship(
            "TestModelSerializerUserModel", back_populates="addresses"
        )

    tables = [
        TestModelSerializerUserModel.__table__,
        TestModelSerializerAddressModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestModelSerializer, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestModelSerializer, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def create_table(self, table):
        Base.metadata.create_all(ENGINE, tables=[table, ])

    def remove_table(self, table):
        Base.metadata.remove(table)

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_create(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel
                exclude = ('addresses', )

        data = {'name': 'default_admin', 'gender': 'male'}
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.data)
        session = SESSION()
        user = session\
            .query(self.TestModelSerializerUserModel)\
            .filter(self.TestModelSerializerUserModel.name == data['name'])\
            .first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, self.TestModelSerializerUserModel)
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.gender, data['gender'])

        session.delete(user)
        session.commit()
        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_create_with_relation_data(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        session = SESSION()
        address = self.TestModelSerializerAddressModel(email='test@email.com')
        session.add(address)
        session.commit()
        data = {
            'name': 'admin_with_email',
            'addresses': [{'id': address.id}, ],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.create(instance.validated_data)
        user = session \
            .query(self.TestModelSerializerUserModel) \
            .filter(self.TestModelSerializerUserModel.name == data['name']) \
            .first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, self.TestModelSerializerUserModel)
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.gender, data['gender'])
        self.assertEqual(user.addresses[0].id, address.id)

        session.delete(user)
        session.delete(address)
        session.commit()
        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_create_raise_type_error(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        session = SESSION()
        address = self.TestModelSerializerAddressModel(email='test@email.com')
        session.add(address)
        session.commit()
        data = {
            'name': 'admin_with_email',
            'addresses': [{'id': address.id}, ],
            'gender': 'male'

        }
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)

        self.assertRaises(TypeError, instance.create, data)

        session.delete(address)
        session.commit()
        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_update(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel
                exclude = ('addresses', )

        data = {'name': 'admin_for_update_v1', 'gender': 'male'}
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.save()
        session = SESSION()
        user = session \
            .query(self.TestModelSerializerUserModel) \
            .filter(self.TestModelSerializerUserModel.name == data['name']) \
            .first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, self.TestModelSerializerUserModel)
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.gender, data['gender'])

        data = {'name': 'admin_for_update_v2', 'gender': 'female'}
        instance = UserSerializer(user, data=data, partial=True)
        instance.is_valid(raise_exception=True)
        updated_user = instance.save()

        self.assertIsNotNone(updated_user)
        self.assertIsInstance(updated_user, self.TestModelSerializerUserModel)
        self.assertEqual(updated_user.name, data['name'])
        self.assertEqual(updated_user.gender, data['gender'])

        session.delete(user)
        session.commit()
        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_update_with_relations(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        session = SESSION()
        address = self.TestModelSerializerAddressModel(email='test@email.com')
        session.add(address)
        session.commit()
        data = {
            'name': 'admin_for_update_v1',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.save()
        user = session \
            .query(self.TestModelSerializerUserModel) \
            .filter(self.TestModelSerializerUserModel.name == data['name']) \
            .first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, self.TestModelSerializerUserModel)
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.gender, data['gender'])

        data = {
            'name': 'admin_for_update_v2',
            'addresses': [{'id': address.id}, ],
            'gender': 'male'
        }
        instance = UserSerializer(user, data=data, partial=True)
        instance.is_valid(raise_exception=True)
        updated_user = instance.save()

        self.assertIsNotNone(updated_user)
        self.assertIsInstance(updated_user, self.TestModelSerializerUserModel)
        self.assertEqual(updated_user.name, data['name'])
        self.assertEqual(updated_user.gender, data['gender'])
        self.assertEqual(len(updated_user.addresses), 1)
        self.assertEqual(updated_user.addresses[0].id, address.id)

        session.delete(address)
        session.delete(user)
        session.commit()
        session.close()

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_update_raises_validate_error_for_object_does_not_exist(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        session = SESSION()
        address = self.TestModelSerializerAddressModel(email='test@email.com')
        session.add(address)
        session.commit()
        data = {
            'name': 'admin_for_update_v1',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)
        instance.is_valid(raise_exception=True)
        instance.save()
        user = session \
            .query(self.TestModelSerializerUserModel) \
            .filter(self.TestModelSerializerUserModel.name == data['name']) \
            .first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, self.TestModelSerializerUserModel)
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.gender, data['gender'])

        data = {
            'name': 'admin_for_update_v2',
            'addresses': [{'id': address.id}, ],
            'gender': 'male'
        }
        instance = UserSerializer(user, data=data, partial=True)
        instance.is_valid(raise_exception=True)
        session.delete(user)
        session.commit()

        self.assertRaises(ValidationError, instance.save)

        session.delete(address)
        session.commit()
        session.close()

    def test_run_validation(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True,
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data, allow_null=True)

        self.assertEqual(instance.run_validation(data), data)

    def test_run_validation_returns_empty_value(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True
            )

            class Meta:
                model = self.TestModelSerializerUserModel

        instance = UserSerializer(allow_null=True)

        self.assertIsNone(instance.run_validation(None))

    def test_run_validation_raises_error_for_assert(self):

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True,
            )

            class Meta:
                model = self.TestModelSerializerUserModel

            def validate(self, data):
                return None  # suppose, that something happens wrong

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data, allow_null=True)

        self.assertRaises(ValidationError, instance.run_validation, data)

    def test_run_validation_raises_error_for_validation_error(self):

        class AdminNameValidator(BaseValidator):
            def __call__(self, data):
                if data['name'] == 'admin':
                    raise ValidationError("Permission denied.")

        class UserSerializer(ModelSerializer):
            addresses = serializers.PrimaryKeyRelatedField(
                queryset=Query(self.TestModelSerializerAddressModel),
                many=True,
            )

            class Meta:
                model = self.TestModelSerializerUserModel
                validators = [AdminNameValidator(), ]

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data, allow_null=True)

        self.assertRaises(ValidationError, instance.run_validation, data)

    @override_settings(SQLALCHEMY_SESSION=SESSION)
    def test_get_default_field_value(self):

        class TestGetDefaultFieldValueUserModel(Base):
            __tablename__ = 'test_get_default_field_value_users_model'
            id = Column(Integer, primary_key=True)
            name = Column(String(50), default='user')
            fullname = Column(String(50), onupdate='updated fullname')

        class UserSerializer(ModelSerializer):

            class Meta:
                model = TestGetDefaultFieldValueUserModel

        # For example, in real case `_get_default_field_value` method
        # could be called when you specified field as unique
        self.create_table(TestGetDefaultFieldValueUserModel.__table__)

        model = TestGetDefaultFieldValueUserModel
        data = {'name': 'admin', 'fullname': 'test'}
        instance = UserSerializer(data=data)

        self.assertEqual(
            instance._get_default_field_value(model.name),
            model.name.default
        )
        self.assertEqual(
            instance._get_default_field_value(model.fullname),
            model.fullname.onupdate
        )

        self.remove_table(TestGetDefaultFieldValueUserModel.__table__)

    def test_build_relational_field(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        self.assertIsInstance(instance.fields['addresses'], ManyRelatedField)

    def test_build_nested_field(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel
                depth = 1

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        address_serializer = instance.fields['addresses']
        self.assertIsInstance(address_serializer, ModelSerializer)
        self.assertEqual(
            address_serializer.__class__.__name__,
            "NestedSerializer"
        )

    def test_build_property_field(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel
                fields = ('id', 'name', 'user_info')

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        self.assertIsInstance(
            instance.fields['user_info'],
            fields.ReadOnlyField
        )

    def test_build_url_field(self):

        class UserSerializer(HyperlinkedModelSerializer):
            class Meta:
                model = self.TestModelSerializerUserModel
                fields = ('url', 'name', 'addresses')
                extra_kwargs = {'url': {'view_name': 'users'}}

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        url_serializer = instance.fields['url']
        self.assertIsInstance(url_serializer, HyperlinkedIdentityField)
        self.assertEqual(
            url_serializer.__class__.__name__,
            "HyperlinkedIdentityField"
        )

    def test_build_unknown_field(self):

        class UserSerializer(ModelSerializer):

            class Meta:
                model = self.TestModelSerializerUserModel
                fields = ('id', 'name', 'invalid_field')

        data = {
            'name': 'admin_for_update_v1',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        with self.assertRaises(ImproperlyConfigured):
            serializer_fields = instance.fields  # NOQA


class TestHyperlinkModelSerializer(unittest.TestCase):

    class TestHyperlinkModelSerializerUserModel(Base):
        __tablename__ = 'test_hyperlink_model_serializer_users_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        gender = Column(Enum(*('male', 'female')), nullable=True)
        addresses = relationship(
            "TestHyperlinkModelSerializerAddressModel",
            back_populates="user"
        )

    class TestHyperlinkModelSerializerAddressModel(Base):
        __tablename__ = 'test_hyperlink_model_serializer_addresses_model'
        id = Column(Integer, primary_key=True)
        email = Column(String, nullable=False)
        user_id = Column(
            Integer,
            ForeignKey('test_hyperlink_model_serializer_users_model.id')
        )
        user = relationship(
            "TestHyperlinkModelSerializerUserModel",
            back_populates="addresses"
        )

    tables = [
        TestHyperlinkModelSerializerUserModel.__table__,
        TestHyperlinkModelSerializerAddressModel.__table__
    ]

    @classmethod
    def setUpClass(cls):
        super(TestHyperlinkModelSerializer, cls).setUpClass()
        Base.metadata.create_all(ENGINE, tables=cls.tables)

    @classmethod
    def tearDownClass(cls):
        super(TestHyperlinkModelSerializer, cls).tearDownClass()
        for table in cls.tables:
            Base.metadata.remove(table)

    def test_build_nested_field(self):

        class UserSerializer(HyperlinkedModelSerializer):

            class Meta:
                model = self.TestHyperlinkModelSerializerUserModel
                depth = 1
                fields = ('id', 'name', 'addresses')
                extra_kwargs = {'url': {'view_name': 'users'}}

        data = {
            'name': 'admin',
            'addresses': [],
            'gender': 'male'
        }
        instance = UserSerializer(data=data)

        address_serializer = instance.fields['addresses']
        self.assertIsInstance(address_serializer, HyperlinkedModelSerializer)
        self.assertEqual(
            address_serializer.__class__.__name__,
            "NestedSerializer"
        )
