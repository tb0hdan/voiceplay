#-*- coding: utf-8 -*-
""" New tracks module """

import datetime
import random
random.seed()
import re

from voiceplay.datasources.mbapi import MBAPI
from voiceplay.utils.track import TrackNormalizer

from .basetask import BasePlayerTask


class NewTask(BasePlayerTask):
    """
    Find and play recent/new tracks by provided artist
    """
    __group__ = ['play']
    __regexp__ = ['^play (?:fresh|new) (?:tracks|songs) (?:from|by) (.+)$']
    __priority__ = 150
    __actiontype__ = 'new_tracks_task'

    @classmethod
    def play_new_tracks(cls, artist):
        """
        Play new tracks by provided artist
        """
        mbapi = MBAPI()
        artist = cls.lfm().get_corrected_artist(artist)
        artist_mbid = mbapi.get_artist_mbid(artist)
        releases = mbapi.get_releases(artist_mbid, rtypes=['album'])
        # get this year's albums
        year = datetime.date.today().year
        albums = []
        tracks = []
        for release in releases:
            if not release.get('date', 0):
                continue
            date = int(release.get('date', 0))
            if year >= date >= year - 1:
                album_mbid = release.get('mbid', '')
                if album_mbid:
                    albums.append(album_mbid)

        for album in albums:
            for release in mbapi.get_recordings(album):
                title = release.get('title', '')
                if title and TrackNormalizer.track_ok(title):
                    tracks.append(u'{0!s} - {1!s}'.format(artist, title))

        releases = mbapi.get_releases(artist_mbid, rtypes=['single'])
        for release in releases:
            date = int(release.get('date', 0))
            if year >= date >= year - 1:
                title = release.get('title', '')
                # TODO: move this out to track blacklists
                if title and TrackNormalizer.track_ok(title):
                    tracks.append(u'{0!s} - {1!s}'.format(artist, title))

        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        """
        Run task
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        artist = re.match(regexp, message, re.I).groups()[0]
        artist = cls.lfm().get_corrected_artist(artist)
        cls.say('Playing new tracks by %s' % artist)
        cls.play_new_tracks(artist)
