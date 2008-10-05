"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""
__version__ = '$Id: test_cssvalue.py 1473 2008-09-15 21:15:54Z cthedot $'

# from decimal import Decimal # maybe for later tests?
import xml.dom
import basetest
import cssutils
import types

class XTestCase(basetest.BaseTestCase):

    def setUp(self):
        pass

    def test_x(self):
        v = cssutils.css.CSSValue()
        
        tests = {
                 '1': (True, '1'),
                 '1 2': (True, '1 2'),
                 '1   2': (True, '1 2'),
                 '1,2': (True, '1, 2'),
                 '1,  2': (True, '1, 2'),
                 '1  ,2': (True, '1, 2'),
                 '1  ,  2': (True, '1, 2'),
                 '1/2': (True, '1/2'),
                 '1/  2': (True, '1/2'),
                 '1  /2': (True, '1/2'),
                 '1  /  2': (True, '1/2'),
                 # comment
                 '1/**/2': (True, '1/**/2'),
                 '1 /**/2': (True, '1/**/ 2'),
                 '1/**/ 2': (True, '1/**/ 2'),
                 '1 /**/ 2': (True, '1/**/ 2'),
                 '1  /*a*/  /*b*/  2': (True, '1/*a*//*b*/ 2'),
                 # , before
                 '1,/**/2': (True, '1/**/, 2'),
                 '1 ,/**/2': (True, '1/**/, 2'),
                 '1, /**/2': (True, '1/**/, 2'),
                 '1 , /**/2': (True, '1/**/, 2'),
                 # , after
                 '1/**/,2': (True, '1/**/, 2'),
                 '1/**/ ,2': (True, '1/**/, 2'),
                 '1/**/, 2': (True, '1/**/, 2'),
                 '1/**/ , 2': (True, '1/**/, 2'),
                 # all
                 '1/*a*/  ,/*b*/  2': (True, '1/*a*//*b*/, 2'),
                 '1  /*a*/,  /*b*/2': (True, '1/*a*//*b*/, 2'),
                 '1  /*a*/  ,  /*b*/  2': (True, '1/*a*//*b*/, 2'),
                 }
        for css, exp in tests.items():
            v.cssText = css
            wellformed, res = exp
            self.assertEqual(wellformed, v.wellformed)
            self.assertEqual(res, v.cssText)


if __name__ == '__main__':
    import unittest
    unittest.main()
