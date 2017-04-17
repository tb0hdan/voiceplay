#-*- coding: utf-8 -*-
""" Station playback module """

import random
random.seed()
import re

from voiceplay.datasources.lastfm import StationCrawl
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher, ThreadGroup
from .basetask import BasePlayerTask


class Station(APIV1Resource):
    """
    Station API endpoint
    """
    route_base = '/api/v1/play/station/<station>'
    queue = None
    def get(self, station):
        """
        HTTP GET handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and station:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % station + 'station')
            result = {'status': 'ok', 'message': message}
        return result


class StationTask(BasePlayerTask):
    """
    Player station task. Play top tracks for provided genre.
    """
    __group__ = ['play']
    __regexp__ = ['^play (.+) station$']
    __priority__ = 10

    @classmethod
    def play_station(cls, station):
        """
        Play top tracks for station
        TODO: Fix in https://github.com/tb0hdan/voiceplay/issues/22
        """
        sc = StationCrawl()
        sc.put_genre(station)

        tg = ThreadGroup(restart=False)
        tg.targets = [sc.genre_loop, sc.playlist_loop]
        tg.start_all()

        already_played = []
        while True:
            for track in cls.tracks_with_prefetch(sc.playlist):
                if cls.get_exit():  # pylint:disable=no-member
                    sc.set_exit(True)
                    tg.stop_all()
                    break
                cls.play_full_track(track)
                already_played.append(track)
            if sorted(already_played) == sorted(sc.playlist) or cls.get_exit():
                break

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        station = re.match(regexp, message, re.I).groups()[0]
        cls.say('Playing %s station' % station)
        cls.play_station(station)
