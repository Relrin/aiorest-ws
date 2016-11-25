# -*- coding: utf-8 -*-
"""
Field entities, implemented for support Django ORM.

Every class, represented here, is associated with one certain field type of
table relatively to Django ORM. Each of them field also used later for
serializing/deserializing object of ORM.
"""
import datetime
import re
import uuid

from aiorest_ws.conf import settings
from aiorest_ws.db.orm import fields
from aiorest_ws.db.orm.django.compat import get_remote_field, \
    value_from_object
from aiorest_ws.db.orm.fields import empty
from aiorest_ws.db.orm.validators import MaxLengthValidator
from aiorest_ws.utils.date.dateparse import parse_duration

from django.forms import FilePathField as DjangoFilePathField
from django.forms import ImageField as DjangoImageField
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator, RegexValidator, \
    URLValidator, ip_address_validators
from django.utils import six
from django.utils.duration import duration_string
from django.utils.encoding import is_protected_type
from django.utils.ipv6 import clean_ipv6_address

__all__ = (
    'IntegerField', 'BooleanField', 'CharField', 'ChoiceField',
    'MultipleChoiceField', 'FloatField', 'NullBooleanField', 'DecimalField',
    'TimeField', 'DateField', 'DateTimeField', 'DurationField', 'ListField',
    'DictField', 'HStoreField', 'JSONField', 'ModelField', 'ReadOnlyField',
    'SerializerMethodField', 'EmailField', 'RegexField', 'SlugField',
    'URLField', 'UUIDField', 'IPAddressField', 'FilePathField', 'FileField',
    'ImageField', 'CreateOnlyDefault'
)


class IntegerField(fields.IntegerField):
    pass


class BooleanField(fields.BooleanField):
    pass


class CharField(fields.CharField):
    pass


class ChoiceField(fields.ChoiceField):
    pass


class MultipleChoiceField(ChoiceField):
    default_error_messages = {
        'invalid_choice': u'"{input}" is not a valid choice.',
        'not_a_list': u'Expected a list of items but got type "{input_type}".',
        'empty': u'This selection may not be empty.'
    }

    def __init__(self, *args, **kwargs):
        self.allow_empty = kwargs.pop('allow_empty', True)
        super(MultipleChoiceField, self).__init__(*args, **kwargs)

    def get_value(self, dictionary):
        if self.field_name not in dictionary:
            if getattr(self.root, 'partial', False):
                return empty
        return dictionary.get(self.field_name, empty)

    def to_internal_value(self, data):
        if isinstance(data, type('')) or not hasattr(data, '__iter__'):
            self.raise_error('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            self.raise_error('empty')

        return {
            super(MultipleChoiceField, self).to_internal_value(item)
            for item in data
        }

    def to_representation(self, value):
        return {
            self.choice_strings_to_values.get(str(item), item)
            for item in value
        }


class FloatField(fields.FloatField):
    pass


class NullBooleanField(fields.NullBooleanField):
    pass


class DecimalField(fields.DecimalField):
    pass


class TimeField(fields.TimeField):
    pass


class DateField(fields.DateField):
    pass


class DateTimeField(fields.DateTimeField):
    pass


class DurationField(fields.AbstractField):
    default_error_messages = {
        'invalid': u"Duration has wrong format. Use one of these formats "
                   u"instead: {format}.",
    }

    def to_internal_value(self, value):
        if isinstance(value, datetime.timedelta):
            return value
        parsed = parse_duration(str(value))
        if parsed is not None:
            return parsed
        self.raise_error('invalid', format='[DD] [HH:[MM:]]ss[.uuuuuu]')

    def to_representation(self, value):
        return duration_string(value)


class ListField(fields.ListField):
    pass


class DictField(fields.DictField):
    pass


class HStoreField(fields.HStoreField):
    pass


class JSONField(fields.JSONField):
    pass


class ModelField(fields.ModelField):
    default_error_messages = {
        'max_length': u'Ensure this field has no more than {max_length} '
                      u'characters.'
    }

    def __init__(self, model_field, **kwargs):
        # The `max_length` option is supported by Django's base `Field` class,
        # so we'd better support it here
        max_length = kwargs.pop('max_length', None)
        super(ModelField, self).__init__(model_field, **kwargs)
        if max_length is not None:
            message = self.error_messages['max_length'].format(max_length=max_length)  # NOQA
            self.validators.append(MaxLengthValidator(max_length, message=message))  # NOQA

    def to_internal_value(self, data):
        rel = get_remote_field(self.model_field, default=None)
        if rel is not None:
            return rel.to._meta.get_field(rel.field_name).to_python(data)
        return self.model_field.to_python(data)

    def to_representation(self, obj):
        value = value_from_object(self.model_field, obj)
        if is_protected_type(value):
            return value
        return self.model_field.value_to_string(obj)


class ReadOnlyField(fields.ReadOnlyField):
    pass


class SerializerMethodField(fields.SerializerMethodField):
    pass


class CreateOnlyDefault(fields.CreateOnlyDefault):
    pass


class EmailField(CharField):
    default_error_messages = {
        "invalid": u"Enter a valid email address."
    }

    def __init__(self, **kwargs):
        super(EmailField, self).__init__(**kwargs)
        validator = EmailValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)


class RegexField(CharField):
    default_error_messages = {
        'invalid': u"This value does not match the required pattern."
    }

    def __init__(self, regex, **kwargs):
        super(RegexField, self).__init__(**kwargs)
        validator = RegexValidator(
            regex, message=self.error_messages['invalid']
        )
        self.validators.append(validator)


class SlugField(CharField):
    default_error_messages = {
        'invalid': u'Enter a valid "slug" consisting of letters, numbers, '
                   u'underscores or hyphens.'
    }

    def __init__(self, **kwargs):
        super(SlugField, self).__init__(**kwargs)
        slug_regex = re.compile(r'^[-a-zA-Z0-9_]+$')
        validator = RegexValidator(
            slug_regex, message=self.error_messages['invalid']
        )
        self.validators.append(validator)


class URLField(CharField):
    default_error_messages = {
        'invalid': u"Enter a valid URL."
    }

    def __init__(self, **kwargs):
        super(URLField, self).__init__(**kwargs)
        validator = URLValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)


class UUIDField(fields.AbstractField):
    valid_formats = ('hex_verbose', 'hex', 'int', 'urn')

    default_error_messages = {
        'invalid': u'"{value}" is not a valid UUID.'
    }

    def __init__(self, **kwargs):
        self.uuid_format = kwargs.pop('format', 'hex_verbose')
        if self.uuid_format not in self.valid_formats:
            raise ValueError(
                'Invalid format for uuid representation. '
                'Must be one of "{0}"'.format('", "'.join(self.valid_formats))
            )
        super(UUIDField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, uuid.UUID):
            try:
                if isinstance(data, int):
                    return uuid.UUID(int=data)
                elif isinstance(data, str):
                    return uuid.UUID(hex=data)
                else:
                    self.raise_error('invalid', value=data)
            except ValueError:
                self.raise_error('invalid', value=data)
        return data

    def to_representation(self, value):
        if self.uuid_format == 'hex_verbose':
            return str(value)
        else:
            return getattr(value, self.uuid_format)


class IPAddressField(CharField):
    """Support both IPAddressField and GenericIPAddressField"""

    default_error_messages = {
        'invalid': u"Enter a valid IPv4 or IPv6 address."
    }

    def __init__(self, protocol='both', **kwargs):
        self.protocol = protocol.lower()
        self.unpack_ipv4 = (self.protocol == 'both')
        super(IPAddressField, self).__init__(**kwargs)
        validators, error_message = ip_address_validators(protocol, self.unpack_ipv4)  # NOQA
        self.validators.extend(validators)

    def to_internal_value(self, data):
        if not isinstance(data, six.string_types):
            self.raise_error('invalid', value=data)

        if ':' in data:
            try:
                if self.protocol in ('both', 'ipv6'):
                    return clean_ipv6_address(data, self.unpack_ipv4)
            except DjangoValidationError:
                self.raise_error('invalid', value=data)

        return super(IPAddressField, self).to_internal_value(data)


class FilePathField(ChoiceField):
    default_error_messages = {
        'invalid_choice': u'"{input}" is not a valid path choice.'
    }

    def __init__(self, path, match=None, recursive=False, allow_files=True,
                 allow_folders=False, required=None, **kwargs):
        # Defer to Django's FilePathField implementation to get the
        # valid set of choices
        field = DjangoFilePathField(
            path, match=match, recursive=recursive, allow_files=allow_files,
            allow_folders=allow_folders, required=required
        )
        kwargs['choices'] = field.choices
        super(FilePathField, self).__init__(**kwargs)


class FileField(fields.AbstractField):
    default_error_messages = {
        'required': u'No file was submitted.',
        'invalid': u'The submitted data was not a file. Check the encoding '
                   u'type on the form.',
        'no_name': u'No filename could be determined.',
        'empty': u'The submitted file is empty.',
        'max_length': u'Ensure this filename has at most {max_length} '
                      u'characters (it has {length}).',
    }

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        self.allow_empty_file = kwargs.pop('allow_empty_file', False)
        if 'use_url' in kwargs:
            self.use_url = kwargs.pop('use_url')
        super(FileField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            # `UploadedFile` objects should have name and size attributes
            file_name = data.name
            file_size = data.size
        except AttributeError:
            self.raise_error('invalid')

        if not file_name:
            self.raise_error('no_name')
        if not self.allow_empty_file and not file_size:
            self.raise_error('empty')
        if self.max_length and len(file_name) > self.max_length:
            self.raise_error(
                'max_length', max_length=self.max_length, length=len(file_name)
            )

        return data

    def to_representation(self, value):
        use_url = getattr(self, 'use_url', settings.UPLOADED_FILES_USE_URL)

        if not value:
            return None

        if use_url:
            if not getattr(value, 'url', None):
                # If the file has not been saved it may not have a URL
                return None
            url = value.url
            return url
        return value.name


class ImageField(FileField):
    default_error_messages = {
        'invalid_image': u'Upload a valid image. The file you uploaded was '
                         u'either not an image or a corrupted image.'
    }

    def __init__(self, *args, **kwargs):
        self._DjangoImageField = kwargs.pop(
            '_DjangoImageField', DjangoImageField
        )
        super(ImageField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # Image validation is a bit grungy, so we'll just outright
        # defer to Django's implementation so we don't need to
        # consider it, or treat PIL as a test dependency
        file_object = super(ImageField, self).to_internal_value(data)
        django_field = self._DjangoImageField()
        django_field.error_messages = self.error_messages
        django_field.to_python(file_object)
        return file_object
