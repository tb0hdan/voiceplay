import platform
import requests
from voiceplay.datasources.lastfm import VoicePlayLastFm
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
        if platform.system() == 'Darwin':
            lfm = VoicePlayLastFm()
            url = lfm.get_artist_icon(artist)

            import gntp.notifier

            growl = gntp.notifier.GrowlNotifier(
                applicationName="VoicePlay",
                notifications=["Played tracks"],
                defaultNotifications=["Played tracks"],
            )
            growl.register()

            growl.notify(
                noteType="Played tracks",
                title=track.encode('utf-8'),
                description='',
                icon=url,
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
