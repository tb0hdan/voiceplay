#-*- coding: utf-8 -*-
""" Top tracks module """

import json
import random
random.seed()
import re
import requests

from bs4 import BeautifulSoup

from voiceplay.utils.requestor import WSRequestor

from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.utils.helpers import SingleQueueDispatcher
from voiceplay.utils.track import TrackNormalizer
from .basetask import BasePlayerTask


class TopTracksResource(APIV1Resource):
    """
    Top tracks API endpoint
    """
    route_base = '/api/v1/play/top/<query>'
    queue = None
    def post(self, query):
        """
        HTTP POST handler
        """
        result = {'status': 'timeout', 'message': ''}
        if self.queue and query:
            dispatcher = SingleQueueDispatcher(queue=self.queue)
            message = dispatcher.send_and_wait('play top' + ' %s ' % query + 'tracks')
            result = {'status': 'ok', 'message': message}
        return result


class RS500Requestor(WSRequestor):
    """
    Rolling stone 5000 greatest songs requestor
    """
    cache_file = 'rs500.dat'
    base_url = 'https://www.rollingstone.com/music/lists/the-500-greatest-songs-of-all-time-20110407'

    @staticmethod
    def normalize_item(rs_track):
        """
        Normalize track name
        """
        title = rs_track.get('title', '')
        # some safety
        if not title:
            return []
        artist, track = re.match('^(.+)\,\s\'?(.+)\'?$', title).groups()
        return [artist, track.rstrip("'")]

    def get_tracks(self, page_url, cookies):
        """
        Get tracks from single page
        """
        tracks = []
        resp = requests.get(page_url, headers=self.headers, cookies=cookies)
        items = json.loads(resp.text).get('items', [])
        for item in items:
            tracks.append(self.normalize_item(item))
        return tracks

    def get_all(self):
        """
        Get tracks from all pages
        """
        all_tracks = []
        data = requests.get(self.base_url, headers=self.headers)
        cookies = data.cookies
        for page in range(1, 10 + 1):
            tracks = self.get_tracks(self.base_url + '?json=true&page={0}&limit=50'.format(page), cookies)
            all_tracks += tracks
        return [item for item in all_tracks if not TrackNormalizer.is_locally_blacklisted(item)]


class BB100Requestor(WSRequestor):
    """
    Billboard hot 100 tracks requestor
    """
    cache_file = 'bb100.dat'
    base_url = 'http://www.billboard.com/charts/hot-100'

    def get_all(self):
        """
        Get all tracks
        """
        all_tracks = []
        data = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'div' and 'chart-row__title' in tag.get('class', [])):
            artist = None
            title = None
            for title in element.find_all(lambda tag: tag.name == 'h2' and 'chart-row__song' in tag.get('class', [])):
                if title.text:
                    title = title.text.strip()
                    break
            for artist in element.find_all(lambda tag: tag.name == 'a' and 'chart-row__artist' in tag.get('class', [])):
                if artist.text:
                    artist = artist.text.strip()
                    break
            if title and artist:
                all_tracks.append(u'{0!s} - {1!s}'.format(artist, title))
        return [item for item in all_tracks if not TrackNormalizer.is_locally_blacklisted(item)]


class RedditMusicRequestor(WSRequestor):
    """
    Reddit hot music requestor
    """
    cache_file = 'reddit_music.dat'
    base_url = 'https://www.reddit.com/r/Music/search.json?q=flair%3A%22music+streaming%22&sort=hot&restrict_sr=on&t=week'

    def get_all(self):
        """
        Get all tracks
        """
        all_tracks = []
        data = requests.get(self.base_url, headers=self.headers)
        children = json.loads(data.text).get('data', {}).get('children', [])
        for element in children:
            track = element.get('data', {}).get('title', '')
            if not track:
                continue
            track = re.sub('\s\[(.+)$', '', track)
            all_tracks.append(track)
        return [item for item in all_tracks if not TrackNormalizer.is_locally_blacklisted(item)]


class TopTracksTask(BasePlayerTask):
    """
    Play top tracks from different services
    """
    __group__ = ['play', 'top']
    __regexp__ = ['^play top (?:songs|tracks)(?:\sin\s(.+))?$', '^(?:play\stop|top) 500 tracks?$',
                  '^(?:play\stop|top) 100 tracks?$', '^(?:play\stop|top) reddit tracks?$']
    __priority__ = 40

    @classmethod
    def run_top_tracks_geo(cls, country):
        """
        Shuffle top tracks global or for specific country
        """
        if country:
            tracks = cls.lfm().get_top_tracks_geo(country)
        else:
            tracks = cls.lfm().get_top_tracks_global()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def run_rs500(cls, *args):
        """
        Shuffle Rolling stone 500 tracks
        """
        rs = RS500Requestor()
        tracks = [u'{0!s} - {1!s}'.format(artist, track) for artist, track in rs.get_check_all()]
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def run_bb100(cls, *args):
        """
        Shuffle Billboard 100 tracks
        """
        bb = BB100Requestor()
        tracks = bb.get_check_all()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def run_reddit_music(cls, *args):
        """
        Shuffle reddit music
        """
        rm = RedditMusicRequestor()
        tracks = rm.get_check_all()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():  # pylint:disable=no-member
                break
            cls.play_full_track(track)

    @classmethod
    def process(cls, regexp, message):
        """
        Run task / dispatch commands
        """
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        param = None
        if re.match(regexp, message, re.I).groups():
            param = re.match(regexp, message, re.I).groups()[0]
            msg = 'Playing top track for country %s' % param
            method = cls.run_top_tracks_geo
        elif '100' in regexp:
            msg = 'Playing Billboard top 100 tracks'
            method = cls.run_bb100
        elif '500' in regexp:
            msg = 'Playing Rolling Stone top 500 greatest songs'
            method = cls.run_rs500
        elif 'reddit' in regexp:
            msg = 'Playing Reddit music (hot week)'
            method = cls.run_reddit_music
        else:
            msg = 'Playing global top tracks'
            method = cls.run_top_tracks_geo
        cls.say(msg)
        method(param)
