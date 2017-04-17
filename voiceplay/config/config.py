#-*- coding: utf-8 -*-
""" Configuration reader module """

import multiprocessing
import os

import kaptan

from six import with_metaclass

from voiceplay.utils.helpers import Singleton


class Config(with_metaclass(Singleton)):
    """
    VoicePlay configuration object
    """
    # Simple POST request
    bugtracker_url = 'http://7d93bbb8914ae5ed56b28e41554ce380063b2ab8.bugtracker.0x21h.net/'
    external_services = ['google', 'lastfm', 'vimeo']
    cache_dir = '~/.cache/voiceplay'
    persistent_dir = '~/.config/voiceplay'
    config_search_order = ['config.yaml', os.path.expanduser('~/.config/voiceplay/config.yaml')]
    # 3 -> 9 due to pretty fast remote HTTP cache
    prefetch_count = 9
    webapp_port = 8000
    cpu_count = multiprocessing.cpu_count()

    def __init__(self, cfg_file=None):
        self.config = kaptan.Kaptan(handler="yaml")
        if not cfg_file:
            for fname in self.config_search_order:
                if os.path.exists(fname):
                    cfg_file = fname
                    break
        self.config.import_config(cfg_file)

    @classmethod
    def extend_local(cls, data):
        """
        TODO: extend config class with __getattr__
        """
        # persistent_dir
        persistent_dir = data.get('persistent_dir', None)
        if not persistent_dir:
            persistent_dir = cls.persistent_dir
        persistent_dir = os.path.expanduser(persistent_dir)
        if not os.path.exists(persistent_dir):
            os.makedirs(persistent_dir)
        data['persistent_dir'] = persistent_dir
        # cache_dir
        cache_dir = data.get('cache_dir', None)
        if not cache_dir:
            cache_dir = cls.cache_dir
        cache_dir = os.path.expanduser(cache_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        data['cache_dir'] = cache_dir
        # prefetch count
        prefetch_count = data.get('prefetch_count', None)
        if not prefetch_count:
            prefetch_count = cls.prefetch_count
        data['prefetch_count'] = prefetch_count
        # bugtracker
        bugtracker_url = data.get('bugtracker_url', None)
        if not bugtracker_url:
            bugtracker_url = cls.bugtracker_url
        data['bugtracker_url'] = bugtracker_url
        # webapp
        webapp_port = data.get('webapp_port', None)
        if not webapp_port:
            webapp_port = cls.webapp_port
        data['webapp_port'] = webapp_port
        # cpu_count
        cpu_count = data.get('cpu_count', None)
        if not cpu_count:
            cpu_count = cls.cpu_count
        data['cpu_count'] = cpu_count
        #
        return data


    @classmethod
    def cfg_data(cls):
        """
        Return configuration data as dictionary
        """
        obj = cls()
        data = obj.extend_local(obj.config.configuration_data)
        return data
