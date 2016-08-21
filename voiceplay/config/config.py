#-*- coding: utf-8 -*-
''' Configuration reader module '''

import kaptan
from six import with_metaclass

from voiceplay.utils.helpers import Singleton


class Config(with_metaclass(Singleton)):
    '''
    VoicePlay configuration object
    '''
    def __init__(self, cfg_file='config.yaml'):
        self.config = kaptan.Kaptan()
        self.config.import_config(cfg_file)

    @classmethod
    def cfg_data(cls):
        '''
        Return configuration data as dictionary
        '''
        obj = cls()
        return obj.config.configuration_data
