#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
''' VoicePlay main module '''

import argparse
import json
import kaptan
import logging
import os
import platform
import pylast
import random
random.seed()
import re
import requests
import speech_recognition as sr
# Having subprocess here makes me feel sad ;-(
import subprocess
import sys
import time
import vimeo

from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
from dailymotion import Dailymotion
from math import trunc
from tempfile import mkstemp
from urllib import quote
from youtube_dl import YoutubeDL

__version__ = '0.1.0'

class MyParser(object):
    '''
    Parse text commands
    '''
    known_actions = {'play': [{r'^play (.+) station$': 'station_artist'},
                              {r'^play some music by (.+)$': 'shuffle_artist'},
                              {r'^play top tracks by (.+)$': 'top_tracks_artist'},
                              {r'^play top tracks(?:\sin\s(.+))?$': 'top_tracks_geo'},
                              {r'^play (.+)?my library$': 'shuffle_local_library'},
                              {r'^play (.+) by (.+)$': 'single_track_artist'}]}

    def __init__(self, wake_word='vicki'):
        self.wake_word = wake_word
        self.normalize_phrases = self.load_phrases(self.wake_word)

    @staticmethod
    def load_phrases(wake_word, normalize_file='normalize.json'):
        '''
        Load normalization phrases
        '''
        with open(normalize_file, 'rb') as normalize_fh:
            data = json.loads(normalize_fh.read())
        return data[wake_word]

    def normalize(self, sentence):
        '''
        Run normalization
        '''
        message = sentence.lower()
        result = message
        # first pass
        for phrase in self.normalize_phrases:
            if message.startswith(phrase):
                result = re.sub(r'^%s' % phrase, self.normalize_phrases[phrase], message)
        if result != message:
            message = result
        #
        # second pass
        for phrase in self.normalize_phrases:
            if message.startswith(phrase):
                result = re.sub(r'^%s' % phrase, self.normalize_phrases[phrase], message)
        return result

    def parse(self, message):
        '''
        Parse incoming message
        '''
        result = self.normalize(message)
        start = False
        action_phrase = []
        for word in result.split(' '):
            if word == self.wake_word:
                continue
            # confirm proper type
            if self.known_actions.get(word):
                start = True
            if start and word:
                action_phrase.append(word)
        response = ' '.join(action_phrase)
        return response

    def get_action_type(self, action_phrase):
        '''
        Get action type depending on incoming message
        '''
        action = action_phrase.split(' ')[0]
        if self.known_actions.get(action, None) is None:
            raise ValueError('Unknown action %r in phrase %r' % (action, action_phrase))
        action_type = None
        for regs in self.known_actions.get(action):
            reg = regs.keys()[0]
            if re.match(reg, action_phrase) is not None:
                action_type = regs[reg]
                break
        if action_phrase and action_phrase.startswith('play') and not action_type:
            reg = '^play (.+)$'
            action_type = 'track_number_artist'
        return action_type, reg, action_phrase

class VoicePlayLastFm(object):
    '''
    Last.Fm API
    '''
    def __init__(self, cfg_file='config.yaml'):
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        cfg_data = config.configuration_data

        self.network = pylast.LastFMNetwork(api_key=cfg_data['lastfm']['key'],
                                            api_secret=cfg_data['lastfm']['secret'])

    def get_top_tracks_geo(self, country_code):
        '''
        Country name: ISO 3166-1
        '''
        tracks = self.network.get_geo_top_tracks(country_code)
        return self.trackarize(tracks)

    def get_top_tracks_global(self):
        '''
        Global top tracks (chart)
        '''
        tracks = self.network.get_top_tracks()
        return self.trackarize(tracks)

    def get_top_tracks(self, artist):
        '''
        Get top tracks by artist
        '''
        aobj = pylast.Artist(artist, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    def get_station(self, station):
        '''
        Get station
        '''
        aobj = pylast.Tag(station, self.network)
        tracks = aobj.get_top_tracks()
        return self.trackarize(tracks)

    def get_corrected_artist(self, artist):
        '''
        Get corrected artist
        '''
        a_s = pylast.ArtistSearch(artist, self.network)
        reply = a_s.get_next_page()
        if isinstance(reply, list) and reply:
            return reply[0].name
        else:
            return ''

    def get_query_type(self, query):
        '''
        Detect whether query is just artist or artist - track
        '''
        query = query.lower()
        text = query.capitalize()
        if self.get_corrected_artist(text).lower() == text.lower():
            reply = 'artist'
        else:
            reply = 'artist_track'
        return reply

    @staticmethod
    def trackarize(array):
        '''
        Convert lastfm track entities to track names
        '''
        top_tracks = []
        for track in array:
            top_tracks.append(track.item.artist.name + ' - ' + track.item.title)
        return top_tracks

    @staticmethod
    def numerize(array):
        '''
        Name tracks
        '''
        reply = []
        for idx, element in enumerate(array):
            reply.append('%s: %s' % (idx + 1, element))
        return reply


class TextToSpeech(object):
    '''
    MAC/Linux TTS
    '''
    def __init__(self):
        system = platform.system()
        if system == 'Darwin':
            from AppKit import NSSpeechSynthesizer
            voice = 'Vicki'
            base = 'com.apple.speech.synthesis.voice'
            self.voice = base + '.' + voice
            self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)
            self.say = self.__say_mac
        elif system == 'Linux':
            from festival import sayText
            self.say = self.__say_linux
        else:
            raise NotImplementedError('Platform not supported')

    def __say_linux(self, message):
        '''
        Read aloud message Linux
        '''
        sayText(message)

    def __say_mac(self, message):
        '''
        Read aloud message MAC
        '''
        self.speech.startSpeakingString_(message)
        while self.speech.isSpeaking():
            time.sleep(0.5)


class Vicki(object):
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

    def __init__(self, cfg_file='config.yaml'):
        # logger is the earliest bird
        self.init_logger()
        #
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        self.cfg_data = config.configuration_data
        self.rec = sr.Recognizer()
        self.lfm = VoicePlayLastFm()
        self.parser = MyParser()
        self.tts = TextToSpeech()
        self.logger.warning('Vicki init completed')

    def init_logger(self, name='voiceplay'):
        '''
        Initialize logger
        '''
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)

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
            self.tts.say('Playing %s track by %s' % (adj, artist))
            # play track with track number
            self.play_track_by_number(key)
        else:
            if self.lfm.get_query_type(phrase) == 'artist':
                tracks = self.lfm.get_top_tracks(self.lfm.get_corrected_artist(phrase))[:10]
                numerized = ', '.join(self.lfm.numerize(tracks))
                reply = re.sub(r'^(.+)\.\s\d\:\s', '1: ', numerized)
                self.tts.say('Here are some top tracks by %s: %s' % (phrase,
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
        self.logger.warning('Playing track: %s - %s', number, tid)
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
        self.logger.warning('Getting track: %s - %s', number, tid)
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
        url = 'http://pleer.com/search?page=1&q=%s&sort_mode=0&sort_by=0&quality=all&onlydata=true' % quote(query)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.com/search?q=%s' % term}
        r = requests.get(url, headers=headers)
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

    def pleer_download(self, track_id, filename, chunk_size=8196):
        '''
        Download track
        '''
        url = 'http://pleer.com/site_api/files/get_url'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://pleer.com/en/download/page/%s' % track_id}
        reply = requests.post(url, data={'action': 'download', 'id': track_id})
        result = json.loads(reply.text).get('track_link')
        r = requests.get(result, headers=headers, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

    def download_hook(self, response):
        '''
        YDL download hook
        '''
        if response['status'] == 'finished':
            self.logger.warning('Done downloading, now converting ...')

    def play_full_track(self, trackname):
        '''
        Play full track
        '''
        vid = None
        baseurl = None
        sources = [{'method': self.pleer_search, 'baseurl': 'http://pleer.com/en/download/page/'},
                   {'method': self.vimeo_search, 'baseurl': 'https://vimeo.com/'},
                   {'method': self.dailymotion_search, 'baseurl': 'http://www.dailymotion.com/video/'}]
        for source in sources:
            results = source.get('method')(trackname)
            if results:
                vid = results[0][1]
                baseurl = source.get('baseurl')
                break
        # fallback
        if not results:
            results = self.youtube_search(trackname)
            vid = results[0][1]
            baseurl = 'https://youtu.be/'

        ydl_opts = {'keepvideo': False, 'verbose': False, 'format': 'bestaudio/best',
                    'quiet': True,
                    'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '5',
                                        'nopostoverwrites': True, 'key': 'FFmpegExtractAudio'},
                                       {'exec_cmd': 'mplayer {}; rm -f {}',
                                        'key': 'ExecAfterDownload'}],
                    'logger': self.logger,
                    'progress_hooks': [self.download_hook]}

        self.logger.warning('Using source url %s', baseurl + vid)
        if baseurl == 'http://pleer.com/en/download/page/':
            tmp = mkstemp()[1]
            self.pleer_download(vid, tmp)
            subprocess.call(['mplayer', tmp])
            os.remove(tmp)
        else:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([baseurl + vid])

    @staticmethod
    def play_local_library(message):
        fnames = []
        library = os.path.expanduser('~/Music')
        for root, _, files in os.walk(library, topdown=False):
            for name in files:
                if name.lower().endswith('.mp3'):
                    fnames.append(os.path.join(root, name))
        random.shuffle(fnames)
        for fname in fnames:
            subprocess.call(['mplayer', fname])

    def play_station(self, station):
        '''
        Play top tracks for station
        '''
        tracks = self.lfm.get_station(station)
        random.shuffle(tracks)
        for track in tracks:
            self.play_full_track(track)

    def play_from_parser(self, message):
        '''
        Process incoming message
        '''
        parsed = self.parser.parse(message)
        action_type, reg, action_phrase = self.parser.get_action_type(parsed)
        self.logger.warning('Action type: %s', action_type)
        if action_type == 'single_track_artist':
            track, artist = re.match(reg, action_phrase).groups()
            self.play_full_track('%s - %s' % (artist, track))
        elif action_type == 'top_tracks_artist':
            artist = re.match(reg, action_phrase).groups()[0]
            self.run_play_cmd(artist)
        elif action_type == 'shuffle_artist':
            artist = re.match(reg, action_phrase).groups()[0]
            self.tts.say('Shuffling %s' % artist)
            self.run_shuffle_artist(artist)
        elif action_type == 'track_number_artist':
            number = re.match(reg, action_phrase).groups()[0]
            self.logger.warning(number)
            self.run_play_cmd(number)
        elif action_type == 'shuffle_local_library':
            msg = re.match(reg, action_phrase).groups()[0]
            self.logger.warning(msg)
            self.play_local_library(msg)
        elif action_type == 'top_tracks_geo':
            country = re.match(reg, action_phrase).groups()[0]
            if country:
                msg = 'Playing top track for country %s' % country
            else:
                msg = 'Playing global top tracks'
            self.tts.say(msg)
            self.run_top_tracks_geo(country)
        elif action_type == 'station_artist':
            station = re.match(reg, action_phrase).groups()[0]
            self.tts.say('Playing %s station' % station)
            self.play_station(station)
        else:
            msg = 'Vicki thinks you said ' + message
            self.tts.say(msg)
            self.logger.warning(msg)

    def process_request(self, request):
        '''
        process request
        '''
        try:
            self.play_from_parser(request)
        except Exception as exc:
            self.logger.error(exc)
            self.tts.say('Vicki could not process your request')

    def run_forever(self):
        '''
        Main loop
        '''
        while True:
            with sr.Microphone() as source:
                msg = 'Vicki is listening'
                self.tts.say(msg)
                self.logger.warning(msg)
                audio = self.rec.listen(source)
            try:
                result = self.rec.recognize_google(audio)
            except sr.UnknownValueError:
                msg = 'Vicki could not understand audio'
                self.tts.say(msg)
                self.logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.tts.say(msg)
                self.logger.warning('{0}; {1}'.format(msg, e))
                result = None
            if result:
                self.process_request(result)
            elif result and result.lower() in ['shutdown']:
                msg = 'Vicki is shutting down, see you later'
                self.tts.say(msg)
                self.logger.warning(msg)
                break

class MyArgumentParser(object):
    '''
    Parse command line arguments
    '''
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VoicePlay')

    def configure(self):
        '''
        Configure argument parser
        '''
        self.parser.add_argument('-c', action="store_true", default=False, dest='console',
                                 help='Start console')
        self.parser.add_argument('--version', action='version', version='%(prog)s ' +  __version__)

    def parse(self, argv=None):
        '''
        Parse command line arguments
        '''
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        vicki = Vicki()
        if result.console:
            from IPython import Config
            from IPython.terminal.embed import InteractiveShellEmbed
            config = Config()
            # basic configuration
            config.TerminalInteractiveShell.confirm_exit = False
            #
            embed = InteractiveShellEmbed(config=config, banner1='')
            embed.mainloop()
        else:
            vicki.run_forever()

if __name__ == '__main__':
    parser = MyArgumentParser()
    parser.configure()
    parser.parse()
