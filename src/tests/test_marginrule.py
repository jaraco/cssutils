"""Testcases for cssutils.css.CSSPageRule"""

import xml.dom
import test_cssrule
import cssutils

class MarginRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(MarginRuleTestCase, self).setUp()
        
        cssutils.ser.prefs.useDefaults()
        self.r = cssutils.css.CSSPageRule()
        self.rRO = cssutils.css.CSSPageRule(readonly=True)
        self.r_type = cssutils.css.CSSPageRule.PAGE_RULE#
        self.r_typeString = 'PAGE_RULE'

    def tearDown(self):
        cssutils.ser.prefs.useDefaults()
            
    def test_init(self):
        "CSSPageRule.__init__()"
        # TODO
        self.assertEqual(1, 0)

if __name__ == '__main__':
    import unittest
    unittest.main()
