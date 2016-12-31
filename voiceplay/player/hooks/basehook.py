#-*- coding: utf-8 -*-
""" Player hook model """


class BasePlayerHook(object):
    """
    This class should be inherited by all discoverable hooks
    """
    argparser = None

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        Run action on item playback start
        """
        pass

    @classmethod
    def on_playback_pause(cls, *args, **kwargs):
        """
        Run action on item playback pause
        """
        pass

    @classmethod
    def on_playback_resume(cls, *args, **kwargs):
        """
        Run action on item playback resum
        """
        pass

    @classmethod
    def on_playback_stop(cls, *args, **kwargs):
        """
        Run action on item playback stop
        """
        pass

    @classmethod
    def on_playback_error(cls, *args, **kwargs):
        """
        Run action on item playback error
        """
        pass
