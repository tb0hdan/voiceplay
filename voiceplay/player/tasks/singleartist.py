class SingleArtistTask(BasePlayerTask):
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
