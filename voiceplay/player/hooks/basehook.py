class BasePlayerHook(object):
    '''
    base hook
    '''
    @classmethod
    def on_playback_start(cls, trackname):
        pass

    @classmethod
    def on_playback_pause(cls, trackname):
        pass

    @classmethod
    def on_playback_resume(cls, trackname):
        pass

    @classmethod
    def on_playback_stop(cls, trackname):
        pass

    @classmethod
    def on_playback_error(cls, trackname):
        pass
