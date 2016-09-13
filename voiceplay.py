#!/usr/bin/env python

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

if __name__ == '__main__':
    main()
