class AlbumTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = 
    __actiontype__ = 

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
