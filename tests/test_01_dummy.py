import unittest

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
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(s) for s in classes])
    unittest.TextTestRunner(verbosity=2).run(alltests)

