#!/usr/bin/env python

from Foundation import NSUserNotification, NSUserNotificationCenter
from Foundation import (NSDate, NSTimer, NSRunLoop, NSDefaultRunLoopMode, NSSearchPathForDirectoriesInDomains,
                        NSMakeRect, NSLog, NSObject)
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem, NSAlert, NSTextField, NSImage
from PyObjCTools import AppHelper

import rumps
from voiceplay.cli.main import main
# stubs for py2app
# hooks
from voiceplay.player.hooks.logonly import LogOnlyPlayerHook
from voiceplay.player.hooks.osd import OSDNotification

# player tasks
from voiceplay.player.tasks.album import AlbumTask
from voiceplay.player.tasks.geo import GeoTask
from voiceplay.player.tasks.locallibrary import LocalLibraryTask
from voiceplay.player.tasks.singleartist import SingleArtistTask
from voiceplay.player.tasks.singletrack import SingleTrackArtistTask
from voiceplay.player.tasks.station import StationTask
from voiceplay.player.tasks.what import WhatTask

# track sources
from voiceplay.datasources.track.dmn import DailyMotionSource
from voiceplay.datasources.track.plr import PleerSource
from voiceplay.datasources.track.vmo import VimeoSource
from voiceplay.datasources.track.ytb import YoutubeSource



class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("Awesome App")

if __name__ == "__main__":
    main(noblock=True)
    AwesomeStatusBarApp().run()
