#-*- coding: utf-8 -*-
""" VoicePlay Text to Speech engine module """

import platform
import time

# works after installing `future` package
from queue import Queue  # pylint:disable=import-error

from voiceplay import __title__
from voiceplay.logger import logger
from voiceplay.utils.helpers import ThreadGroup

class TextToSpeech(object):
    """
    MAC/Linux TTS
    """
    def __init__(self):
        self.thread = None
        self.shutdown = False
        system = platform.system()
        if system == 'Darwin':
            try:
                from AppKit import NSSpeechSynthesizer
                voice = 'Vicki'
                base = 'com.apple.speech.synthesis.voice'
                self.voice = base + '.' + voice
                self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(self.voice)
                # sierra?
                if not self.speech:
                    self.speech = NSSpeechSynthesizer.alloc().initWithVoice_(base + '.' + 'Victoria')
                self.say = self.__say_mac
            except ImportError:
                # osx lacks appkit support for python3 (sigh)
                self.say = self.__say_dummy
        elif system == 'Linux':
            self.say = self.__say_linux
        else:
            raise NotImplementedError('Platform not supported')
        self.queue = Queue()

    @staticmethod
    def __say_linux(message):
        """
        Read message aloud (Linux)
        """
        from festival import sayText  # pylint:disable=import-error
        sayText(message)

    def __say_mac(self, message):
        """
        Read message aloud (MAC)
        """
        self.speech.startSpeakingString_(message)
        while self.speech.isSpeaking():
            time.sleep(0.1)

    def __say_dummy(self, message):
        """
        Dummy TTS, does nothing
        """
        pass

    def poll_loop(self):
        """
        Poll speech queue
        """
        while not self.shutdown:
            if not self.queue.empty():
                message = self.queue.get()
                logger.debug('TTS: %r', message)
                self.say(message)
                self.queue.task_done()
            else:
                time.sleep(0.01)
        logger.debug('TTS poll_loop exit')

    def start(self):
        """
        Start TTS as a separate thread
        """
        logger.debug('Starting TTS engine...')
        self.threads = ThreadGroup()
        self.threads.targets = [self.poll_loop]
        self.threads.start_all()

    def stop(self):
        """
        Set shutdown flag and wait for thread to exit
        """
        self.shutdown = True
        self.threads.stop_all()

    def say_put(self, message):
        """
        Add message to speech queue
        """
        self.queue.put(message)
