import unittest
from tests import mytestrunner
from voiceplay.webapp.pages.indexpage.index import IndexView
from voiceplay.webapp.baseresource import APIV1Resource
from voiceplay.webapp.vpweb import WebApp, StandaloneApplication, WrapperApplication

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
