# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.auth.user.utils import generate_password_hash, \
    convert_db_row_to_dict, construct_update_sql, USER_MODEL_FIELDS, \
    USER_MODEL_FIELDS_WITHOUT_PK


@pytest.mark.parametrize("password, expected", [
    ('', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    ('123456',
     '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
])
def test_generate_password_hash(password, expected):
    assert generate_password_hash(password) == expected


@pytest.mark.parametrize("row, mapped_fields", [
    ((1, 'admin', '123456', 'test', 'user', 0, 0, 1, 1), USER_MODEL_FIELDS),
    (('admin', '123456', '', '', 0, 0, 1, 1), USER_MODEL_FIELDS_WITHOUT_PK),
])
def test_convert_db_row_to_dict(row, mapped_fields):
    user_data = convert_db_row_to_dict(row, mapped_fields)
    if mapped_fields == USER_MODEL_FIELDS:
        assert user_data['id'] == row[0]
        row = row[1:]
    assert user_data['username'] == row[0]
    assert user_data['password'] == row[1]
    assert user_data['first_name'] == row[2]
    assert user_data['last_name'] == row[3]
    assert user_data['is_superuser'] == row[4]
    assert user_data['is_staff'] == row[5]
    assert user_data['is_user'] == row[6]
    assert user_data['is_active'] == row[7]


@pytest.mark.parametrize("updated_fields", [
    ({'is_superuser': True, 'is_user': False}),
    ({'is_user': False}),
    ({}),
])
def test_construct_update_sql(updated_fields):
    update_query, query_args = construct_update_sql(**updated_fields)
    assert len(updated_fields) == len(query_args)
