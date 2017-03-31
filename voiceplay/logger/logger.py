#-*- coding: utf-8 -*-
"""
Configure/Initialize custom logger
TODO: use configuration file
"""

import logging

from voiceplay import __title__
logging.basicConfig()
logger = logging.getLogger(__title__)
logger.setLevel(logging.INFO)
