#-*- coding: utf-8 -*-
''' get version, etc '''

import os

__title__ = 'voiceplay'
__version_file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'VERSION')
__version__ = open(__version_file__, 'rb').read().strip()
__author__ = 'Bohdan Turkynewych'
__license__ = 'UNLICENSE'
__copyright__ = 'public domain'
