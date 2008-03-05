# -*- coding: utf-8 -*-
"""Testcases for cssutils.css.CSSCharsetRule"""
__version__ = '$Id$'

import os
import tempfile
import xml.dom
import basetest
import cssutils
import codecs

class CSSutilsTestCase(basetest.BaseTestCase):

    def test_parse(self):
        "cssutils.parse()"
        css = u'a:after { content: "羊蹄€\u2020" }'

        fd, name = tempfile.mkstemp('_cssutilstest.css')
        t = os.fdopen(fd, 'wb')
        t.write(css.encode('utf-8'))
        t.close()
        
        self.assertRaises(
            UnicodeDecodeError, cssutils.parse, name, 'ascii')
        
        # ???
        s = cssutils.parse(name, encoding='iso-8859-1')
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))
        self.assertEqual(s.cssRules[0].selectorText, 'a:after')
        
        s = cssutils.parse(name, encoding='utf-8')
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))
        self.assertEqual(s.cssRules[0].selectorText, 'a:after')

        css = u'@charset "iso-8859-1"; a:after { content: "ä" }'
        t = codecs.open(name, 'w', 'iso-8859-1')
        t.write(css)
        t.close()
        
        self.assertRaises(
            UnicodeDecodeError, cssutils.parse, name, 'ascii')
        
        s = cssutils.parse(name, encoding='iso-8859-1')
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))
        self.assertEqual(s.cssRules[1].selectorText, 'a:after')

        self.assertRaises(
            UnicodeDecodeError, cssutils.parse, name, 'utf-8')

        # clean up
        os.remove(name)

    def test_parseString(self):
        "cssutils.parseString()"
        exp = '''a {
    left: 0
    }'''
        s = cssutils.parseString(exp)
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))
        self.assertEqual(exp, s.cssText)

    def test_setCSSSerializer(self):
        "cssutils.setSerializer() and cssutils.ser"
        s = cssutils.parseString('a { left: 0 }')
        exp4 = '''a {
    left: 0
    }'''
        exp1 = '''a {
 left: 0
 }'''
        self.assertEqual(exp4, s.cssText)
        newser = cssutils.CSSSerializer(cssutils.serialize.Preferences(indent=' '))
        cssutils.setSerializer(newser)
        self.assertEqual(exp1, s.cssText)
        newser = cssutils.CSSSerializer(cssutils.serialize.Preferences(indent='    '))
        cssutils.ser = newser
        self.assertEqual(exp4, s.cssText)


if __name__ == '__main__':
    import unittest
    unittest.main()
