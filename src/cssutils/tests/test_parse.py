# -*- coding: utf-8 -*-
"""tests for parsing which does not raise Exceptions normally
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils

class CSSStyleSheetTestCase(basetest.BaseTestCase):

    def test_roundtrip(self):
        "cssutils encodings"
        css1 = ur'''@charset "utf-8";
/* ä */'''
        s = cssutils.parseString(css1)
        css2 = unicode(s.cssText, 'utf-8')
        self.assertEqual(css1, css2)

        s = cssutils.parseString(css2)
        s.cssRules[0].encoding='ascii'
        css3 = ur'''@charset "ascii";
/* \E4  */'''
        self.assertEqual(css3, unicode(s.cssText, 'utf-8'))

    def test_escapes(self):
        "cssutils escapes"
        css = ur'\43\x { \43\x: \43\x !import\41nt }'
        sheet = cssutils.parseString(css)
        self.assertEqual(sheet.cssText, ur'''C\x {
    c\x: C\x !important
    }''')

        css = ur'\ x{\ x :\ x ;y:1} '
        sheet = cssutils.parseString(css)
        self.assertEqual(sheet.cssText, ur'''\ x {
    \ x: \ x;
    y: 1
    }''')

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
        self.assertEqual(u'', s.cssText)

    def test_invalid(self):
        "cssutils.parseString(INVALID_CSS)"
        tests = {
            u'a {color: blue}} a{color: red} a{color: green}':
                u'''a {
    color: blue
    }
a {
    color: green
    }'''
            }

        for css in tests:
            exp = tests[css] 
            if exp == None:
                exp = css
            s = cssutils.parseString(css)
            self.assertEqual(exp, s.cssText)

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
