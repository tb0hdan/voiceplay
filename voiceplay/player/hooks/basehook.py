class BasePlayerHook(object):
    '''
    base hook
    '''
    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        pass

    @classmethod
    def on_playback_pause(cls, *args, **kwargs):
        pass

    @classmethod
    def on_playback_resume(cls, *args, **kwargs):
        pass

    @classmethod
    def on_playback_stop(cls, *args, **kwargs):
        pass

    @classmethod
    def on_playback_error(cls, *args, **kwargs):
        pass
