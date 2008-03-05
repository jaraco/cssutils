# -*- coding: utf-8 -*-
"""Tests for parsing which does not raise Exceptions normally"""
__version__ = '$Id$'

import xml.dom
import basetest
import cssutils

class CSSStyleSheetTestCase(basetest.BaseTestCase):

    def test_parseString(self):
        tests = {
            # for unicode encoding is ignored
            (u'@namespace "a";', 'BOGUS'): u'@namespace "a";',  
            ('@namespace "a";', None): u'@namespace "a";',
            ('@namespace "a";', 'ascii'): u'@namespace "a";',
            # automatic convertion  
            ('@namespace "b";', 'ascii'): '@namespace "b";',
            # result is str not unicode
            ('@namespace "\xc3\xa4";', None): '@namespace "\xc3\xa4";',  
            ('@namespace "\xc3\xa4";', 'utf-8'): '@namespace "\xc3\xa4";'  
        }
        for test in tests:
            css, encoding = test
            sheet = cssutils.parseString(css, encoding=encoding)
            self.assertEqual(tests[test], sheet.cssText)

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

    def test_nesting(self):
        "cssutils.parseString nesting"
        # examples from csslist 27.11.2007
        tests = {
            '@1; div{color:green}': u'div {\n    color: green\n    }', 
            '@1 []; div{color:green}': u'div {\n    color: green\n    }', 
            '@1 [{}]; div { color:green; }': u'div {\n    color: green\n    }', 
            '@media all { @ } div{color:green}': 
                u'div {\n    color: green\n    }',
            # should this be u''? 
            '@1 { [ } div{color:green}': u'',
            # red was eaten:
            '@1 { [ } ] div{color:red}div{color:green}': u'div {\n    color: green\n    }', 
             }
        for css, exp in tests.items():
            self.assertEqual(exp, cssutils.parseString(css).cssText)

    def test_specialcases(self):
        "cssutils.parseString(special_case)"
        tests = {
            u'''
    a[title="a not s\
o very long title"] {/*...*/}''': u'''a[title="a not so very long title"] {
    /*...*/
    }'''
        }
        for css in tests:
            exp = tests[css] 
            if exp == None:
                exp = css
            s = cssutils.parseString(css)
            self.assertEqual(exp, s.cssText)

    def test_iehack(self):
        "IEhack: $property"
        # $color is not color!
        css = 'a { color: green; $color: red; }'
        s = cssutils.parseString(css)

        p1 = s.cssRules[0].style.getProperty('color')
        self.assertEqual('color', p1.name)
        self.assertEqual('color', p1.literalname)
        self.assertEqual('color', p1.normalname) # DEPRECATED
        self.assertEqual('red', s.cssRules[0].style.getPropertyValue('$color'))

        p2 = s.cssRules[0].style.getProperty('$color')
        self.assertEqual('$color', p2.name)
        self.assertEqual('$color', p2.literalname)
        self.assertEqual('$color', p2.normalname) # DEPRECATED
        self.assertEqual('green', s.cssRules[0].style.getPropertyValue('color'))
        self.assertEqual('green', s.cssRules[0].style.color)

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
