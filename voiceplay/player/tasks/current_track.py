#-*- coding: utf-8 -*-
""" Get current track task module """

import re
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class CurrentTrackResource(APIV1Resource):
    route = '/api/v1/tracks/current'
    queue = None
    def get(self):
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('current_track')
            result = {'status': 'ok', 'message': message}
        return result


class CurrentTrackTask(BasePlayerTask):
    """
    Get current track
    """
    __group__ = ['current_track']
    __regexp__ = ['^current_track(.+)?$']
    __priority__ = 190

    @classmethod
    def process(cls, regexp, message):
        """
        Run task (i.e. play item as is by employing rich search
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        current_track = cls.get_current_track()
        cls.say('Current track is %s' % current_track)
        return current_track
