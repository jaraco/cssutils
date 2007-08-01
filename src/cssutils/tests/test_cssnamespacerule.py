"""testcases for cssutils.css.CSSImportRule"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a5, $LastChangedRevision$'


import xml.dom

import test_cssrule

import cssutils


class CSSNamespaceRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSNamespaceRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSNamespaceRule()
        self.rRO = cssutils.css.CSSNamespaceRule(readonly=True)
        self.r_type = cssutils.css.CSSRule.NAMESPACE_RULE


    def test_init(self):
        "CSSNamespaceRule.__init__()"
        super(CSSNamespaceRuleTestCase, self).test_init()

        self.assertEqual(None, self.r.uri)
        self.assertEqual(u'', self.r.prefix)
        self.assertEqual(u'', self.r.cssText)


    def test_InvalidModificationErr(self):
        "CSSNamespaceRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@namespace')
        

    def test_incomplete(self):
        "CSSNamespaceRule (incomplete)"
        tests = {
            u'@namespace "uri': u'@namespace "uri";'
        }
        self.do_equal_p(tests) # parse

    def test_initparameter(self):
        "CSSNamespaceRule.__init__(uri=None, prefix=u'')"
        r = cssutils.css.CSSNamespaceRule(u'uri', u'prefix')
        self.assertEqual(u'uri', r.uri)
        self.assertEqual(u'prefix', r.prefix)
        self.assertEqual(u'@namespace prefix "uri";', r.cssText)

        r = cssutils.css.CSSNamespaceRule(u'uri')
        self.assertEqual(u'uri', r.uri)
        self.assertEqual(u'', r.prefix)
        self.assertEqual(u'@namespace "uri";', r.cssText)


    def test_uri(self):
        "CSSNamespaceRule.uri"
        # set
        self.r.uri = 'x'
        self.assertEqual('x' , self.r.uri)
        self.assertEqual(u'@namespace "x";', self.r.cssText)

        self.r.uri = '"' # weird but legal
        self.assertEqual(u'@namespace "\\"";', self.r.cssText)


    def test_prefix(self):
        "CSSNamespaceRule.prefix"
        r = cssutils.css.CSSNamespaceRule()
        # set
        r.prefix = 'p'
        self.assertEqual('p' , r.prefix)
        self.assertEqual(u'', r.cssText)
        r.uri = 'u'
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
            u'@namespace p;': xml.dom.SyntaxErr, # no uri 
            u'@namespace "u" p;': xml.dom.SyntaxErr, # order
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@namespace p url(x)': xml.dom.SyntaxErr, # missing ;
            u'@namespace p "u"': xml.dom.SyntaxErr, # missing ;
            })
        self.do_raise_r(tests) # set cssText


if __name__ == '__main__':
    import unittest
    unittest.main() 