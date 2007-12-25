"""Testcases for cssutils.css.selector.Selector.

what should happen here?
    - star 7 hack::
        x*
        does not validate but works in IE>5 and FF...

"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils

class SelectorTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = cssutils.css.Selector('*')

    def test_init(self):
        "Selector.__init__()"
        s = cssutils.css.Selector('*')

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
            u'a * b': None,

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

            u'''#a''': None,
            u'''#a1''': None,
            u'''#1a''': None, # valid to grammar but not for HTML
            u'''#1''': None, # valid to grammar but not for HTML
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
            # namespaceprefixes
            u'''|e''': None,
            u'''*|e''': None,
            u'''n|e''': None,
            u'''n|*''': None,
            u'''*|b[x|a]''': None,

            u'''x:lang(de) y''': None,
            u'''x:nth-child(odd) y''': None,
            
            u':not(y)': None,
            u'x:not(y)': None,
            u'.x:not(y)': None,
            
            # escapes
            ur'\74\72 td': 'trtd',
            ur'\74\72  td': 'tr td',
            ur'\74\000072 td': 'trtd',
            ur'\74\000072  td': 'tr td',
            
            u'a/**/ b': None,
            u'a /**/b': None,
            u'a /**/ b': None,
            u'a  /**/ b': u'a /**/ b',
            u'a /**/  b': u'a /**/ b'
            }
        # do not parse as not complete
        self.do_equal_r(tests, att='selectorText')

        tests = {
            u'': xml.dom.SyntaxErr,
            u'1': xml.dom.SyntaxErr,
            u'a*b': xml.dom.SyntaxErr,
            u'a *b': xml.dom.SyntaxErr,
            u'a* b': xml.dom.SyntaxErr,
            u'a/**/b': xml.dom.SyntaxErr,

            u'#': xml.dom.SyntaxErr,
            u'|': xml.dom.SyntaxErr,

            u':': xml.dom.SyntaxErr,
            u'::': xml.dom.SyntaxErr,
            u': a': xml.dom.SyntaxErr,
            u':: a': xml.dom.SyntaxErr,
            u':a()': xml.dom.SyntaxErr, # no value
            u'::a()': xml.dom.SyntaxErr, # no value
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

            u'not(x)': xml.dom.SyntaxErr, # no valid function

            # only one selector!
            u',': xml.dom.InvalidModificationErr,
            u',a': xml.dom.InvalidModificationErr,
            u'a,': xml.dom.InvalidModificationErr,
            }
        # only set as not complete
        self.do_raise_r(tests, att='_setSelectorText')

    def test_reprANDstr(self):
        "Selector.__repr__(), .__str__()"
        sel=u'a+b'

        s = cssutils.css.Selector(selectorText=sel)

        self.assert_(sel in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(sel == s2.selectorText)

    def test_prefixes(self):
        "Selector.prefixes"
        sel=u'a|x1 a|x2 |y *|z [b|x] [a|x="1"]'
        s = cssutils.css.Selector(selectorText=sel)
        
        self.assertEqual(set('ab'), s.prefixes)

if __name__ == '__main__':
    import unittest
    unittest.main()
