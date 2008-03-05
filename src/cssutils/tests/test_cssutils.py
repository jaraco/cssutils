# -*- coding: iso-8859-1 -*-
"""Testcases for cssutils.css.CSSCharsetRule"""
__version__ = '$Id$'

import os
import xml.dom
import basetest
import cssutils
import codecs

class CSSutilsTestCase(basetest.BaseTestCase):

    def test_parse(self):
        "cssutils.parse()"
        # temp css for tests
        name = '__cssutils_temptestfile__.css'
        css = u'a:after { content: "äu\u2020" }'

        if os.path.exists(name):
            raise IOError('skipping test as file "%s" exists' % name)

        css = u'a:after { content: "äu\u2020" }'
        t = codecs.open(name, 'w', encoding='utf-8')
        t.write(css)
        t.close()
        self.assertRaises(
            UnicodeDecodeError, cssutils.parse, name, 'ascii')
        s = cssutils.parse(name, 'iso-8859-1') #???
        s = cssutils.parse(name, 'utf-8')
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))

        css = u'a:after { content: "ä" }'
        t = codecs.open(name, 'w', 'iso-8859-1')
        t.write(css)
        t.close()
        self.assertRaises(
            UnicodeDecodeError, cssutils.parse, name, 'ascii')
        s = cssutils.parse(name, 'iso-8859-1')
        self.assertEqual(cssutils.css.CSSStyleSheet, type(s))

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
