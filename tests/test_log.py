# -*- coding: utf-8 -*-
import logging
import unittest

from aiorest_ws.log import configure_logger, DEFAULT_LOGGING_SETTINGS


class TestConfigureLogger(unittest.TestCase):

    def compare_settings(self, logger, settings):
        self.assertEqual(logger.name, 'aiorest-ws')
        self.assertTrue(logger.hasHandlers())

        for user_handler_name in settings['loggers']['aiorest-ws']['handlers']:
            cls = settings['handlers'][user_handler_name]['class']
            cls_name = cls.split('.')[-1]
            formatter = settings['handlers'][user_handler_name]['formatter']
            format = settings['formatters'][formatter]['format']
            datefmt = settings['formatters'][formatter]['datefmt']
            level = settings['handlers'][user_handler_name]['level']

            handlers_cls = [handler.__class__.__name__
                            for handler in logger.handlers]
            index = handlers_cls.index(cls_name)

            obj = logger.handlers[index]
            self.assertEqual(obj.formatter._fmt, format)
            self.assertEqual(obj.formatter.datefmt, datefmt)
            self.assertEqual(obj.level, eval('logging.{0}'.format(level)))

    def test_default_configuration(self):
        configure_logger()
        logger = logging.getLogger('aiorest-ws')
        self.compare_settings(logger, DEFAULT_LOGGING_SETTINGS)

    def test_custom_configuration(self):
        user_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': "[%(asctime)s] [%(levelname)s] %(message)s",
                    'datefmt': "%d/%b/%Y %H:%M:%S"
                },
            },
            'handlers': {
                'default': {
                    'level': 'DEBUG',
                    'class': 'logging.NullHandler',
                    'formatter': 'standard',
                },
            },
            'loggers': {
                'aiorest-ws': {
                    'handlers': ['default', ],
                    'level': 'DEBUG',
                    'propagate': False
                }
            }
        }
        configure_logger(user_config)
        logger = logging.getLogger('aiorest-ws')
        self.compare_settings(logger, user_config)
