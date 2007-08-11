__author__ = '$LastChangedBy: doerwalter $'
__date__ = '$LastChangedDate: 2007-08-02 22:58:23 +0200 (Do, 02 Aug 2007) $'
__version__ = '$LastChangedRevision: 160 $'

import xml.dom
import basetest
import cssutils.css

class CSSPrimitiveValueTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSPrimitiveValue.__init__()"
        v = cssutils.css.CSSPrimitiveValue(u'1')
        self.assert_(u'1' == v.cssText)
        self.assert_(v.valid == True)

        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_("CSS_PRIMITIVE_VALUE" == v.cssValueTypeString)

        self.assert_(v.CSS_NUMBER == v.primitiveType)
        self.assert_("CSS_NUMBER" == v.primitiveTypeString)

        # DUMMY to be able to test empty constructor call
        self.assertRaises(xml.dom.SyntaxErr, v.__init__, None)

        #self.assertRaises(xml.dom.InvalidAccessErr, v.getCounterValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRGBColorValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRectValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getStringValue)

    def test_CSS_UNKNOWN(self):
        "CSSPrimitiveValue.CSS_UNKNOWN"
        v = cssutils.css.CSSPrimitiveValue(u'#1')
        self.assert_(v.valid == True)
        self.assert_(v.CSS_RGBCOLOR == v.primitiveType)

        # only CSS_UNKNOWN if invalid for now
        v.valid = False
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
            (('rgb(1,2,3,4)', '#123', '#123456'), 'CSS_RGBCOLOR'), 
            (('rgba(1,2,3)',), 'CSS_RGBACOLOR')]
        for examples, name in defs: 
            for x in examples:
                v = cssutils.css.CSSPrimitiveValue(x)
                self.assert_(getattr(v, name) == v.primitiveType)
                self.assert_(name == v.primitiveTypeString)


    def test_repr(self):
        "CSSPrimitiveValue.__repr__()"
        v = cssutils.css.CSSPrimitiveValue('111')
        self.assert_('111' in repr(v))
        self.assert_('CSS_NUMBER' in repr(v))


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



if __name__ == '__main__':
    import unittest
    unittest.main()
