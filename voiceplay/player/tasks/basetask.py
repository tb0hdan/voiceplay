import os
import re

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.datasources.track.basesource import TrackSource
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.helpers import track_to_hash

class BasePlayerTask(object):
    '''
    base player task
    '''
    lfm = VoicePlayLastFm()
    cfg_data = Config.cfg_data()

    @staticmethod
    def trackfilter(search_term, search_result):
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

    @classmethod
    def tracks_with_prefetch(cls, tracklist):
        total = len(tracklist)
        for idx, track in enumerate(tracklist):
            # do prefetch here
            if idx + 1 <= total - 1:
                trackname = tracklist[idx + 1]
                full_path = os.path.join(cls.cfg_data.get('cache_dir'), track_to_hash(trackname)) + '.mp3'
                if not os.path.exists(full_path) and cls.prefetch_callback and callable(cls.prefetch_callback):
                    logger.debug('Adding %r to prefetch queue', trackname.encode('utf-8'))
                    cls.prefetch_callback(trackname)
            yield track

    @classmethod
    def track_filter_fn(cls, search_term, track_result_pair):
        '''
        wrapper around trackfilter
        '''
        return cls.trackfilter(search_term, track_result_pair[0])

    @classmethod
    def download_full_track(cls, trackname):
        '''
        Play full track
        '''
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
                logger.debug(message)
            tracks = [track for track in results if cls.track_filter_fn(trackname, track)]
            if tracks:
                logger.debug('Getting track using %r', source.__name__)
                url = source.__baseurl__ + tracks[0][1]
                try:
                    filename = source.download(trackname, url)
                    if not filename:
                        continue
                    break
                except Exception as exc:
                    message = 'Processing of source url %s failed with %r\n' % (url, exc)
                    message += 'Continuing using next source url...'
                    logger.debug(message)
        return filename

    @classmethod
    def play_full_track(cls, trackname):
        full_path = os.path.join(cls.cfg_data.get('cache_dir'), track_to_hash(trackname)) + '.mp3'
        if not os.path.exists(full_path):
            logger.debug('Track %r is not cached at %r', trackname, full_path)
            full_path = cls.download_full_track(trackname)
        else:
            logger.debug('Using cache for %r at %r', trackname, full_path)
        cls.player.play(full_path, trackname)