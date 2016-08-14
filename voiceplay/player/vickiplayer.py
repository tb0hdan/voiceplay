''' VickiPlayer module '''
import re
import sys
if sys.version_info.major == 2:
    from Queue import Queue
elif sys.version_info.major == 3:
    from queue import Queue

import threading
import time

from voiceplay.config import Config
from voiceplay.logger import logger
from voiceplay.utils.loader import PluginLoader
from .backend.vlc import VLCPlayer
from .tasks.basetask import BasePlayerTask

class VickiPlayer(object):
    '''
    Vicki player class
    '''
    def __init__(self, tts=None, cfg_file='config.yaml', debug=False):
        self.debug = debug
        self.tts = tts
        self.queue = Queue()
        self.p_queue = Queue()
        self.cfg_data = Config.cfg_data()
        self.player = VLCPlayer(debug=self.debug)
        self.shutdown_flag = False
        self.exit_task = False
        self.player_tasks = sorted(PluginLoader().find_classes('voiceplay.player.tasks', BasePlayerTask),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))
        self.known_actions = self.get_actions(self.player_tasks)

    @staticmethod
    def get_actions(tasks):
        actions = []
        for task in tasks:
            for action in task.__group__:
                if not action in actions:
                    actions.append(action)
        return actions

    def get_exit(self):
        return self.exit_task

    def put(self, message):
        self.queue.put(message)

    def parse(self, message):
        '''
        Parse incoming message
        '''
        start = False
        action_phrase = []
        for word in message.split(' '):
            if word in self.known_actions:
                start = True
            if start and word:
                action_phrase.append(word)
        response = ' '.join(action_phrase)
        return response

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
            self.queue.task_done()
        logger.debug('Vickiplayer.cmd_loop exit')

    def task_loop(self):
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
            ran = False
            for task in self.player_tasks:
                for regexp in task.__regexp__:
                    if re.match(regexp, parsed) is not None:
                        ran = True
                        task.get_exit = self.get_exit
                        task.player = self.player
                        task.tts = self.tts
                        task.process(regexp, parsed)
                        break
            if not ran:
                msg = 'I think you said ' + parsed
                self.tts.say_put(msg)
                logger.warning(msg)
            self.p_queue.task_done()
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
