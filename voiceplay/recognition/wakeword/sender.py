#-*- coding: utf-8 -*-
''' VoicePlay wakeword module '''

import socket
import sys
if sys.version_info.major == 2:
    from Queue import Queue  # pylint:disable=import-error
elif sys.version_info.major == 3:
    from queue import Queue  # pylint:disable=import-error

import threading
import time
import extlib.snowboydetect.snowboydecoder as snowboydecoder

from voiceplay.logger import logger
from voiceplay.utils.helpers import restart_on_crash

class WakeWordListener(object):
    '''
    Separate wakeword listener process class
    '''
    models = ["extlib/snowboydetect/resources/Vicki_en.pmdl",
              "extlib/snowboydetect/resources/Viki_de.pmdl",
              "extlib/snowboydetect/resources/Viki_fr.pmdl"]

    def __init__(self):
        self.wake_up = False
        self.exit = False
        self.ip = '127.0.0.1'
        self.port = '63455'
        self.queue = Queue()

    def async_worker(self):
        while not self.exit:
            if not self.queue.empty():
                message = self.queue.get()
            else:
                time.sleep(0.05)
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.ip, int(self.port)))
                len_sent = s.send(message)
                response = s.recv(1024)
                self.queue.task_done()
            except Exception as exc:
                logger.error('TCPAsync worker failed with %r, restarting...', exc)

    def wakeword_listener(self):
        print ('starting detector!')
        th = threading.Thread(name='TCPAsync', target=restart_on_crash, args=(self.async_worker,))
        th.setDaemon(True)
        th.start()
        sensitivity = [0.5, 0.3, 0.3]#[0.5] * len(self.models)
        self.detector = snowboydecoder.HotwordDetector(self.models, sensitivity=sensitivity, audio_gain=1)
        try:
            self.detector.start(detected_callback=self.wakeword_callback, interrupt_check=self.interrupt_check, sleep_time=0.03)
        except (KeyboardInterrupt, SystemExit):
            self.exit = True
            th.join()

    def interrupt_check(self):
        return self.exit

    def wakeword_callback(self):
        print ('wakey!')
        self.queue.put('wakeup')

if __name__ == '__main__':
    listener = WakeWordListener()
    listener.wakeword_listener()
