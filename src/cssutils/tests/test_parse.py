"""tests for parsing which does not raise Exceptions normally
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils

class CSSStyleSheetTestCase(basetest.BaseTestCase):

    def test_invalidstring(self):
        "cssutils.parseString(INVALID_STRING)"
        validfromhere = '@namespace "x";'
        csss = (
            u'''@charset "ascii
                ;''' + validfromhere,
            u'''@charset 'ascii
                ;''' + validfromhere,
            u'''@namespace "y
                ;''' + validfromhere,
            u'''@import "y
                ;''' + validfromhere,
            u'''@import url('a
                );''' + validfromhere,
            u'''@unknown "y
                ;''' + validfromhere)
        for css in csss:
            s = cssutils.parseString(css)
            self.assertEqual(validfromhere, s.cssText)

        css = u'''a { font-family: "Courier
                ; }'''
        s = cssutils.parseString(css)
        self.assertEqual(u'a {}', s.cssText)

    def test_attributes(self):
        "cssutils.parseString(href, media)"
        s = cssutils.parseString("a{}", href="file:foo.css", media="screen, projection, tv")
        self.assertEqual(s.href, "file:foo.css")
        self.assertEqual(s.media.mediaText, "screen, projection, tv")

        s = cssutils.parseString("a{}", href="file:foo.css", media=["screen", "projection", "tv"])
        self.assertEqual(s.media.mediaText, "screen, projection, tv")

    def tearDown(self):
        # needs to be reenabled here for other tests
        cssutils.log.raiseExceptions = True


if __name__ == '__main__':
    import unittest
    unittest.main()
