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
        self.r = cssutils.css.CSSNamespaceRule()
        self.rRO = cssutils.css.CSSNamespaceRule(readonly=True)
        self.r_type = cssutils.css.CSSRule.NAMESPACE_RULE
        self.r_typeString = 'NAMESPACE_RULE'

    def test_init(self):
        "CSSNamespaceRule.__init__()"
        super(CSSNamespaceRuleTestCase, self).test_init()

        self.assertEqual(None, self.r.namespaceURI)
        self.assertEqual(u'', self.r.prefix)
        self.assertEqual(u'', self.r.cssText)

    def test_InvalidModificationErr(self):
        "CSSNamespaceRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@namespace')

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

    def test_initparameter(self):
        "CSSNamespaceRule.__init__(namespaceURI=None, prefix=u'')"
        r = cssutils.css.CSSNamespaceRule(u'uri', u'prefix')
        self.assertEqual(u'uri', r.namespaceURI)
        self.assertEqual(u'prefix', r.prefix)
        self.assertEqual(u'@namespace prefix "uri";', r.cssText)

        r = cssutils.css.CSSNamespaceRule(u'uri')
        self.assertEqual(u'uri', r.namespaceURI)
        self.assertEqual(u'', r.prefix)
        self.assertEqual(u'@namespace "uri";', r.cssText)

    def test_namespaceURI(self):
        "CSSNamespaceRule.namespaceURI"
        # set
        self.r.namespaceURI = 'x'
        self.assertEqual('x' , self.r.namespaceURI)
        self.assertEqual(u'@namespace "x";', self.r.cssText)
        # deprecated:
        self.assertEqual('x' , self.r.uri)

        self.r.namespaceURI = '"' # weird but legal
        self.assertEqual(u'@namespace "\\"";', self.r.cssText)

    def test_prefix(self):
        "CSSNamespaceRule.prefix"
        r = cssutils.css.CSSNamespaceRule()
        # set
        r.prefix = 'p'
        self.assertEqual('p' , r.prefix)
        self.assertEqual(u'', r.cssText)
        r.namespaceURI = 'u'
        self.assertEqual('p' , r.prefix)
        self.assertEqual(u'@namespace p "u";', r.cssText)

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
        self.do_equal_r(tests)

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
        self.do_raise_r(tests) # set cssText

    def test_reprANDstr(self):
        "CSSNamespaceRule.__repr__(), .__str__()"
        namespaceURI=u'http://example.com'
        prefix=u'ex'

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
