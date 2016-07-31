import threading
import time
from extlib.vlcpython.vlc import Instance

class VLCPlayer(object):
    '''
    '''
    def __init__(self):
        self.exit = False
        self.instance = Instance()
        self.player = None

    def start(self):
        self.player = self.instance.media_player_new()

    def shutdown(self):
        self.exit = True

    def play(self, path):
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
