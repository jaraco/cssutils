"""testcases for cssutils.CSSSerializer
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import basetest
import cssutils

class CSSSerializerTestCase(basetest.BaseTestCase):
    """
    testcases for cssutils.CSSSerializer
    """
##    def test_init(self):
##        "CSSSerializer.__init__()"

    def _resetprefs(self):
        cssutils.ser.prefs = cssutils.serialize.Preferences()

    def test_preferences(self):
        "Preferences"
        self._resetprefs()
        self.assertEqual(cssutils.ser.prefs.defaultAtKeyword, True)
        self.assertEqual(cssutils.ser.prefs.defaultPropertyName, True)
        self.assertEqual(cssutils.ser.prefs.importHrefFormat, None)
        self.assertEqual(cssutils.ser.prefs.indent, 4 * u' ')
        self.assertEqual(cssutils.ser.prefs.keepAllProperties, False)
        self.assertEqual(cssutils.ser.prefs.keepComments, True)
        self.assertEqual(cssutils.ser.prefs.lineNumbers, False)
        self.assertEqual(cssutils.ser.prefs.lineSeparator, u'\n')
        self.assertEqual(cssutils.ser.prefs.omitLastSemicolon, True)
        self.assertEqual(cssutils.ser.prefs.removeInvalid, True)

    def test_defaultAtKeyword(self):
        "CSSSerializer Preferences.defaultAtKeyword"
        s = cssutils.parseString(u'@im\port "x";')
        self.assertEqual(u'@import "x";', s.cssText)
        cssutils.ser.prefs.defaultAtKeyword = True
        self.assertEqual(u'@import "x";', s.cssText)
        cssutils.ser.prefs.defaultAtKeyword = False
        self.assertEqual(u'@im\\port "x";', s.cssText)

        self._resetprefs()

    def test_defaultPropertyName(self):
        "CSSSerializer Preferences.defaultPropertyName"
        # does not actually work as once the name is set it is used also if used with
        # a backslash in it later...

        s = cssutils.parseString(u'a { c\olor: green; }')
        self.assertEqual(u'a {\n    color: green\n    }', s.cssText)
        cssutils.ser.prefs.defaultPropertyName = True
        self.assertEqual(u'a {\n    color: green\n    }', s.cssText)
        cssutils.ser.prefs.defaultPropertyName = False
        self.assertEqual(u'a {\n    c\\olor: green\n    }', s.cssText)

        s = cssutils.parseString(u'a { color: red; c\olor: green; }')
        self.assertEqual(u'a {\n    c\\olor: green\n    }', s.cssText)
        cssutils.ser.prefs.defaultPropertyName = False
        self.assertEqual(u'a {\n    c\\olor: green\n    }', s.cssText)
        cssutils.ser.prefs.defaultPropertyName = True
        self.assertEqual(u'a {\n    color: green\n    }', s.cssText)

        self._resetprefs()

    def test_importHrefFormat(self):
        "CSSSerializer Preferences.importHrefFormat"
        r0 = cssutils.css.CSSImportRule(u'not')
        r1 = cssutils.css.CSSImportRule(u'str', hreftype="string")
        r2 = cssutils.css.CSSImportRule(u'uri', hreftype="uri")
        self.assertEqual(u'@import url(not);', r0.cssText)
        self.assertEqual(u'@import "str";', r1.cssText)
        self.assertEqual(u'@import url(uri);', r2.cssText)

        cssutils.ser.prefs.importHrefFormat = 'string'
        self.assertEqual(u'@import "not";', r0.cssText)
        self.assertEqual(u'@import "str";', r1.cssText)
        self.assertEqual(u'@import "uri";', r2.cssText)

        cssutils.ser.prefs.importHrefFormat = 'uri'
        self.assertEqual(u'@import url(not);', r0.cssText)
        self.assertEqual(u'@import url(str);', r1.cssText)
        self.assertEqual(u'@import url(uri);', r2.cssText)

        cssutils.ser.prefs.importHrefFormat = 'not defined'
        self.assertEqual(u'@import url(not);', r0.cssText)
        self.assertEqual(u'@import "str";', r1.cssText)
        self.assertEqual(u'@import url(uri);', r2.cssText)

        self._resetprefs()

    def test_indent(self):
        "CSSSerializer Preferences.ident"
        s = cssutils.parseString(u'a { left: 0 }')
        exp4 = u'''a {
    left: 0
    }'''
        exp1 = u'''a {
 left: 0
 }'''
        self.assertEqual(exp4, s.cssText)
        cssutils.ser.prefs.indent = ' '
        self.assertEqual(exp1, s.cssText)
        cssutils.ser.prefs.indent = '    '
        self.assertEqual(exp4, s.cssText)

        self._resetprefs()

    def test_lineNumbers(self):
        "CSSSerializer Preferences.lineNumbers"
        s = cssutils.parseString('a {top: 1; left: 2}')
        exp0 = '''a {
    top: 1;
    left: 2
    }'''
        exp1 = '''1: a {
2:     top: 1;
3:     left: 2
4:     }'''
        self.assertEqual(False, cssutils.ser.prefs.lineNumbers)
        self.assertEqual(exp0, s.cssText)
        cssutils.ser.prefs.lineNumbers = True
        self.assertEqual(True, cssutils.ser.prefs.lineNumbers)
        self.assertEqual(exp1, s.cssText)

        self._resetprefs()

    def test_lineSeparator(self):
        "CSSSerializer Preferences.lineSeparator"
        s = cssutils.parseString('a { x:1;y:2}')
        self.assertEqual('a {\n    x: 1;\n    y: 2\n    }', s.cssText)
        # cannot be indented as no split possible
        cssutils.ser.prefs.lineSeparator = u''
        self.assertEqual('a {x: 1;y: 2    }', s.cssText)
        # no valid css but should work
        cssutils.ser.prefs.lineSeparator = u'XXX'
        self.assertEqual('a {XXX    x: 1;XXX    y: 2XXX    }', s.cssText)

        self._resetprefs()

    def test_keepComments(self):
        "CSSSerializer Preferences.keepComments"
        s = cssutils.parseString('/*1*/ a { /*2*/ }')
        cssutils.ser.prefs.keepComments = False
        self.assertEqual('a {}', s.cssText)

        self._resetprefs()

    def test_keepAllProperties(self):
        "CSSSerializer Preferences.keepAllProperties"
        css = '''a {
            color: pink;
            color: red;
            c\olor: blue;
            c\olor: green;
            }'''
        s = cssutils.parseString(css)
        # keep only last
        self.assertEqual(u'a {\n    color: green\n    }', s.cssText)
        # keep all
        cssutils.ser.prefs.keepAllProperties = True
        self.assertEqual(u'a {\n    color: pink;\n    color: red;\n    c\olor: blue;\n    c\olor: green\n    }', s.cssText)

        self._resetprefs()

    def test_Property(self):
        "CSSSerializer.do_Property"
        name="color"
        value="red"
        priority="!important"

        s = cssutils.css.property.Property(
            name=name, value=value, priority=priority)
        self.assertEqual(u'color: red !important',
                    cssutils.ser.do_Property(s))

        s = cssutils.css.property.Property(
            name=name, value=value)
        self.assertEqual(u'color: red',
                    cssutils.ser.do_Property(s))


if __name__ == '__main__':
    import unittest
    unittest.main()
