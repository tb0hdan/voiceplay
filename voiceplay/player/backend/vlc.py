#-*- coding: utf-8 -*-

import sys
import time
import traceback
from extlib.vlcpython.vlc import Instance, Meta
from voiceplay.logger import logger
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.track import normalize

class VLCPlayer(object):
    '''
    VLC player backend
    '''
    def __init__(self, debug=False):
        self.debug = debug
        opts = ['--file-caching=10000', '--disc-caching=10000',
                '--live-caching=10000', '--network-caching=10000',
                '--metadata-network-access', '--audio-replay-gain-mode=track',
                '--no-playlist-cork']
        if self.debug:
            opts.append('--verbose=2')
        else:
            opts.append('--quiet')
        self.argparser = None
        self.exit = False
        self.instance = Instance(tuple(opts))
        self.player = None
        self.paused = False
        self.player_hooks = sorted(PluginLoader().find_classes('voiceplay.player.hooks', BasePlayerHook),
                         cmp=lambda x, y: cmp(x.__priority__, y.__priority__))

    def run_hooks(self, evt, *args, **kwargs):
        for hook in self.player_hooks:
            hook.argparser = self.argparser
            method = getattr(hook, evt)
            if method:
                try:
                    method(*args, **kwargs)
                except Exception as exc:
                    exc_type, exc_value, exc_trace = sys.exc_info()
                    trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_trace))
                    logger.debug('Method %r crashed with %r:%s, restarting...', method, exc.message, trace)

    @property
    def volume(self):
        return self.player.audio_get_volume()

    @volume.setter
    def volume(self, value):
        return self.player.audio_set_volume(value)

    def start(self):
        self.player = self.instance.media_player_new()

    def shutdown(self):
        self.player.stop()
        self.exit = True

    def meta_or_track(self, track):
        meta = self.player.get_media().get_meta(Meta.NowPlaying)
        result = meta if meta else track
        return normalize(result)

    def play(self, path, track, block=True):
        try:
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.play()
        except Exception as exc:
            self.run_hooks('on_playback_error', exception=exc)
            return False
        track_name = None
        # allow playback to start
        time.sleep(3)
        while True:
            if self.exit:
                break
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                pass
            if not self.player.is_playing() and not self.paused:
                break
            if self.meta_or_track(track) != track_name:
                track_name = self.meta_or_track(track)
                self.run_hooks('on_playback_start', path=path, track=track_name)
        return True

    def pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.paused = True
            self.run_hooks('on_playback_pause')

    def resume(self):
        if not self.player.is_playing() and self.paused:
            self.player.pause()
            self.paused = False
            self.run_hooks('on_playback_resume')

    def stop(self):
        self.player.stop()
        self.run_hooks('on_playback_stop')
