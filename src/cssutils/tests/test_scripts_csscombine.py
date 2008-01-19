"""
testcases for cssutils.scripts.csscombine
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2008-01-12 21:28:54 +0100 (Sa, 12 Jan 2008) $'
__version__ = '$LastChangedRevision: 831 $'

import os
import basetest
from cssutils.scripts import csscombine
import cssutils

class CSSCombine(basetest.BaseTestCase):

    def test_combine(self):
        "scripts.csscombine"
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, 
                         '@charset "utf-8";a{color:green}body{color:#fff;background:#000}' 
                         )
        combined = csscombine(csspath, targetencoding='ascii')
        self.assertEqual(combined, 
                         '@charset "ascii";a{color:green}body{color:#fff;background:#000}' 
                         )

        cssutils.log.raiseExceptions = True 

    def tearDown(self):
        # needs to be re-enabled here for other tests
        cssutils.log.raiseExceptions = True
        cssutils.ser.prefs.useDefaults() 


if __name__ == '__main__':
    import unittest
    unittest.main()
