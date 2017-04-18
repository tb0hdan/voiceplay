#-*- coding: utf-8 -*-
""" VoicePlay wakeword sender module """

import os
import socket
import time

# works after installing `future` package
from queue import Queue  # pylint:disable=import-error

import voiceplay.extlib.snowboydetect.snowboydecoder as snowboydecoder

from voiceplay.logger import logger
from voiceplay.utils.helpers import ThreadGroup

class WakeWordListener(object):
    """
    Separate wakeword listener process class
    Multiple models are supported
    """
    models = ["resources/Vicki_en.pmdl",
              "resources/Viki_de.pmdl",
              "resources/Viki_fr.pmdl"]

    def __init__(self):
        self.wake_up = False
        self.exit = False
        self.ip = '127.0.0.1'
        self.port = '63455'
        self.queue = Queue()
        self.basedir = os.path.dirname(snowboydecoder.__file__)

    def async_worker(self):
        """
        Asynchronous notifier
        """
        while not self.exit:
            if not self.queue.empty():
                message = self.queue.get()
            else:
                time.sleep(0.05)
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.ip, int(self.port)))
                _ = s.send(message)
                _ = s.recv(1024)
                self.queue.task_done()
            except Exception as exc:
                logger.error('TCPAsync worker failed with %r, restarting...', exc)

    def wakeword_listener(self):
        """
        Wakeword listener
        """
        logger.warning('starting detector!')
        threads = ThreadGroup()
        threads.targets = [self.async_worker]
        threads.start_all()
        sensitivity = [0.5, 0.3, 0.3]#[0.5] * len(self.models)
        self.detector = snowboydecoder.HotwordDetector([os.path.join(self.basedir, model) for model in self.models], sensitivity=sensitivity, audio_gain=1)
        try:
            self.detector.start(detected_callback=self.wakeword_callback, interrupt_check=self.interrupt_check, sleep_time=0.03)
        except (KeyboardInterrupt, SystemExit):
            self.exit = True
            threads.stop_all()

    def interrupt_check(self):
        """
        interrupt checker
        Returns true if exit was requested
        """
        return self.exit

    def wakeword_callback(self):
        """
        Wakeword callback. Puts "wakeup" command in queue
        """
        logger.warning('wakey!')
        self.queue.put(b'wakeup')

if __name__ == '__main__':
    listener = WakeWordListener()
    listener.wakeword_listener()
