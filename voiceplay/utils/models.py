#-*- coding: utf-8 -*-
""" VoicePlay models module (for plugins, etc) """

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm

class BaseCfgModel(object):
    """
    Configuration model for application
    """
    _cfg_data = None

    @classmethod
    def cfg_data(cls):
        """
        Return configuration data
        """
        if not cls._cfg_data:
            cls._cfg_data = Config.cfg_data()
        return cls._cfg_data


class BaseLfmModel(BaseCfgModel):
    """
    Configuration model for application (same as above) plus Last.FM object
    """
    _lfm = None

    @classmethod
    def lfm(cls):
        """
        Return Last.FM object
        """
        if not cls._lfm:
            cls._lfm = VoicePlayLastFm()
        return cls._lfm
