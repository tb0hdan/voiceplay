#-*- coding: utf-8 -*-
""" Track history task module """

import os
import random
random.seed()
import re
from voiceplay.database import voiceplaydb
from voiceplay.logger import logger
from .basetask import BasePlayerTask


class LocalHistoryTask(BasePlayerTask):
    """
    All played track names are stored locally.
    This tasks enables playback of that.
    """
    __group__ = ['play', 'shuffle']
    __regexp__ = ['^play (.+)?my history$', '^shuffle (.+)?my history$']
    __priority__ = 160
    __actiontype__ = 'shuffle_local_history'

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
        msg = re.match(regexp, message).groups()[0]
        logger.warning(msg)
        cls.say('Shuffling songs based on track history')
        cls.play_track_history(msg)
