#-*- coding: utf-8 -*-
""" VickiPlayer module """

import re
import sys
if sys.version_info.major == 2:
    from Queue import Queue  # pylint:disable=import-error
elif sys.version_info.major == 3:
    from queue import Queue  # pylint:disable=import-error

import time
from functools import cmp_to_key
from voiceplay.config import Config
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.helpers import ThreadGroup, cmp
from .backend.vlc import VLCPlayer
from .tasks.basetask import BasePlayerTask

class VickiPlayer(object):
    """
    Vicki player class
    """
    def __init__(self, tts=None, cfg_file='config.yaml', debug=False):
        self.debug = debug
        self.tts = tts
        self.queue = Queue()
        self.p_queue = Queue()
        self.prefetch_q = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = VLCPlayer(debug=self.debug)
        self.shutdown_flag = False
        self.exit_task = False
        self._argparser = None
        self.player_tasks = sorted(PluginLoader().find_classes('voiceplay.player.tasks', BasePlayerTask),
                         key=cmp_to_key(lambda x, y: cmp(x.__priority__, y.__priority__)))
        self.known_actions = self.get_actions(self.player_tasks)

    @property
    def argparser(self):
        """
        Managed property, returns argument parser
        """
        return self._argparser

    @argparser.setter
    def argparser(self, argobj):
        """
        Managed property, sets argument parser
        """
        self._argparser = argobj
        self.player.argparser = argobj

    @staticmethod
    def get_actions(tasks):
        """
        Returns list of available actions
        """
        actions = []
        for task in tasks:
            for action in task.__group__:
                if not action in actions:
                    actions.append(action)
        return actions

    def get_exit(self):
        """
        Returns true if exit was requested
        """
        return self.exit_task

    def put(self, message):
        """
        Put message in queue for processing
        """
        self.queue.put(message)

    def parse(self, message):
        """
        Parse incoming message
        """
        start = False
        action_phrase = []
        for word in message.split(' '):
            if word.lower() in self.known_actions:
                start = True
            if start and word:
                action_phrase.append(word)
        response = ' '.join(action_phrase)
        return response

    def play_from_parser(self, message):
        """
        Handle message and call respective actions
        """
        orig_message = message
        message = message.lower()
        stop_set = ['stop', 'stock', 'top']
        next_set = ['next', 'max', 'maxed', 'text']
        pause_set = ['pause', 'boss']
        resume_set = ['resume']
        quit_set = ['quit', 'shutdown']
        all_set = stop_set + next_set + pause_set + resume_set + quit_set
        if message in all_set:
            if message in stop_set:
                self.player.stop()
                self.exit_task = True
            elif message in next_set:
                self.player.stop()
            elif message in pause_set:
                self.player.pause()
            elif message in resume_set:
                self.player.resume()
            elif message in quit_set:
                self.player.shutdown()
                self.shutdown_flag = True
                self.exit_task = True
        else:
            self.exit_task = True
            if message.startswith('play'):
                self.player.stop()
            self.p_queue.put(orig_message)
        return None, False

    def cmd_loop(self):
        """
        Run command loop / periodically check for commands from queue
        """
        while not self.shutdown_flag:
            if not self.queue.empty():
                message = self.queue.get()
            else:
                time.sleep(0.01)
                continue
            self.play_from_parser(message)
            self.queue.task_done()
        logger.debug('Vickiplayer.cmd_loop exit')

    def run_player_tasks(self, message):
        """
        Run player tasks
        """
        ran = False
        for task in self.player_tasks:
            for regexp in task.__regexp__:
                if re.match(regexp, message, re.I) is not None:
                    ran = True
                    task.prefetch_callback = self.add_to_prefetch_q
                    task.argparser = self._argparser
                    task.get_exit = self.get_exit
                    task.player = self.player
                    task.tts = self.tts
                    task.process(regexp, message)
                    break
            if ran:
                break
        return ran

    def task_loop(self):
        """
        Check periodically for tasks from queue
        """
        while not self.shutdown_flag:
            if not self.p_queue.empty():
                parsed = self.parse(self.p_queue.get())
            else:
                time.sleep(0.01)
                continue
            logger.debug('task_loop got from queue: %r', parsed)
            if not parsed:
                continue
            self.exit_task = False
            ran = self.run_player_tasks(parsed)
            if not ran:
                msg = 'I think you said ' + parsed
                self.tts.say_put(msg)
                logger.warning(msg)
            self.p_queue.task_done()
        logger.debug('VickiPlayer.task_loop exit')

    def prefetch_loop(self):
        """
        Prefetch loop allows significant speedup in playback as it fetches tracks in background
        """
        while not self.shutdown_flag:
            if not self.prefetch_q.empty():
                trackname = self.prefetch_q.get()
            else:
                time.sleep(0.01)
                continue
            logger.debug('prefetch_loop got from queue: %r', trackname.encode('utf-8'))
            start = time.time()
            BasePlayerTask.download_full_track(trackname)
            elapsed = round(time.time() - start, 3)
            logger.debug('prefetch_loop finished downloading, took %ss', elapsed)

    def add_to_prefetch_q(self, item):
        """
        Add track to prefetch queue
        """
        self.prefetch_q.put(item)

    def start(self):
        """
        Start VickiPlayer and auxiliary loops using thread group
        """
        # non-blocking start
        self.player.start()
        self.thread_group = ThreadGroup()
        self.thread_group.targets = [self.task_loop, self.cmd_loop, self.prefetch_loop]
        self.thread_group.start_all()

    def shutdown(self):
        """
        Shutdown VickiPlayer and auxiliary loops
        """
        self.shutdown_flag = True
        self.exit_task = True
        self.player.shutdown()
        self.thread_group.stop_all()
