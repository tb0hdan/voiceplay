import unittest
from tests import mytestrunner
from voiceplay.utils.helpers import (Singleton,
                                     ThreadGroup,
                                     SingleQueueDispatcher,
                                     track_to_hash,
                                     purge_cache,
                                     restart_on_crash,
                                     run_hooks,
                                     cmp,
                                     unbreakable_input)
from voiceplay.utils.loader import PluginLoader
from voiceplay.utils.models import BaseCfgModel, BaseLfmModel
from voiceplay.utils.requestor import WSRequestor
from voiceplay.utils.score import DateMan, VideoScoreCalculator
from voiceplay.utils.snowboydownloader import SnowboyDownloader
from voiceplay.utils.track import TrackNormalizer

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
