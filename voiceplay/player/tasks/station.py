class StationTask(BasePlayerTask):

    __group__ = 'play'
    __regexp__ = 
    __actiontype__ = 

    @classmethod
    def play_station(cls, station):
        '''
        Play top tracks for station
        '''
        tracks = cls.lfm.get_station(station)
        random.shuffle(tracks)
        for track in tracks:
            if cls.exit_task:
                break
            cls.play_full_track(track)
