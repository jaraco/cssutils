"""testcases for cssutils.css.CSSRule
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils.css

class CSSRuleTestCase(basetest.BaseTestCase):
    """
    base class for all CSSRule subclass tests

    overwrite setUp with the appriopriate values, will be used in
    test_init and test_readonly
    overwrite all tests as you please, use::

        super(CLASSNAME, self).test_TESTNAME(params)

    to use the base class tests too
    """
    def setUp(self):
        """
        OVERWRITE!
        self.r is the rule
        self.rRO the readonly rule
        relf.r_type the type as defined in CSSRule
        """
        super(CSSRuleTestCase, self).setUp()
        self.sheet = cssutils.css.CSSStyleSheet()
        self.r = cssutils.css.CSSRule()
        self.rRO = cssutils.css.CSSRule()
        self.rRO._readonly = True # must be set here!
        self.r_type = cssutils.css.CSSRule.UNKNOWN_RULE
        self.r_typeString = 'UNKNOWN_RULE'

    def test_init(self):
        "CSSRule.type and init"
        self.assertEqual(self.r_type, self.r.type)
        self.assertEqual(self.r_typeString, self.r.typeString)
        self.assertEqual(u'', self.r.cssText)
        self.assertEqual(None, self.r.parentRule)
        self.assertEqual(None, self.r.parentStyleSheet)

    def test_readonly(self):
        "CSSRule readonly"
        self.assertEqual(True, self.rRO._readonly)
        self.assertEqual(u'', self.rRO.cssText)
        self.assertRaises(xml.dom.NoModificationAllowedErr,
                          self.rRO._setCssText, u'x')
        self.assertEqual(u'', self.rRO.cssText)

    def _test_InvalidModificationErr(self, startwithspace):
        """
        CSSRule.cssText InvalidModificationErr

        called by subclasses

        startwithspace

        for test starting with this not the test but " test" is tested
        e.g. " @page {}"
        exception is the style rule test
        """
        tests = (u'',
                 u'/* comment */',
                 u'@charset "utf-8";',
                 u'@font-face {}',
                 u'@import url(x);',
                 u'@media all {}',
                 u'@namespace "x";'
                 u'@page {}',
                 u'@unknown;',
                 u'a style rule {}'
                 )
        for test in tests:
            if startwithspace in (u'a style rule', ) and test in (
                u'/* comment */', u'a style rule {}'):
                continue

            if test.startswith(startwithspace):
                test = u' %s' % test

            self.assertRaises(xml.dom.InvalidModificationErr,
                 self.r._setCssText, test)


if __name__ == '__main__':
    import unittest
    unittest.main()
