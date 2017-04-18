#-*- coding: utf-8 -*-
""" OSD (on screen display) notification module """

import os
import platform
import sys
from tempfile import mkstemp
from voiceplay import __title__
from voiceplay.datasources.albumart import AlbumArt
from voiceplay.logger import logger
from .basehook import BasePlayerHook


class OSDNotification(object):
    """
    OSD notification (osx + growl / Linux GI)
    """

    @classmethod
    def notify(cls, *args, **kwargs):
        """
        Notification dispatcher that calls platform specific method
        """
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser and argparser.osd):
            return
        artist = track.split(' - ')[0]
        album_art = AlbumArt()
        icon = album_art.get(artist)
        if sys.version_info.major == 2:
            track = track.encode('utf-8')
        if platform.system() == 'Darwin' and icon:
            cls.darwin_notify(track, icon)
        elif platform.system() == 'Linux' and icon:
            cls.darwin_notify(track, icon)
            cls.linux_notify(track, icon)

    @classmethod
    def linux_notify(cls, message, icon):
        """
        Linux OSD using GI
        """
        from gi.repository import Notify  # pylint:disable=import-error
        if not os.environ.get('DISPLAY'):
            # try default
            os.environ['DISPLAY'] = ':0.0'
        Notify.init(__title__)
        icon_file = mkstemp()[1]
        with open(icon_file, 'wb') as fh:
            fh.write(icon)
        n = Notify.Notification.new(message, '', icon_file)
        try:
            n.show()
        except Exception as exc:
            # No X running, etc
            logger.error('OSD failed with: %r', exc)
        os.remove(icon_file)

    @classmethod
    def darwin_notify(cls, message, icon):
        """
        OSX notification using Growl
        """
        import gntp.notifier  # pylint:disable=import-error

        growl = gntp.notifier.GrowlNotifier(applicationName=__title__,
                                            notifications=["Played tracks"],
                                            defaultNotifications=["Played tracks"],)
        try:
            growl.register()
            growl.notify(noteType="Played tracks",
                         title=message,
                         description='',
                         icon=icon,
                         sticky=False,
                         priority=1,)
        except Exception as exc:
            logger.debug('Growl notification failed with: %r', exc)


class OSDPlayerHook(BasePlayerHook):
    """
    OSD hook
    """
    __priority__ = 20

    @classmethod
    def configure_argparser(cls, parser):
        """
        Configure argument parser for this hook
        """
        parser.add_argument('-o', '--osd', action='store_true',
                                 default=False,
                                 dest='osd',
                                 help='Enable OSD')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        watch for on_playback_start events only
        """
        OSDNotification.notify(*args, argparser=cls.argparser, **kwargs)
