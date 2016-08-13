import re
from .basetask import BasePlayerTask

class AlbumTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = '^play (?:songs|tracks) from (.+) by (.+)$'
    __priority__ = 60
    __actiontype__ = 'artist_album'

    @classmethod
    def play_artist_album(cls, artist, album):
        '''
        Play all tracks from album
        '''
        tracks = cls.lfm.get_tracks_for_album(artist, album)
        random.shuffle(tracks)
        for track in tracks:
            if cls.exit_task:
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, message):
        album, artist = re.match(cls.__regexp__, message).groups()
        cls.play_artist_album(artist, album)
