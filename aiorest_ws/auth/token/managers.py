# -*- coding: utf-8 -*-
"""
    Token managers, proposed for generating/validating tokens.
"""
__all__ = ('JSONWebTokenManager', )

import json
import time

import hashlib
import hmac
from base64 import b64encode, b64decode
from aiorest_ws.auth.token.exceptions import ParsingTokenException, \
    InvalidSignatureException, TokenNotBeforeException, TokenExpiredException


class JSONWebTokenManager(object):
    """Default JWT manager for aiorest-ws library.

    This manager written under inspire of the articles below:
        https://scotch.io/tutorials/the-anatomy-of-a-json-web-token
        https://en.wikipedia.org/wiki/JSON_Web_Token
    """
    HASH_FUNCTIONS = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512
    }

    HASH_ALGORITHM = "HS256"
    SECRET_KEY = "secret_key"
    RESERVED_NAMES = ('iss', 'sub', 'aud', 'exp', 'nbf', 'ait', 'jti')

    def _encode_data(self, data):
        data = json.dumps(data).encode('utf-8')
        return b64encode(data).decode('utf-8')

    def _decode_data(self, data):
        data = b64decode(data).decode('utf-8')
        return json.loads(data)

    def _generate_header(self):
        header = self._encode_data({"typ": "JWT", "alg": self.HASH_ALGORITHM})
        return header

    def _generate_payload(self, data):
        payload = self._encode_data(data)
        return payload

    def _generate_signature(self, header, payload):
        key = self.SECRET_KEY.encode('utf-8')
        data = "{0}.{1}".format(header, payload).encode('utf-8')
        hash_func = self.HASH_FUNCTIONS[self.HASH_ALGORITHM]

        hmac_obj = hmac.new(key, data, digestmod=hash_func)
        digest = hmac_obj.hexdigest().encode('utf-8')
        signature = b64encode(digest).decode('utf-8')
        return signature

    def _used_reserved_keys(self, data):
        return set(data.keys()) & set(self.RESERVED_NAMES)

    def _check_token_timestamp(self, token, key):
        token_timestamp = token.get(key, None)
        if token_timestamp:
            return time.time() > float(token_timestamp)
        return False

    def _is_valid_signature(self, header, payload, token_signature):
        server_signature = self._generate_signature(header, payload)
        if token_signature != server_signature:
            return False
        return True

    def _is_not_be_accepted(self, token):
        if self._check_token_timestamp(token, 'nbf'):
            return True
        return False

    def _is_expired_token(self, token):
        if self._check_token_timestamp(token, 'exp'):
            return True
        return False

    def set_reserved_attribute(self, token, attribute, value):
        if attribute in self.RESERVED_NAMES and value:
            # if user define "exp" argument, than necessary calculate timestamp
            if attribute == 'exp':
                current_time_in_seconds = int(time.time())
                expired_timestamp = current_time_in_seconds + value
                token.update({'exp': expired_timestamp})
            # for any other JSON Web Token attributes just set value
            else:
                token[attribute] = value

    def generate(self, data, *args, **kwargs):
        defined_attrs = self._used_reserved_keys(kwargs)
        for key in defined_attrs:
            self.set_reserved_attribute(data, key, kwargs[key])

        header = self._generate_header()
        payload = self._generate_payload(data)
        signature = self._generate_signature(header, payload)
        token = "{0}.{1}.{2}".format(header, payload, signature)
        return token

    def verify(self, token):
        try:
            header, payload, signature = token.split('.')
        except:
            raise ParsingTokenException()

        if not self._is_valid_signature(header, payload, signature):
            raise InvalidSignatureException()

        token_data = self._decode_data(payload)

        if self._is_not_be_accepted(token_data):
            raise TokenNotBeforeException()

        if self._is_expired_token(token_data):
            raise TokenExpiredException()

        return token_data
