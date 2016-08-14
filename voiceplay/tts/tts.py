''' VoicePlay Text to Speech engine module '''
import platform
import sys
if sys.version_info.major == 2:
    from Queue import Queue
elif sys.version_info.major == 3:
    from queue import Queue

import threading
import time

from voiceplay import __title__
from voiceplay.logger import logger

class TextToSpeech(object):
    '''
    MAC/Linux TTS
    '''
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

    def poll_loop(self):
        '''
        Poll speech queue
        '''
        while not self.shutdown:
            if not self.queue.empty():
                self.say(self.queue.get())
                self.queue.task_done()
            else:
                time.sleep(0.01)
        logger.debug('TTS poll_loop exit')

    def start(self):
        '''
        Start TTS as a separate thread
        '''
        self.thread = threading.Thread(name='TTS', target=self.poll_loop)
        self.thread.start()

    def stop(self):
        '''
        Set shutdown flag and wait for thread to exit
        '''
        self.shutdown = True
        self.thread.join()

    def say_put(self, message):
        '''
        Add message to speech queue
        '''
        self.queue.put(message)
