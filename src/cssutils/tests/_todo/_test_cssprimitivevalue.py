__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.55_5, SVN revision $LastChangedRevision$'

import unittest
import xml.dom

import cssutils.cssprimitivevalue


class CSSPrimitiveValueTestCase(unittest.TestCase):

    def test_init(self):
        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
        self.assertEqual(u'1', v.cssText)
        self.assertEqual(v.CSS_PRIMITIVE_VALUE, v.cssValueType)

        # DUMMY to be able to test empty constructor call
        self.assertRaises(xml.dom.SyntaxErr, v.__init__, None)

        self.assertRaises(xml.dom.InvalidAccessErr, v.getCounterValue)
        self.assertRaises(xml.dom.InvalidAccessErr, v.getRGBColorValue)
        self.assertRaises(xml.dom.InvalidAccessErr, v.getRectValue)
        self.assertRaises(xml.dom.InvalidAccessErr, v.getStringValue)

    def test_readonly(self):
        pass 
        
    def test_cssText(self):
        pass
        
    def test_primitiveValue(self):
        pass

    def test_getFloat(self):
        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
        self.assertRaises(xml.dom.InvalidAccessErr, v.getFloatValue, 
            v.CSS_UNKNOWN)

    def test_setFloat(self):
        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
        v.setFloatValue(v.CSS_MM, '8')
        # TODO: more tests
        
    def test_setString(self):
        v = cssutils.cssprimitivevalue.PrimitiveValue(u'1')
        v.setStringValue(v.CSS_STRING, 'brown')
        # TODO: more tests

    def test_typeRGBColor(self):
        v = cssutils.cssprimitivevalue.PrimitiveValue('RGB(1, 5, 10)')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)

        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1, 5, 10)')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)

        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, 5%, 10%)')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
        self.assertEqual(u'rgb(1.0%, 5.0%, 10.0%)', v.cssText)
    
        v = cssutils.cssprimitivevalue.PrimitiveValue('  rgb(  1 ,5,  10  )')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb (1,5,10)')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, .5%, 10.1%)')
        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)


        
if __name__ == '__main__':
    unittest.main() 