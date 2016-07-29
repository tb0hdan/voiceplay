#!/usr/bin/env python
#-*- coding: utf-8 -*-
''' VoicePlay wakeword module '''

import socket
import threading
import time
import extlib.snowboydetect.snowboydecoder as snowboydecoder

class WakeWordListener(object):
    def __init__(self):
        self.wake_up = False
        self.exit = False
        self.ip = '127.0.0.1'
        self.port = '63455'

    def send_tcp_message(self, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, int(self.port)))
        len_sent = s.send(message)
        response = s.recv(1024)

    def send_tcp_message_async(self, message):
        try:
            th = threading.Thread(name='TCPAsync', target=self.send_tcp_message, args=(message,))
            th.setDaemon(True)
            th.start()
        except Exception as exc:
            pass

    def wakeword_listener(self):
        print ('starting detector!')
        self.detector = snowboydecoder.HotwordDetector("extlib/snowboydetect/resources/Vicki.pmdl", sensitivity=0.5, audio_gain=1)
        self.detector.start(detected_callback=self.wakeword_callback, interrupt_check=self.interrupt_check, sleep_time=0.03)

    def interrupt_check(self):
        return self.exit

    def wakeword_callback(self):
        print ('wakey!')
        self.send_tcp_message_async('wakeup')
        self.wake_up = True

    def run_forever(self):
        th = threading.Thread(target=self.wakeword_listener)
        th.setDaemon(True)
        th.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.exit = True
                th.join()
                break

if __name__ == '__main__':
    listener = WakeWordListener()
    listener.run_forever()
