#-*- coding: utf-8 -*-
''' VoicePlay speech handler '''

import logging
import speech_recognition as sr
import threading
import time

from voiceplay.logger import logger
from voiceplay.tts.tts import TextToSpeech
from voiceplay.player.vickiplayer import VickiPlayer


class Vicki(object):
    '''
    Vicki main class
    '''

    def __init__(self, debug=False):
        self.debug = debug
        self.rec = sr.Recognizer()
        self.tts = TextToSpeech()
        self.shutdown = False
        if self.debug:
            logger.setLevel(logging.DEBUG)
        logger.debug('Vicki init completed')
        self.player = VickiPlayer(tts=self.tts, debug=self.debug)
        self.wakeword_receiver = None
        self.listener = None

    def wakeword_callback(self, message):
        logger.debug(message)
        self.wake_up = True

    def background_listener(self):
        msg = 'Vicki is listening'
        self.tts.say_put(msg)
        # TODO: Fix this using callback or something so that 
        # we do not record ourselves
        time.sleep(3)
        logger.warning(msg)
        self.wake_up = False
        while not self.shutdown:

            if self.wake_up:
                logger.warning('Wake word!')
                self.tts.say_put('Yes')
                self.wake_up = False
            else:
                time.sleep(0.01)
                continue

            volume = self.player.player.volume
            self.player.player.volume = 30
            logger.debug('recog start')
            # command goes next
            try:
                with sr.Microphone() as source:
                    self.rec.adjust_for_ambient_noise(source)
                    audio = self.rec.listen(source, timeout=5)
            except sr.WaitTimeoutError:
                self.player.player.player.audio_set_volume(volume)
                continue
            try:
                result = self.rec.recognize_google(audio)
            except sr.UnknownValueError:
                msg = 'I could not understand audio'
                self.tts.say_put(msg)
                logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.tts.say_put(msg)
                logger.warning('{0}; {1}'.format(msg, e))
                result = None
            logger.debug('recog end')
            self.player.player.volume = volume
            if result:
                result = result.lower()  # pylint:disable=no-member
                logger.debug('Putting %r into processing queue', repr(result))
                # allow commands to be processed by player instance first
                self.player.put(result)
                # process local cmd
                if result in ['shutdown']:
                    self.stop()
        logger.debug('Vicki.Listener exit')

    def stop(self):
        '''
        Set shutdown flag and wait for the threads to exit
        '''
        self.shutdown = True  # for threads
        self.tts.stop()
        self.player.shutdown()
        if self.wakeword_receiver:
            self.wakeword_receiver.shutdown()

    def run_forever_new(self, wakeword_receiver, noblock=False):
        '''
        Main loop
        '''
        self.wakeword_receiver = wakeword_receiver
        if noblock:
            th = threading.Thread(target=self.background_listener)
            th.start()
            return
        while not self.shutdown:
            try:
                self.background_listener()
            except KeyboardInterrupt:
                self.stop()
            except Exception as exc:
                logger.debug('Background listener failed with %r, restarting...', exc)
