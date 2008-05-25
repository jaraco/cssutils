# -*- coding: utf-8 -*-
"""Tests for parsing which does not raise Exceptions normally"""
__version__ = '$Id$'

import xml.dom
import basetest
import cssutils

class CSSParserTestCase(basetest.BaseTestCase):

    def test_parseString(self):
        "CSSParser.parseString()"
        tests = {
            # (byte) string, encoding: encoding, cssText
            ('/*a*/', None): ('utf-8', u'/*a*/'),
            ('/*a*/', 'ascii'): ('ascii', '@charset "ascii";\n/*a*/'),
            ('/*\xc3\xa4*/', None): ('utf-8', '/*\xc3\xa4*/'),  
            ('/*\xc3\xa4*/', 'utf-8'): ('utf-8', '@charset "utf-8";\n/*\xc3\xa4*/'),  
            ('@charset "ascii";/*a*/', None): ('ascii', u'@charset "ascii";\n/*a*/'),
            ('@charset "utf-8";/*a*/', None): ('utf-8', u'@charset "utf-8";\n/*a*/'),
            ('@charset "iso-8859-1";/*a*/', None): ('iso-8859-1', u'@charset "iso-8859-1";\n/*a*/'),
            
            # unicode string, no encoding: encoding, cssText
            (u'/*€*/', None): (
               'utf-8', u'/*€*/'.encode('utf-8')),  
            (u'@charset "iso-8859-1";/*ä*/', None): (
                'iso-8859-1', u'@charset "iso-8859-1";\n/*ä*/'.encode('iso-8859-1')),  
            (u'@charset "utf-8";/*€*/', None): (
                'utf-8', u'@charset "utf-8";\n/*€*/'.encode('utf-8')),  
            (u'@charset "utf-16";/**/', None): (
                'utf-16', u'@charset "utf-16";\n/**/'.encode('utf-16')),  
            # unicode string, encoding utf-8: encoding, cssText            
            (u'/*€*/', 'utf-8'): ('utf-8', 
               u'@charset "utf-8";\n/*€*/'.encode('utf-8')),  
            (u'@charset "iso-8859-1";/*ä*/', 'utf-8'): (
                'utf-8', u'@charset "utf-8";\n/*ä*/'.encode('utf-8')),  
            (u'@charset "utf-8";/*€*/', 'utf-8'): (
                'utf-8', u'@charset "utf-8";\n/*€*/'.encode('utf-8')),  
            (u'@charset "utf-16";/**/', 'utf-8'): (
                'utf-8', u'@charset "utf-8";\n/**/'.encode('utf-8')),
            # probably not what is wanted but does not raise:  
            (u'/*€*/', 'ascii'): (
               'ascii', u'@charset "ascii";\n/*\\20AC */'.encode('utf-8')),  
            (u'/*€*/', 'iso-8859-1'): (
               'iso-8859-1', u'@charset "iso-8859-1";\n/*\\20AC */'.encode('utf-8')),  
        }
        for test in tests:
            css, encoding = test
            sheet = cssutils.parseString(css, encoding=encoding)
            encoding, cssText = tests[test]
            self.assertEqual(encoding, sheet.encoding)
            self.assertEqual(cssText, sheet.cssText)

        tests = [
            # encoded css, overiding encoding 
            (u'/*€*/'.encode('utf-8'), 'ascii'), 
            (u'a'.encode('ascii'), 'utf-16'),
            (u'/*ä*/'.encode('iso-8859-1'), 'ascii'),
            (u'/*€*/'.encode('utf-16'), 'utf-8'),
        ]
        for test in tests:
            self.assertRaises(UnicodeDecodeError, cssutils.parseString, test[0], test[1])

    def test_fetcher(self):
        """CSSParser.fetcher
        
        order:
           0. explicity given encoding OVERRIDE (cssutils only)
           
           1. An HTTP "charset" parameter in a "Content-Type" field (or similar parameters in other protocols)
           2. BOM and/or @charset (see below)
           3. <link charset=""> or other metadata from the linking mechanism (if any)
           4. charset of referring style sheet or document (if any)
           5. Assume UTF-8
        """
        tests = {
            # css, encoding, (mimetype, encoding, importcss):
            #    encoding, importIndex, importEncoding, importText            

            # 0/0 override/override => ASCII/ASCII
            (u'@charset "utf-16"; @import "x";', 'ASCII', ('iso-8859-1', 
                                                          '@charset "latin1";/*t*/')): (
                 'ascii', 1, 'ascii', '@charset "ascii";\n/*t*/'),
            # 1/1 not tested her but same as next
            # 2/1 @charset/HTTP => UTF-16/ISO-8859-1
            (u'@charset "UTF-16"; @import "x";', None, ('ISO-8859-1', 
                                                       '@charset "latin1";/*t*/')): (
                 'utf-16', 1, 'iso-8859-1', '@charset "iso-8859-1";\n/*t*/'),
            # 2/2 @charset/@charset => UTF-16/ISO-8859-1
            (u'@charset "UTF-16"; @import "x";', None, (None, 
                                                      '@charset "ISO-8859-1";/*t*/')): (
                 'utf-16', 1, 'iso-8859-1', '@charset "iso-8859-1";\n/*t*/'),
            # 2/4 @charset/referrer => ASCII/ASCII
            ('@charset "ASCII"; @import "x";', None, (None, '/*t*/')): (
                 'ascii', 1, 'ascii', '@charset "ascii";\n/*t*/'),
            # 5/5 default/default or referrer
            ('@import "x";', None, (None, '/*t*/')): (
                 'utf-8', 0, 'utf-8', '/*t*/')
        }
        
        def make_fetcher(encoding, content):
            "make a fetcher with specified data"
            def fetcher(url):
                return encoding, content            
            return fetcher
        
        parser = cssutils.CSSParser()
        for test in tests:
            css, encoding, fetchdata = test
            sheetencoding, importIndex, importEncoding, importText = tests[test]

            # use setFetcher
            parser.setFetcher(make_fetcher(*fetchdata))
            # use init
            parser2 = cssutils.CSSParser(fetcher=make_fetcher(*fetchdata))

            sheet = parser.parseString(css, encoding=encoding)
            sheet2 = parser2.parseString(css, encoding=encoding)

            # sheet
            self.assertEqual(sheet.encoding, sheetencoding)
            self.assertEqual(sheet2.encoding, sheetencoding)
            # imported sheet
            self.assertEqual(sheet.cssRules[importIndex].styleSheet.encoding, 
                             importEncoding)
            self.assertEqual(sheet2.cssRules[importIndex].styleSheet.encoding, 
                             importEncoding)
            self.assertEqual(sheet.cssRules[importIndex].styleSheet.cssText, 
                             importText)
            self.assertEqual(sheet2.cssRules[importIndex].styleSheet.cssText, 
                             importText)

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
