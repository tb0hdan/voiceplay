#-*- coding: utf-8 -*-

import inspect
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class LogOnlyPlayerHook(BasePlayerHook):
    '''
    Log only hook
    '''
    __priority__ = 10

    @classmethod
    def debugself(cls, *args, **kwargs):
        name = inspect.stack()[1][3]
        logger.debug('{0}.{1}: args: {2!r} kwargs: {3!r}'.format(cls.__name__, name,
                                           args, kwargs))
    @classmethod
    def on_playback_start(cls, *args, **kwargs):
         cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_pause(cls, *args, **kwargs):
         cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_resume(cls, *args, **kwargs):
         cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_stop(cls, *args, **kwargs):
         cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_error(cls, *args, **kwargs):
         cls.debugself(*args, **kwargs)
