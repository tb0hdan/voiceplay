import kaptan
import pylast

class VoicePlayLastFm(object):
    '''
    Last.Fm API
    '''
    def __init__(self, cfg_file='config.yaml'):
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        cfg_data = config.configuration_data

        self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                            api_secret=cfg_data['lastfm']['secret'])

    def get_top_tracks_geo(self, country_code):
        '''
        Country name: ISO 3166-1
        '''
        tracks = self.network.get_geo_top_tracks(country_code)
        return self.trackarize(tracks)

    def get_top_tracks_global(self):
        '''
        Global top tracks (chart)
        '''
        tracks = self.network.get_top_tracks()
        return self.trackarize(tracks)

    def get_top_tracks(self, artist):
        '''
        Get top tracks by artist
        '''
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    def get_station(self, station):
        '''
        Get station
        '''
        aobj = pylast.Tag(station, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    def get_top_albums(self, artist):
        album_list = []
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        albums = aobj.get_top_albums()
        for album in albums:
            album_list.append(album.item.title)
        return album_list

    def get_tracks_for_album(self, artist, album):
        result = []
        artist = self.get_corrected_artist(artist)
        tracks = pylast.Album(artist, album.title(), self.network).get_tracks()
        for track in tracks:
            result.append(track.artist.name + ' - ' + track.title)
        return result

    def get_corrected_artist(self, artist):
        '''
        Get corrected artist
        '''
        a_s = pylast.ArtistSearch(artist, self.network)
        reply = a_s.get_next_page()
        if isinstance(reply, list) and reply:
            return reply[0].name
        else:
            return artist

    def get_query_type(self, query):
        '''
        Detect whether query is just artist or artist - track
        '''
        query = query.lower()
        text = query.capitalize()
        if self.get_corrected_artist(text).lower() == text.lower():
            reply = 'artist'
        else:
            reply = 'artist_track'
        return reply

    @staticmethod
    def trackarize(array):
        '''
        Convert lastfm track entities to track names
        '''
        top_tracks = []
        for track in array:
            top_tracks.append(track.item.artist.name + ' - ' + track.item.title)
        return top_tracks

    @staticmethod
    def numerize(array):
        '''
        Name tracks
        '''
        reply = []
        for idx, element in enumerate(array):
            reply.append('%s: %s' % (idx + 1, element))
        return reply
