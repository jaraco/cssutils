"""testcases for cssutils.css.CSSImportRule"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import test_cssrule
import cssutils

class CSSNamespaceRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSNamespaceRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSNamespaceRule(namespaceURI='x')
        #self.rRO = cssutils.css.CSSNamespaceRule(namespaceURI='x',
        #                                         readonly=True)
        self.r_type = cssutils.css.CSSRule.NAMESPACE_RULE
        self.r_typeString = 'NAMESPACE_RULE'

    def test_init(self):
        "CSSNamespaceRule.__init__()"
        # cannot use here as self.r and self rRO and not useful
        #super(CSSNamespaceRuleTestCase, self).test_init()
        
        tests = [
                 (None, None),
                 ('', ''),
                 (None, u''),
                 (u'', None),
                 (u'', u'no-uri'),
                 ]
        for uri, p in tests:            
            r = cssutils.css.CSSNamespaceRule(namespaceURI=uri, prefix=p)
            self.assertEqual(None, r.namespaceURI)
            self.assertEqual(u'', r.prefix)
            self.assertEqual(u'', r.cssText)
        
        r = cssutils.css.CSSNamespaceRule(namespaceURI='example')
        self.assertEqual('example', r.namespaceURI)
        self.assertEqual(u'', r.prefix)
        self.assertEqual(u'@namespace "example";', r.cssText)

        r = cssutils.css.CSSNamespaceRule(namespaceURI='example', prefix='p')
        self.assertEqual('example', r.namespaceURI)
        self.assertEqual(u'p', r.prefix)
        self.assertEqual(u'@namespace p "example";', r.cssText)

    def test_InvalidModificationErr(self):
        "CSSNamespaceRule.cssText InvalidModificationErr"
        tests = (u'/* comment */',
                 u'@charset "utf-8";',
                 u'@font-face {}',
                 u'@import url(x);',
                 u'@media all {}',
                 u'@page {}',
                 u'@unknown;',
                 u'a style rule {}'
                 # TODO: u''
                 )
        def _do(test):
            r = cssutils.css.CSSNamespaceRule(cssText=test)
        for test in tests:
            self.assertRaises(xml.dom.InvalidModificationErr, _do, test)

    def test_incomplete(self):
        "CSSNamespaceRule (incomplete)"
        tests = {
            u'@namespace "uri': u'@namespace "uri";',
            u"@namespace url(x": u'@namespace "x";',
            u"@namespace url('x": u'@namespace "x";',
            u'@namespace url("x;': u'@namespace "x;";',
            u'@namespace url( "x;': u'@namespace "x;";',
            u'@namespace url("x ': u'@namespace "x ";',
            u'@namespace url(x ': u'@namespace "x";',
        }
        self.do_equal_p(tests) # parse
        tests = {
            u'@namespace "uri': xml.dom.SyntaxErr,
            u"@namespace url(x": xml.dom.SyntaxErr,
            u"@namespace url('x": xml.dom.SyntaxErr,
            u'@namespace url("x;': xml.dom.SyntaxErr,
            u'@namespace url( "x;': xml.dom.SyntaxErr,
            u'@namespace url("x ': xml.dom.SyntaxErr,
            u'@namespace url(x ': xml.dom.SyntaxErr           
            }
        self.do_raise_r(tests) # set cssText

    def test_namespaceURI(self):
        "CSSNamespaceRule.namespaceURI"
        # set only initially
        r = cssutils.css.CSSNamespaceRule(namespaceURI='x')
        self.assertEqual('x' , r.namespaceURI)
        self.assertEqual(u'@namespace "x";', r.cssText)

        r = cssutils.css.CSSNamespaceRule(namespaceURI='"')
        self.assertEqual(u'@namespace "\\"";', r.cssText)
        
        self.assertRaises(xml.dom.NoModificationAllowedErr, 
                          r._setNamespaceURI, 'x')

        self.assertRaises(xml.dom.NoModificationAllowedErr, 
                          r._setCssText, '@namespace "u";')

    def test_prefix(self):
        "CSSNamespaceRule.prefix"
        r = cssutils.css.CSSNamespaceRule(namespaceURI='u')
        r.prefix = 'p'
        self.assertEqual('p' , r.prefix)
        self.assertEqual(u'@namespace p "u";', r.cssText)

        r = cssutils.css.CSSNamespaceRule(cssText='@namespace x "u";')
        r.prefix = 'p'
        self.assertEqual('p' , r.prefix)
        self.assertEqual(u'@namespace p "u";', r.cssText)

        valid = (None, u'')
        for prefix in valid:
            r.prefix = prefix
            self.assertEqual(r.prefix, u'')
            self.assertEqual(u'@namespace "u";', r.cssText)
            
        valid = ('a', '_x', 'a1', 'a-1')
        for prefix in valid:
            r.prefix = prefix
            self.assertEqual(r.prefix, prefix)
            self.assertEqual(u'@namespace %s "u";' % prefix, r.cssText)
                    
        invalid = ('1', ' x', ' ', ',')
        for prefix in invalid:
            self.assertRaises(xml.dom.SyntaxErr, r._setPrefix, prefix)

    def test_cssText(self):
        "CSSNamespaceRule.cssText"
        tests = {
            u'@namespace p "u";': None,
            u"@namespace p 'u';": u'@namespace p "u";',

            u'@\\namespace p "u";': u'@namespace p "u";',
            u'@NAMESPACE p "u";': u'@namespace p "u";',

            u'@namespace  p  "u"  ;': u'@namespace p "u";',
            u'@namespace p"u";': u'@namespace p "u";',
            u'@namespace p "u";': u'@namespace p "u";',

            u'@namespace/*1*/p/*2*/"u"/*3*/;': u'@namespace/*1*/ p/*2*/ "u"/*3*/;',

            # deprecated
            u'@namespace p url(u);': u'@namespace p "u";',
            u'@namespace p url(\'u\');': u'@namespace p "u";',
            u'@namespace p url(\"u\");': u'@namespace p "u";',
            u'@namespace p url( \"u\" );': u'@namespace p "u";',
            }
        self.do_equal_p(tests)
        #self.do_equal_r(tests) # cannot use here as always new r is needed
        for test, expected in tests.items():
            r = cssutils.css.CSSNamespaceRule(cssText=test)
            if expected is None:
                expected = test
            self.assertEqual(expected, r.cssText)

        tests = {
            u'@namespace;': xml.dom.SyntaxErr, # nothing
            u'@namespace p;': xml.dom.SyntaxErr, # no namespaceURI
            u'@namespace "u" p;': xml.dom.SyntaxErr, # order
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@namespace p url(x)': xml.dom.SyntaxErr, # missing ;
            u'@namespace p "u"': xml.dom.SyntaxErr, # missing ;
            })
        #self.do_raise_r(tests) # cannot use here as always new r is needed
        def _do(test):
            r = cssutils.css.CSSNamespaceRule(cssText=test)
        for test, expected in tests.items():
            self.assertRaises(expected, _do, test)

    def test_reprANDstr(self):
        "CSSNamespaceRule.__repr__(), .__str__()"
        namespaceURI=u'http://example.com'
        prefix=u'prefix'

        s = cssutils.css.CSSNamespaceRule(namespaceURI=namespaceURI, prefix=prefix)

        self.assert_(namespaceURI in str(s))
        self.assert_(prefix in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(namespaceURI == s2.namespaceURI)
        self.assert_(prefix == s2.prefix)


if __name__ == '__main__':
    import unittest
    unittest.main()
