#-*- coding: utf-8 -*-
""" MPlayer backend """

import time

# fork of https://github.com/baudm/mplayer.py at https://github.com/tb0hdan/mplayer.py/
from mplayer import Player


class MPlayer(object):
    def __init__(self, *args, **kwargs):
        self.argparser = None
        self.exit = False
        self.paused = False
        self.player = Player()

    def set_argparser(self, argparser):
        self.argparser = argparser

    def start(self, *args, **kwargs):
        pass

    @property
    def is_playing(self):
        if self.player.filename and not self.paused:
            status = True
        else:
            status = False
        return status

    def play(self, path, track, block=True):
        self.player.loadfile(path)
        self.player.pause()
        time.sleep(3)
        if block:
            while self.player.filename:
                if self.exit:
                    break
                try:
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    pass

    def pause(self):
        if self.is_playing:
            self.paused = True
            self.player.pause()

    def stop(self):
        self.player.stop()

    def resume(self):
        if not self.is_playing:
            self.pause = False
            self.player.pause()

    def shutdown(self):
        if self.player.is_alive():
            self.player.quit()
