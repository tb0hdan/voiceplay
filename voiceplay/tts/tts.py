import platform
import sys
if sys.version_info.major == 2:
    from Queue import Queue
elif sys.version_info.major == 3:
    from queue import Queue

import time

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
