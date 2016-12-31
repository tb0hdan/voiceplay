# -*- coding: utf-8 -*-
""" VoicePlay database container """

import datetime
import os
import time
from pony.orm import db_session, select, commit
from voiceplay.logger import logger
from voiceplay.config import Config
from .entities import db, Artist, PlayedTracks, LastFmCache

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
                tracks = PlayedTracks(track=trackname, created_at=dt, updated_at=dt, playcount=1)
                return 1

    def get_played_tracks(self):
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
            cache = LastFmCache(method_args=method + args, created_at=dt, updated_at=dt, content=content)
            commit()


voiceplaydb = VoicePlayDB()
voiceplaydb.configure()
