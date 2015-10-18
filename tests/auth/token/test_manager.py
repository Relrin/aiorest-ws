# -*- coding: utf-8 -*-
import hmac
import json
import time
import unittest

from base64 import b64encode, b64decode

from aiorest_ws.auth.token.managers import JSONWebTokenManager
from aiorest_ws.auth.token.exceptions import ParsingTokenException, \
    InvalidSignatureException, TokenNotBeforeException, TokenExpiredException


class JSONWebTokenManagerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.json_manager = JSONWebTokenManager()

    def _generate_token_timestamp(self, delta):
        current_time_in_seconds = int(time.time())
        token_timestamp = current_time_in_seconds + delta
        return token_timestamp

    def test_encode_data(self):
        data = {'key': 'value'}
        utf8_data = json.dumps(data).encode('utf-8')
        encoded_data = b64encode(utf8_data).decode('utf-8')
        self.assertEqual(self.json_manager._encode_data(data), encoded_data)

    def test_decode_data(self):
        encoded_data = 'eyJrZXkiOiAidmFsdWUifQ=='  # {'key': 'value'}
        decoded_data = b64decode(encoded_data).decode('utf-8')
        data = json.loads(decoded_data)
        self.assertEqual(self.json_manager._decode_data(encoded_data), data)

    def test_generate_header(self):
        encoded_header = self.json_manager._encode_data(
            {"typ": "JWT", "alg": self.json_manager.HASH_ALGORITHM}
        )
        self.assertEqual(self.json_manager._generate_header(), encoded_header)

    def test_generate_payload(self):
        data = {'key': 'value'}
        encoded_data = self.json_manager._encode_data(data)
        self.assertEqual(
            self.json_manager._generate_payload(data),
            encoded_data
        )

    def test_generate_signature(self):
        data = {'key': 'value'}
        header = self.json_manager._generate_header()
        payload = self.json_manager._generate_payload(data)

        key = self.json_manager.SECRET_KEY.encode('utf-8')
        data = "{0}.{1}".format(header, payload).encode('utf-8')
        hash_func = self.json_manager.HASH_FUNCTIONS[
            self.json_manager.HASH_ALGORITHM
        ]
        hmac_obj = hmac.new(key, data, digestmod=hash_func)
        digest = hmac_obj.hexdigest().encode('utf-8')
        generated_signature = b64encode(digest).decode('utf-8')

        self.assertEqual(
            self.json_manager._generate_signature(header, payload),
            generated_signature
        )

    def test_used_reserved_keys_1(self):
        user_data = {
            'iss': None,
            'sub': None,
            'aud': None,
            'exp': None,
        }
        self.assertEqual(
            self.json_manager._used_reserved_keys(user_data),
            set(user_data.keys())
        )

    def test_used_reserved_keys_2(self):
        user_data = {'my_field': 'value'}
        self.assertEqual(
            self.json_manager._used_reserved_keys(user_data),
            set({})
        )

    def test_check_token_with_timestamp_lesser_current_time(self):
        token = {'exp': self._generate_token_timestamp(-5)}
        self.assertTrue(self.json_manager._check_token_timestamp(token, 'exp'))

    def test_check_token_with_timestamp_greater_current_time(self):
        token = {'exp': self._generate_token_timestamp(5)}
        self.assertFalse(
            self.json_manager._check_token_timestamp(token, 'exp')
        )

    def test_check_token_without_defined_key(self):
        token = {}
        self.assertFalse(
            self.json_manager._check_token_timestamp(token, 'exp')
        )

    def test_is_invalid_signature_return_true(self):
        data = {'key': 'value'}
        header = self.json_manager._generate_header()
        payload = self.json_manager._generate_payload(data)
        signature = self.json_manager._generate_signature(header, payload)
        signature = '=' + signature[1:]
        self.assertTrue(
            self.json_manager._is_invalid_signature(header, payload, signature)
        )

    def test_is_invalid_signature_return_false(self):
        data = {'key': 'value'}
        header = self.json_manager._generate_header()
        payload = self.json_manager._generate_payload(data)
        signature = self.json_manager._generate_signature(header, payload)
        self.assertFalse(
            self.json_manager._is_invalid_signature(header, payload, signature)
        )

    def test_is_not_be_accepted_return_true(self):
        token = {'nbf': self._generate_token_timestamp(-5)}
        self.assertTrue(self.json_manager._is_not_be_accepted(token))

    def test_is_not_be_accepted_return_false(self):
        token = {'nbf': self._generate_token_timestamp(5)}
        self.assertFalse(self.json_manager._is_not_be_accepted(token))

    def test_is_not_be_accepted_return_false_when_no_nfb_key(self):
        token = {}
        self.assertFalse(self.json_manager._is_not_be_accepted(token))

    def test_is_expired_token_return_true(self):
        token = {'exp': self._generate_token_timestamp(-5)}
        self.assertTrue(self.json_manager._is_expired_token(token))

    def test_is_expired_token_return_false(self):
        token = {'exp': self._generate_token_timestamp(5)}
        self.assertFalse(self.json_manager._is_expired_token(token))

    def test_is_expired_token_return_false_when_no_exp_key(self):
        token = {}
        self.assertFalse(self.json_manager._is_expired_token(token))

    def test_set_reserved_attribute(self):
        token_attributes = {
            'iss': 'test',
            'sub': 'test',
            'aud': 'test',
            'exp': 5,
            'nbf': 5,
            'ait': 'test',
            'jti': 'test',
        }
        token = {}
        for attribute, value in token_attributes.items():
            self.json_manager.set_reserved_attribute(token, attribute, value)
            if attribute in ['exp', 'nbf']:
                timestamp = self._generate_token_timestamp(value)
                self.assertEqual(token[attribute], timestamp)
            else:
                self.assertEqual(token[attribute], value)

    def test_set_reserved_attribute_for_none_reserved_attribute(self):
        token = {}
        self.json_manager.set_reserved_attribute(token, 'test_attr', None)
        self.assertEqual(token, {})

    def test_generate(self):
        test_data = {'key': 'value'}
        self.json_manager.set_reserved_attribute(test_data, 'iss', 'test')
        header = self.json_manager._generate_header()
        payload = self.json_manager._generate_payload(test_data)
        signature = self.json_manager._generate_signature(header, payload)
        token = "{0}.{1}.{2}".format(header, payload, signature)
        test_token_data = {'key': 'value'}
        self.assertEqual(
            self.json_manager.generate(test_token_data, iss='test'),
            token
        )

    def test_verify(self):
        data = {'key': 'value'}
        token = self.json_manager.generate(data)
        self.assertEqual(self.json_manager.verify(token), data)

    def test_raised_parsing_token_exception_in_verify(self):
        data = {'key': 'value'}
        token = self.json_manager.generate(data) + '.'
        self.assertRaises(
            ParsingTokenException,
            self.json_manager.verify, token
        )

    def test_raised_invalid_signature_exception_in_verify(self):
        data = {'key': 'value'}
        token = self.json_manager.generate(data)
        header, payload, signature = token.split('.')
        signature = '=' + signature[1:]
        token = "{0}.{1}.{2}".format(header, payload, signature)
        self.assertRaises(
            InvalidSignatureException,
            self.json_manager.verify, token
        )

    def test_raised_token_not_before_exception_in_verify(self):
        data = {'key': 'value'}
        token = self.json_manager.generate(data, nbf=-5)
        self.assertRaises(
            TokenNotBeforeException,
            self.json_manager.verify, token
        )

    def test_raised_token_expired_exception_in_verify(self):
        data = {'key': 'value'}
        token = self.json_manager.generate(data, exp=-5)
        self.assertRaises(
            TokenExpiredException,
            self.json_manager.verify, token
        )
