"""testcases for cssutils.css.CSSStyleRuleTestCase"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'


import xml.dom

import test_cssrule

import cssutils


class CSSStyleRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSStyleRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSStyleRule()
        self.rRO = cssutils.css.CSSStyleRule(readonly=True)
        self.r_type = cssutils.css.CSSStyleRule.STYLE_RULE


    def test_init(self):
        "CSSStyleRule.type and init"
        super(CSSStyleRuleTestCase, self).test_init()
        self.assertEqual(u'', self.r.cssText)
        self.assertEqual(cssutils.css.selectorlist.SelectorList,
                         type(self.r.selectorList))
        self.assertEqual(u'', self.r.selectorText)
        self.assertEqual(cssutils.css.CSSStyleDeclaration,
                         type(self.r.style))
        self.assertEqual(self.r, self.r.style.parentRule)


    def test_InvalidModificationErr(self):
        "CSSStyleRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'a style rule')


    def test_cssText(self):
        "CSSStyleRule.cssText"
        tests = {
            u'''* {}''': None,
            u'a {}': None,
            u'b { a: 1; }': u'b {\n    a: 1\n    }',
            # mix of comments and properties
            u'c1 {/*1*/a:1;}': u'c1 {\n    /*1*/\n    a: 1\n    }',
            u'c2 {a:1;/*2*/}': u'c2 {\n    a: 1;\n    /*2*/\n    }',
            u'd1 {/*0*/}': u'd1 {\n    /*0*/\n    }',
            u'd2 {/*0*//*1*/}': u'd2 {\n    /*0*/\n    /*1*/\n    }'
            }
        self.do_equal_p(tests) # parse
        self.do_equal_r(tests) # set cssText

        tests = {
            u'''a;''': xml.dom.SyntaxErr,
            u'''a {''': xml.dom.SyntaxErr,
            u'''a {{}''': xml.dom.SyntaxErr,
            u'''a }''': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'''a {}x''': xml.dom.SyntaxErr, # trailing
            u'''/*x*/''': xml.dom.SyntaxErr,
            })
        self.do_raise_r(tests) # set cssText


    def test_selectorList(self):
        "CSSStyleRule.selectorList"
        r = cssutils.css.CSSStyleRule()

        r.selectorList.appendSelector(u'a')
        self.assertEqual(1, r.selectorList.length)     
        self.assertEqual(u'a', r.selectorText)

        r.selectorList.appendSelector(u' b  ')
        # only simple selector!
        self.assertRaises(xml.dom.InvalidModificationErr,
                          r.selectorList.appendSelector, u'  h1, x ')
        
        self.assertEqual(2, r.selectorList.length)
        self.assertEqual(u'a, b', r.selectorText)


    def test_selectorText(self):
        "CSSStyleRule.selectorText"
        r = cssutils.css.CSSStyleRule()
        
        r.selectorText = u'a'
        self.assertEqual(1, r.selectorList.length)     
        self.assertEqual(u'a', r.selectorText)
        
        r.selectorText = u' b, h1  '
        self.assertEqual(2, r.selectorList.length)
        self.assertEqual(u'b, h1', r.selectorText)


    def test_style(self):
        "CSSStyleRule.style"
        d = cssutils.css.CSSStyleDeclaration()
        self.r.style = d
        self.assertEqual(d, self.r.style)

        # check if parentRule of sd set
        self.assertEqual(self.r, d.parentRule)


if __name__ == '__main__':
    import unittest
    unittest.main()