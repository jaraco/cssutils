"""testcases for cssutils.css.CSSUnkownRule"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'


import xml.dom

import test_cssrule

import cssutils


class CSSUnknownRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSUnknownRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSUnknownRule()
        self.rRO = cssutils.css.CSSUnknownRule(readonly=True)
        self.r_type = cssutils.css.CSSUnknownRule.UNKNOWN_RULE


    def test_init(self):
        "CSSUnknownRule.type and init"
        super(CSSUnknownRuleTestCase, self).test_init()

        # only name
        r = cssutils.css.CSSUnknownRule(cssText=u'@init;')
        self.assertEqual(u'@init;', r.cssText)

        r = cssutils.css.CSSUnknownRule(cssText=u'@-init;')
        self.assertEqual(u'@-init;', r.cssText)

        r = cssutils.css.CSSUnknownRule(cssText=u'@_w-h-a-012;')
        self.assertEqual(u'@_w-h-a-012;', r.cssText)

        # name and content
        r = cssutils.css.CSSUnknownRule(cssText=u'@init xxx;')
        self.assertEqual(u'@init xxx;', r.cssText)

        # name and block
        r = cssutils.css.CSSUnknownRule(cssText=u'@init { xxx }')
        self.assertEqual(u'@init { xxx }', r.cssText)

        # name and content and block
        r = cssutils.css.CSSUnknownRule(cssText=u'@init xxx { yyy }')
        self.assertEqual(u'@init xxx { yyy }', r.cssText)


    def test_InvalidModificationErr(self):
        "CSSUnknownRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@unknown')


##    def test_cssText(self):
##        "CSSUnknownRule.cssText"
##        tests = {
##            '''
##        @three-dee {
##          @background-lighting {
##            azimuth: 30deg;
##            elevation: 190deg;
##          }
##        }
##            ''': None
##        }
##        self.do_equal_p(tests)


    def test_SyntaxErr(self):
        "CSSUnknownRule.cssText"
        # at keyword
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@;')
        self.assertRaises(xml.dom.InvalidModificationErr,
                          self.r._setCssText, '@{}')
        # rule end
##        self.assertRaises(xml.dom.SyntaxErr,
##                          self.r._setCssText, '@x }  ')
##        self.assertRaises(xml.dom.SyntaxErr,
##                          self.r._setCssText, '@x }  ;')
##        self.assertRaises(xml.dom.SyntaxErr,
##                          self.r._setCssText, '@x {  ')
##        self.assertRaises(xml.dom.SyntaxErr,
##                          self.r._setCssText, '@x {  ;')
##        self.assertRaises(xml.dom.SyntaxErr,
##                          self.r._setCssText, '@x ')
            

if __name__ == '__main__':
    import unittest
    unittest.main() 