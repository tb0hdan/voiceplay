''' VickiPlayer module '''
import os
import random
random.seed()
import re
import sys
if sys.version_info.major == 2:
    from Queue import Queue
elif sys.version_info.major == 3:
    from queue import Queue

import threading
import time

from voiceplay.config import Config
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.datasources.track.tracksource import TrackSource
from voiceplay.cmdprocessor.parser import MyParser
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from .backend.vlc import VLCPlayer

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

    def __init__(self, tts=None, cfg_file='config.yaml', debug=False):
        self.debug = debug
        self.tts = tts
        self.lfm = VoicePlayLastFm()
        self.parser = MyParser()
        self.queue = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = VLCPlayer(debug=self.debug)
        self.shutdown_flag = False
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

    def play_full_track(self, trackname):
        '''
        Play full track
        '''
        vid = None
        baseurl = None
        sources = sorted(PluginLoader().find_classes('voiceplay.datasources.track', TrackSource),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))
        for source in sources:
            try:
                results = source.search(trackname)
            except Exception as exc:
                results = []
                message = 'Source %r search failed with %r\n' % (source, exc)
                message += 'Continuing using next source provider...'
                logger.debug(message)
            tracks = [track for track in results if self.track_filter_fn(trackname, track)]
            if tracks:
                url = source.__baseurl__ + tracks[0][1]
                try:
                    filename = source.download(url)
                    if self.player.play(filename):
                        break
                except Exception as exc:
                    message = 'Playback of source url %s failed with %r\n' % (url, exc)
                    message += 'Continuing using next source url...'
                    logger.debug(message)

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
            if message == 'stop':
                self.exit_task = True
                self.player.stop()
            elif message in ['next', 'max']:
                self.player.stop()
            elif message == 'pause':
                self.player.pause()
            elif message == 'resume':
                self.player.resume()
            elif message == 'quit':
                self.exit_task = True
                self.player.shutdown()
                self.queue.put('quit')
        else:
            self.exit_task = True
            self.queue.put(message)
        return None, False

    def task_loop(self):
        while True:
            if self.shutdown_flag:
                break
            if not self.queue.empty():
                message = self.queue.get()
                # process playback control commands first
                self.play_from_parser(message.lower())
                # continue with commands
                parsed = self.parser.parse(self.queue.get())
            else:
                time.sleep(0.01)
                continue
            self.exit_task = False
            logger.debug('task_loop got from queue: %r', parsed)
            if not parsed:
                continue
            action_type, reg, action_phrase = self.parser.get_action_type(parsed)
            logger.debug('Action type: %s', action_type)
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
        # non-blocking start
        self.player.start()
        self.task_thread = threading.Thread(name='player_task_pool', target=self.task_loop)
        self.task_thread.setDaemon = True
        self.task_thread.start()

    def shutdown(self):
        self.shutdown_flag = True
        self.exit_task = True
        self.player.shutdown()
        self.task_thread.join()
