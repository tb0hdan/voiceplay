import unittest
from tests import mytestrunner
from voiceplay.datasources.albumart import AlbumArt
from voiceplay.datasources.playlists.guesser.guesser import library_guesser
from voiceplay.datasources.playlists.libraries.itunes import iTunesLibrary
from voiceplay.datasources.playlists.libraries.shazam import ShazamDownloadLibrary
from voiceplay.datasources.playlists.libraries.textfile import TextFileLibrary
from voiceplay.datasources.playlists.libraries.m3ufile import M3UFileLibrary
from voiceplay.datasources.playlists.libraries.plsfile import PLSFileLibrary
from voiceplay.datasources.playlists.libraries.asxfile import ASXFileLibrary
from voiceplay.datasources.track.basesource import TrackSource
from voiceplay.datasources.track.dmn import DailyMotionSource
from voiceplay.datasources.track.plr import PleerSource
from voiceplay.datasources.track.vmo import VimeoSource
from voiceplay.datasources.track.ytb import YoutubeSource
from voiceplay.datasources.lastfm import VoicePlayLastFm
from voiceplay.datasources.mbapi import MBAPI


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
