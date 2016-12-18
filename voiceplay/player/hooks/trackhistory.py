#-*- coding: utf-8 -*-

import os
import requests
from voiceplay.database import voiceplaydb
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class TrackHistory(object):
    '''
    Save track history
    '''
    @classmethod
    def notify(cls, *args, **kwargs):
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser):
            return
        if argparser.no_track_save:
            logger.debug('TrackHistory disabled for this session...')
            return
        voiceplaydb.update_played_tracks(track)


class TrackHistoryHook(BasePlayerHook):
    '''
    Log only hook
    '''
    __priority__ = 40

    @classmethod
    def configure_argparser(cls, parser):
        parser.add_argument('-n', '--no-track-save', action='store_true',
                                 default=False,
                                 dest='no_track_save',
                                 help='Disable track history for this session')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        TrackHistory.notify(*args, argparser=cls.argparser, **kwargs)