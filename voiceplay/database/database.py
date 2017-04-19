# -*- coding: utf-8 -*-
""" VoicePlay database container """

import datetime
import os
from pony.orm import db_session, commit
from voiceplay.config import Config
from .entities import (db,
                       Artist,
                       PlayedTracks,
                       LastFmCache,
                       ServiceCache)


class VoicePlayDB(object):
    """
    VoicePlay Database
    """
    def __init__(self, filename=None, debug=False):
        self.debug = debug
        self.db = db
        if filename:
            self.filename = filename
        else:
            try:
                os.makedirs(os.path.expanduser(Config.persistent_dir))
            except Exception as _:
                pass
            self.filename = os.path.expanduser(os.path.join(Config.persistent_dir, 'sqlite.db'))

    @staticmethod
    def get_dt():
        """
        Get datetime object
        TODO: Make this simpler
        """
        d = datetime.datetime.now()
        dt = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
        return dt

    def configure(self):
        """
        Configure database
        """
        self.db.bind('sqlite', self.filename, create_db=True)
        self.db.generate_mapping(create_tables=True)

    def write_artist_image(self, artist, picture):
        """
        Store artist cover image
        """
        with db_session:
            dt = self.get_dt()
            # pylint:disable=unexpected-keyword-arg,no-value-for-parameter
            artist = Artist(name=artist, created_at=dt, updated_at=dt, image=picture)

    def get_artist_image(self, artist):
        """
        Get artist cover image
        """
        with db_session:
            # pylint:disable=no-value-for-parameter
            artist = Artist.get(name=artist)
            if artist and artist.image:
                dt = self.get_dt()
                artist.updated_at = dt
                return artist.image
            else:
                return None

    def update_played_tracks(self, trackname):
        """
        Update played tracks count
        """
        with db_session:
            tracks = PlayedTracks.get(track=trackname)
            dt = self.get_dt()
            if tracks and tracks.playcount:
                playcount = tracks.playcount + 1
                created_at = tracks.created_at
                #
                tracks.updated_at = dt
                tracks.playcount = playcount
                return playcount
            else:
                created_at = dt
                tracks = PlayedTracks(track=trackname, created_at=created_at, updated_at=dt, playcount=1,
                                      status='neutral')
                return 1

    @staticmethod
    def get_played_tracks():
        """
        Get list of playback history
        """
        with db_session:
            return [record.track for record in PlayedTracks.select()]

    def get_lastfm_method(self, method, args, expires=7):
        """
        Wrapper for caching last.fm method responses in database
        Works with expiration date.
        """
        with db_session:
            result = None
            record = LastFmCache.get(method_args=method + args)
            dt = self.get_dt()
            if record and dt - record.updated_at <= datetime.timedelta(days=expires):
                result = record.content
            elif record:
                LastFmCache[record.method_args].delete()
            return result

    def set_lastfm_method(self, method, args, content):
        """
        Store last.fm method response in database
        Works with expiration date.
        """
        with db_session:
            dt = self.get_dt()
            _ = LastFmCache(method_args=method + args, created_at=dt, updated_at=dt, content=content)
            commit()

    def get_cached_service(self, service_name, expires=1):
        """
        Get service response from database.
        https://github.com/tb0hdan/voiceplay/issues/15
        """
        with db_session:
            result = None
            record = ServiceCache.get(service_name=service_name)
            dt = self.get_dt()
            if record and dt - record.updated_at <= datetime.timedelta(days=expires):
                result = record.content
            elif record:
                ServiceCache[record.service_name].delete()
            return result

    def set_cached_service(self, service_name, content):
        """
        Store service response in database
        Works with expiration date.
        https://github.com/tb0hdan/voiceplay/issues/15
        """
        with db_session:
            dt = self.get_dt()
            _ = ServiceCache(service_name=service_name, created_at=dt, updated_at=dt, content=content)
            commit()

    def set_track_status(self, trackname, status):
        """
        Update track status:
        love/neutral/ban
        """
        if not status in ['loved', 'neutral', 'banned']:
            return
        with db_session:
            track = PlayedTracks.get(track=trackname)
            if track and track.status != status:
                track.status = status
            elif not track:
                dt = self.get_dt()
                PlayedTracks(track=trackname, created_at=dt, updated_at=dt, playcount=1, status=status)

    @staticmethod
    def get_track_status(trackname):
        """
        Get track status
        """
        with db_session:
            track = PlayedTracks.get(track=trackname)
            if track:
                status = track.status
            else:
                status = 'neutral'
        return status


voiceplaydb = VoicePlayDB()
voiceplaydb.configure()
