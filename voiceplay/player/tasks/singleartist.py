import random
random.seed()
import re
from .basetask import BasePlayerTask


class SingleArtistTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = '^play some (?:music|tracks?|songs?) by (.+)$'
    __priority__ = 20
    __actiontype__ = 'shuffle_artist'

    @classmethod
    def run_shuffle_artist(cls, artist):
        '''
        Shuffle artist tracks
        '''
        if cls.lfm.get_query_type(artist) == 'artist':
            tracks = cls.lfm.get_top_tracks(cls.lfm.get_corrected_artist(artist))
            random.shuffle(tracks)
            for track in tracks:
                if cls.exit_task:
                    break
                cls.play_full_track(track)

    @classmethod
    def process(cls, message):
        artist = re.match(cls.__regexp__, message).groups()[0]
        #self.tts.say_put('Shuffling %s' % artist)
        cls.run_shuffle_artist(artist)
