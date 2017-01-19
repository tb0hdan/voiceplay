import unittest

def testrunner(classes):
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(s) for s in classes])
    unittest.TextTestRunner(verbosity=2).run(alltests)
