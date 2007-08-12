"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""
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
        self.assert_(u'' == v.cssText)
        self.assert_(None is  v.cssValueType)
        self.assert_(None == v.cssValueTypeString)

    def test_cssText(self):
        "CSSValue.cssText"
        v = cssutils.css.CSSValue()
        v.cssText = u'1px'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        self.assert_(u'1px' == v.cssText)
        self.assert_(False is v.valid)

        v = cssutils.css.CSSValue(_propertyname="left")
        v.cssText = u'1px'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        self.assert_(u'1px' == v.cssText)
        self.assert_(True is v.valid)
        
        v.cssText = u'  1   px    '
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assert_('1 px' == v._value)
        self.assert_('1 px' == v.cssText)
        self.assert_(False is v.valid)

        v = cssutils.css.CSSValue(_propertyname="left")
        v.cssText = u'  1   px    '
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assert_(u'1 px' == v.cssText)
        self.assert_(False is v.valid)


        v.cssText = u'expression(document.body.clientWidth > 972 ? "1014px": "100%" )'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_UNKNOWN == v.primitiveType)
        self.assert_('expression(document.body.clientWidth > 972 ? "1014px": "100%" )' == v._value)
        self.assert_('expression(document.body.clientWidth > 972 ? "1014px": "100%" )' == v.cssText)
        self.assert_(False is v.valid)

    def test_valid(self):
        "CSSValue.valid"
        # context property must be set
        tests = [
            ('color', '1', False),
            ('color', 'red', True),
            ('left', '1', False),
            ('left', '1px', True)
            ]
        for n, v, exp in tests:
            v = cssutils.css.CSSValue(cssText=v, _propertyname=n)
            self.assert_(v.valid is exp)
        
    def test_cssValueType(self):
        "CSSValue.cssValueType .cssValueTypeString"
        tests = [
            ([u'inherit'], 'CSS_INHERIT'),     
            (['1', '1%', '1em', '1ex', '1px', '1cm', '1mm', '1in', '1pt', '1pc',
              '1deg', '1rad', '1grad', '1ms', '1s', '1hz', '1khz', '1other',
               '"string"', "'str ing'", 'url(x)', 'red', 
               'attr(a)', 'counter()', 'rect(1px,2px,3px,4px)', 
               'rgb(0,0,0)', '#000', '#000000', 'rgba(0,0,0,0)'], 
             'CSS_PRIMITIVE_VALUE'),
            ([u'1px 1px', 'red blue green x'], 'CSS_VALUE_LIST')     
            #([], 'CSS_CUSTOM') # what is a custom value?
            ]
        for values, name in tests:
            for value in values:
                v = cssutils.css.CSSValue(cssText=value)
                self.assert_(value == v.cssText)
                self.assert_(name == v.cssValueTypeString)
                self.assert_(getattr(v, name) == v.cssValueType)

    def test_readonly(self):
        "(CSSValue._readonly)"
        v = cssutils.css.CSSValue(cssText='inherit')
        self.assert_(False is v._readonly)

        v = cssutils.css.CSSValue(cssText='inherit', readonly=True)
        self.assert_(True is v._readonly)
        self.assert_(u'inherit', v.cssText)
        self.assertRaises(xml.dom.NoModificationAllowedErr, v._setCssText, u'x')
        self.assert_(u'inherit', v.cssText)

    def test_repr(self):
        "CSSValue.__repr__()"
        v = cssutils.css.CSSValue(cssText='inherit')
        self.assert_('CSS_INHERIT' in repr(v))
        # no CSSValue but CSSPrimitiveValue now!
        v.cssText='red'
        self.assert_('primitiveType' in repr(v)) 


class CSSPrimitiveValueTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSPrimitiveValue.__init__()"
        v = cssutils.css.CSSPrimitiveValue(u'1')
        self.assert_(u'1' == v.cssText)
        self.assert_(v.valid == False)

        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_("CSS_PRIMITIVE_VALUE" == v.cssValueTypeString)

        self.assert_(v.CSS_NUMBER == v.primitiveType)
        self.assert_("CSS_NUMBER" == v.primitiveTypeString)

        # DUMMY to be able to test empty constructor call
        #self.assertRaises(xml.dom.SyntaxErr, v.__init__, None)

        #self.assertRaises(xml.dom.InvalidAccessErr, v.getCounterValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRGBColorValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRectValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getStringValue)

    def test_CSS_UNKNOWN(self):
        "CSSPrimitiveValue.CSS_UNKNOWN"
        v = cssutils.css.CSSPrimitiveValue(u'expression(false)')
        self.assert_(v.valid == False)
        self.assert_(v.CSS_UNKNOWN == v.primitiveType)
        self.assert_('CSS_UNKNOWN' == v.primitiveTypeString)

    def test_CSS_NUMBER_AND_OTHER_DIMENSIONS(self):
        "CSSPrimitiveValue.CSS_NUMBER .. CSS_DIMENSION"
        defs = [
            ('', 'CSS_NUMBER'),
            ('%', 'CSS_PERCENTAGE'),
            ('em', 'CSS_EMS'),
            ('ex', 'CSS_EXS'),
            ('px', 'CSS_PX'),
            ('cm', 'CSS_CM'),
            ('mm', 'CSS_MM'),
            ('in', 'CSS_IN'),
            ('pt', 'CSS_PT'),
            ('pc', 'CSS_PC'),
            ('deg', 'CSS_DEG'),
            ('rad', 'CSS_RAD'),
            ('grad', 'CSS_GRAD'),
            ('ms', 'CSS_MS'),
            ('s', 'CSS_S'),
            ('hz', 'CSS_HZ'),
            ('khz', 'CSS_KHZ'),
            ('other_dimension', 'CSS_DIMENSION')]
        for dim, name in defs:
            for n in (0, -1, 1, 1.1, -1.1):
                v = cssutils.css.CSSPrimitiveValue('%i%s' % (n, dim))
                self.assert_(getattr(v, name) == v.primitiveType)
                self.assert_(name == v.primitiveTypeString)

    def test_CSS_STRING_AND_OTHER(self):
        "CSSPrimitiveValue.CSS_STRING .. CSS_RGBCOLOR"
        defs = [
            (('""', "''", '"some thing"', "' A\\ND '"), 'CSS_STRING'),
            (('url(a)', 'url("a b")', "url(' ')"), 'CSS_URI'), 
            (('some', 'or_anth-er'), 'CSS_IDENT'), 
            (('attr(a)', 'attr(b)'), 'CSS_ATTR'), 
            (('counter(1)', 'counter(2)'), 'CSS_COUNTER'), 
            (('rect(1,2,3,4)',), 'CSS_RECT'), 
            (('rgb(1,2,3)', 'rgb(10%, 20%, 30%)', '#123', '#123456'), 
                 'CSS_RGBCOLOR'), 
            (('rgba(1,2,3,4)','rgba(10%, 20%, 30%, 40%)', ), 
                 'CSS_RGBACOLOR')
            ]
        for examples, name in defs: 
            for x in examples:
                v = cssutils.css.CSSPrimitiveValue(x)
                self.assert_(getattr(v, name) == v.primitiveType)
                self.assert_(name == v.primitiveTypeString)

#    def test_getFloat(self):
#        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
#        self.assertRaises(xml.dom.InvalidAccessErr, v.getFloatValue,
#            v.CSS_UNKNOWN)
#
#    def test_setFloat(self):
#        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
#        v.setFloatValue(v.CSS_MM, '8')
#        # TODO: more tests
#
#    def test_setString(self):
#        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
#        v.setStringValue(v.CSS_STRING, 'brown')
#        # TODO: more tests
#
#    def test_typeRGBColor(self):
#        v = cssutils.cssprimitivevalue.PrimitiveValue('RGB(1, 5, 10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1, 5, 10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, 5%, 10%)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1.0%, 5.0%, 10.0%)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('  rgb(  1 ,5,  10  )')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb (1,5,10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, .5%, 10.1%)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)

    def test_repr(self):
        "CSSPrimitiveValue.__repr__()"
        v = cssutils.css.CSSPrimitiveValue('111')
        self.assert_('111' in repr(v))
        self.assert_('CSS_NUMBER' in repr(v))

        
if __name__ == '__main__':
    import unittest
    unittest.main()
