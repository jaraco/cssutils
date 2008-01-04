# -*- coding: utf-8 -*-
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
#    def test_init(self):
#        "CSSSerializer.__init__()"

    def test_useDefaults(self):
        "Preferences.useDefaults()"
        cssutils.ser.prefs.useDefaults()
        self.assertEqual(cssutils.ser.prefs.defaultAtKeyword, True)
        self.assertEqual(cssutils.ser.prefs.defaultPropertyName, True)
        self.assertEqual(cssutils.ser.prefs.importHrefFormat, None)
        self.assertEqual(cssutils.ser.prefs.indent, 4 * u' ')
        self.assertEqual(cssutils.ser.prefs.keepAllProperties, True)
        self.assertEqual(cssutils.ser.prefs.keepComments, True)
        self.assertEqual(cssutils.ser.prefs.keepEmptyRules, False)
        self.assertEqual(cssutils.ser.prefs.lineNumbers, False)
        self.assertEqual(cssutils.ser.prefs.lineSeparator, u'\n')
        self.assertEqual(cssutils.ser.prefs.listItemSpacer, u' ')
        self.assertEqual(cssutils.ser.prefs.omitLastSemicolon, True)
        self.assertEqual(cssutils.ser.prefs.paranthesisSpacer, u' ')
        self.assertEqual(cssutils.ser.prefs.propertyNameSpacer, u' ')
        self.assertEqual(cssutils.ser.prefs.validOnly, False)
        self.assertEqual(cssutils.ser.prefs.wellformedOnly, True)
        # DEPRECATED
        self.assertEqual(cssutils.ser.prefs.removeInvalid, True)

    def test_useMinified(self):
        "Preferences.useMinified()"
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.useMinified()
        self.assertEqual(cssutils.ser.prefs.defaultAtKeyword, True)
        self.assertEqual(cssutils.ser.prefs.defaultPropertyName, True)
        self.assertEqual(cssutils.ser.prefs.importHrefFormat, 'string')
        self.assertEqual(cssutils.ser.prefs.indent, u'')
        self.assertEqual(cssutils.ser.prefs.keepAllProperties, True)
        self.assertEqual(cssutils.ser.prefs.keepComments, False)
        self.assertEqual(cssutils.ser.prefs.keepEmptyRules, False)
        self.assertEqual(cssutils.ser.prefs.lineNumbers, False)
        self.assertEqual(cssutils.ser.prefs.lineSeparator, u'')
        self.assertEqual(cssutils.ser.prefs.listItemSpacer, u'')
        self.assertEqual(cssutils.ser.prefs.omitLastSemicolon, True)
        self.assertEqual(cssutils.ser.prefs.paranthesisSpacer, u'')
        self.assertEqual(cssutils.ser.prefs.propertyNameSpacer, u'')
        self.assertEqual(cssutils.ser.prefs.validOnly, False)
        self.assertEqual(cssutils.ser.prefs.wellformedOnly, True)
        # DEPRECATED
        self.assertEqual(cssutils.ser.prefs.removeInvalid, True)
        
        css = u'''
    /*1*/
    @import url(x) tv , print;
    @media all {}
    @media all {
        a {}
    }
    @media all {
        a { color: red; }
    }
    @page {}
    a {}
    a , b { top : 1px ; 
        font-family : arial ,  'some' 
        }
    '''
        s = cssutils.parseString(css)
        self.assertEqual(s.cssText, 
            u'''@import "x" tv,print;@media all{a{color:red}}a,b{top:1px;font-family:arial,'some'}''' 
            )

    def test_defaultAtKeyword(self):
        "Preferences.defaultAtKeyword"
        cssutils.ser.prefs.useDefaults()
        
        s = cssutils.parseString(u'@im\\port "x";')
        self.assertEqual(u'@import "x";', s.cssText)
        cssutils.ser.prefs.defaultAtKeyword = True
        self.assertEqual(u'@import "x";', s.cssText)
        cssutils.ser.prefs.defaultAtKeyword = False
        self.assertEqual(u'@im\\port "x";', s.cssText)

    def test_defaultPropertyName(self):
        "Preferences.defaultPropertyName"
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.keepAllProperties = False

        # does not actually work as once the name is set it is used also 
        # if used with a backslash in it later...

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

    def test_importHrefFormat(self):
        "Preferences.importHrefFormat"
        cssutils.ser.prefs.useDefaults()

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

    def test_indent(self):
        "Preferences.ident"
        cssutils.ser.prefs.useDefaults()

        s = cssutils.parseString(u'a { left: 0 }')
        exp4 = u'''a {
    left: 0
    }'''
        exp1 = u'''a {
 left: 0
 }'''
        cssutils.ser.prefs.indent = ' '
        self.assertEqual(exp1, s.cssText)
        cssutils.ser.prefs.indent = 4* ' '
        self.assertEqual(exp4, s.cssText)

    def test_keepAllProperties(self):
        "Preferences.keepAllProperties"
        cssutils.ser.prefs.useDefaults()

        css = '''a {
            color: pink;
            color: red;
            c\olor: blue;
            c\olor: green;
            }'''
        s = cssutils.parseString(css)
        # keep only last
        cssutils.ser.prefs.keepAllProperties = False
        self.assertEqual(u'a {\n    color: green\n    }', s.cssText)
        # keep all
        cssutils.ser.prefs.keepAllProperties = True
        self.assertEqual(u'a {\n    color: pink;\n    color: red;\n    c\olor: blue;\n    c\olor: green\n    }', s.cssText)

    def test_keepComments(self):
        "Preferences.keepComments"
        cssutils.ser.prefs.useDefaults()

        s = cssutils.parseString('/*1*/ a { /*2*/ }')
        cssutils.ser.prefs.keepComments = False
        self.assertEqual('', s.cssText)
        cssutils.ser.prefs.keepEmptyRules = True
        self.assertEqual('a {}', s.cssText)

    def test_keepEmptyRules(self):
        "Preferences.keepEmptyRules"
        # CSSStyleRule
        css = u'''a {}
a {
    /*1*/
    }
a {
    color: red
    }'''
        s = cssutils.parseString(css)
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.keepEmptyRules = True
        self.assertEqual(css, s.cssText)
        cssutils.ser.prefs.keepEmptyRules = False
        self.assertEqual(u'a {\n    /*1*/\n    }\na {\n    color: red\n    }', 
                         s.cssText)
        cssutils.ser.prefs.keepComments = False
        self.assertEqual(u'a {\n    color: red\n    }', 
                         s.cssText)

        # CSSMediaRule
        css = u'''@media tv {
    }
@media all {
    /*1*/
    }
@media print {
    a {}
    }
@media print {
    a {
        /*1*/
        }
    }
@media all {
    a {
        color: red
        }
    }'''
        s = cssutils.parseString(css)
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.keepEmptyRules = True
   #     self.assertEqual(css, s.cssText)
        cssutils.ser.prefs.keepEmptyRules = False
        self.assertEqual('''@media all {
    /*1*/
    }
@media print {
    a {
        /*1*/
        }
    }
@media all {
    a {
        color: red
        }
    }''', s.cssText)
        cssutils.ser.prefs.keepComments = False
        self.assertEqual('''@media all {
    a {
        color: red
        }
    }''', s.cssText)

    def test_lineNumbers(self):
        "Preferences.lineNumbers"
        cssutils.ser.prefs.useDefaults()

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

    def test_lineSeparator(self):
        "Preferences.lineSeparator"
        cssutils.ser.prefs.useDefaults()

        s = cssutils.parseString('a { x:1;y:2}')
        self.assertEqual('a {\n    x: 1;\n    y: 2\n    }', s.cssText)
        # cannot be indented as no split possible
        cssutils.ser.prefs.lineSeparator = u''
        self.assertEqual('a {x: 1;y: 2    }', s.cssText)
        # no valid css but should work
        cssutils.ser.prefs.lineSeparator = u'XXX'
        self.assertEqual('a {XXX    x: 1;XXX    y: 2XXX    }', s.cssText)

    def test_listItemSpacer(self):
        "Preferences.listItemSpacer"
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.keepEmptyRules = True
        
        css = '''
        @import "x" print, tv;
a, b {}'''
        s = cssutils.parseString(css)
        self.assertEqual(u'@import "x" print, tv;\na, b {}', s.cssText)
        cssutils.ser.prefs.listItemSpacer = u''
        self.assertEqual(u'@import "x" print,tv;\na,b {}', s.cssText)

    def test_omitLastSemicolon(self):
        "Preferences.omitLastSemicolon"
        cssutils.ser.prefs.useDefaults()
        
        css = 'a { x: 1; y: 2 }'
        s = cssutils.parseString(css)
        self.assertEqual(u'a {\n    x: 1;\n    y: 2\n    }', s.cssText)
        cssutils.ser.prefs.omitLastSemicolon = False
        self.assertEqual(u'a {\n    x: 1;\n    y: 2;\n    }', s.cssText)

    def test_paranthesisSpacer(self):
        "Preferences.paranthesisSpacer"
        cssutils.ser.prefs.useDefaults()
        css = 'a { x: 1; y: 2 }'
        s = cssutils.parseString(css)
        self.assertEqual(u'a {\n    x: 1;\n    y: 2\n    }', s.cssText)
        cssutils.ser.prefs.paranthesisSpacer = u''
        self.assertEqual(u'a{\n    x: 1;\n    y: 2\n    }', s.cssText)
        
    def test_propertyNameSpacer(self):
        "Preferences.propertyNameSpacer"
        cssutils.ser.prefs.useDefaults()
        css = 'a { x: 1; y: 2 }'
        s = cssutils.parseString(css)
        self.assertEqual(u'a {\n    x: 1;\n    y: 2\n    }', s.cssText)
        cssutils.ser.prefs.propertyNameSpacer = u''
        self.assertEqual(u'a {\n    x:1;\n    y:2\n    }', s.cssText)

    def test_CSSStyleSheet(self):
        "CSSSerializer.do_CSSStyleSheet"
        css = u'/* κουρος */'
        sheet = cssutils.parseString(css)
        self.assertEqual(css, unicode(sheet.cssText, 'utf-8'))
        
        css = u'@charset "utf-8";\n/* κουρος */'
        sheet = cssutils.parseString(css)
        self.assertEqual(css, unicode(sheet.cssText, 'utf-8'))
        sheet.cssRules[0].encoding = 'ascii'
        self.assertEqual('@charset "ascii";\n/* \\3BA \\3BF \\3C5 \\3C1 \\3BF \\3C2  */', 
                         sheet.cssText)

    def test_Property(self):
        "CSSSerializer.do_Property"
        cssutils.ser.prefs.useDefaults()

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

    def test_escapeSTRINGtype(self):
        "CSSSerializer._escapeSTRINGtype"
        css = ur'''@import url("ABC\a");
@import "ABC\a";
@import 'ABC\a';
a[href='"\a\22\27"'] {
    a: "\a\d\c";
    b: "\a \d \c ";
    c: "\"";
    d: "\22";
    e: '\'';
    content: '\27';
    }'''
        exp = ur'''@import url("ABC\a ");
@import "ABC\a ";
@import "ABC\a ";
a[href='"\a "\'"'] {
    a: "\a \d \c ";
    b: "\a \d \c ";
    c: "\"";
    d: "\"";
    e: '\'';
    content: '\''
    }'''
        sheet = cssutils.parseString(css)
        self.assertEqual(sheet.cssText, exp)
    
    
if __name__ == '__main__':
    import unittest
    unittest.main()
