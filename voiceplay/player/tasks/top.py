import json
import os
import random
random.seed()
import re
import requests

from bs4 import BeautifulSoup

from voiceplay.config import Config
from voiceplay.logger import logger
from .basetask import BasePlayerTask

class WSRequestor(object):
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'
                                            ])}

    def get_check_all(self):
        try:
            os.makedirs(os.path.expanduser(Config.persistent_dir))
        except Exception as exc:
            logger.debug('Persistent directory exists, good...')
        cache_file = os.path.expanduser(os.path.join(Config.persistent_dir, self.cache_file))

        if os.path.exists(cache_file):
            logger.debug('Using %s cached version...', self.cache_file)
            result = json.loads(open(cache_file, 'r').read())
        else:
            logger.debug('Fetching and storing fresh %s version...', self.cache_file)
            result = self.get_all()
            with open(cache_file, 'w') as file_handle:
                file_handle.write(json.dumps(result))
        return result


class RS500Requestor(WSRequestor):
    cache_file = 'rs500.dat'
    base_url = 'https://www.rollingstone.com/music/lists/the-500-greatest-songs-of-all-time-20110407'

    @staticmethod
    def normalize_item(rs_track):
        title = rs_track.get('title', '')
        # some safety
        if not title:
            return []
        artist, track = re.match('^(.+)\,\s\'?(.+)\'?$', title).groups()
        return [artist, track.rstrip("'")]

    def get_tracks(self, page_url, cookies):
        tracks = []
        resp = requests.get(page_url, headers=self.headers, cookies=cookies)
        items = json.loads(resp.text).get('items', [])
        for item in items:
            tracks.append(self.normalize_item(item))
        return tracks

    def get_all(self):
        all_tracks = []
        data = requests.get(self.base_url, headers=self.headers)
        cookies = data.cookies
        for page in range(1, 10 + 1):
            tracks = self.get_tracks(self.base_url + '?json=true&page={0}&limit=50'.format(page), cookies)
            all_tracks += tracks
        return all_tracks


class BB100Requestor(WSRequestor):
    cache_file = 'bb100.dat'
    base_url = 'http://www.billboard.com/charts/hot-100'

    def get_all(self):
        all_tracks = []
        data = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(''.join(data.text), 'html.parser')
        for element in soup.find_all(lambda tag: tag.name == 'div' and 'chart-row__title' in tag.get('class', [])):
            for title in element.find_all(lambda tag: tag.name == 'h2' and 'chart-row__song' in tag.get('class', [])):
                if title.text:
                    break
            for artist in element.find_all(lambda tag: tag.name == 'a' and 'chart-row__artist' in tag.get('class', [])):
                if artist.text:
                    break
            all_tracks.append(u'{0!s} - {1!s}'.format(artist.text.strip(), title.text.strip()))
        return all_tracks



class TopTracksTask(BasePlayerTask):

    __group__ = ['play', 'top']
    __regexp__ = ['^play top (?:songs|tracks)(?:\sin\s(.+))?$', '^(?:play\stop|top) 500 tracks?$',
                  '^(?:play\stop|top) 100 tracks?$']
    __priority__ = 40
    __actiontype__ = 'top_tracks_task'

    @classmethod
    def run_top_tracks_geo(cls, country):
        '''
        Shuffle location tracks
        '''
        if country:
            tracks = cls.lfm.get_top_tracks_geo(country)
        else:
            tracks = cls.lfm.get_top_tracks_global()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():
                break
            cls.play_full_track(track)

    @classmethod
    def run_rs500(cls):
        rs = RS500Requestor()
        tracks = [u'{0!s} - {1!s}'.format(artist, track) for artist, track in rs.get_check_all()]
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():
                break
            cls.play_full_track(track)

    @classmethod
    def run_bb100(cls):
        bb = BB100Requestor()
        tracks = bb.get_check_all()
        random.shuffle(tracks)
        for track in cls.tracks_with_prefetch(tracks):
            if cls.get_exit():
                break
            cls.play_full_track(track)


    @classmethod
    def process(cls, regexp, message):
        cls.logger.debug('Message: %r matches %r, running %r', message, regexp, cls.__name__)
        if re.match(regexp, message).groups():
            country = re.match(regexp, message).groups()[0]
            msg = 'Playing top track for country %s' % country
            cls.tts.say_put(msg)
            cls.run_top_tracks_geo(country)
        elif '100' in regexp:
            msg = 'Playing Billboard top 100 tracks'
            cls.tts.say_put(msg)
            cls.run_bb100()
        elif '500' in regexp:
            msg = 'Playing Rolling Stone top 500 greatest songs'
            cls.tts.say_put(msg)
            cls.run_rs500()
        else:
            msg = 'Playing global top tracks'
            cls.tts.say_put(msg)
            cls.run_top_tracks_geo(country)
