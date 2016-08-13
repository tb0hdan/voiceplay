import re
from voiceplay.datasources.track.basesource import TrackSource
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from voiceplay.datasources.lastfm import VoicePlayLastFm


class BasePlayerTask(object):
    '''
    base player task
    '''
    lfm = VoicePlayLastFm()

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
    def track_filter_fn(cls, search_term, track_result_pair):
        '''
        wrapper around trackfilter
        '''
        return cls.trackfilter(search_term, track_result_pair[0])

    @classmethod
    def play_full_track(cls, trackname):
        '''
        Play full track
        '''
        vid = None
        baseurl = None
        sources = sorted(PluginLoader().find_classes('voiceplay.datasources.track', TrackSource),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))

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
                logger.debug('Starting playback using %r', source.__name__)
                url = source.__baseurl__ + tracks[0][1]
                try:
                    filename = source.download(url)
                    if cls.player.play(filename):
                        break
                except Exception as exc:
                    message = 'Playback of source url %s failed with %r\n' % (url, exc)
                    message += 'Continuing using next source url...'
                    logger.debug(message)
