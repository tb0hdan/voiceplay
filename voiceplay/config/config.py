#-*- coding: utf-8 -*-
''' Configuration reader module '''

import kaptan
import os
from six import with_metaclass

from voiceplay.utils.helpers import Singleton


class Config(with_metaclass(Singleton)):
    '''
    VoicePlay configuration object
    '''
    cache_dir = '~/.cache/voiceplay'

    def __init__(self, cfg_file='config.yaml'):
        self.config = kaptan.Kaptan()
        self.config.import_config(cfg_file)

    @classmethod
    def extend_local(cls, data):
        '''
        '''
        cache_dir = data.get('cache_dir', None)
        if not cache_dir:
            cache_dir = cls.cache_dir
        cache_dir = os.path.expanduser(cache_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        data['cache_dir'] = cache_dir
        return data

    @classmethod
    def cfg_data(cls):
        '''
        Return configuration data as dictionary
        '''
        obj = cls()
        data = obj.extend_local(obj.config.configuration_data)
        return data
