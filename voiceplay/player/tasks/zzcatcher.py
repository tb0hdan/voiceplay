#-*- coding: utf-8 -*-
""" Catcher playback task module """


import re
from voiceplay.webapp.baseresource import APIV1Resource
from .basetask import BasePlayerTask


class ZZCatcherResource(APIV1Resource):
    route = '/api/v1/play/zzcatch/<query>'
    queue = None
    def post(self, query):
        if self.queue and query:
            self.queue.put('play' + ' %s ' % query)
        return {'status': 'ok'}


class ZZCatcherTask(BasePlayerTask):
    """
    ZZCatcher diverts query that wasn't processed by tasks to source plugins,
    e.g. this allows playback by lyrics
    This should be the last 'play' task, please put any other with lower priority.
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+)$']
    __priority__ = 15000

    @classmethod
    def process(cls, regexp, message):
        """
        Run task (i.e. play item as is by employing rich search
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        query = re.match(regexp, message, re.I).groups()[0]
        cls.say('Playing %s' % (query))
        cls.play_full_track(query)
