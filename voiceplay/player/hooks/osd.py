#-*- coding: utf-8 -*-

import os
import platform
import requests
from tempfile import mkstemp
from voiceplay import __title__
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.logger import logger
from .basehook import BasePlayerHook

class OSDNotification(object):
    '''
    OSD notification (osx + growl so far)
    '''
    @classmethod
    def notify(cls, *args, **kwargs):
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser and argparser.osd):
            return
        artist = track.split(' - ')[0]
        lfm = VoicePlayLastFm()
        url = lfm.get_artist_icon(artist)
        if platform.system() == 'Darwin':
            cls.darwin_notify(track, url)
        elif platform.system() == 'Linux':
            cls.linux_notify(track, url)

    @classmethod
    def linux_notify(cls, message, icon_url):
        from gi.repository import Notify  # pylint:disable=import-error
        Notify.init(__title__)
        icon_file = mkstemp()[1]
        r = requests.get(icon_url, stream=True)
        with open(icon_file, 'wb') as fh:
            for chunk in r.iter_content(1024):
                fh.write(chunk)
        n = Notify.Notification.new(message, '', icon_file)
        try:
            n.show()
        except Exception as exc:
            # No X running, etc
            logger.error('OSD failed with: %r', exc)
        os.remove(icon_file)

    @classmethod
    def darwin_notify(cls, message, icon_url):
        import gntp.notifier  # pylint:disable=import-error

        growl = gntp.notifier.GrowlNotifier(
                applicationName=__title__,
                notifications=["Played tracks"],
                defaultNotifications=["Played tracks"],
        )
        growl.register()
        growl.notify(
                noteType="Played tracks",
                title=message.encode('utf-8'),
                description='',
                icon=icon_url,
                sticky=False,
                priority=1,
        )


class OSDPlayerHook(BasePlayerHook):
    '''
    Log only hook
    '''
    __priority__ = 20

    @classmethod
    def configure_argparser(cls, parser):
        parser.add_argument('-o', '--osd', action='store_true',
                                 default=False,
                                 dest='osd',
                                 help='Enable OSD')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        OSDNotification.notify(*args, argparser=cls.argparser, **kwargs)
