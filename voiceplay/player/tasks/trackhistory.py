#-*- coding: utf-8 -*-
""" Track history task module """

import random
random.seed()
import re
from voiceplay.database import voiceplaydb
from voiceplay.logger import logger
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class LocalHistoryResource(APIV1Resource):
    """
    Local history playback API endpoint
    """
    route_base = '/api/v1/play/localhistory'
    queue = None
    def post(self):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play my history')
            result = {'status': 'ok', 'message': message}
        return result


class LocalHistoryTask(BasePlayerTask):
    """
    All played track names are stored locally.
    This tasks enables playback of that.
    """
    __group__ = ['play', 'shuffle']
    __regexp__ = ['^play (.+)?my history$', '^shuffle (.+)?my history$']
    __priority__ = 160

    @classmethod
    def play_track_history(cls, message):
        """
        Get list of all tracks from local history
        TODO: Limit this
        """
        tracks = voiceplaydb.get_played_tracks()
        random.shuffle(tracks)
        for track in tracks:
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        msg = re.match(regexp, message, re.I).groups()[0]
        logger.warning(msg)
        cls.say('Shuffling songs based on track history')
        cls.play_track_history(msg)
