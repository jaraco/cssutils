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
        self.assertEqual(set(), s.prefixes)
        self.assertEqual('*', s.selectorText)
        self.assertEqual((0,0,0,0), s.specitivity)

        s = cssutils.css.Selector('a|b')
        self.assertEqual(set('a'), s.prefixes)
        self.assertEqual('a|b', s.selectorText)
        self.assertEqual((0,0,0,1), s.specitivity)

    def test_prefixes(self):
        "Selector.prefixes"
        sel=u'a|x1 a|x2 |y *|z [b|x] [a|x="1"]'
        s = cssutils.css.Selector(selectorText=sel)
        
        self.assertEqual(set('ab'), s.prefixes)

    def test_selectorText(self):
        "Selector.selectorText"
        tests = {
            # combinators
            u'a+b>c~e f': None,
            u'a+b': None,
            u'a  +  b': 'a+b',
            u'a\n  +\t  b': 'a+b',
            u'a~b': None,
            u'a b': None,
            u'a   b': 'a b',
            u'a\nb': 'a b',
            u'a\tb': 'a b',
            u'a   #b': 'a #b',
            u'a   .b': 'a .b',
            u'a * b': None,
            # >
            u'a>b': None,
            u'a> b': 'a>b',
            u'a >b': 'a>b',
            u'a > b': 'a>b',
            # +
            u'a+b': None,
            u'a+ b': 'a+b',
            u'a +b': 'a+b',
            u'a + b': 'a+b',
            # ~
            u'a~b': None,
            u'a~ b': 'a~b',
            u'a ~b': 'a~b',
            u'a ~ b': 'a~b',

            # type selector
            u'a': None,
            u'h1-a_x__--': None,
            u'a-a': None,
            u'a_a': None,
            u'-a': None,
            u'_': None,
            u'-_': None,
            ur'-\72': u'-r',
            #ur'\25': u'%', # TODO: should be escaped!
            u'.a a': None,
            u'a1': None,
            u'a1-1': None,
            u'.a1-1': None,
            u'|e': None,
            u'*|e': None,
            u'*|*': None,
            u'n|*': None,
            u'n|e': None,
            u'-a_x12|e': None,
            u'*|b[x|a]': None,

            # universal
            u'*': None,
            u'*/*x*/': None,
            u'* /*x*/': None,
            u'*:hover': None,
            u'* :hover': None,
            u'*:lang(fr)': None,
            u'* :lang(fr)': None,
            u'*::first-line': None,
            u'* ::first-line': None,
            u'*[lang=fr]': None,
            u'[lang=fr]': None,

            # HASH
            u'''#a''': None,
            u'''#a1''': None,
            u'''#1a''': None, # valid to grammar but not for HTML
            u'''#1''': None, # valid to grammar but not for HTML
            u'''a#b''': None,
            u'''a #b''': None,
            u'''a#b.c''': None,
            u'''a.c#b''': None,
            u'''a #b.c''': None,
            u'''a .c#b''': None,

            # class
            u'ab': 'ab',
            u'a.b': None,
            u'a.b.c': None,
            u'.a1._1': None,

            # attrib
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
            
            # pseudo-elements
            u'a x:first-line': None,
            u'a x:first-letter': None,
            u'a x:before': None,
            u'a x:after': None,
            u'a x::selection': None,
            
            u'x:lang(de) y': None,
            u'x:nth-child(odd) y': None,
            # functional pseudo
            u'x:func(+-2px22.3"s"i)': None,
            u'x:func(+)': None,
            u'x:func(1px)': None,
            u'x:func(23.4)': None,
            u'x:func("s")': None,
            u'x:func(i)': None,
            
            # negation
            u':not(y)': None,
            u':not(   y  \t\n)': u':not(y)',
            u'*:not(y)': None,
            u'x:not(y)': None,
            u'.x:not(y)': None,
            u':not(*)': None,
            u':not(#a)': None,
            u':not(.a)': None,
            u':not([a])': None,
            u':not(:first-letter)': None,
            u':not(::first-letter)': None,
            
            # escapes
            ur'\74\72 td': 'trtd',
            ur'\74\72  td': 'tr td',
            ur'\74\000072 td': 'trtd',
            ur'\74\000072  td': 'tr td',
            
            # comments
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
            u'-1': xml.dom.SyntaxErr,
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

            # functional pseudo
            u'*:lang(': xml.dom.SyntaxErr,
            u'*:lang()': xml.dom.SyntaxErr, # no arg

            # negation
            u'not(x)': xml.dom.SyntaxErr, # no valid function
            u':not()': xml.dom.SyntaxErr, # no arg
            u':not(x': xml.dom.SyntaxErr, # no )
            u':not(-': xml.dom.SyntaxErr, # not allowed
            u':not(+': xml.dom.SyntaxErr, # not allowed

            # only one selector!
            u',': xml.dom.InvalidModificationErr,
            u',a': xml.dom.InvalidModificationErr,
            u'a,': xml.dom.InvalidModificationErr,

            # TODO: u'#a#b': xml.dom.SyntaxErr,
           
            }
        # only set as not complete
        self.do_raise_r(tests, att='_setSelectorText')

    def test_specitivity(self):
        "Selector.specitivity"
        selector = cssutils.css.Selector()
        tests = {
            u'*': (0,0,0,0),
            u'li': (0,0,0,1),
            u'li:first-line': (0,0,0,2),
            u'ul li': (0,0,0,2),
            u'ul ol+li': (0,0,0,3),
            u'h1 + *[rel=up]': (0,0,1,1),
            u'ul ol li.red': (0,0,1,3),
            u'li.red.level': (0,0,2,1),
            u'#x34y': (0,1,0,0),
            
            u'UL OL LI.red': (0,0,1,3),
            u'LI.red.level': (0,0,2,1),
            u'#s12:not(FOO)': (0,1,0,1),
            u'button:not([DISABLED])': (0,0,1,1), #?
            u'*:not(FOO)': (0,0,0,1),
            
            # elements
            u'a+b': (0,0,0,2),
            u'a>b': (0,0,0,2),
            u'a b': (0,0,0,2),
            u'* a': (0,0,0,1),
            u'a *': (0,0,0,1),
            u'a * b': (0,0,0,2),

            u'a:hover': (0,0,0,1),

            u'a:first-line': (0,0,0,2),
            u'a:first-letter': (0,0,0,2),
            u'a:before': (0,0,0,2),
            u'a:after': (0,0,0,2),
            
            # classes and attributes
            u'.a': (0,0,1,0),
            u'*.a': (0,0,1,0),
            u'a.a': (0,0,1,1),
            u'.a.a': (0,0,2,0), # IE<7 False (0,0,1,0) 
            u'a.a.a': (0,0,2,1), 
            u'.a.b': (0,0,2,0),
            u'a.a.b': (0,0,2,1),
            u'.a .a': (0,0,2,0),
            u'*[x]': (0,0,1,0),
            u'*[x]': (0,0,1,0),
            u'*[x]': (0,0,1,0),
            u'*[x=a]': (0,0,1,0),
            u'*[x~=a]': (0,0,1,0),
            u'*[x|=a]': (0,0,1,0),
            u'*[x^=a]': (0,0,1,0),
            u'*[x*=a]': (0,0,1,0),
            u'*[x$=a]': (0,0,1,0),
            u'*[x][y]': (0,0,2,0),
            
            # ids
            u'#a': (0,1,0,0),
            u'*#a': (0,1,0,0),
            u'x#a': (0,1,0,1),
            u'.x#a': (0,1,1,0),
            u'a.x#a': (0,1,1,1),
            u'#a#a': (0,2,0,0), # e.g. html:id + xml:id
            u'#a#b': (0,2,0,0), 
            u'#a #b': (0,2,0,0),
            }
        for text in tests:
            selector.selectorText = text
            self.assertEqual(tests[text], selector.specitivity)
            
    def test_reprANDstr(self):
        "Selector.__repr__(), .__str__()"
        sel=u'a+b'
        
        s = cssutils.css.Selector(selectorText=sel)

        self.assert_(sel in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(sel == s2.selectorText)


if __name__ == '__main__':
    import unittest
    unittest.main()
