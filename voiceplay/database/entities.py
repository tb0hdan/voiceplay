# -*- coding: utf-8 -*-
""" VoicePlay database entities container """

from datetime import datetime
from pony.orm import Database, PrimaryKey, Required
from pony.orm.ormtypes import buffer

# pylint:disable=invalid-name
db = Database()


class Artist(db.Entity):
    """
    Artist database entity container
    """
    name = PrimaryKey(str)
    created_at = Required(datetime)
    updated_at = Required(datetime)
    image = Required(buffer)


class PlayedTracks(db.Entity):
    """
    Save played tracks for history and stats
    """
    track = PrimaryKey(str)
    created_at = Required(datetime)
    updated_at = Required(datetime)
    playcount = Required(int)
    # loved/banned/neutral
    status = Required(str)


class LastFmCache(db.Entity):
    """
    Cache last.fm results
    """
    method_args = PrimaryKey(str)
    created_at = Required(datetime)
    updated_at = Required(datetime)
    content = Required(str)


class ServiceCache(db.Entity):
    """
    Cache service results
    """
    service_name = PrimaryKey(str)
    created_at = Required(datetime)
    updated_at = Required(datetime)
    content = Required(str)
