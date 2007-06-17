"""Testcases for cssutils.css.selector.Selector."""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2, $LastChangedRevision$'

import xml.dom

import basetest

from cssutils.css.selector import Selector


class SelectorTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = Selector('*')

    def test_init(self):
        "Selector.__init__()"
        s = Selector('*')

    def test_selectorText(self):
        "Selector.selectorText"
        tests = {
            u'''*''': None,
            u'''*/*x*/''': None,
            u'''* /*x*/''': None,
            u'''*:hover''': None,
            u'''* :hover''': None,
            u'''*:lang(fr)''': None,
            u'''* :lang(fr)''': None,
            u'''*::first-line''': None,
            u'''* ::first-line''': None,
            u'''*[lang=fr]''': None,
            u'''[lang=fr]''': None,

            u'''a''': None,
            u'''h1''': None,
            u'''.a a''': None,

            u'''a1''': None,
            u'''a1-1''': None,
            u'''.a1-1''': None,
            u'''.a1._1''': None,

            u'''[x]''': None,
            u'''*[x]''': None,
            u'''a[x]''': None,
            u'''a[ x]''': 'a[x]',
            u'''a[x ]''': 'a[x]',
            u'''a [x]''': 'a [x]',
            u'''* [x]''': None, # is really * *[x]

            u'''a[x="1"]''': None,
            u'''a[x ="1"]''': 'a[x="1"]',
            u'''a[x= "1"]''': 'a[x="1"]',
            u'''a[x = "1"]''': 'a[x="1"]',
            u'''a[ x = "1"]''': 'a[x="1"]',
            u'''a[x = "1" ]''': 'a[x="1"]',
            u'''a[ x = "1" ]''': 'a[x="1"]',
            u'''a [ x = "1" ]''': 'a [x="1"]',

            u'''a[x~=a1]''': None,
            u'''a[x ~=a1]''': 'a[x~=a1]',
            u'''a[x~= a1]''': 'a[x~=a1]',
            u'''a[x ~= a1]''': 'a[x~=a1]',
            u'''a[ x ~= a1]''': 'a[x~=a1]',
            u'''a[x ~= a1 ]''': 'a[x~=a1]',
            u'''a[ x ~= a1 ]''': 'a[x~=a1]',
            u'''a [ x ~= a1 ]''': 'a [x~=a1]', # same as next!
            u'''a *[ x ~= a1 ]''': 'a *[x~=a1]',

            u'''a[x|=en]''': None,
            u'''a[x|= en]''': 'a[x|=en]',
            u'''a[x |=en]''': 'a[x|=en]',
            u'''a[x |= en]''': 'a[x|=en]',
            u'''a[ x |= en]''': 'a[x|=en]',
            u'''a[x |= en ]''': 'a[x|=en]',
            u'''a[ x |= en]''': 'a[x|=en]',
            u'''a [ x |= en]''': 'a [x|=en]',
            # CSS3
            u'''a[x^=en]''': None,
            u'''a[x$=en]''': None,
            u'''a[x*=en]''': None,

            u'''a[/*1*/x/*2*/]''': None,
            u'''a[/*1*/x/*2*/=/*3*/a/*4*/]''': None,
            u'''a[/*1*/x/*2*/~=/*3*/a/*4*/]''': None,
            u'''a[/*1*/x/*2*/|=/*3*/a/*4*/]''': None,

            u'''a b''': None,
            u'''a   b''': 'a b',
            u'''a   #b''': 'a #b',
            u'''a   .b''': 'a .b',
            u'''ab''': 'ab',
            u'''a.b''': None,
            u'''a.b.c''': None,

            u'''a#b''': None,
            u'''a #b''': None,

            u'''a>b''': None,
            u'''a> b''': 'a>b',
            u'''a >b''': 'a>b',
            u'''a > b''': 'a>b',
            # CSS2 combinator +
            u'''a+b''': None,
            u'''a+ b''': 'a+b',
            u'''a +b''': 'a+b',
            u'''a + b''': 'a+b',
            # CSS3 combinator ~
            u'''a~b''': None,
            u'''a~ b''': 'a~b',
            u'''a ~b''': 'a~b',
            u'''a ~ b''': 'a~b',

            u'''a+ b c''': 'a+b c',
            # namespaces
            u'''|e''': None,
            u'''*|e''': None,
            u'''n|e''': None,
            u'''n|*''': None,
            u'''*|b[x|a]''': None,
            }
        # do not parse as not complete
        self.do_equal_r(tests, att='selectorText') 

        tests = {
            u'': xml.dom.SyntaxErr,
            u'1': xml.dom.SyntaxErr,

            u'#': xml.dom.SyntaxErr,
            u'|': xml.dom.SyntaxErr,

            u':': xml.dom.SyntaxErr,
            u'::': xml.dom.SyntaxErr,
            u': a': xml.dom.SyntaxErr,
            u':: a': xml.dom.SyntaxErr,
            u'::a()': xml.dom.SyntaxErr, # pseudoelement only
            u':::a': xml.dom.SyntaxErr,
            u':1': xml.dom.SyntaxErr,

            u'#.x': xml.dom.SyntaxErr,
            u'.': xml.dom.SyntaxErr,
            u'.1': xml.dom.SyntaxErr,
            u'.a.1': xml.dom.SyntaxErr,

            u'[a': xml.dom.SyntaxErr,
            u'a]': xml.dom.SyntaxErr,
            u'[a b]': xml.dom.SyntaxErr,
            u'[=b]': xml.dom.SyntaxErr,
            u'[a=]': xml.dom.SyntaxErr,
            u'[a|=]': xml.dom.SyntaxErr,
            u'[a~=]': xml.dom.SyntaxErr,
            u'[a=1]': xml.dom.SyntaxErr,

            u'a +': xml.dom.SyntaxErr,
            u'a >': xml.dom.SyntaxErr,
            u'a ++ b': xml.dom.SyntaxErr,
            u'a + > b': xml.dom.SyntaxErr,


            u'*:lang(': xml.dom.SyntaxErr,

            # only one selector!
            u',': xml.dom.InvalidModificationErr,
            u',a': xml.dom.InvalidModificationErr,
            u'a,': xml.dom.InvalidModificationErr,
            }
        # only set as not complete
        self.do_raise_r(tests, att='_setSelectorText') 


if __name__ == '__main__':
    import unittest
    unittest.main()