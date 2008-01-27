"""testcases for cssutils.css.CSSPageRule
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import test_cssrule
import cssutils

class CSSPageRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSPageRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSPageRule()
        self.rRO = cssutils.css.CSSPageRule(readonly=True)
        self.r_type = cssutils.css.CSSPageRule.PAGE_RULE#
        self.r_typeString = 'PAGE_RULE'

    def test_init(self):
        "CSSPageRule.__init__()"
        super(CSSPageRuleTestCase, self).test_init()

        r = cssutils.css.CSSPageRule()
        self.assertEqual(u'', r.selectorText)
        self.assertEqual(cssutils.css.CSSStyleDeclaration, type(r.style))
        self.assertEqual(r, r.style.parentRule)

        # until any properties
        self.assertEqual(u'', r.cssText)

    def test_InvalidModificationErr(self):
        "CSSPageRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@page')
        tests = {
            u'@pag {}': xml.dom.InvalidModificationErr,
            }
        self.do_raise_r(tests)

    def test_incomplete(self):
        "CSSPageRule (incomplete)"
        tests = {
            u'@page :left { ':
                u'', # no } and no content
            u'@page :left { color: red':
                u'@page :left {\n    color: red\n    }', # no }
        }
        self.do_equal_p(tests) # parse

    def test_cssText(self):
        "CSSPageRule.cssText"
        EXP = u'@page :%s {\n    margin: 0\n    }'
        tests = {
            u'@page {margin:0;}': u'@page {\n    margin: 0\n    }',

            u'@page:left{margin:0;}': EXP % u'left',
            u'@page :left { margin: 0 }': EXP % u'left',
            u'@page :right { margin: 0 }': EXP % u'right',
            u'@page :first { margin: 0 }': EXP % u'first',
            u'@page :UNKNOWNIDENT { margin: 0 }': EXP % u'UNKNOWNIDENT',

            u'@PAGE:left{margin:0;}': u'@page :left {\n    margin: 0\n    }',
            u'@\\page:left{margin:0;}': u'@page :left {\n    margin: 0\n    }',

            u'@page/*1*/:left/*2*/{margin:0;}':
                u'@page /*1*/:left/*2*/ {\n    margin: 0\n    }',
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        tests = {
            u'@page : {}': xml.dom.SyntaxErr,
            u'@page :/*1*/left {}': xml.dom.SyntaxErr,
            u'@page : left {}': xml.dom.SyntaxErr,
            u'@page :left :right {}': xml.dom.SyntaxErr,
            u'@page :left a {}': xml.dom.SyntaxErr,

            u'@page :left;': xml.dom.SyntaxErr,
            u'@page :left }': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@page :left {': xml.dom.SyntaxErr, # no }
            })
        self.do_raise_r(tests) # set cssText

    def test_selectorText(self):
        "CSSPageRule.selectorText"
        tests = {
            u'': u'',
            u':left': None,
            u':right': None,
            u':first': None,
            u':UNKNOWNIDENT': None,

            u' :left': u':left',
            u':left': u':left',
            u'/*1*/:left/*a*/': u':left',
            u'/*1*/ :left /*a*/ /*b*/': u':left',
            u':left/*a*/': u':left',
            u'/*1*/:left': u':left',
            }
        self.do_equal_r(tests, att='selectorText')

        tests = {
            u':': xml.dom.SyntaxErr,
            u':/*1*/left': xml.dom.SyntaxErr,
            u': left': xml.dom.SyntaxErr,
            u':left :right': xml.dom.SyntaxErr,
            u':left a': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests, att='_setSelectorText')

    def test_style(self):
        "CSSPageRule.style"
        d = cssutils.css.CSSStyleDeclaration()
        self.r.style = d
        self.assertEqual(d.cssText, self.r.style.cssText)
        self.assertEqual(None, d.parentRule)

    def test_properties(self):
        "CSSPageRule.style properties"
        r = cssutils.css.CSSPageRule()
        r.style.cssText = '''
        margin-top: 0;
        margin-right: 0;
        margin-bottom: 0;
        margin-left: 0;
        margin: 0;

        page-break-before: auto;
        page-break-after: auto;
        page-break-inside: auto;

        orphans: 3;
        widows: 3;
        '''
        exp = u'''@page {
    margin-top: 0;
    margin-right: 0;
    margin-bottom: 0;
    margin-left: 0;
    margin: 0;
    page-break-before: auto;
    page-break-after: auto;
    page-break-inside: auto;
    orphans: 3;
    widows: 3
    }'''
        self.assertEqual(exp, r.cssText)

    def test_reprANDstr(self):
        "CSSPageRule.__repr__(), .__str__()"
        sel=u':left'
        
        s = cssutils.css.CSSPageRule(selectorText=sel)
        
        self.assert_(sel in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(sel == s2.selectorText)


if __name__ == '__main__':
    import unittest
    unittest.main()
