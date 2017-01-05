#-*- coding: utf-8 -*-
""" Single track playback module """

import re
from .basetask import BasePlayerTask


class SingleTrackArtistTask(BasePlayerTask):
    """
    Single track playback class.
    The simplest form of player task, can be used as a reference for writing new tasks.
    """
    __group__ = ['play']
    __regexp__ = ['^play (?!fresh|new)\s?(?!tracks|songs)(.+) bu?(?:t|y) (.+)$']
    __priority__ = 70
    __actiontype__ = 'single_track_artist'

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        track, artist = re.match(regexp, message, re.I).groups()
        # TODO add track correction here
        cls.say('%s by %s' % (track, artist))
        cls.play_full_track('%s - %s' % (artist, track))
