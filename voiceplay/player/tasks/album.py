import random
random.seed()
import re
from .basetask import BasePlayerTask

class AlbumTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = ['^play (?:songs|tracks) from (.+) by (.+)$']
    __priority__ = 60
    __actiontype__ = 'artist_album'

    @classmethod
    def play_artist_album(cls, artist, album):
        '''
        Play all tracks from album
        '''
        tracks = cls.lfm.get_tracks_for_album(artist, album)
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        album, artist = re.match(regexp, message).groups()
        cls.say('%s album by %s' % (album, artist))
        cls.play_artist_album(artist, album)
