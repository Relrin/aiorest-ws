# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.auth.user.utils import generate_password_hash


@pytest.mark.parametrize("password, expected", [
    ('', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    ('123456',
     '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
])
def test_generate_password_hash(password, expected):
    assert generate_password_hash(password) == expected
