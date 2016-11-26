# -*- coding: utf-8 -*-
"""
Default settings for configuration behaviour of aiorest-ws framework.
"""

# -----------------------------------------------
#  Basic settings
# -----------------------------------------------
# Default datetime input and output formats
ISO_8601 = 'iso-8601'
DATE_FORMAT = ISO_8601
DATE_INPUT_FORMATS = (ISO_8601, )

DATETIME_FORMAT = ISO_8601
DATETIME_INPUT_FORMATS = (ISO_8601, )

TIME_FORMAT = ISO_8601
TIME_INPUT_FORMATS = (ISO_8601,)

# Local time zone for this installation. All choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone
TIME_ZONE = 'America/Chicago'

# If you set this to True, Django will use timezone-aware datetimes
USE_TZ = False

# Encoding charset for string, files, etc.
DEFAULT_ENCODING = 'utf-8'

UNICODE_JSON = True
COMPACT_JSON = True
COERCE_DECIMAL_TO_STRING = True
UPLOADED_FILES_USE_URL = True

# -----------------------------------------------
#  Database
# -----------------------------------------------
# This dictionary very useful, cause we can customize it and set required
# drivers, paths, credentials, for every user database
DATABASES = {}
USE_ORM_ENGINE = False

# SQLAlchemy ORM variables
SQLALCHEMY_ENGINE = None
SQLALCHEMY_SESSION = None

# -----------------------------------------------
#  REST configuration
# -----------------------------------------------
REST_CONFIG = {
    # Exception handling
    'NON_FIELD_ERRORS_KEY': 'non_field_errors',

    # Hyperlink settings
    'URL_FIELD_NAME': 'url',
}

# -----------------------------------------------
#  Middleware
# -----------------------------------------------
# List of middleware classes, which assigned for the main router. All
# middlewares will be used in the order of enumeration. Keep in mind, when
# use this feature
MIDDLEWARE_CLASSES = ()

# -----------------------------------------------
# Logging
# -----------------------------------------------
DEFAULT_LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] [%(levelname)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] "
                      "%(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'aiorest-ws': {
            'handlers': ['default', ],
            'level': 'INFO',
            'propagate': False
        },
        'debug': {
            'handlers': ['debug', ],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
