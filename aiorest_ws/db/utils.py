# -*- coding: utf-8 -*-
"""
    Functions for processing data from raw SQL queries.
"""
__all__ = ('convert_db_row_to_dict', )


def convert_db_row_to_dict(row, mapped_fields):
    """Convert row of database to dictionary.

    :param row: row of database.
    :param mapped_fields: list of tuple, which means field names.
    """
    data = {}
    for field, value in zip(mapped_fields, row):
        data[field] = value
    return data
