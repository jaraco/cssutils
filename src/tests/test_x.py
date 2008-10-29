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
        "CSSValue.cssText Syntax"
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
                 '1/**/2': (True, '1 /**/ 2'),
                 '1 /**/2': (True, '1 /**/ 2'),
                 '1/**/ 2': (True, '1 /**/ 2'),
                 '1 /**/ 2': (True, '1 /**/ 2'),
                 '1  /*a*/  /*b*/  2': (True, '1 /*a*/ /*b*/ 2'),
                 # , before
                 '1,/**/2': (True, '1, /**/ 2'),
                 '1 ,/**/2': (True, '1, /**/ 2'),
                 '1, /**/2': (True, '1, /**/ 2'),
                 '1 , /**/2': (True, '1, /**/ 2'),
                 # , after
                 '1/**/,2': (True, '1 /**/, 2'),
                 '1/**/ ,2': (True, '1 /**/, 2'),
                 '1/**/, 2': (True, '1 /**/, 2'),
                 '1/**/ , 2': (True, '1 /**/, 2'),
                 # all
                 '1/*a*/  ,/*b*/  2': (True, '1 /*a*/, /*b*/ 2'),
                 '1  /*a*/,  /*b*/2': (True, '1 /*a*/, /*b*/ 2'),
                 '1  /*a*/  ,  /*b*/  2': (True, '1 /*a*/, /*b*/ 2'),
                 }
        for css, exp in tests.items():
            v.cssText = css
            wellformed, res = exp
            self.assertEqual(wellformed, v.wellformed)
            self.assertEqual(res, v.cssText)

    def test_prioriy(self):
        "Property.priority"
        s = cssutils.parseString('a { color: red }')
        self.assertEqual(u'a {\n    color: red\n    }', s.cssText)
        self.assertEqual(u'', s.cssRules[0].style.getPropertyPriority('color'))

        s = cssutils.parseString('a { color: red !important }')
        self.assertEqual(u'a {\n    color: red !important\n    }', s.cssText)
        self.assertEqual(u'important', s.cssRules[0].style.getPropertyPriority('color'))
        
        # invalid but kept!
        s = cssutils.parseString('a { color: red !x }')
        self.assertEqual(u'a {\n    color: red !x\n    }', s.cssText)
        self.assertEqual(u'x', s.cssRules[0].style.getPropertyPriority('color'))

        p = cssutils.css.Property(u'color', u'red', u'')
        self.assertEqual(p.priority, u'')
        p = cssutils.css.Property(u'color', u'red', u'!important')
        self.assertEqual(p.priority, u'important')
        self.assertRaisesMsg(xml.dom.SyntaxErr, 
                             u'', 
                             cssutils.css.Property, u'color', u'red', u'x')
        cssutils.log.raiseExceptions = False
        p = cssutils.css.Property(u'color', u'red', u'!x')
        self.assertEqual(p.priority, u'x')
        p = cssutils.css.Property(u'color', u'red', u'!x')
        self.assertEqual(p.priority, u'x')
        cssutils.log.raiseExceptions = True
        
        

if __name__ == '__main__':
    import unittest
    unittest.main()
