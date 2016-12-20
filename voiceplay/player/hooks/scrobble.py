#-*- coding: utf-8 -*-

import os
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class TrackScrobble(object):
    '''
    Save track history
    '''
    @classmethod
    def notify(cls, *args, **kwargs):
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser):
            return
        if argparser.no_track_scrobble:
            logger.debug('TrackScrobble disabled for this session...')
            return
        artist = track.split(' - ')[0]
        title = track.split(' - ')[1]
        lfm = VoicePlayLastFm()
        lfm.scrobble(artist, title)


class ScrobbleHook(BasePlayerHook):
    '''
    Scrobble hook
    '''
    __priority__ = 50

    @classmethod
    def configure_argparser(cls, parser):
        parser.add_argument('-ns', '--no-scrobble', action='store_true',
                                 default=False,
                                 dest='no_track_scrobble',
                                 help='Disable track scrobbling for this session')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        TrackScrobble.notify(*args, argparser=cls.argparser, **kwargs)
