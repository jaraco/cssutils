___author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.55_5, SVN revision $LastChangedRevision$'

import unittest
import xml.dom

import cssutils.cssvalue_other as cvo


class RGBColorTestCase(unittest.TestCase):

    def test_init(self):
        v = cvo.RGBColor(0, 10, 255)
        self.assertEqual(u'rgb(0, 10, 255)', v.cssText)

        v = cvo.RGBColor(0.0, 49.5, 100.8)
        self.assertEqual(u'rgb(0.0%, 49.5%, 100.8%)', v.cssText)

        v = cvo.RGBColor(u' 0   ', u' 10  ', u' 255   ')
        self.assertEqual(u'rgb(0, 10, 255)', v.cssText)

        v = cvo.RGBColor(u'  0.0  %  ', u'49.5%', u' 100.8   %  ')
        self.assertEqual(u'rgb(0.0%, 49.5%, 100.8%)', v.cssText)
    
        v = cvo.RGBColor(u'  0.0  ', 1, u' 100.8   %  ')
        self.assertEqual(u'rgb(0.0%, 1, 100.8%)', v.cssText)

        v = cvo.RGBColor(-2000, -1.23, u' 100.8   %  ')
        self.assertEqual(u'rgb(-2000, -1.23%, 100.8%)', v.cssText)

        self.assertRaises(xml.dom.SyntaxErr, v.__init__, u'1', u'red', u'red')


class RectTestCase(unittest.TestCase):

    def test_init(self):
        v = cvo.Rect()


class CounterTestCase(unittest.TestCase):   

    def test_init(self):
        v = cvo.Counter()
        

if __name__ == '__main__':
    unittest.main() 