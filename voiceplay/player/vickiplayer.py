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
        self.parser = MyParser()
        self.queue = Queue()
        self.p_queue = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = VLCPlayer(debug=self.debug)
        self.shutdown_flag = False
        self.exit_task = False
        self.player_tasks = sorted(PluginLoader().find_classes('voiceplay.player.tasks', BasePlayerTask),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))


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
            ran = False
            for task in self.player_tasks:
                if re.match(task.__regexp__, parsed) is not None:
                    ran = True
                    task.exit_task = self.exit_task
                    task.player = self.player
                    task.tts = self.tts
                    task.process(parsed)
                    break
            if not ran:
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
