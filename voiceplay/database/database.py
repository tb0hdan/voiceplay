# -*- coding: utf-8 -*-
''' VoicePlay database container '''

import datetime
import os
import time
from pony.orm import db_session, select
from voiceplay.logger import logger
from voiceplay.config import Config
from .entities import db, Artist, PlayedTracks

class VoicePlayDB(object):
    '''
    VoicePlay Database
    '''
    def __init__(self, filename=None, debug=False):
        self.debug = debug
        self.db = db
        if filename:
            self.filename = filename
        else:
            self.filename = os.path.expanduser(os.path.join(Config.persistent_dir, 'sqlite.db'))

    @staticmethod
    def get_dt():
        d = datetime.datetime.now()
        dt = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
        return dt

    def configure(self):
        self.db.bind('sqlite', self.filename, create_db=True)
        self.db.generate_mapping(create_tables=True)

    def write_artist_image(self, artist, picture):
        with db_session:
            dt = self.get_dt()
            # pylint:disable=unexpected-keyword-arg,no-value-for-parameter
            artist = Artist(name=artist, created_at=dt, updated_at=dt, image=picture)

    def get_artist_image(self, artist):
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
        with db_session:
            return [record.track for record in PlayedTracks.select()]


voiceplaydb = VoicePlayDB()
voiceplaydb.configure()
