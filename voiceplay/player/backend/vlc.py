#-*- coding: utf-8 -*-
""" VLC player backend """

import re
import sys
import time
import traceback
from functools import cmp_to_key
from voiceplay import __title__
from voiceplay.extlib.vlcpython.vlc import Instance, Meta
from voiceplay.logger import logger
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.track import normalize, track_ok
from voiceplay.utils.helpers import cmp

class VLCProfileModel(object):
    """
    VLC profile model
    """
    headers = {}
    opts = ['--file-caching=10000', '--disc-caching=10000',
            '--live-caching=10000', '--network-caching=10000',
            '--metadata-network-access', '--audio-replay-gain-mode=track',
            '--no-playlist-cork']
    @classmethod
    def get_options(cls):
        """
        Get libvlc options
        """
        return cls.opts

    @classmethod
    def get_headers(cls):
        """
        Get libvlc HTTP headers (HTTP access module)
        """
        return cls.headers


class VLCDefaultProfile(VLCProfileModel):
    """
    Default VLC profile
    """
    pass


class VLCDIFMProfile(VLCProfileModel):
    """
    DI.FM VLC profile
    """
    @classmethod
    def get_options(cls):
        """
        Get libvlc options
        """
        opts = ["--http-referrer=http://www.di.fm"]
        return cls.opts + opts

    @classmethod
    def get_headers(cls):
        """
        Get libvlc HTTP headers (HTTP access module)
        """
        headers = cls.headers
        headers['user-agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
        return headers


class VLCPlayer(object):
    """
    VLC player backend using libvlc python bindings
    """
    def __init__(self, debug=False, profile='default'):
        self.debug = debug
        self.argparser = None
        self.exit = False
        self.player = None
        self.paused = False
        self.player_hooks = sorted(PluginLoader().find_classes('voiceplay.player.hooks', BasePlayerHook),
                         key=cmp_to_key(lambda x, y: cmp(x.__priority__, y.__priority__)))
        self.instance = self.reinit_instance(debug=debug, profile=profile)
        self._current_track = None

    @staticmethod
    def reinit_instance(debug=False, profile='default'):
        """
        Reinitialize libvlc instance using new options
        TODO: fix this
        """
        if profile == 'difm':
            profile = VLCDIFMProfile
        # store other profiles somewhere here
        # fallback to default
        else:
            profile = VLCDefaultProfile
        opts = profile.get_options()
        headers = profile.get_headers()
        if debug:
            opts.append('--verbose=2')
        else:
            opts.append('--quiet')
        instance = Instance(tuple(opts))
        if headers.get('user-agent', ''):
            logger.debug('Setting user agent to: %s', headers.get('user-agent'))
            instance.set_user_agent(__title__, headers.get('user-agent'))
        return instance

    def run_hooks(self, evt, *args, **kwargs):
        """
        Run player hooks
        """
        for hook in self.player_hooks:
            hook.argparser = self.argparser
            method = getattr(hook, evt)
            if method:
                try:
                    method(*args, **kwargs)
                except Exception as exc:
                    exc_type, exc_value, exc_trace = sys.exc_info()
                    trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_trace))
                    logger.debug('Method %r crashed (see message below), restarting...\n%s\n', method, trace)

    @property
    def volume(self):
        """
        Get player volume
        """
        return self.player.audio_get_volume()

    @volume.setter
    def volume(self, value):
        """
        Set player volume
        """
        return self.player.audio_set_volume(value)

    @property
    def current_track(self):
        """
        Get current track
        """
        return self._current_track

    @current_track.setter
    def current_track(self, track_name):
        """
        Set current track
        """
        self._current_track = track_name
        return self._current_track

    def start(self):
        """
        Start libvlc player
        """
        self.player = self.instance.media_player_new()

    def shutdown(self):
        """
        Shutdown libvlc player
        """
        self.player.stop()
        self.exit = True

    def meta_or_track(self, track):
        """
        Return metadata based on ICY/META. Fallback to provided value.
        """
        meta = self.player.get_media().get_meta(Meta.NowPlaying)
        result = meta if meta else track
        return normalize(result)

    def play(self, path, track, block=True):
        """
        Play track using libvlc player
        """
        # do some magic here
        if path and re.match('^http://(.+)\.di\.fm\:?(?:[0-9]+)?/(.+)$', path):
            logger.debug('Reinitializing player...')
            self.instance = self.reinit_instance(debug=self.debug, profile='difm')
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
                self.current_track = track_name
                if track_ok(track_name):
                    self.run_hooks('on_playback_start', path=path, track=track_name)
                else:
                    logger.debug('Track %r matches blacklist %s, hooks not ran.', track_name, 'voiceplay.utils.track')
        return True

    def pause(self):
        """
        Pause libvlc player
        """
        if self.player.is_playing():
            self.player.pause()
            self.paused = True
            self.run_hooks('on_playback_pause')

    def resume(self):
        """
        Resume libvlc player
        """
        if not self.player.is_playing() and self.paused:
            self.player.pause()
            self.paused = False
            self.run_hooks('on_playback_resume')

    def stop(self):
        """
        Stop libvlc player
        """
        self.player.stop()
        self.run_hooks('on_playback_stop')
