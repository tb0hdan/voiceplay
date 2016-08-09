import inspect
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class LogOnlyPlayerHook(BasePlayerHook):
    '''
    base hook
    '''
    @classmethod
    def on_playback_start(cls, trackname):
        logger.debug('{0}.{1}: {2}'.format(cls.__name__, inspect.currentframe().f_code.co_name,
                                           trackname))

    @classmethod
    def on_playback_pause(cls, trackname):
        logger.debug('{0}.{1}: {2}'.format(cls.__name__, inspect.currentframe().f_code.co_name,
                                           trackname))

    @classmethod
    def on_playback_resume(cls, trackname):
        logger.debug('{0}.{1}: {2}'.format(cls.__name__, inspect.currentframe().f_code.co_name,
                                           trackname))

    @classmethod
    def on_playback_stop(cls, trackname):
        logger.debug('{0}.{1}: {2}'.format(cls.__name__, inspect.currentframe().f_code.co_name,
                                           trackname))

    @classmethod
    def on_playback_error(cls, trackname):
        logger.debug('{0}.{1}: {2}'.format(cls.__name__, inspect.currentframe().f_code.co_name,
                                           trackname))
