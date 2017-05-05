#-*- coding: utf-8 -*-
""" Last.FM API module with retries and caching """

import datetime
import json
import logging
import random
random.seed()
import sys
import time

from copy import deepcopy
# works after installing `future` package
from queue import Queue  # pylint:disable=import-error


import pylast

from tqdm import tqdm

from voiceplay.config import Config
from voiceplay.database import voiceplaydb
from voiceplay.logger import logger
from voiceplay.utils.helpers import debug_traceback
from voiceplay.utils.track import TrackNormalizer


def lfm_retry(retry_count=1):
    """
    Retry + cache decorator
    """
    def lfm_retry_func(func):
        """
        retry function
        """
        def func_wrapper(*args, **kwargs):
            """
            function wrapper
            """
            rargs = list(args)
            rargs.pop(0)
            rargs = str(rargs) + str(kwargs)
            func_name = str(func.__name__)
            result = voiceplaydb.get_lastfm_method(func_name, rargs)
            result = json.loads(result) if result else None
            if result:
                return result
            for _ in range(1, retry_count + 1):
                try:
                    result = func(*args, **kwargs)
                    if result:
                        voiceplaydb.set_lastfm_method(func_name, rargs, json.dumps(result))
                    break
                except Exception as exc:
                    message = 'Method/function %r failed with %r, retrying...' % (func_name, exc)
                    debug_traceback(sys.exc_info(), __file__, message=message)
            return result
        return func_wrapper
    return lfm_retry_func


class VoicePlayLastFm(object):
    """
    Last.Fm API
    """
    def __init__(self):
        cfg_data = Config.cfg_data()
        try:
            self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                                api_secret=cfg_data['lastfm']['secret'],
                                                username=cfg_data['lastfm']['username'],
                                                password_hash=cfg_data['lastfm']['password'])
            self.scrobble_enabled = True
        except Exception as _:
            # last.fm network registration failed, possibly due to scrobbling/API issue, try data only
            self.scrobble_enabled = False
            self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                            api_secret=cfg_data['lastfm']['secret'])

    @lfm_retry(retry_count=3)
    def get_top_tracks_geo(self, country_code):
        """
        Get top tracks based on country of origin.
        Country name: ISO 3166-1
        """
        tracks = self.network.get_geo_top_tracks(country_code)
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_top_tracks_global(self):
        """
        Global top tracks (chart)
        """
        tracks = self.network.get_top_tracks()
        return self.trackarize(tracks)

    @lfm_retry(retry_count=3)
    def get_top_tracks(self, artist):
        """
        Get top tracks by artist
        """
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        tracks = self.trackarize(aobj.get_top_tracks())
        return [item for item in tracks if not TrackNormalizer.is_locally_blacklisted(item)]

    @lfm_retry(retry_count=3)
    def get_station(self, query):
        """
        Get station based on artist/tag
        """
        if self.get_query_type(query) != 'artist':
            aobj = pylast.Tag(query, self.network)
            tracks = self.trackarize(aobj.get_top_tracks())
        else:
            tracks = []
            for artist in self.get_similar_artists(query):
                tracks += self.get_top_tracks(artist)
        return tracks

    @lfm_retry(retry_count=3)
    def get_top_albums(self, artist):
        """
        Get top albums for provided artist
        """
        album_list = []
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        albums = aobj.get_top_albums()
        for album in albums:
            album_list.append(album.item.title)
        return album_list

    @lfm_retry(retry_count=3)
    def get_tracks_for_album(self, artist, album):
        """
        Get top tracks for artist + album
        """
        result = []
        artist = self.get_corrected_artist(artist)
        tracks = pylast.Album(artist, album.title(), self.network).get_tracks()
        for track in tracks:
            pretty_track = track.artist.name + ' - ' + track.title
            if not TrackNormalizer.is_locally_blacklisted(pretty_track):
                result.append(pretty_track)
        return result

    @lfm_retry(retry_count=3)
    def get_corrected_artist(self, artist):
        """
        Get corrected artist
        """
        a_s = pylast.ArtistSearch(artist, self.network)
        reply = a_s.get_next_page()
        if isinstance(reply, list) and reply:
            return reply[0].name
        else:
            return artist

    @lfm_retry(retry_count=3)
    def get_query_type(self, query):
        """
        Detect whether query is just artist or artist - track or tag (dull smiley)
        """
        query = query.lower()
        text = query.capitalize()
        # known issue, see http://www.last.fm/music/Vocal+Trance
        if query == 'vocal trance':
            reply = 'artist_track'
        elif self.get_corrected_artist(text).lower() == text.lower():
            reply = 'artist'
        else:
            reply = 'artist_track'
        return reply

    @lfm_retry(retry_count=3)
    def get_artist_icon(self, artist, image_size=pylast.COVER_SMALL):
        """
        Get artist icon
        supported sizes: small, medium, large
        """
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        return aobj.get_cover_image(image_size)

    @lfm_retry(retry_count=3)
    def get_artist_tags(self, artist, limit=10):
        """
        Get artist tags
        """
        tags = []
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        # make sure this is sorted
        for tag in sorted(aobj.get_top_tags(), key=lambda item: int(item.weight), reverse=True):
            tags.append(tag.item.get_name().lower())
        return tags[:limit]

    @lfm_retry(retry_count=3)
    def get_similar_artists(self, artist, limit=10):
        """
        Get similar artists
        """
        artist = self.get_corrected_artist(artist)
        result = []
        aobj = pylast.Artist(artist, self.network)
        for artist in aobj.get_similar():
            result.append(artist.item.name)
        return result[:limit]

    def get_recent_tracks(self, limit=20):
        """
        Get list of recently played tracks
        """
        tracklist = []
        user = self.network.get_user(self.network.username)
        for track in user.get_recent_tracks(limit=limit):
            artist = track.track.get_artist().name
            title = track.track.get_title()
            if sys.version_info.major == 2:
                artist = artist.encode('utf8')
                title = title.encode('utf8')
            tracklist.append('{0!s} - {1!s}'.format(artist, title))
        return tracklist

    def scrobble(self, artist, track):
        """
        Scrobble track
        """
        if sys.version_info.major == 2:
            artist = artist.encode('utf8')
            track = track.encode('utf8')
        full_track = '{0!s} - {1!s}'.format(artist, track)
        if not self.scrobble_enabled:
            logger.debug('Scrobbling disabled, track %r not sent', full_track)
            return
        recent_tracks = self.get_recent_tracks(limit=1)
        if full_track in recent_tracks:
            logger.debug('Scrobbling skipped, track %r already scrobbled', full_track)
            return
        logger.debug('Scrobbling track: %r', full_track)
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        self.network.scrobble(artist=artist, title=track, timestamp=timestamp)

    @staticmethod
    def trackarize(array):
        """
        Convert lastfm track entities to track names
        TODO: find better name for this method
        """
        top_tracks = []
        for track in array:
            top_tracks.append(track.item.artist.name + ' - ' + track.item.title)
        return top_tracks

    @staticmethod
    def numerize(array):
        """
        Name tracks
        """
        reply = []
        for idx, element in enumerate(array):
            reply.append('%s: %s' % (idx + 1, element))
        return reply


class StationCrawl(object):
    """
    Last.FM station crawler (recursive search)
    """
    playlist_get_timeout = 60
    artist_genre_blacklist = {'black metal': ['Justin Bieber', 'Selena Gomez', 'One Direction',
                                              'Ariana Grande', 'Marilyn Manson', 'Jack Ü', 'Muse'],
                              'vocal trance': ['Groove Coverage', 'Sylver', 'Fragma', 'Franky Tunes',
                                               'Paffendorf', 'Mario Lopez', 'Niels van Gogh',
                                               'Дмитрий Филатов', 'Lasgo', 'Ian Van Dahl',
                                               'Dj Sammy', 'Jan Wayne']}

    def __init__(self):
        self.lfm = VoicePlayLastFm()
        self.exit = False
        self.genre_queue = Queue()
        self.playlist_queue = Queue()
        self.session_playlist = []

    def artist_blacklisted_for_genre(self, artist, genre):
        """
        Check if artist is blacklisted for specific genre
        """
        blacklisted = False
        blacklisted_artists = self.artist_genre_blacklist.get(genre.lower(), [])
        if artist.encode('utf-8') in blacklisted_artists:
            logger.debug('Artist %s is blacklisted for genre %s', artist, genre.lower())
            blacklisted = True
        return blacklisted

    def similar_artists(self, artist, genre):
        """
        Find similar artists for artist/genre combination
        """
        sm_artists = []
        similar = self.lfm.get_similar_artists(artist)
        iterator = tqdm(similar) if logger.level == logging.DEBUG else similar
        for similar_artist in iterator:
            if genre.lower() in self.lfm.get_artist_tags(similar_artist) and not similar_artist in sm_artists and not self.artist_blacklisted_for_genre(similar_artist, genre):
                logger.debug('Genre match for %s', similar_artist)
                sm_artists.append(similar_artist)
        return sm_artists

    def for_genre(self, genre):
        """
        Search tracks for a specific genre and add them to playlist
        """
        sm_artists = []
        # seed data
        logger.debug(genre)
        tracks = self.lfm.get_station(genre)
        random.shuffle(tracks)
        for track in tracks:
            artist = track.split(' - ')[0]
            # check station blacklist
            if self.artist_blacklisted_for_genre(artist, genre):
                continue
            # check history /banned/ blacklist
            if TrackNormalizer.is_locally_blacklisted(track):
                logger.debug('Track %s is blacklisted using "ban" command', track)
                continue
            self.playlist_queue.put(track)
            for atmp in self.similar_artists(artist, genre):
                if not atmp in sm_artists:
                    # new one
                    sm_artists.append(atmp)
                    [self.playlist_queue.put(tr) for tr in self.lfm.get_top_tracks(atmp)[:3]]
        # operate on dataset
        result = sm_artists
        for artist in sm_artists:
            tmp = self.similar_artists(artist, genre)
            for aname in tmp:
                if not aname in sm_artists and not aname in result:
                    # new one
                    result.append(aname)
                    [self.playlist_queue.put(tr) for tr in self.lfm.get_top_tracks(aname)[:3]]

    def put_genre(self, genre):
        """
        Add genre to queue
        """
        self.genre_queue.put(genre)

    def genre_loop(self):
        """
        Poll queue for newly added genres
        """
        while not self.exit:
            if self.genre_queue.empty():
                time.sleep(0.01)
                continue
            else:
                item = self.genre_queue.get()
                self.for_genre(item)

    def playlist_loop(self):
        """
        Poll playlist for newly added tracks
        """
        while not self.exit:
            if self.playlist_queue.empty():
                time.sleep(0.01)
                continue
            else:
                item = self.playlist_queue.get()
                if not item in self.session_playlist:
                    self.session_playlist.append(item)
                    session_playlist = deepcopy(self.session_playlist)
                    random.shuffle(session_playlist)
                    self.session_playlist = session_playlist

    def set_exit(self, status):
        """
        Set exit flag
        """
        self.exit = status

    @property
    def playlist(self):
        """
        Return current playlist
        """
        start = time.time()
        while time.time() - start <= self.playlist_get_timeout:
            if not self.session_playlist:
                time.sleep(0.1)
            else:
                break
        return self.session_playlist
