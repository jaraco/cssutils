"""
tests for parsing which does not raise Exceptions normally
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, $LastChangedRevision$'

import xml.dom

import basetest

import cssutils

class CSSStyleSheetTestCase(basetest.BaseTestCase):

    def setUp(self):
        # should be be disabled here??
        ##cssutils.log.raiseExceptions = False
        pass


    def test_invalidstring(self):
        "cssutils.parseString(INVALID_STRING)"
        validfromhere = '@import "x";'
        csss = (
            u'''@charset "ascii
                ;''' + validfromhere,
            u'''@charset 'ascii
                ;''' + validfromhere,
            u'''@import "x
                ;''' + validfromhere,
            u'''@unknown "x
                ;''' + validfromhere)
        for css in csss:
            s = cssutils.parseString(css)
            self.assertEqual(validfromhere, s.cssText)

        css = u'''a { font-family: "Courier
                ; }'''
        s = cssutils.parseString(css)
        self.assertEqual(u'a {}', s.cssText)
        

    def tearDown(self):
        # needs to be reenabled here for other tests
        cssutils.log.raiseExceptions = True
        

if __name__ == '__main__':
    import unittest
    unittest.main()
