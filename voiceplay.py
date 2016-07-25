#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
''' VoicePlay main module '''

from __future__ import print_function, unicode_literals
import argparse
import colorama
import json
import kaptan
import logging
import os
import platform
import pylast
import random
random.seed()
import re
import readline
import requests
import speech_recognition as sr
# Having subprocess here makes me feel sad ;-(
import signal
import subprocess
import sys
import threading
import time
import vimeo

from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
from dailymotion import Dailymotion
from math import trunc

if sys.version_info.major == 2:
    from Queue import Queue
    from urllib import quote
    from pipes import quote as shell_quote
elif sys.version_info.major == 3:
    from builtins import input as raw_input
    from queue import Queue
    from urllib.parse import quote
    from shlex import quote as shell_quote
else:
    raise RuntimeError('What kind of system is this?!?!')


from tempfile import mkstemp, mkdtemp
from youtube_dl import YoutubeDL

__version__ = '0.1.3'

class Console(object):
    '''
    Console mode
    '''
    def __init__(self, banner='Welcome to voiceplay console!'):
        self.name = 'voiceplay'
        self.default_prompt = '%s [%s]%s '
        self.exit = False
        self.banner = banner
        self.commands = {}

    def add_handler(self, keyword, method, aliases=None):
        aliases = aliases if aliases else []
        self.commands[keyword] = {'method': method, 'aliases': aliases}

    @property
    def format_prompt(self):
        result = self.default_prompt % (time.strftime('%H:%M:%S'),
                                        colorama.Fore.GREEN + colorama.Style.BRIGHT + self.name + colorama.Style.RESET_ALL,
                                        colorama.Fore.CYAN + colorama.Style.BRIGHT + '>' + colorama.Style.RESET_ALL)
        return result

    def parse_command(self, command):
        result = None
        should_be_printed = True
        command = command.strip().lower()
        for kwd in self.commands:
            if command.startswith(kwd) or [c for c in self.commands[kwd]['aliases'] if command.startswith(c)]:
                try:
                    result, should_be_printed = self.commands[kwd]['method'](command)
                    break
                except KeyboardInterrupt:
                    pass
        return result, should_be_printed

    def quit_command(self, cmd):
        self.exit = True
        result = None
        should_be_printed = False
        return result, should_be_printed

    def clear_command(self, cmd):
        sys.stderr.flush()
        sys.stderr.write("\x1b[2J\x1b[H")
        result = None
        should_be_printed = False
        return result, should_be_printed

    def complete(self, _, state):
        text = readline.get_line_buffer()
        if not text:
            return [c + ' ' for c in self.commands][state]
        results = [c + ' ' for c in self.commands if c.startswith(text)]
        return results[state]

    def run_exit(self):
        print ('Goodbye!')

    def run_console(self):
        inp = None
        colorama.init()
        # FSCK! Details here: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)
        # Add handlers
        self.add_handler('quit', self.quit_command, ['exit', 'logout'])
        self.add_handler('clear', self.clear_command, ['cls', 'clr'])
        #
        if self.banner:
            print (self.banner)
        while True:
            print (self.format_prompt, end='')
            try:
                inp = raw_input()
                if sys.version_info.major == 2:
                    inp = inp.decode('utf-8')
            except KeyboardInterrupt:
                pass
            except EOFError:
                self.exit = True
                inp = None
            if inp:
                result, should_be_printed = self.parse_command(inp)
            if self.exit:
                self.run_exit()
                break


class ConsolePlayer(object):
    '''
    Console player
    '''
    def __init__(self, *args, **kwargs):
        self.lock = threading.Lock()
        self.stdout_pool = []
        self.stderr_pool = []

    def player_stdout_thread(self):
        while self.proc.poll() is None:
            line = self.proc.stdout.readline().rstrip('\n')
            if line:
                self.stdout_pool.append(line.strip())

    def player_stderr_thread(self):
        while self.proc.poll() is None:
            line = self.proc.stderr.readline().rstrip('\n')
            if line:
                self.stderr_pool.append(line.strip())

    def send_command(self, command):
        with self.lock:
            self.proc.stdin.write(command + '\n')

    def stop(self):
        os.killpg(self.proc.pid, signal.SIGTERM)
        self.stdout_thread.join()
        self.stderr_thread.join()

    def start(self):
        self.proc = subprocess.Popen(self.command,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     close_fds=True,
                                     preexec_fn=os.setsid)

        self.stdout_thread = threading.Thread(name='player_stdout', target=self.player_stdout_thread)
        self.stdout_thread.setDaemon(True)
        self.stdout_thread.start()

        self.stderr_thread = threading.Thread(name='player_stderr', target=self.player_stderr_thread)
        self.stderr_thread.setDaemon(True)
        self.stderr_thread.start()


class MPlayerSlave(ConsolePlayer):
    '''
    MPlayer slave
    '''
    def __init__(self, *args, **kwargs):
        self.command = ['mplayer', '-slave', '-idle',
               '-really-quiet', '-msglevel', 'global=6:cplayer=4', '-msgmodule',
               '-vo', 'null', '-cache', '1024']
        super(MPlayerSlave, self).__init__(*args, **kwargs)
        self._state = 'started'

    def play(self, uri, block=True):
        cmd = 'loadfile %s' % uri
        self.send_command(cmd.encode('utf-8'))
        time.sleep(1)
        if block:
            while self.state != 'stopped':
                time.sleep(0.5)

    def stop_playback(self):
        if self._state in ['playing', 'paused']:
            self.send_command('stop')
            self._state = 'stopped'

    def pause(self):
        if self._state == 'playing':
            self.send_command('pause')
            self._state = 'paused'

    def resume(self):
        if self._state == 'paused':
            self.send_command('pause')
            self._state = 'playing'

    def shutdown(self):
        self.send_command('quit')
        time.sleep(0.5)
        self.stop()

    def get_state(self):
        for line in self.stdout_pool:
            if line.startswith('GLOBAL: EOF code'):
                self._state = 'stopped'
                break
            if line.startswith('CPLAYER: Starting playback'):
                self._state = 'playing'
                break
        self.stdout_pool = []
        if self.proc is not None:
            self._state = 'notrunning'


    @property
    def state(self):
        self.get_state()
        return self._state
 

class MyParser(object):
    '''
    Parse text commands
    '''
    known_actions = {'play': [{r'^play (.+) station$': 'station_artist'},
                              {r'^play some (?:music|tracks?|songs?) by (.+)$': 'shuffle_artist'},
                              {r'^play top (?:songs|tracks) by (.+)$': 'top_tracks_artist'},
                              {r'^play top (?:songs|tracks)(?:\sin\s(.+))?$': 'top_tracks_geo'},
                              {r'^play (.+)?my library$': 'shuffle_local_library'},
                              {r'^play (?:songs|tracks) from (.+) by (.+)$': 'artist_album'},
                              {r'^play (.+) by (.+)$': 'single_track_artist'}],
                     'shuffle': [{r'^shuffle (.+)?my library$': 'shuffle_local_library'}],
                     'shutdown': [{'shutdown': 'shutdown_action'},
                                  {'shut down': 'shutdown_action'}],
                     'what': [{r'^what are top albums (?:by|for) (.+)$': 'top_albums_artist'},
                              {r'^what are top (?:songs|tracks) (?:by|for) (.+)$': 'top_tracks_artist'}]
                    }

    def __init__(self, wake_word='vicki'):
        self.wake_word = wake_word

    def parse(self, message):
        '''
        Parse incoming message
        '''
        start = False
        action_phrase = []
        for word in message.split(' '):
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
            reg = list(regs.keys())[0]
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
        artist = self.get_corrected_artist(artist)
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

    def get_top_albums(self, artist):
        album_list = []
        artist = self.get_corrected_artist(artist)
        aobj = pylast.Artist(artist, self.network)
        albums = aobj.get_top_albums()
        for album in albums:
            album_list.append(album.item.title)
        return album_list

    def get_tracks_for_album(self, artist, album):
        result = []
        artist = self.get_corrected_artist(artist)
        tracks = pylast.Album(artist, album.title(), self.network).get_tracks()
        for track in tracks:
            result.append(track.artist.name + ' - ' + track.title)
        return result

    def get_corrected_artist(self, artist):
        '''
        Get corrected artist
        '''
        a_s = pylast.ArtistSearch(artist, self.network)
        reply = a_s.get_next_page()
        if isinstance(reply, list) and reply:
            return reply[0].name
        else:
            return artist

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
    def __init__(self, name='voiceplay'):
        system = platform.system()
        if system == 'Darwin':
            try:
                from AppKit import NSSpeechSynthesizer
                voice = 'Vicki'
                base = 'com.apple.speech.synthesis.voice'
                self.voice = base + '.' + voice
                self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)
                self.say = self.__say_mac
            except ImportError:
                # osx lacks appkit support for python3 (sigh)
                self.say = self.__say_dummy
        elif system == 'Linux':
            from festival import sayText
            self.say = self.__say_linux
        else:
            raise NotImplementedError('Platform not supported')
        self.queue = Queue()

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

    def __say_dummy(self, message):
        '''
        Dummy TTS
        '''
        pass

    def say_poll(self):
        while True:
            if self.queue.empty():
                time.sleep(1)
            else:
                self.say(self.queue.get())

    def say_put(self, message):
        self.queue.put(message)


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
        self.init_logger()
        config = kaptan.Kaptan()
        config.import_config(cfg_file)
        self.cfg_data = config.configuration_data
        self.player = MPlayerSlave()
        self.player.start()
        self.shutdown = False
        self.exit_task = False

    def init_logger(self, name='VickiPlayer'):
        '''
        Initialize logger
        '''
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)

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
            self.logger.warning('Done downloading, now converting ...')
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
                    'logger': self.logger,
                    'progress_hooks': [self.download_hook]}

        self.logger.warning('Using source url %s', url)
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
                    self.logger.error(message)

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
        if message in ['stop', 'pause', 'next', 'quit']:
            if message in ['stop', 'next']:
                self.player.stop_playback()
            elif message == 'pause':
                self.player.pause()
            elif message == 'quit':
                self.player.shutdown()
        else:
            self.queue.put(message)
        return None, False

    def task_loop(self):
        while True:
            while self.queue.empty():
                if self.shutdown:
                    break
                time.sleep(0.5)
            if self.shutdown:
                break
            parsed = self.parser.parse(self.queue.get())
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
                self.tts.say_put('Shuffling %s' % artist)
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
                self.logger.warning(msg)
            elif action_type == 'artist_album':
                album, artist = re.match(reg, action_phrase).groups()
                self.play_artist_album(artist, album)
            else:
                msg = 'Vicki thinks you said ' + message
                self.tts.say_put(msg)
                self.logger.warning(msg)

    def start(self):
        self.task_thread = threading.Thread(name='player_task_pool', target=self.task_loop)
        self.task_thread.setDaemon = True
        self.task_thread.start()

    def stop(self):
        self.shutdown = True
        self.player.shutdown()
        self.task_thread.join()


class Vicki(object):
    '''
    Vicki main class
    '''

    def __init__(self):
        self.init_logger()
        self.rec = sr.Recognizer()
        self.tts = TextToSpeech()
        self.queue = Queue()
        self.shutdown = False
        self.logger.debug('Vicki init completed')
        self.player = VickiPlayer(tts=self.tts)

    def init_logger(self, name='Vicki'):
        '''
        Initialize logger
        '''
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)

    def process_request(self, request):
        '''
        process request
        '''
        try:
            self.player.play_from_parser(request)
        except Exception as exc:
            self.logger.error(exc)
            self.tts.say_put('Vicki could not process your request')

    def background_listener(self):
        msg = 'Vicki is listening'
        self.tts.say_put(msg)
        # TODO: Fix this using callback or something so that 
        # we do not record ourselves
        time.sleep(3)
        self.logger.warning(msg)
        while True:
            if self.shutdown:
                break
            with sr.Microphone() as source:
                # TODO: Test effectiveness of this method
                self.rec.adjust_for_ambient_noise(source)
                try:
                    audio = self.rec.listen(source, timeout=5)
                except sr.WaitTimeoutError:
                    continue
            try:
                result = self.rec.recognize_sphinx(audio)
            except sr.UnknownValueError:
                msg = 'Vicki could not understand audio'
                self.tts.say_put(msg)
                self.logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.tts.say_put(msg)
                self.logger.warning('{0}; {1}'.format(msg, e))
                result = None
            if not result in ['we k.', 'waiting', 'gritty', 'winking', 'we see it', 'sweetie',
                              'we keep', 'we see', 'when did', 'wait a', 'we did', "we didn't"]:
                self.logger.warning('Heard %r', result)
                continue
            else:
                self.logger.warning('Wake word! %r', result)
                self.tts.say_put('Yes')

            # command goes next
            with sr.Microphone() as source:
                audio = self.rec.listen(source)
            try:
                result = self.rec.recognize_google(audio)
            except sr.UnknownValueError:
                msg = 'Vicki could not understand audio'
                self.tts.say_put(msg)
                self.logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.tts.say_put(msg)
                self.logger.warning('{0}; {1}'.format(msg, e))
                result = None
            if result:
                self.queue.put(result)

    def background_executor(self):
        while True:
            if self.shutdown:
                break
            if not self.queue.empty():
                message = self.queue.get()
                if message == 'shutdown':
                    self.shutdown = True
                    self.player.stop()
                else:
                    self.process_request(message)
            time.sleep(1)

    def background_speaker(self):
        self.tts.say_poll()

    def run_forever_new(self):
        '''
        Main loop
        '''
        listener = threading.Thread(name='BackgroundListener', target=self.background_listener)
        listener.setDaemon(True)

        player = threading.Thread(name='BackgroundPlayer', target=self.background_executor)
        player.setDaemon(True)

        speaker = threading.Thread(name='BackgroundSpeaker', target=self.background_speaker)
        speaker.setDaemon(True)

        listener.start()
        player.start()
        speaker.start()
        while True:
            if self.shutdown:
                break
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown = True  # for threads
                listener.join()
                player.join()
                speaker.join()
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
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-c', '--console', action='store_true', default=False, dest='console',
                           help='Start console')
        group.add_argument('-cd', '--console-devel', action='store_true', default=False, dest='console_devel',
                           help='Start development console')
        self.parser.add_argument('--version', action='version', version='%(prog)s ' +  __version__)

    @staticmethod
    def ipython_console():
        '''
        Run ipython console
        '''
        from traitlets.config import Config
        from IPython.terminal.embed import InteractiveShellEmbed
        config = Config()
        # basic configuration
        config.TerminalInteractiveShell.confirm_exit = False
        #
        embed = InteractiveShellEmbed(config=config, banner1='')
        embed.mainloop()

    def player_console(self, vicki):
        console = Console()
        console.add_handler('play', vicki.player.play_from_parser, ['pause', 'shuffle', 'next', 'stop'])
        console.add_handler('what', vicki.player.play_from_parser)
        console.run_console()

    def parse(self, argv=None):
        '''
        Parse command line arguments
        '''
        argv = sys.argv if not argv else argv
        result = self.parser.parse_args(argv[1:])
        vicki = Vicki()
        if result.console:
            vicki.player.start()
            self.player_console(vicki)
            vicki.player.stop()
        elif result.console_devel:
            self.ipython_console()
        else:
            vicki.run_forever_new()


if __name__ == '__main__':
    parser = MyArgumentParser()
    parser.configure()
    parser.parse()
