# -*- coding: utf-8 -*-
"""
    Token managers, proposed for generating/validating tokens.
"""
import hashlib
import hmac
import json
import time

from base64 import b64encode, b64decode
from aiorest_ws.auth.token.exceptions import ParsingTokenException, \
    InvalidSignatureException, TokenNotBeforeException, TokenExpiredException

__all__ = ('JSONWebTokenManager', )


class JSONWebTokenManager(object):
    """JSON Web Token (or shortly JWT) manager for the aiorest-ws library.

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
        """Encode passed data to base64.

        :param data: dictionary object.
        """
        data = json.dumps(data).encode('utf-8')
        return b64encode(data).decode('utf-8')

    def _decode_data(self, data):
        """Decode passed data to JSON.

        :param data: dictionary object.
        """
        data = b64decode(data).decode('utf-8')
        return json.loads(data)

    def _generate_header(self):
        """Generate header for the token."""
        header = self._encode_data({"typ": "JWT", "alg": self.HASH_ALGORITHM})
        return header

    def _generate_payload(self, data):
        """Generate payload for the token.

        :param data: dictionary object.
        """
        payload = self._encode_data(data)
        return payload

    def _generate_signature(self, header, payload):
        """Generate signature for the token.

        :param header: token header.
        :param payload: token payload.
        """
        key = self.SECRET_KEY.encode('utf-8')
        data = "{0}.{1}".format(header, payload).encode('utf-8')
        hash_func = self.HASH_FUNCTIONS[self.HASH_ALGORITHM]

        hmac_obj = hmac.new(key, data, digestmod=hash_func)
        digest = hmac_obj.hexdigest().encode('utf-8')
        signature = b64encode(digest).decode('utf-8')
        return signature

    def _used_reserved_keys(self, data):
        """Get set of used reserved keys."""
        return set(data.keys()) & set(self.RESERVED_NAMES)

    def _check_token_timestamp(self, token, key):
        """Check token timestamp.

        :param token: dictionary object.
        :param key: field of token as a string.
        """
        token_timestamp = token.get(key, None)
        if token_timestamp:
            return time.time() > float(token_timestamp)
        return False

    def _is_invalid_signature(self, header, payload, token_signature):
        """Validate token by signature.

        :param header: header of token.
        :param payload: payload of token.
        :param token_signature: signature of token as a string.
        """
        server_signature = self._generate_signature(header, payload)
        if token_signature != server_signature:
            return True
        return False

    def _is_not_be_accepted(self, token):
        """Check for token is can be accepted or not.

        :param token: dictionary object.
        """
        return self._check_token_timestamp(token, 'nbf')

    def _is_expired_token(self, token):
        """Check for token expired or not.

        :param token: dictionary object.
        """
        return self._check_token_timestamp(token, 'exp')

    def set_reserved_attribute(self, token, attribute, value):
        """Set for token reserved attribute.

        :param token: dictionary object.
        :param attribute: updated reserved field of JSON Web Token.
        :param value: initialized value.
        """
        if attribute in self.RESERVED_NAMES and value:
            # if user define "exp" or "nbf" argument, than calculate timestamp
            if attribute in ['exp', 'nbf']:
                current_time_in_seconds = int(time.time())
                expired_timestamp = current_time_in_seconds + value
                token.update({attribute: expired_timestamp})
            # for any other JSON Web Token attributes just set value
            else:
                token[attribute] = value

    def generate(self, data, *args, **kwargs):
        """Generate token.

        :param data: dictionary, which will be stored inside token.
        :param args: tuple of arguments.
        :param kwargs: dictionary of reserved JSON Web Token fields, which
                       shall be overridden for token.
        """
        defined_attrs = self._used_reserved_keys(kwargs)
        for key in defined_attrs:
            self.set_reserved_attribute(data, key, kwargs[key])

        header = self._generate_header()
        payload = self._generate_payload(data)
        signature = self._generate_signature(header, payload)
        token = "{0}.{1}.{2}".format(header, payload, signature)
        return token

    def verify(self, token):
        """Verify passed token.

        :param token: validated token (as `header.payload.signature`).
        """
        try:
            header, payload, signature = token.split('.')
        except:
            raise ParsingTokenException()

        if self._is_invalid_signature(header, payload, signature):
            raise InvalidSignatureException()

        token_data = self._decode_data(payload)

        if self._is_not_be_accepted(token_data):
            raise TokenNotBeforeException()

        if self._is_expired_token(token_data):
            raise TokenExpiredException()

        return token_data
