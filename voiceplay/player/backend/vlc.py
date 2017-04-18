#-*- coding: utf-8 -*-
""" VLC player backend """

import re
import sys
import time

from distutils.version import LooseVersion
from functools import cmp_to_key

from voiceplay import __title__
from voiceplay.logger import logger
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.track import normalize, track_ok
from voiceplay.utils.helpers import cmp, run_hooks

class VLCProfileModel(object):
    """
    VLC profile model
    """
    headers = {}
    opts = ['--file-caching=10000', '--disc-caching=10000',
            '--live-caching=10000', '--network-caching=10000',
            '--audio-replay-gain-mode=track',
            '--no-playlist-cork']

    @classmethod
    def get_options(cls):
        """
        Get libvlc options
        """
        from voiceplay.extlib.vlcpython.vlc import libvlc_get_version
        version = libvlc_get_version()
        if sys.version_info.major == 3:
            version = version.decode()
        version = version.split(' ')[0]
        opts = cls.opts
        if LooseVersion(version) >= LooseVersion('2.2.4'):
            opts.append('--metadata-network-access')
        return opts

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


class VLCInstance(object):
    """
    VLC player backend using libvlc python bindings
    """
    def __init__(self, argparser=None, debug=False, profile='default'):
        self.debug = debug
        self.argparser = argparser
        self.exit = False
        self.paused = False
        self.player_hooks = sorted(PluginLoader().find_classes('voiceplay.player.hooks', BasePlayerHook),
                                   key=cmp_to_key(lambda x, y: cmp(x.__priority__, y.__priority__)))
        self._current_track = None
        self.player, self.instance = self.create_instance(debug=debug, profile=profile)

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
        from voiceplay.extlib.vlcpython.vlc import Meta
        meta = self.player.get_media().get_meta(Meta.NowPlaying)
        result = meta if meta else track
        return normalize(result)

    def play(self, path, track, block=True):
        """
        Play track using libvlc player
        """
        try:
            media = self.instance.media_new(path)
            self.player.set_media(media)
            self.player.play()
        except Exception as exc:
            run_hooks(self.argparser, self.player_hooks, 'on_playback_error', exception=exc)
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
                    run_hooks(self.argparser, self.player_hooks, 'on_playback_start', path=path, track=track_name)
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
            run_hooks(self.argparser, self.player_hooks, 'on_playback_pause')

    def resume(self):
        """
        Resume libvlc player
        """
        if not self.player.is_playing() and self.paused:
            self.player.pause()
            self.paused = False
            run_hooks(self.argparser, self.player_hooks, 'on_playback_resume')

    def stop(self):
        """
        Stop libvlc player
        """
        self.player.stop()
        run_hooks(self.argparser, self.player_hooks, 'on_playback_stop')

    @staticmethod
    def create_instance(debug=False, profile='default'):
        """
        Create VLC instance
        """
        from voiceplay.extlib.vlcpython.vlc import Instance
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
        agent = headers.get('user-agent', '')
        if agent:
            logger.debug('Setting user agent to: %s', agent)
            instance.set_user_agent(__title__, agent)
        player = instance.media_player_new()
        return player, instance


class VLCPlayer(object):
    """
    VLC Player wrapper class
    """
    argparser = None
    debug = False
    player = None

    @classmethod
    def play(cls, path, track, block=True):
        """
        play file/url using VLC
        """
        logger.debug('VLCPlayer.play.argparser: %r', cls.argparser)
        restore = False
        if path and re.match('^http://(.+)\.di\.fm\:?(?:[0-9]+)?/(.+)$', path):
            logger.debug('Reinitializing player...')
            cls.player.stop()
            cls.player.instance.release()
            cls.player = None
            cls.player = VLCInstance(argparser=cls.argparser, debug=cls.debug, profile='difm')
            restore = True
        cls.player.play(path, track, block=block)
        if restore and cls.player:
            cls.player.stop()
            cls.player.instance.release()
            cls.player = None
            cls.player = VLCInstance(argparser=cls.argparser, debug=cls.debug)

    @classmethod
    def resume(cls):
        """
        Resume playback
        """
        cls.player.resume()

    @classmethod
    def pause(cls):
        """
        Pause playback
        """
        cls.player.pause()

    @classmethod
    def stop(cls):
        """
        Stop playback
        """
        if cls.player:
            cls.player.stop()

    @classmethod
    def start(cls, debug=False):
        """
        Start player
        """
        logger.debug('VLCPlayer.start.argparser: %r', cls.argparser)
        cls.debug = debug
        if not cls.player:
            cls.player = VLCInstance(argparser=cls.argparser, debug=debug)

    @classmethod
    def shutdown(cls):
        """
        Shutdown player
        """
        cls.player.shutdown()
        cls.player = None

    @classmethod
    def get_volume(cls):
        """
        Get playback volume (software mixer)
        """
        return cls.player.volume

    @classmethod
    def set_volume(cls, volume):
        """
        Set playback volume (software mixer)
        """
        cls.player.volume = volume

    @classmethod
    def current_track(cls):
        """
        Return track that is being currently played
        """
        return cls.player.current_track

    @classmethod
    def set_argparser(cls, argparser):
        """
        Set argument parser for VLC wrapper (additional configuration)
        """
        cls.argparser = argparser
