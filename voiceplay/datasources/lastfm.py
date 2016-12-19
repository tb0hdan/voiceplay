#-*- coding: utf-8 -*-

import json
import pylast
from voiceplay.config import Config
from voiceplay.database import voiceplaydb
from voiceplay.logger import logger

def lfm_retry(retry_count=1):
    def lfm_retry_func(func):
        def func_wrapper(*args, **kwargs):
            rargs = list(args)
            rargs.pop(0)
            rargs = str(rargs) + str(kwargs)
            func_name = str(func.func_name)
            result = voiceplaydb.get_lastfm_method(func_name, rargs)
            result = json.loads(result) if result else None
            if result:
                return result
            for retry in xrange(1, retry_count + 1):
                try:
                    result = func(*args, **kwargs)
                    if result:
                        voiceplaydb.set_lastfm_method(func_name, rargs, json.dumps(result))
                    break
                except Exception as exc:
                    logger.debug('Method/function %r failed with %r, retrying...', func_name, exc)
            return result
        return func_wrapper
    return lfm_retry_func

class VoicePlayLastFm(object):
    '''
    Last.Fm API
    '''
    def __init__(self):
        cfg_data = Config.cfg_data()
        self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                            api_secret=cfg_data['lastfm']['secret'])

    @lfm_retry(retry_count=3)
    def get_top_tracks_geo(self, country_code):
        '''
        Country name: ISO 3166-1
        '''
        tracks = self.network.get_geo_top_tracks(country_code)
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_top_tracks_global(self):
        '''
        Global top tracks (chart)
        '''
        tracks = self.network.get_top_tracks()
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_top_tracks(self, artist):
        '''
        Get top tracks by artist
        '''
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_station(self, station):
        '''
        Get station
        '''
        aobj = pylast.Tag(station, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_top_albums(self, artist):
        album_list = []
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        albums = aobj.get_top_albums()
        for album in albums:
            album_list.append(album.item.title)
        return album_list

    @lfm_retry(retry_count=3)
    def get_tracks_for_album(self, artist, album):
        result = []
        artist = self.get_corrected_artist(artist)
        tracks = pylast.Album(artist, album.title(), self.network).get_tracks()
        for track in tracks:
            result.append(track.artist.name + ' - ' + track.title)
        return result

    @lfm_retry(retry_count=3)
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

    @lfm_retry(retry_count=3)
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

    @lfm_retry(retry_count=3)
    def get_artist_icon(self, artist, image_size=pylast.COVER_SMALL):
        '''
        Get artist icon
        supported sizes: small, medium, large
        '''
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        return aobj.get_cover_image(image_size)

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
