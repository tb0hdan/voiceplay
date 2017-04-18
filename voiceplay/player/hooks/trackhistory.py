#-*- coding: utf-8 -*-
""" Track history hook module """

from voiceplay.database import voiceplaydb
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class TrackHistory(object):
    """
    Save track history
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
        if argparser.no_track_save:
            logger.debug('TrackHistory disabled for this session...')
            return
        voiceplaydb.update_played_tracks(track)


class TrackHistoryHook(BasePlayerHook):
    """
    Track history hook
    """
    __priority__ = 40

    @classmethod
    def configure_argparser(cls, parser):
        """
        Configure argument parser for this hook
        """
        parser.add_argument('-n', '--no-track-save', action='store_true',
                            default=False,
                            dest='no_track_save',
                            help='Disable track history for this session')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        watch for on_playback_start events only
        """
        TrackHistory.notify(*args, argparser=cls.argparser, **kwargs)
