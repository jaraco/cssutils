"""Testcases for cssutils.css.selectorlist.SelectorList."""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
from cssutils.css.selectorlist import SelectorList

class SelectorListTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = SelectorList()

    def test_init(self):
        "SelectorList.__init__() and .length"
        s = SelectorList()
        self.assertEqual(0, s.length)

        s = SelectorList('a, b')
        self.assertEqual(2, s.length)
        self.assertEqual(u'a, b', s.selectorText)

        s = SelectorList(selectorText='a')
        self.assertEqual(1, s.length)
        self.assertEqual(u'a', s.selectorText)

    def test_appendSelector(self):
        "SelectorList.appendSelector() and .length"
        s = SelectorList()
        s.appendSelector('a')
        self.assertEqual(1, s.length)

        self.assertRaises(xml.dom.InvalidModificationErr,
                          s.appendSelector, 'b,')
        self.assertEqual(1, s.length)

        self.assertEqual(u'a', s.selectorText)

    def test_selectorText(self):
        "SelectorList.selectorText"
        s = SelectorList()
        s.selectorText = u'a, b'
        self.assertEqual(u'a, b', s.selectorText)
        self.assertRaises(xml.dom.SyntaxErr, s._setSelectorText, u',')
        # not changed as invalid!
        self.assertEqual(u'a, b', s.selectorText)

        tests = {
            u'*': None,
            u'/*1*/*': None,
            u'/*1*/*, a': None,
            u'a, b': None,
            u'a ,b': u'a, b',
            u'a , b': u'a, b',
            u'a, b, c': u'a, b, c',
            u'#a, x#a, .b, x.b': u'#a, x#a, .b, x.b',
            }
        # do not parse as not complete
        self.do_equal_r(tests, att='selectorText')

        tests = {
            u'': xml.dom.SyntaxErr,
            u' ': xml.dom.SyntaxErr,
            u',': xml.dom.SyntaxErr,
            u'a,': xml.dom.SyntaxErr,
            u',a': xml.dom.SyntaxErr,
            u'/* 1 */,a': xml.dom.SyntaxErr,
            }
        # only set as not complete
        self.do_raise_r(tests, att='_setSelectorText')


if __name__ == '__main__':
    import unittest
    unittest.main()
