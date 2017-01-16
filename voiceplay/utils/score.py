#-*- coding: utf-8 -*-
""" Video scoring module """

import re
from math import log10, pow as math_pow
from voiceplay.logger import logger

# pylint:disable=too-few-public-methods
class DateMan(object):
    '''
    Time and date manipulation
    '''
    @staticmethod
    def iso2hms(isodate):
        '''
        Convert ISO date to H:M:S
        '''
        if not isodate.startswith('PT'):
            return None
        if isodate.endswith('M'):
            isodate = isodate + '0S'
        isodate = re.sub('(PT|S)', '', re.sub('(H|M)', ':', isodate))
        result = ''
        if len(isodate) <= 2:
            isodate = '00:' + isodate
        arr = isodate.split(':')
        for idx, val in enumerate(arr):
            if not val:
                continue
            if int(val) < 10 and int(val) != 0 and len(val) == 1:
                val = '0' + val
            if int(val) == 0 and len(val) == 1:
                val = '0' + val
            if idx + 1 < len(arr):
                result += val + ':'
            else:
                result += val
        return result


class VideoScoreCalculator(object):
    '''
    Get video score based on meta information
    '''
    default_score = 100
    def __init__(self, debug=False):
        self.debug = debug
        self.ruleset = [self.album_in_title, self.prefer_licensed, self.prefer_processed,
                        self.prefer_vevo, self.live_in_title, self.prefer_official,
                        self.cover_in_title, self.prefer_original, self.prefer_startswith,
                        self.lyrics_in_title, self.at_in_title, self.guitar_lesson_in_title,
                        self.with_tabs_in_title, self.acoustic_in_title, self.prefer_music_video,
                        self.prefer_no_parody, self.prefer_no_karaoke, self.prefer_no_tutorial,
                        self.prefer_no_chipmunks, self.prefer_popular, self.prefer_shorter,
                        self.prefer_official_video, self.mashup_penalty, self.behind_scenes_penalty,
                        self.audio_in_title, self.teaser_in_title, self.megamix_penalty,
                        self.concert_and_studio_penalty, self.preview_in_title, self.prefer_no_trailer,
                        self.remix_in_title, self.prefer_no_makeup]

    def log(function):
        def wrapper(self, *args, **kwargs):
            if self.debug:
                logger.error('Enter %s', function.__name__)
            result = function(self, *args, **kwargs)
            if self.debug:
                logger.error('Exit %s with result %s', function.__name__, result)
            return result
        return  wrapper


    @log
    def concert_and_studio_penalty(self, video_metadata, query):
        known_studios = ['o2 arena', 'capital summertime', 'dancing with the stars',
                         'the ellen degeneres', 'on today show', 'make room concert',
                         'on letterman', 'at farm aid', 'ancienne belgium', 'honda stage',
                         'iheartradio theater', 'on snl', 'on directv', 'gramercy',
                         'honda center', 'concert']
        title = video_metadata[0].lower()
        score = 0
        for studio in known_studios:
            if studio in query.lower():
                continue
            if studio in title:
                score = -20
                break
        return score

    @log
    def album_in_title(self, video_metadata, query):
        album = video_metadata[0].lower()
        if 'full album' in query.lower():
            score = 0
        elif 'full album' in album:
            score = -40
        else:
            score = 0
        return score

    @log
    def acoustic_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'acoustic' in query.lower():
            score = 0
        elif 'acoustic' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def preview_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'preview' in query.lower():
            score = 0
        elif 'preview' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def remix_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'remix' in query.lower():
            score = 0
        elif 'remix' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def mashup_penalty(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'mashup' in query.lower():
            score = 0
        elif 'mashup' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def megamix_penalty(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'megamix' in query.lower():
            score = 0
        elif 'megamix' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def behind_scenes_penalty(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'behind the scenes' in query.lower() or 'making of' in query.lower():
            score = 0
        elif 'behind the scenes' in title or 'making of' in title:
            score = -30
        else:
            score = 0
        return score

    @log
    def cover_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'cover' in query.lower():
            score = 0
        elif 'cover' in title:
            score = -40
        else:
            score = 0
        return score

    @log
    def guitar_lesson_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'guitar lesson' in query.lower():
            score = 0
        elif 'guitar lesson' in title:
            score = -40
        else:
            score = 0
        return score


    @log
    def with_tabs_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'with tabs' in query.lower():
            score = 0
        elif 'with tabs' in title:
            score = -40
        else:
            score = 0
        return score

    @log
    def at_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if '@' in query.lower():
            score = 0
        elif '@' in title:
            score = -40
        else:
            score = 0
        return score

    @log
    def prefer_licensed(self, video_metadata, query):
        metadata = video_metadata[2]
        metadata = metadata.get('metadata', {}).get('contentDetails', {}).get('licensedContent', None)
        if metadata == False:
            score = -10
        else:
            score = 0
        return score

    @log
    def prefer_processed(self, video_metadata, query):
        metadata = video_metadata[2]
        metadata = metadata.get('metadata', {}).get('status', {}).get('uploadStatus', None)
        if metadata != 'processed':
            score = -50
        else:
            score = 0
        return score

    @log
    def prefer_vevo(self, video_metadata, query):
        metadata = video_metadata[2]
        metadata = metadata.get('channelTitle', None)
        if metadata.lower().endswith('vevo'):
            score = 40
        else:
            score = 0
        return score

    @log
    def prefer_music_video(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'music video' in title:
            score = 35
        else:
            score = 0
        return score


    @log
    def live_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if re.match(r'.+\(?.+live?.+?\)?', query.lower(), flags=re.I) is not None:
            score = 0
        elif re.match(r'.+\(?.+live?.+?\)?', title, flags=re.I) is not None:
            score = -50
        else:
            score = 0
        return score

    @log
    def teaser_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if re.match(r'.+\(?.+teaser?.+?\)?', query.lower(), flags=re.I) is not None:
            score = 0
        elif re.match(r'.+\(?.+teaser?.+?\)?', title, flags=re.I) is not None:
            score = -50
        else:
            score = 0
        return score

    @log
    def audio_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if re.match(r'.+\(?.+audio?.+?\)?', query.lower(), flags=re.I) is not None:
            score = 0
        elif re.match(r'.+\(?.+audio?.+?\)?', title, flags=re.I) is not None:
            score = -20
        else:
            score = 0
        return score

    @log
    def lyrics_in_title(self, video_metadata, query):
        title = video_metadata[0].lower()
        if re.match(r'.+\(?.+lyric?.+?\)?', query.lower(), flags=re.I) is not None:
            score = 0
        elif re.match(r'.+\(?.+lyric?.+?\)?', title, flags=re.I) is not None:
            score = -50
        else:
            score = 0
        return score

    @log
    def prefer_official(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'official' in query.lower():
            score = 0
        elif 'official' in title:
            score = 20
        else:
            score = 0
        return score

    @log
    def prefer_official_video(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'official video' in query.lower():
            score = 0
        elif 'official video' in title:
            score = 20
        else:
            score = 0
        return score

    @log
    def prefer_original(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'original' in query.lower():
            score = 0
        elif 'original' in title:
            score = 20
        else:
            score = 0
        return score

    @log
    def prefer_no_parody(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'parody' in query.lower():
            score = 0
        elif 'parody' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def prefer_no_karaoke(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'karaoke' in query.lower():
            score = 0
        elif 'karaoke' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def prefer_no_trailer(self, video_metadata, query):
        title = video_metadata[0].lower()
        if 'trailer' in query.lower():
            score = 0
        elif 'trailer' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def prefer_no_tutorial(self, video_metadata, query):
        title = video_metadata[0].lower()
        # TODO: Extend this
        if 'tutorial' in query.lower():
            score = 0
        elif 'tutorial' in title:
            score = -30
        else:
            score = 0
        return score

    @log
    def prefer_no_makeup(self, video_metadata, query):
        title = video_metadata[0].lower()
        # TODO: Extend this
        if 'makeup' in query.lower():
            score = 0
        elif 'makeup' in title:
            score = -30
        else:
            score = 0
        return score

    @log
    def prefer_no_chipmunks(self, video_metadata, query):
        title = video_metadata[0].lower()
        # TODO: Extend this
        if 'chipmunks' in query.lower():
            score = 0
        elif 'chipmunks' in title:
            score = -20
        else:
            score = 0
        return score

    @log
    def prefer_startswith(self, video_metadata, query):
        title = video_metadata[0].lower()
        query = query.lower()
        query = query.split('-')[0]
        if title.startswith(query.lower()):
            score = 30
        else:
            score = 0
        return score


    @log
    def prefer_popular(self, video_metadata, query):
        ratio = int(video_metadata[2].get('satisfaction', 0))
        score = int(log10(1 + 100 / ( 1 + 100 - ratio)) * 5)
        return score

    @log
    def prefer_shorter(self, video_metadata, query):
        duration = video_metadata[2].get('metadata', {}).get('contentDetails', {}).get('duration', {})
        duration = DateMan.iso2hms(duration)
        duration = duration.split(':')
        duration.reverse()
        length = 0
        try:
            for idx, item in enumerate(duration):
                length += int(duration[idx]) * math_pow(60, idx)
        except Exception as exc:
            logger.error('score:prefer_shorter:%r', duration)
            return 0
        # less than 15 minutes
        if length <= 900:
            score = 0
        else:
            score = -20
        return score

    def calculate(self, video_metadata, query):
        if type(video_metadata) != list or len(video_metadata) != 3:
            raise RuntimeError('%r %s %r' % (self.__class__, ' got invalid data (type): ', video_metadata))
        score = self.default_score
        for rule in self.ruleset:
            score += rule(video_metadata, query)
        return score
