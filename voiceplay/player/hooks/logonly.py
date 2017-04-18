#-*- coding: utf-8 -*-
""" Only log player hook module """

import inspect
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class LogOnlyPlayerHook(BasePlayerHook):
    """
    Only log player state changes. Useful for development/debugging
    """
    __priority__ = 10

    @classmethod
    def debugself(cls, *args, **kwargs):
        """
        Logging wrapper
        """
        name = inspect.stack()[1][3]
        logger.debug('%s.%s: args: %r kwargs: %r',
                     cls.__name__,
                     name,
                     args,
                     kwargs)

    @classmethod
    def on_recognition_start(cls, *args, **kwargs):
        """
        Run log action on recognition start
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_recognition_progress(cls, *args, **kwargs):
        """
        Run log action on recognition progress
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_recognition_end(cls, *args, **kwargs):
        """
        Run log action on recognition end
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        Run log action on item playback start
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_pause(cls, *args, **kwargs):
        """
        Run log action on item playback pause
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_resume(cls, *args, **kwargs):
        """
        Run log action on item playback resume
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_stop(cls, *args, **kwargs):
        """
        Run log action on item playback stop
        """
        cls.debugself(*args, **kwargs)

    @classmethod
    def on_playback_error(cls, *args, **kwargs):
        """
        Run log action on item playback error
        """
        cls.debugself(*args, **kwargs)
