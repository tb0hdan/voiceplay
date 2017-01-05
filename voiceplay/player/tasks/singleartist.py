#-*- coding: utf-8 -*-
""" Single artist playback module """

import random
random.seed()
import re
from .basetask import BasePlayerTask


class SingleArtistTask(BasePlayerTask):
    """
    Single artist playback class
    """
    __group__ = ['play']
    __regexp__ = ['^play some (?!fresh|new)\s?(?:music|tracks?|songs?) by (.+)$']
    __priority__ = 20
    __actiontype__ = 'shuffle_artist'

    @classmethod
    def run_shuffle_artist(cls, artist):
        """
        Shuffle artist tracks
        """
        if cls.lfm.get_query_type(artist) == 'artist':
            tracks = cls.lfm.get_top_tracks(cls.lfm.get_corrected_artist(artist))
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
        cls.say('Shuffling songs by %s' % artist)
        cls.run_shuffle_artist(artist)
