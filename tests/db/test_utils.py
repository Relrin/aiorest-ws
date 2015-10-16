# -*- coding: utf-8 -*-
import pytest

from aiorest_ws.db.utils import convert_db_row_to_dict


@pytest.mark.parametrize("row, mapped_fields", [
    (('some_token', None), ('token', 'value')),
    ((), ()),
])
def test_convert_db_row_to_dict(row, mapped_fields):
    data = convert_db_row_to_dict(row, mapped_fields)

    assert set(row) == set(data.values())
    assert set(mapped_fields) == set(data.keys())


@pytest.mark.parametrize("row, mapped_fields", [
    (('value', None), ()),
    ((), ('field_1', 'field_2'))
])
def test_convert_db_row_to_dict_with_unfilled_data(row, mapped_fields):
    data = convert_db_row_to_dict(row, mapped_fields)

    assert set([]) == set(data.values())
    assert set([]) == set(data.keys())
