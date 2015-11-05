# -*- coding: utf-8 -*-
"""
    Default settings for configuration behaviour of aiorest-ws framework.
"""

# -----------------------------------------------
#  Basic settings
# -----------------------------------------------
# Default datetime input and output formats
ISO_8601 = 'iso-8601'

# Encoding charset for string, files, etc.
DEFAULT_ENCODING = 'utf-8'

# -----------------------------------------------
#  Database
# -----------------------------------------------
# This dictionary very useful, cause we can customize it and set required
# drivers, paths, credentials, for every user database
DATABASES = {}

# -----------------------------------------------
#  Middleware
# -----------------------------------------------
# List of middleware classes, which assigned for the main router. All
# middlewares will be used in the order of enumeration. Keep in mind, when
# use this feature.
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
