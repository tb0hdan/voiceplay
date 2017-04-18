#-*- coding: utf-8 -*-
""" Last.FM scrobbling module """

import sys
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.logger import logger
from voiceplay.utils.helpers import debug_traceback
from .basehook import BasePlayerHook


class TrackScrobble(object):
    """
    Save track history for Last.FM (and compatibles)
    """

    @classmethod
    def notify(cls, *args, **kwargs):
        """
        Notification dispatcher
        """
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser):
            return
        if argparser.no_track_scrobble:
            logger.debug('TrackScrobble disabled for this session...')
            return
        if len(track.split(' - ')) < 2:
            logger.debug('Cannot scrobble without complete track: %r', track)
        else:
            artist = track.split(' - ')[0]
            title = track.split(' - ')[1]
            lfm = VoicePlayLastFm()
            lfm.scrobble(artist, title)


class ScrobbleHook(BasePlayerHook):
    """
    Scrobble hook
    """
    __priority__ = 50

    @classmethod
    def configure_argparser(cls, parser):
        """
        Configure argument parser for this hook
        """
        parser.add_argument('-ns', '--no-scrobble', action='store_true',
                                 default=False,
                                 dest='no_track_scrobble',
                                 help='Disable track scrobbling for this session')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        watch for on_playback_start events only
        """
        try:
            TrackScrobble.notify(*args, argparser=cls.argparser, **kwargs)
        except Exception as _:
            message = 'Method %r crashed (see message below), track was not scrobbled...' % 'ScrobbleHook.on_playback_start'
            debug_traceback(sys.exc_info(), __file__, message=message)
