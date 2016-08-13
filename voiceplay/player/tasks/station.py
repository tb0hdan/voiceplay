import re
from .basetask import BasePlayerTask


class StationTask(BasePlayerTask):

    __group__ = ['play']
    __regexp__ = '^play (.+) station$'
    __priority__ = 10
    __actiontype__ = 'station_artist'

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

    @classmethod
    def process(cls, message):
        station = re.match(cls.__regexp__, message).groups()[0]
        cls.tts.say_put('Playing %s station' % station)
        cls.play_station(station)
