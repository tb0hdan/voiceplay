#-*- coding: utf-8 -*-
""" Something like this module """

import random
random.seed()

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class SomethingLikeThisResource(APIV1Resource):
    """
    Something like this (current track) API endpoint
    """
    route_base = '/api/v1/play/somethinglikethis'
    queue = None
    def post(self):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play something like this')
            result = {'status': 'ok', 'message': message}
        return result


class SomethingLikeThisTask(BasePlayerTask):
    """
    Starts a station with tracks similar to what's being currently playing
    """
    __group__ = ['play']
    __regexp__ = ['^play (?:songs|tracks|something) like this(.+)?$']
    __priority__ = 170

    @classmethod
    def play_similar_tracks(cls, track):
        """
        Shuffle artist tracks
        TODO: Fix this in https://github.com/tb0hdan/voiceplay/issues/22
        """
        tracks = []
        # original
        artist = track.split(' - ')[0]
        artists = cls.lfm().get_similar_artists(artist)
        # feat
        if not artists:
            tmp = artist.lower().split(' feat ')[0]
            if tmp == artist.lower():
                tmp = artist.lower().split(' ft ')[0]
            artists = cls.lfm().get_similar_artists(tmp)

        for artist in artists:
            tracks += cls.lfm().get_top_tracks(artist)
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
        track = cls.get_current_track()
        cls.say('Playing music similar to %s' % track)
        cls.play_similar_tracks(track)
