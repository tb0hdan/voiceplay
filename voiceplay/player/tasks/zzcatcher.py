#-*- coding: utf-8 -*-
""" Catcher playback task module """


import re
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class ZZCatcherResource(APIV1Resource):
    """
    ZZCatcher (magical) API endpoint
    """
    route_base = '/api/v1/play/zzcatch/<query>'
    queue = None
    def post(self, query):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and query:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % query)
            result = {'status': 'ok', 'message': message}
        return result


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
        _, tracks = cls.search_full_track(query, download=False)
        if tracks:
            track = tracks[0][0]
            cls.say('Playing %s' % track)
            cls.play_full_track(track)
        else:
            cls.say('I could not find track with %s lyrics in it')
