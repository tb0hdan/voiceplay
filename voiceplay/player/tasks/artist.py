#-*- coding: utf-8 -*-
""" Artist playback module """

import random
random.seed()
import re

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class Artist(APIV1Resource):
    """
    Artist API endpoint
    """
    route_base = '/api/v1/play/artist/<artist>/<query>'
    queue = None
    def post(self, artist, query):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and artist and query:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play' + ' %s ' % query + ' by ' + artist)
            result = {'status': 'ok', 'message': message}
        return result


class SingleArtistTask(BasePlayerTask):
    """
    Single artist playback class
    """
    __group__ = ['play']
    __regexp__ = ['^play some (?!fresh|new)\s?(?:music|tracks?|songs?) by (.+)$']
    __priority__ = 20

    @classmethod
    def run_shuffle_artist(cls, artist):
        """
        Shuffle artist tracks
        """
        if cls.lfm().get_query_type(artist) == 'artist':
            tracks = cls.lfm().get_top_tracks(cls.lfm().get_corrected_artist(artist))
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
        artist = re.match(regexp, message, re.I).groups()[0]
        artist = cls.lfm().get_corrected_artist(artist)
        cls.say('Shuffling songs by %s' % artist)
        cls.run_shuffle_artist(artist)

class SingleTrackArtistTask(BasePlayerTask):
    """
    Single track playback class.
    The simplest form of player task, can be used as a reference for writing new tasks.
    """
    __group__ = ['play']
    __regexp__ = ['^play (?!fresh|new)\s?(?!tracks|songs)(.+) bu?(?:t|y) (.+)$']
    __priority__ = 70

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        track, artist = re.match(regexp, message, re.I).groups()
        # TODO add track correction here
        artist = cls.lfm().get_corrected_artist(artist)
        cls.say('%s by %s' % (track, artist))
        cls.play_full_track('%s - %s' % (artist, track))
