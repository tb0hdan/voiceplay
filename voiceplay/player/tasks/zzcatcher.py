#-*- coding: utf-8 -*-

import re
from .basetask import BasePlayerTask


class ZZCatcherTask(BasePlayerTask):
    """
    This should be the last 'play' task, please put any other with lower priority.
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+)$']
    __priority__ = 15000
    __actiontype__ = 'zzcatcher_query_playback'

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        query = re.match(regexp, message).groups()[0]
        cls.say('Playing %s' % (query))
        cls.play_full_track(query)
