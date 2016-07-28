#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' VoicePlay wakeword module '''

import threading
import time
import extlib.snowboydetect.snowboydecoder as snowboydecoder

class D(object):
    def __init__(self):
        self.wake_up = False
        self.exit = False

    def wakeword_listener(self):
        print ('starting detector!')
        self.detector = snowboydecoder.HotwordDetector("extlib/snowboydetect/resources/Vicki.pmdl", sensitivity=0.5, audio_gain=1)
        self.detector.start(detected_callback=self.wakeword_callback, interrupt_check=self.interrupt_check, sleep_time=0.03)

    def interrupt_check(self):
        return self.exit

    def wakeword_callback(self):
        print ('wakey!')
        self.wake_up = True

    def run_forever(self):
        th = threading.Thread(target=self.wakeword_listener)
        th.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.exit = True
                th.join()
                break


d = D()
d.run_forever()