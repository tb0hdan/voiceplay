import json
import os
import random
random.seed()
import re
import requests
import sys
if sys.version_info.major == 2:
    from Queue import Queue
    from urllib import quote
elif sys.version_info.major == 3:
    from queue import Queue
    from urllib.parse import quote

import threading
import time
import vimeo

from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
from dailymotion import Dailymotion
from math import trunc
from tempfile import mkstemp, mkdtemp
from youtube_dl import YoutubeDL

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.cmdprocessor.parser import MyParser
from voiceplay.logger import logger
from .player import MPlayerSlave

class VickiPlayer(object):
    '''
    Vicki player class
    '''
    numbers = {'1': {'name': 'one', 'adjective': 'first'},
               '2': {'name': 'two', 'adjective': 'second'},
               '3': {'name': 'three', 'adjective': 'third'},
               '4': {'name': 'four', 'adjective': 'fourth'},
               '5': {'name': 'five', 'adjective': 'fifth'},
               '6': {'name': 'six', 'adjective': 'sixth'},
               '7': {'name': 'seven', 'adjective': 'seventh'},
               '8': {'name': 'eight', 'adjective': 'eighth'},
               '9': {'name': 'nine', 'adjective': 'ninth'},
               '10': {'name': 'ten', 'adjective': 'tenth'}}

    def __init__(self, tts=None, cfg_file='config.yaml'):
        self.tts = tts
        self.lfm = VoicePlayLastFm()
        self.parser = MyParser()
        self.queue = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = MPlayerSlave()
        self.shutdown = False
        self.exit_task = False

    @staticmethod
    def trackfilter(search_term, search_result):
        track_is_ok = True
        regset = ['(\(|\]|\{).?FULL (ALBUM|SET|CONCERT|MOVIE)?.+(\(|\]|\})?',
                  '(\(|\[|\{)KARAOKE?.+(\)|\]\})',
                  '(\(|\[).?LIVE (AT|\@|ON).+?(\(|\])',
                  '\(?(REMIX|BOOTLEG|MASH\-?UP)(.+)\)?']
        # allow exact match
        if search_term.lower() == search_result.lower():
            return track_is_ok
        # proceed with patterns
        for reg in regset:
            if re.search(reg, search_result.upper()):
                track_is_ok = False
                break
        return track_is_ok

    def track_filter_fn(self, search_term, track_result_pair):
        '''
        wrapper around trackfilter
        '''
        return self.trackfilter(search_term, track_result_pair[0])

    def run_play_cmd(self, phrase):
        '''
        Run play command
        '''
        # play number
        phrase = phrase.strip().lower()
        if not phrase:
            return
        key = str(phrase.split(' ')[0])
        arr = [v for v in self.numbers if self.numbers[v]['name'] == key or self.numbers.get(key)]
        if len(phrase.split(' ')) == 1 and arr:
            if key in self.numbers:
                key = key
            elif arr:
                key = arr[0]
            adj = self.numbers[key]['adjective']
            artist = self.get_track_by_number(key)[0]
            self.tts.say_put('Playing %s track by %s' % (adj, artist))
            # play track with track number
            self.play_track_by_number(key)
        else:
            if self.lfm.get_query_type(phrase) == 'artist':
                tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(phrase))[:10]
                numerized = ', '.join(self.lfm.numerize(tracks))
                reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
                self.tts.say_put('Here are some top tracks by %s: %s' % (phrase,
                                                                     reply))
                # record track numbers
                self.store_tracks(tracks)
            else:
                self.play_full_track(phrase)

    def run_shuffle_artist(self, artist):
        '''
        Shuffle artist tracks
        '''
        if self.lfm.get_query_type(artist) == 'artist':
            tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(artist))
            random.shuffle(tracks)
            for track in tracks:
                if self.exit_task:
                    break
                self.play_full_track(track)

    def run_top_tracks_geo(self, country):
        '''
        Shuffle location tracks
        '''
        if country:
            tracks = self.lfm.get_top_tracks_geo(country)
        else:
            tracks = self.lfm.get_top_tracks_global()
        random.shuffle(tracks)
        for track in tracks:
            if self.exit_task:
                break
            self.play_full_track(track)

    @staticmethod
    def store_tracks(tracks):
        '''
        Store top tracks
        '''
        with open('state.txt', 'wb') as file_handle:
            for track in tracks:
                file_handle.write(track + '\n')

    def play_track_by_number(self, number):
        '''
        Play track by number
        '''
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(self.numbers)):
            if num == number:
                tid = idx if idx > 1 else idx + 1
                break
        logger.warning('Playing track: %s - %s', number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
        for idx, line in enumerate(lines.splitlines()):
            if idx == tid - 1:
                track = line
                break
        if track:
            self.play_full_track(track)

    def get_track_by_number(self, number):
        '''
        Get Artist - Track by number
        '''
        tid = 0
        track = ''
        for idx, num in enumerate(sorted(self.numbers)):
            if num == number:
                tid = idx if idx > 1 else idx + 1
                break
        logger.warning('Getting track: %s - %s', number, tid)
        with open('state.txt', 'rb') as file_handle:
            lines = file_handle.read()
        full_track = ''
        for idx, line in enumerate(lines.splitlines()):
            if idx == tid - 1:
                full_track = line
                break
        if full_track:
            artist = full_track.split(' - ')[0]
            track = full_track.split(' - ')[1]
        else:
            artist = 'unknown'
            track = 'unknown'
        return artist, track

    def dailymotion_search(self, query, max_results=25):
        '''
        Run dailymotion search
        '''
        maxresults = 100
        client = Dailymotion()
        client.set_grant_type('password',
                              api_key=self.cfg_data['dailymotion']['key'],
                              api_secret=self.cfg_data['dailymotion']['secret'],
                              info={'username': self.cfg_data['dailymotion']['username'],
                                    'password': self.cfg_data['dailymotion']['password']},
                              scope=['userinfo'])
        results = []
        pages = trunc(max_results/maxresults)
        pages = pages if pages > 0 else 1
        dquery = {'search': query,
                  'fields':'id,title',
                  'limit': maxresults}
        i = 0
        while i < pages:
            response = client.get('/videos', dquery)
            results += response.get('list', [])
            i += 1
            if not response.get('has_more', False):
                break
        videos = []
        for result in results:
            vid = result.get('id')
            title = result.get('title')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos

    def vimeo_search(self, query, max_results=25):
        '''
        Run vimeo search
        '''
        client = vimeo.VimeoClient(token=self.cfg_data['vimeo']['token'],
                                   key=self.cfg_data['vimeo']['key'],
                                   secret=self.cfg_data['vimeo']['secret'])
        response = client.get('/videos?query=%s' % quote(query))
        result = json.loads(response.text).get('data', [])
        videos = []
        for video in result:
            vid = video.get('uri', '').split('/videos/')[1]
            title = video.get('name', '')
            if not title.lower().startswith(query.lower()):
                continue
            videos.append([title, vid])
        return videos

    def youtube_search(self, query, max_results=25):
        '''
        Run youtube search
        '''
        youtube = build('youtube', 'v3', developerKey=self.cfg_data['google']['key'])
        search_response = youtube.search().list(q=query,
                                                part="id,snippet",
                                                maxResults=max_results).execute()
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append([search_result["snippet"]["title"], search_result["id"]["videoId"]])
        return videos

    def pleer_search(self, query, max_results=25):
        term = quote(query)
        url = 'http://pleer.net/search?page=1&q=%s&sort_mode=0&sort_by=0&quality=all&onlydata=true' % quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/search?q=%s' % term}
        r = requests.get(url, headers=headers, timeout=10)
        result = json.loads(r.text).get('html', '')
        soup = BeautifulSoup(''.join(result), 'html.parser')
        tracks = []
        for el in soup.findAll(lambda tag: tag.name == 'div' and tag.a and tag.a['href'] == '#'):
            tg = el.findParent()
            if not tg.name == 'li':
                continue
            title = '%s - %s' % (tg.get('singer'), tg.get('song'))
            aid = tg.get('link')
            tracks.append([title, aid])
        return tracks

    def pleer_download(self, track_url, filename, chunk_size=8196):
        '''
        Download track
        '''
        track_id = track_url.replace('http://pleer.net/en/download/page/', '')
        url = 'http://pleer.net/site_api/files/get_url'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.net/en/download/page/%s' % track_id}
        reply = requests.post(url, data={'action': 'download', 'id': track_id}, timeout=10)
        result = json.loads(reply.text).get('track_link')
        r = requests.get(result, headers=headers, stream=True, timeout=10)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

    def download_hook(self, response):
        '''
        YDL download hook
        '''
        if response['status'] == 'finished':
            logger.warning('Done downloading, now converting ...')
            self.target_filename = response['filename']

    def play_source_url(self, url):
        '''
        Play source url
        '''
        tmp = mkdtemp()
        template = os.path.join(tmp, '%(title)s-%(id)s.%(ext)s')
        ydl_opts = {'keepvideo': False, 'verbose': False, 'format': 'bestaudio/best',
                    'quiet': True, 'outtmpl': template,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '5',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'}],
                    'logger': logger,
                    'progress_hooks': [self.download_hook]}

        logger.warning('Using source url %s', url)
        if url.startswith('http://pleer.net/en/download/page/'):
            audio_file = mkstemp()[1]
            self.pleer_download(url, audio_file)
        else:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                audio_file = re.sub('\.(.+)$', '.mp3', self.target_filename)
        #subprocess.call(['mplayer', audio_file])
        self.player.play(audio_file)
        #while self.player.state in ['playing', 'started']:
        #    time.sleep(0.5)
        #os.remove(audio_file)
        return True

    def play_full_track(self, trackname):
        '''
        Play full track
        '''
        vid = None
        baseurl = None
        sources = [{'method': self.pleer_search, 'baseurl': 'http://pleer.net/en/download/page/'},
                   {'method': self.vimeo_search, 'baseurl': 'https://vimeo.com/'},
                   {'method': self.dailymotion_search, 'baseurl': 'http://www.dailymotion.com/video/'},
                   {'method': self.youtube_search, 'baseurl': 'https://youtu.be/'}]
        for source in sources:
            try:
                results = source.get('method')(trackname)
            except Exception as exc:
                results = []
                message = 'Source %r search failed with %r\n' % (source, exc)
                message += 'Continuing using next source provider...'
            tracks = [track for track in results if self.track_filter_fn(trackname, track)]
            if tracks:
                url = source.get('baseurl') + tracks[0][1]
                try:
                    if self.play_source_url(url):
                        break
                except Exception as exc:
                    message = 'Playback of source url %s failed with %r\n' % (url, exc)
                    message += 'Continuing using next source url...'
                    logger.error(message)

    def play_local_library(self, message):
        fnames = []
        library = os.path.expanduser('~/Music')
        for root, _, files in os.walk(library, topdown=False):
            for name in files:
                if name.lower().endswith('.mp3'):
                    fnames.append(os.path.join(root, name))
        random.shuffle(fnames)
        for fname in fnames:
            if self.exit_task:
                break
            self.player.play(fname)

    def play_station(self, station):
        '''
        Play top tracks for station
        '''
        tracks = self.lfm.get_station(station)
        random.shuffle(tracks)
        for track in tracks:
            if self.exit_task:
                break
            self.play_full_track(track)

    def play_artist_album(self, artist, album):
        '''
        Play all tracks from album
        '''
        tracks = self.lfm.get_tracks_for_album(artist, album)
        random.shuffle(tracks)
        for track in tracks:
            if self.exit_task:
                break
            self.play_full_track(track)

    def play_from_parser(self, message):
        if message in ['stop', 'pause', 'next', 'quit', 'resume']:
            if message in ['stop', 'next']:
                self.player.stop_playback()
            elif message == 'pause':
                self.player.pause()
            elif message == 'resume':
                self.player.resume()
            elif message == 'quit':
                self.player.shutdown()
                self.queue.put('quit')
        else:
            self.queue.put(message)
        return None, False

    def task_loop(self):
        while True:
            if self.shutdown:
                break
            if not self.queue.empty():
                parsed = self.parser.parse(self.queue.get())
            else:
                time.sleep(0.5)
                continue
            action_type, reg, action_phrase = self.parser.get_action_type(parsed)
            logger.warning('Action type: %s', action_type)
            if action_type == 'single_track_artist':
                track, artist = re.match(reg, action_phrase).groups()
                self.play_full_track('%s - %s' % (artist, track))
            elif action_type == 'top_tracks_artist':
                artist = re.match(reg, action_phrase).groups()[0]
                self.run_play_cmd(artist)
            elif action_type == 'shuffle_artist':
                artist = re.match(reg, action_phrase).groups()[0]
                self.tts.say_put('Shuffling %s' % artist)
                self.run_shuffle_artist(artist)
            elif action_type == 'track_number_artist':
                number = re.match(reg, action_phrase).groups()[0]
                logger.warning(number)
                self.run_play_cmd(number)
            elif action_type == 'shuffle_local_library':
                msg = re.match(reg, action_phrase).groups()[0]
                logger.warning(msg)
                self.play_local_library(msg)
            elif action_type == 'top_tracks_geo':
                country = re.match(reg, action_phrase).groups()[0]
                if country:
                    msg = 'Playing top track for country %s' % country
                else:
                    msg = 'Playing global top tracks'
                self.tts.say_put(msg)
                self.run_top_tracks_geo(country)
            elif action_type == 'station_artist':
                station = re.match(reg, action_phrase).groups()[0]
                self.tts.say_put('Playing %s station' % station)
                self.play_station(station)
            elif action_type == 'top_albums_artist':
                artist = re.match(reg, action_phrase).groups()[0]
                albums = self.lfm.get_top_albums(artist)
                msg = self.lfm.numerize(albums[:10])
                self.tts.say_put('Here are top albums by %s - %s' % (artist, msg))
                logger.warning(msg)
            elif action_type == 'artist_album':
                album, artist = re.match(reg, action_phrase).groups()
                self.play_artist_album(artist, album)
            else:
                msg = 'Vicki thinks you said ' + message
                self.tts.say_put(msg)
                logger.warning(msg)

    def start(self):
        self.player.start()
        self.task_thread = threading.Thread(name='player_task_pool', target=self.task_loop)
        self.task_thread.setDaemon = True
        self.task_thread.start()

    def stop(self):
        self.shutdown = True
        self.player.shutdown()
        self.task_thread.join()
