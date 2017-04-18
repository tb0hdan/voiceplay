# -*- coding: utf-8 -*-
""" Skype mood setter hook """

import platform

from voiceplay import __title__

from .basehook import BasePlayerHook


class SkypeClient(object):
    """
    Skype client class
    """
    def __init__(self, simulate=False):
        self.simulate = simulate
        self.setobj = None
        self.settext = None
        self.initialize_transport()

    @staticmethod
    def macobj():
        """
        Return usable MAC object
        """
        # pylint:disable=no-name-in-module
        from Foundation import NSAppleScript
        obj = NSAppleScript.alloc()
        return obj

    @staticmethod
    def format(message):
        """
        Formats mood message, Skype specific
        """
        message = '(music) ' + message
        return message

    def settext_apple(self, message):
        """
        Set text on Mac system
        """
        command = "tell app \"Skype\"  to send command "
        command += "\"SET PROFILE MOOD_TEXT %s\" script name " % message
        command += "\"%s\"" % __title__
        # pylint:disable=maybe-no-member
        self.setobj.initWithSource_(command)
        # pylint:disable=maybe-no-member
        self.setobj.executeAndReturnError_(None)

    @staticmethod
    def settext_dummy(message):
        """
        Just print status message without actually setting it
        """
        # pylint:disable=superfluous-parens
        print(message)

    def settext_linux(self, message):
        """
        Set text on any other NIX system (via skype4py)
        """
        # pylint:disable=protected-access
        self.setobj.CurrentUserProfile._SetMoodText(message)

    def initialize_transport(self):
        """
        Select setter transport
        """
        if self.simulate:
            self.settext = self.settext_dummy
            return
        if platform.system() == 'Darwin':
            self.setobj = self.macobj()
            self.settext = self.settext_apple
        else:
            import Skype4Py
            skype = Skype4Py.Skype()
            if skype.Client.IsRunning == False:
                skype.Client.Start()
            skype.Attach()
            self.setobj = skype
            self.settext = self.settext_linux

class SkypeNotification(object):
    """
    Skype notification Linux/MAC
    """
    @classmethod
    def notify(cls, *args, **kwargs):
        """
        Notification dispatcher
        """
        argparser = kwargs.get('argparser', '')
        track = kwargs.get('track', '')
        if not (track and argparser and argparser.skype):
            return
        skype = SkypeClient()
        skype.settext(skype.format(track))


class SkypeMoodHook(BasePlayerHook):
    """
    Skype Mood hook
    """
    __priority__ = 30

    @classmethod
    def configure_argparser(cls, parser):
        """
        Configure argument parser for this hook
        """
        parser.add_argument('-s', '--skype', action='store_true',
                            default=False,
                            dest='skype',
                            help='Enable Skype Mood Text')

    @classmethod
    def on_playback_start(cls, *args, **kwargs):
        """
        watch for on_playback_start events only
        """
        SkypeNotification.notify(*args, argparser=cls.argparser, **kwargs)
