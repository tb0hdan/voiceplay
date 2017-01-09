#-*- coding: utf-8 -*-
""" VoicePlay models module (for plugins, etc) """

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm

class BaseCfgModel(object):
    _cfg_data = None

    @classmethod
    def cfg_data(cls):
        if not cls._cfg_data:
            cls._cfg_data = Config.cfg_data()
        return cls._cfg_data

class BaseLfmModel(BaseCfgModel):
    _lfm = None

    @classmethod
    def lfm(cls):
        if not cls._lfm:
            cls._lfm = VoicePlayLastFm()
        return cls._lfm
