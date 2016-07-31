import time
from extlib.vlcpython.vlc import Instance


class VLCPlayer(object):
    '''
    VLC player backend
    '''
    def __init__(self):
        self.exit = False
        self.instance = Instance()
        self.player = None
        self.paused = False

    def start(self):
        self.player = self.instance.media_player_new()

    def shutdown(self):
        self.player.stop()
        self.exit = True

    def play(self, path, block=True):
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        # allow playback to start
        time.sleep(3)
        while True:
            if self.exit:
                break
            try:
                time.sleep(0.01)
            except KeyboardInterrupt:
                pass
            if not self.player.is_playing() and not self.paused:
                break
        return True

    def pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.paused = True

    def resume(self):
        if not self.player.is_playing() and self.paused:
            self.player.pause()
            self.paused = False

    def stop(self):
        self.player.stop()
