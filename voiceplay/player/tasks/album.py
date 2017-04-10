#-*- coding: utf-8 -*-
""" Album playback task module """

import random
random.seed()
import re
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from .basetask import BasePlayerTask


class Album(APIV1Resource):
    """
    Album API endpoint
    """
    route_base = '/api/v1/play/artist/<artist>/album/<album>'
    queue = None
    def post(self, artist, album):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and artist and album:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play tracks from' + ' %s ' % album + ' by ' + artist)
            result = {'status': 'ok', 'message': message}
        return result


class AlbumTask(BasePlayerTask):
    """
    Album playback class
    """
    __group__ = ['play']
    __regexp__ = ['^play (?:songs|tracks) from (.+) by (.+)$']
    __priority__ = 60

    @classmethod
    def play_artist_album(cls, artist, album):
        """
        Play all tracks from album
        """
        tracks = cls.lfm().get_tracks_for_album(artist, album)
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
        album, artist = re.match(regexp, message, re.I).groups()
        artist = cls.lfm().get_corrected_artist(artist)
        cls.say('%s album by %s' % (album, artist))
        cls.play_artist_album(artist, album)
