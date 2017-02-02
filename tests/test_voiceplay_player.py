import unittest
from tests import mytestrunner
from voiceplay.player.backend.vlc import (VLCProfileModel,
                                          VLCDefaultProfile,
                                          VLCDIFMProfile,
                                          VLCInstance,
                                          VLCPlayer)
from voiceplay.player.controls.controls import PlayerControlResource
from voiceplay.player.hooks.basehook import BasePlayerHook
from voiceplay.player.hooks.blink1 import Blink1Hook
from voiceplay.player.hooks.logonly import LogOnlyPlayerHook
from voiceplay.player.hooks.osd import OSDNotification, OSDPlayerHook
from voiceplay.player.hooks.scrobble import TrackScrobble, ScrobbleHook
from voiceplay.player.hooks.skype import SkypeClient, SkypeMoodHook
from voiceplay.player.hooks.trackhistory import TrackHistory, TrackHistoryHook
from voiceplay.player.tasks.album import Album, AlbumTask
from voiceplay.player.tasks.artist import Artist, SingleArtistTask, SingleTrackArtistTask
from voiceplay.player.tasks.basetask import BasePlayerTask
from voiceplay.player.tasks.current_track import CurrentTrackResource, CurrentTrackTask
from voiceplay.player.tasks.difm import (DIFMResource,
                                         DIFMClient,
                                         DIFMTask)
from voiceplay.player.tasks.icecast import (IceCastResource,
                                            IcecastClient,
                                            IcecastTask)
from voiceplay.player.tasks.likethis import SomethingLikeThisResource, SomethingLikeThisTask
from voiceplay.player.tasks.locallibrary import LocalLibrary, LocalLibraryTask
from voiceplay.player.tasks.new import NewTracksResource, NewTask
from voiceplay.player.tasks.radionomy import (RadionomyResource,
                                              RadionomyClient,
                                              RadionomyTask)
from voiceplay.player.tasks.station import Station, StationTask
from voiceplay.player.tasks.top import (TopTracksResource,
                                        RS500Requestor,
                                        BB100Requestor,
                                        RedditMusicRequestor,
                                        TopTracksTask)
from voiceplay.player.tasks.trackbynumber import TrackByNumberTask
from voiceplay.player.tasks.trackhistory import LocalHistoryResource, LocalHistoryTask
from voiceplay.player.tasks.tunein import (TuneInResource,
                                           TuneInClient,
                                           TuneInTask)
from voiceplay.player.tasks.url import URLPlaybackResource, URLTask
from voiceplay.player.tasks.what import WhatTask
from voiceplay.player.tasks.zzcatcher import ZZCatcherResource, ZZCatcherTask
from voiceplay.player.vickiplayer import VickiPlayer


class DummyTestCase(unittest.TestCase):
    '''
    '''
    def setUp(self):
        pass

    def test_01_test_normal(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    classes = [DummyTestCase]
    mytestrunner(classes)
