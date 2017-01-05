#-*- coding: utf-8 -*-
""" Station playback module """

import random
random.seed()
import re
from .basetask import BasePlayerTask


class StationTask(BasePlayerTask):
    """
    Player station task. Play top tracks for provided genre.
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station$']
    __priority__ = 10
    __actiontype__ = 'station_artist'

    @classmethod
    def play_station(cls, station):
        """
        Play top tracks for station
        TODO: Fix in https://github.com/tb0hdan/voiceplay/issues/22
        """
        tracks = cls.lfm.get_station(station)
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        cls.say('Playing %s station' % station)
        cls.play_station(station)
