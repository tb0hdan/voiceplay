import unittest
from tests import mytestrunner
from voiceplay.cli.main import main
from voiceplay.cli.argparser.argparser import Help, MyArgumentParser
from voiceplay.cli.console.console import Console

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
