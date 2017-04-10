#-*- coding: utf-8 -*-
""" Primitive Blink(1) hook :) """

import multiprocessing
import subprocess
import time

from .basehook import BasePlayerHook


class Blink1Hook(BasePlayerHook):
    """
    Blink on recognition events
    Requires: https://blink1.thingm.com/ and blink1-tool
    """
    __priority__ = 100
    proc = None

    @classmethod
    def slow_blink(cls):
        """
        blink slowly
        """
        while True:
            subprocess.call(['blink1-tool', '--blue', '--chase=1'])
            time.sleep(0.5)

    @classmethod
    def on_recognition_start(cls, *args, **kwargs):
        """
        Run log action on recognition start
        """
        subprocess.call(['blink1-tool', '--blue'])
        time.sleep(0.1)
        subprocess.call(['blink1-tool', '--off'])

    @classmethod
    def on_recognition_progress(cls, *args, **kwargs):
        """
        Run log action on recognition progress
        """
        cls.proc = multiprocessing.Process(target=cls.slow_blink)
        cls.proc.start()

    @classmethod
    def on_recognition_end(cls, *args, **kwargs):
        """
        Run log action on recognition end
        """
        if cls.proc:
            cls.proc.terminate()
        subprocess.call(['blink1-tool', '--off'])
