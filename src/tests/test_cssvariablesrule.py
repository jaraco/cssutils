"""Testcases for cssutils.css.CSSPageRule"""
__version__ = '$Id: test_csspagerule.py 1869 2009-10-17 19:37:40Z cthedot $'

import xml.dom
import test_cssrule
import cssutils

class CSSVariablesRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSVariablesRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSVariablesRule()
        self.rRO = cssutils.css.CSSVariablesRule(readonly=True)
        self.r_type = cssutils.css.CSSPageRule.VARIABLES_RULE
        self.r_typeString = 'VARIABLES_RULE'

    def test_init(self):
        "CSSVariablesRule.__init__()"
        super(CSSVariablesRuleTestCase, self).test_init()

        r = cssutils.css.CSSVariablesRule()
        self.assertEqual(cssutils.css.CSSVariablesDeclaration, 
                         type(r.variables))
        self.assertEqual(r, r.variables.parentRule)

        # until any variables
        self.assertEqual(u'', r.cssText)

        # only possible to set @... similar name
        self.assertRaises(xml.dom.InvalidModificationErr, 
                          self.r._setAtkeyword, 'x')

        def checkref(r):
            self.assertEqual(r, r.variables.parentRule)
                
        checkref(cssutils.css.CSSVariablesRule(
                 variables=cssutils.css.CSSVariablesDeclaration('x: 1')))
        
        r = cssutils.css.CSSVariablesRule()
        r.cssText = '@variables { x: 1 }'
        checkref(r)
        
    def test_InvalidModificationErr(self):
        "CSSVariablesRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@variables')
        tests = {
            u'@var {}': xml.dom.InvalidModificationErr,
            }
        self.do_raise_r(tests)

    def test_incomplete(self):
        "CSSVariablesRule (incomplete)"
        tests = {
            u'@variables { ':
                u'', # no } and no content
            u'@variables { x: red':
                u'@variables {\n    x: red\n    }', # no }
        }
        self.do_equal_p(tests) # parse

    def test_cssText(self):
        "CSSVariablesRule"
        EXP = u'@variables {\n    margin: 0\n    }'
        tests = {
             u'@variables {}': u'',
             u'@variables     {margin:0;}': EXP,
             u'@VaRIables {margin:0;}': EXP,
            u'@\\VaRIables {margin:0;}': EXP,

            # comments
            u'@variables   /*1*/   {margin:0;}': 
                u'@variables /*1*/ {\n    margin: 0\n    }',
            u'@variables/*1*/{margin:0;}': 
                u'@variables /*1*/ {\n    margin: 0\n    }',
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

    def test_reprANDstr(self):
        "CSSVariablesRule.__repr__(), .__str__()"
        r = cssutils.css.CSSVariablesRule()
        r.cssText = '@variables { xxx: 1 }'
        self.assert_('xxx' in str(r))

        r2 = eval(repr(r))
        self.assert_(isinstance(r2, r.__class__))
        self.assert_(r.cssText == r2.cssText)


if __name__ == '__main__':
    import unittest
    unittest.main()
