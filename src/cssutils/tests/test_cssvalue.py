"""Testcases for cssutils.css.cssvalue.CSSValue."""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils


class CSSValueTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSValue.__init__()"
        v = cssutils.css.CSSValue()
        self.assertEqual(u'inherit', v.cssText)
        self.assertEqual(v.CSS_INHERIT, v.cssValueType)

        v = cssutils.css.CSSValue(cssText=u'inherit')
        self.assertEqual(u'inherit', v.cssText)
        self.assertEqual(v.CSS_INHERIT, v.cssValueType)

        v = cssutils.css.CSSValue(cssText=u'red')
        self.assertEqual(u'red', v.cssText)
        self.assertEqual(v.CSS_PRIMITIVE_VALUE, v.cssValueType)

        # TODO: more init tests

    def test_cssText(self):
        "CSSValue.cssText"
        v = cssutils.css.CSSValue()
        v.cssText = u'1px'
        self.assertEqual(v.CSS_PRIMITIVE_VALUE, v.cssValueType)
        self.assertEqual(v.CSS_PX, v.primitiveType)
        self.assertEqual(u'1px', v.cssText)

        v.cssText = u'  1   px    '
        self.assertEqual(v.CSS_VALUE_LIST, v.cssValueType)
        self.assertEqual('1 px', v._value)
        self.assertEqual('1 px', v.cssText)

        v.cssText = u'expression(document.body.clientWidth > 972 ? "1014px": "100%" )'
        self.assertEqual(v.CSS_PRIMITIVE_VALUE, v.cssValueType)
        self.assertEqual(v.CSS_UNKNOWN, v.primitiveType)
        self.assertEqual('expression(document.body.clientWidth > 972 ? "1014px": "100%" )', v._value)
        self.assertEqual('expression(document.body.clientWidth > 972 ? "1014px": "100%" )', v.cssText)

    def test_cssValueType(self):
        "CSSValue.cssValueType"
        v = cssutils.css.CSSValue()
        self.assertEqual(v.CSS_INHERIT, v.cssValueType)

    def test_readonly(self):
        "(CSSValue._readonly)"
        v = cssutils.css.CSSValue()
        self.assertEqual(False, v._readonly)

        v = cssutils.css.CSSValue(readonly=True)
        self.assertEqual(True, v._readonly)
        self.assertEqual(u'inherit', v.cssText)
        self.assertRaises(xml.dom.NoModificationAllowedErr, v._setCssText, u'x')
        self.assertEqual(u'inherit', v.cssText)

    def test_repr(self):
        "CSSValue.__repr__()"
        s = cssutils.css.CSSValue()
        self.assert_('CSS_INHERIT' in repr(s))
        #s.value='red'
        #self.assert_('CSS_INHERIT' in repr(s))
        
        
if __name__ == '__main__':
    import unittest
    unittest.main()
