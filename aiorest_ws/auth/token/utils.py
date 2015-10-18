# -*- coding: utf-8 -*-
"""
    Functions and constants, which can be used for work with Token models.
"""

SQL_CREATE_TOKEN_TABLE = """
    CREATE TABLE IF NOT EXISTS aiorest_auth_token
    (id INTEGER PRIMARY KEY NOT NULL,
     name CHAR(64) NOT NULL, -- name of key (admin, api, etc.)
     token TEXT NOT NULL,
     created DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
     expired DATETIME DEFAULT NULL -- for some tokens it doesn't necessary
    );
"""
SQL_TOKEN_GET = """
    SELECT `id`, `name`, `token`, `created`, `expired`, `user_id`
    FROM aiorest_auth_token
    WHERE token=?;
"""
SQL_TOKEN_GET_BY_TOKEN_USERNAME = """
    SELECT aiorest_auth_token.id, `name`, `token`, `created`,
    `expired`, `user_id`
    FROM aiorest_auth_token
    INNER JOIN aiorest_auth_user
    ON aiorest_auth_token.user_id=aiorest_auth_user.id
    WHERE name=? AND username=?;
"""
SQL_TOKEN_ADD = """
    INSERT INTO aiorest_auth_token (`name`, `token`, `expired`, `user_id`)
    VALUES (?, ?, ?, ?);
"""
TOKEN_MODEL_FIELDS = ('id', 'name', 'token', 'created', 'expired', 'user_id')
