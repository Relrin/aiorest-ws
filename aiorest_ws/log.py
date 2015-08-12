# -*- coding: utf-8 -*-
"""
    Logging tool for aiorest-ws framework.
"""
__all__ = ('DEFAULT_LOGGING_SETTINGS', 'logger', )

import logging
import logging.config


DEFAULT_LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] [%(levelname)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format' : "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] "
                       "%(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
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


logging.config.dictConfig(DEFAULT_LOGGING_SETTINGS)
logger = logging.getLogger('aiorest-ws')
