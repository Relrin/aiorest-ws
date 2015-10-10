# -*- coding: utf-8 -*-
"""
    Logging tool for aiorest-ws framework.
"""
__all__ = ('logger', )

import logging
import logging.config

from aiorest_ws.conf import settings

logging.config.dictConfig(settings.DEFAULT_LOGGING_SETTINGS)
logger = logging.getLogger('aiorest-ws')
