import random
random.seed()
import re
from .basetask import BasePlayerTask

class GeoTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play top (?:songs|tracks)(?:\sin\s(.+))?$']
    __priority__ = 40
    __actiontype__ = 'top_tracks_geo'

    @classmethod
    def run_top_tracks_geo(cls, country):
        '''
        Shuffle location tracks
        '''
        if country:
            tracks = cls.lfm.get_top_tracks_geo(country)
        else:
            tracks = cls.lfm.get_top_tracks_global()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        country = re.match(regexp, message).groups()[0]
        if country:
            msg = 'Playing top track for country %s' % country
        else:
            msg = 'Playing global top tracks'
        cls.tts.say_put(msg)
        cls.run_top_tracks_geo(country)