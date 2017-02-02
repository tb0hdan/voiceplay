import unittest
from tests import mytestrunner
from voiceplay.database.database import VoicePlayDB
from voiceplay.database.entities import (Artist,
                                         PlayedTracks,
                                         LastFmCache,
                                         ServiceCache)

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
