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
from voiceplay.datasources.track.basesource import TrackSource
from voiceplay.cmdprocessor.parser import MyParser
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from .backend.vlc import VLCPlayer
from .hooks.basehook import BasePlayerHook
from .tasks.basetask import BasePlayerTask

class VickiPlayer(object):
    '''
    Vicki player class
    '''
    def __init__(self, tts=None, cfg_file='config.yaml', debug=False):
        self.debug = debug
        self.tts = tts
        self.lfm = VoicePlayLastFm()
        self.parser = MyParser()
        self.queue = Queue()
        self.p_queue = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = VLCPlayer(debug=self.debug)
        self.shutdown_flag = False
        self.exit_task = False

    def put(self, message):
        self.queue.put(message)

    def play_from_parser(self, message):
        stop_set = ['stop', 'stock', 'top']
        next_set = ['next', 'max', 'maxed', 'text']
        pause_set = ['pause', 'boss']
        resume_set = ['resume']
        quit_set = ['quit', 'shutdown']
        all_set = stop_set + next_set + pause_set + resume_set + quit_set
        if message in all_set:
            if message in stop_set:
                self.exit_task = True
                self.player.stop()
            elif message in next_set:
                self.player.stop()
            elif message in pause_set:
                self.player.pause()
            elif message in resume_set:
                self.player.resume()
            elif message in quit_set:
                self.shutdown_flag = True
                self.exit_task = True
                self.player.shutdown()
        else:
            self.exit_task = True
            if message.startswith('play'):
                self.player.stop()
            self.p_queue.put(message)
        return None, False

    def cmd_loop(self):
        while not self.shutdown_flag:
            if not self.queue.empty():
                message = self.queue.get()
            else:
                time.sleep(0.01)
                continue
            self.play_from_parser(message)
        logger.debug('Vickiplayer.cmd_loop exit')

    def task_loop(self):
        while not self.shutdown_flag:
            if not self.p_queue.empty():
                parsed = self.parser.parse(self.p_queue.get())
            else:
                time.sleep(0.01)
                continue
            logger.debug('task_loop got from queue: %r', parsed)
            if not parsed:
                continue
            self.exit_task = False
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
                msg = 'I think you said ' + message
                self.tts.say_put(msg)
                logger.warning(msg)
        logger.debug('VickiPlayer.task_loop exit')

    def start(self):
        # non-blocking start
        self.player.start()
        self.task_thread = threading.Thread(name='player_task_pool', target=self.task_loop)
        self.task_thread.start()
        self.cmd_thread = threading.Thread(name='player_cmd_pool', target=self.cmd_loop)
        self.cmd_thread.start()

    def shutdown(self):
        self.shutdown_flag = True
        self.exit_task = True
        self.player.shutdown()
        self.task_thread.join()
        self.cmd_thread.join()
