import unittest
from tests import mytestrunner
from voiceplay.recognition.wakeword.receiver import ThreadedRequestHandler, WakeWordReceiver
# requires snowboy extension
# from voiceplay.recognition.wakeword.sender import WakeWordSender
from voiceplay.recognition.vicki import Vicki

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
