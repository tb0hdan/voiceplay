#-*- coding: utf-8 -*-
""" Base player task module """

import os
import re

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.datasources.track.basesource import TrackSource
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.helpers import track_to_hash


class BasePlayerTask(object):
    """
    base player task model
    """
    lfm = VoicePlayLastFm()
    cfg_data = Config.cfg_data()
    logger = logger

    @classmethod
    def say(cls, msg):
        """
        Use TTS to read message aloud. Does nothing in console mode
        """
        cls.tts.say_put(msg)  # pylint:disable=no-member

    @classmethod
    def play(cls, path, track, block=True):
        """
        Play specified item
        """
        cls.player.play(path, track, block=True)  # pylint:disable=no-member

    @staticmethod
    def trackfilter(search_term, search_result):
        """
        Track filter
        TODO: move this to utils/track.py
        """
        track_is_ok = True
        regset = ['(\(|\]|\{).?FULL (ALBUM|SET|CONCERT|MOVIE)?.+(\(|\]|\})?',
                  '(\(|\[|\{)KARAOKE?.+(\)|\]\})',
                  '(\(|\[).?LIVE (AT|\@|ON).+?(\(|\])',
                  '\(?(REMIX|BOOTLEG|MASH\-?UP)(.+)\)?']
        # allow exact match
        if search_term.lower() == search_result.lower():
            return track_is_ok
        # proceed with patterns
        for reg in regset:
            if re.search(reg, search_result.upper()):
                track_is_ok = False
                break
        return track_is_ok

    @staticmethod
    def track_normalizer(track):
        """
        Normalize track by splitting it in words and capitalizing first letters
        TODO: move this to utils/track.py
        """
        return ' '.join(word.capitalize() for word in track.split(' '))

    @classmethod
    def tracks_with_prefetch(cls, tracklist):
        """
        Add tracks to prefetch to queue (speeds up playback)
        """
        prefetch = cls.cfg_data['prefetch_count']
        cnt = 1
        total = len(tracklist)
        for idx in xrange(0, total):
            prefs = []
            if cnt + prefetch <= total - 1:
                for i in xrange(cnt, cnt + prefetch):
                    prefs.append(tracklist[i])
                cnt += prefetch
            elif cnt <= idx + 1 <= total - 1:
                prefs.append(tracklist[idx + 1])
            if prefs:
                for item in prefs:
                    full_path = os.path.join(cls.cfg_data.get('cache_dir'), track_to_hash(item)) + '.mp3'
                    if not os.path.exists(full_path) and cls.prefetch_callback and callable(cls.prefetch_callback):  # pylint:disable=no-member
                        cls.logger.debug('Adding %r to prefetch queue', item.encode('utf-8'))
                        cls.prefetch_callback(item)  # pylint:disable=no-member
            yield tracklist[idx]

    @classmethod
    def track_filter_fn(cls, search_term, track_result_pair):
        """
        wrapper around trackfilter
        """
        return cls.trackfilter(search_term, track_result_pair[0])

    @classmethod
    def download_full_track(cls, trackname):
        """
        Play full track
        """
        vid = None
        baseurl = None
        sources = sorted(PluginLoader().find_classes('voiceplay.datasources.track', TrackSource),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))

        filename = None
        for source in sources:
            try:
                results = source.search(trackname)
            except Exception as exc:
                results = []
                message = 'Source %r search failed with %r\n' % (source, exc)
                message += 'Continuing using next source provider...'
                cls.logger.debug(message)
            tracks = [track for track in results if cls.track_filter_fn(trackname, track)]
            if tracks:
                cls.logger.debug('Getting track using %r', source.__name__)
                url = source.__baseurl__ + tracks[0][1]
                try:
                    filename = source.download(trackname, url)
                    if not filename:
                        continue
                    break
                except Exception as exc:
                    message = 'Processing of source url %s failed with %r\n' % (url, exc)
                    message += 'Continuing using next source url...'
                    cls.logger.debug(message)
        return filename

    @classmethod
    def play_full_track(cls, trackname):
        """
        Playback track in form: Artist - Title
        """
        trackname = cls.track_normalizer(trackname)
        cls.logger.debug('PFT: ' + trackname)
        full_path = os.path.join(cls.cfg_data.get('cache_dir'), track_to_hash(trackname)) + '.mp3'
        if not os.path.exists(full_path):
            cls.logger.debug('Track %r is not cached at %r', trackname, full_path)
            full_path = cls.download_full_track(trackname)
        else:
            cls.logger.debug('Using cache for %r at %r', trackname, full_path)
        cls.play(full_path, trackname)  # pylint:disable=no-member

    @classmethod
    def play_url(cls, url, description):
        """
        Playback item in form: http://domain/path
        """
        cls.logger.debug('Playing URL: ' + url)
        cls.play(url, description)

    @classmethod
    def get_current_track(cls):
        """
        Return currently playing track
        """
        return cls.player.current_track
