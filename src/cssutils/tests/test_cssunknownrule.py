"""testcases for cssutils.css.CSSUnkownRule"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import test_cssrule
import cssutils

class CSSUnknownRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSUnknownRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSUnknownRule()
        self.rRO = cssutils.css.CSSUnknownRule(readonly=True)
        self.r_type = cssutils.css.CSSUnknownRule.UNKNOWN_RULE
        self.r_typeString = 'UNKNOWN_RULE'

    def test_init(self):
        "CSSUnknownRule.type and init"
        super(CSSUnknownRuleTestCase, self).test_init()

        # only name
        r = cssutils.css.CSSUnknownRule(cssText=u'@init;')
        self.assertEqual(u'@init;', r.cssText)

        # @-... not allowed?
        r = cssutils.css.CSSUnknownRule(cssText=u'@-init;')
        self.assertEqual(u'@-init;', r.cssText)

        r = cssutils.css.CSSUnknownRule(cssText=u'@_w-h-a-012;')
        self.assertEqual(u'@_w-h-a-012;', r.cssText)

        # name and content
        r = cssutils.css.CSSUnknownRule(cssText=u'@init xxx;')
        self.assertEqual(u'@init xxx;', r.cssText)

        # name and block
        r = cssutils.css.CSSUnknownRule(cssText=u'@init { xxx }')
        self.assertEqual(u'@init {\n    xxx\n    }', r.cssText)

        # name and content and block
        r = cssutils.css.CSSUnknownRule(cssText=u'@init xxx { yyy }')
        self.assertEqual(u'@init xxx {\n    yyy\n    }', r.cssText)

    def test_InvalidModificationErr(self):
        "CSSUnknownRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@unknown')

    def test_cssText(self):
        "CSSUnknownRule.cssText"
        tests = {
            '@x;': None,
            '@x {}': None,
            '@x {\n    [()]([{}]){}\n    }': None,
            '@x{ \n \t \f\r}': u'@x {}',
            '@a {\n    @b;\n    }': None,
            '''@a {
    @b {
        x: 1x;
        y: 2y;
        }
    }''': None
        }
        self.do_equal_p(tests)
        self.do_equal_r(tests)

    def test_SyntaxErr(self):
        "CSSUnknownRule.cssText"
        # at keyword 
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@;')
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@{}')
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@ ;')
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@ {}')
        # rule end
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x {}{}')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x {};')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x ;{}')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x ;;')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x }  ')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x }  ;')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x {  ')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x {  ;')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x ')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x (;')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x );')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x [;')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x ];')
        self.assertRaises(xml.dom.SyntaxErr, self.r._setCssText, '@x {[(]()}')

    def test_reprANDstr(self):
        "CSSUnknownRule.__repr__(), .__str__()"        
        s = cssutils.css.CSSUnknownRule(cssText='@x;')
        
        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))


if __name__ == '__main__':
    import unittest
    unittest.main()
