# -*- coding: utf-8 -*-

import unittest
import pathlib
import pk_services

from . import locator

# ---

class Test_00_global(unittest.TestCase) :

    def setUp(self) :
        pass
    
    def tearDown(self):
        pass

    def test_00_Trivial(self) :
        assert True, 'True basic trivial test'
        
if __name__ == '__main__' :
    unittest.main()
