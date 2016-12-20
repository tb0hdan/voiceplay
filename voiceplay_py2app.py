#!/usr/bin/env python

from Foundation import NSUserNotification, NSUserNotificationCenter  # pylint:disable=no-name-in-module
from Foundation import (NSDate, NSTimer, NSRunLoop, NSDefaultRunLoopMode, NSSearchPathForDirectoriesInDomains,  # pylint:disable=no-name-in-module
                        NSMakeRect, NSLog, NSObject)  # pylint:disable=no-name-in-module
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem, NSAlert, NSTextField, NSImage  # pylint:disable=no-name-in-module
from PyObjCTools import AppHelper  # pylint:disable=no-name-in-module

import rumps  # pylint:disable=no-name-in-module
from voiceplay.cli.main import main  # pylint:disable=no-name-in-module
# stubs for py2app
# hooks
from voiceplay.player.hooks.logonly import LogOnlyPlayerHook  # pylint:disable=no-name-in-module
from voiceplay.player.hooks.osd import OSDNotification  # pylint:disable=no-name-in-module

# player tasks
from voiceplay.player.tasks.album import AlbumTask  # pylint:disable=no-name-in-module
from voiceplay.player.tasks.geo import GeoTask  # pylint:disable=import-error
from voiceplay.player.tasks.locallibrary import LocalLibraryTask  # pylint:disable=no-name-in-module
from voiceplay.player.tasks.singleartist import SingleArtistTask  # pylint:disable=no-name-in-module
from voiceplay.player.tasks.singletrack import SingleTrackArtistTask  # pylint:disable=no-name-in-module
from voiceplay.player.tasks.station import StationTask  # pylint:disable=no-name-in-module
from voiceplay.player.tasks.what import WhatTask  # pylint:disable=no-name-in-module

# track sources
from voiceplay.datasources.track.dmn import DailyMotionSource  # pylint:disable=no-name-in-module
from voiceplay.datasources.track.plr import PleerSource  # pylint:disable=no-name-in-module
from voiceplay.datasources.track.vmo import VimeoSource  # pylint:disable=no-name-in-module
from voiceplay.datasources.track.ytb import YoutubeSource  # pylint:disable=no-name-in-module



class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("Awesome App")

if __name__ == "__main__":
    main(noblock=True)
    AwesomeStatusBarApp().run()
