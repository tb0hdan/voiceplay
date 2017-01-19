import unittest

def mytestrunner(tc):
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(s) for s in tc])
    unittest.TextTestRunner(verbosity=2).run(alltests)
