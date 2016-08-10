class GeoTask(BasePlayerTask):

    __group__ = 'play'
    __regexp__ = 
    __actiontype__ = 

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
        for track in tracks:
            if cls.exit_task:
                break
            cls.play_full_track(track)
