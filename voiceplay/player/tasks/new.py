#-*- coding: utf-8 -*-
""" New tracks module """

import datetime
import random
random.seed()
import re

from voiceplay.datasources.mbapi import MBAPI
from voiceplay.utils.track import TrackNormalizer
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher

from .basetask import BasePlayerTask


class NewTracksResource(APIV1Resource):
    """
    New track API endpoint
    """
    route_base = '/api/v1/play/new_tracks/<artist>'
    queue = None
    def post(self, artist):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and artist:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play new tracks by' + ' %s ' % artist)
            result = {'status': 'ok', 'message': message}
        return result


class NewTask(BasePlayerTask):
    """
    Find and play recent/new tracks by provided artist
    """
    __group__ = ['play']
    __regexp__ = ['^play (?:fresh|new) (?:tracks|songs) (?:from|by) (.+)$']
    __priority__ = 150

    @classmethod
    def get_new_tracks(cls, artist, starting_year):
        """
        Get new tracks
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
            date = release.get('date', 0)
            if not re.match('^[0-9]+$', date):
                continue
            if year >= int(date) >= starting_year:
                album_mbid = release.get('mbid', '')
                if album_mbid:
                    albums.append(album_mbid)

        for album in albums:
            for release in mbapi.get_recordings(album):
                title = release.get('title', '')
                if title and TrackNormalizer.track_ok(title) and not TrackNormalizer.is_locally_blacklisted(pretty_track):
                    tracks.append(pretty_track)

        releases = mbapi.get_releases(artist_mbid, rtypes=['single'])
        for release in releases:
            date = release.get('date', 0)
            if not re.match('^[0-9]+$', date):
                continue
            if year >= int(date) >= starting_year:
                title = release.get('title', '')
                pretty_track = u'{0!s} - {1!s}'.format(artist, title)
                if title and TrackNormalizer.track_ok(title) and not TrackNormalizer.is_locally_blacklisted(pretty_track):
                    tracks.append(pretty_track)
        return tracks


    @classmethod
    def play_new_tracks(cls, artist):
        """
        Play new tracks by provided artist
        """
        year = datetime.date.today().year
        year_max = year - 1960 # well, there's possibly a better way to define this :)
        for diff in range(1, year_max + 1):
            starting_year = year - diff
            tracks = cls.get_new_tracks(artist, starting_year)
            if tracks:
                break
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
