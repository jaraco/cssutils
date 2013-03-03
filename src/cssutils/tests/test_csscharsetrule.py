"""Testcases for cssutils.css.CSSCharsetRule"""

import re
import xml.dom
import test_cssrule
import cssutils.css

class CSSCharsetRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSCharsetRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSCharsetRule()
        self.rRO = cssutils.css.CSSCharsetRule(readonly=True)
        self.r_type = cssutils.css.CSSCharsetRule.CHARSET_RULE
        self.r_typeString = 'CHARSET_RULE'

    def test_init(self):
        "CSSCharsetRule.__init__()"      
        super(CSSCharsetRuleTestCase, self).test_init()
        self.assertEqual(None, self.r.encoding)
        self.assertEqual(u'', self.r.cssText)
        
        self.assertRaises(xml.dom.InvalidModificationErr, self.r._setCssText, u'xxx')

    def test_InvalidModificationErr(self):
        "CSSCharsetRule InvalidModificationErr"
        self._test_InvalidModificationErr(u'@charset')

    def test_init_encoding(self):
        "CSSCharsetRule.__init__(encoding)"
        for enc in (None, u'UTF-8', u'utf-8', u'iso-8859-1', u'ascii'):
            r = cssutils.css.CSSCharsetRule(enc)
            if enc is None:
                self.assertEqual(None, r.encoding)
                self.assertEqual(u'', r.cssText)
            else:
                self.assertEqual(enc.lower(), r.encoding)
                self.assertEqual(
                    u'@charset "%s";' % enc.lower(), r.cssText)

        for enc in (' ascii ', ' ascii', 'ascii '):
            self.assertRaisesEx(xml.dom.SyntaxErr,
                    cssutils.css.CSSCharsetRule, enc,
                    exc_pattern=re.compile("Syntax Error"))

        for enc in (u'unknown', ):
            self.assertRaisesEx(xml.dom.SyntaxErr,
                    cssutils.css.CSSCharsetRule, enc,
                    exc_pattern=re.compile("Unknown \(Python\) encoding"))

    def test_encoding(self):
        "CSSCharsetRule.encoding"
        for enc in (u'UTF-8', u'utf-8', u'iso-8859-1', u'ascii'):
            self.r.encoding = enc
            self.assertEqual(enc.lower(), self.r.encoding)
            self.assertEqual(
                u'@charset "%s";' % enc.lower(), self.r.cssText)

        for enc in (None,' ascii ', ' ascii', 'ascii '):
            self.assertRaisesEx(xml.dom.SyntaxErr,
                    self.r.__setattr__, 'encoding', enc,
                    exc_pattern=re.compile("Syntax Error"))

        for enc in (u'unknown', ):
            self.assertRaisesEx(xml.dom.SyntaxErr,
                    self.r.__setattr__, 'encoding', enc,
                    exc_pattern=re.compile("Unknown \(Python\) encoding"))

    def test_cssText(self):
        """CSSCharsetRule.cssText

        setting cssText is ok to use @CHARSET or other but a file
        using parse MUST use ``@charset "ENCODING";``
        """
        tests = {
            u'@charset "utf-8";': None,
            u"@charset 'utf-8';": u'@charset "utf-8";',
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests) # also parse

        tests = {
            # token is "@charset " with space!
            u'@charset;"': xml.dom.InvalidModificationErr,
            u'@CHARSET "UTF-8";': xml.dom.InvalidModificationErr,
            u'@charset "";': xml.dom.SyntaxErr,
            u'''@charset /*1*/"utf-8"/*2*/;''': xml.dom.SyntaxErr,
            u'''@charset /*1*/"utf-8";''': xml.dom.SyntaxErr,
            u'''@charset "utf-8"/*2*/;''': xml.dom.SyntaxErr,
            u'@charset { utf-8 }': xml.dom.SyntaxErr,
            u'@charset "utf-8"': xml.dom.SyntaxErr,
            u'@charset a;': xml.dom.SyntaxErr,
            u'@charset /**/;': xml.dom.SyntaxErr,
            # trailing content
            u'@charset "utf-8";s': xml.dom.SyntaxErr,
            u'@charset "utf-8";/**/': xml.dom.SyntaxErr,
            u'@charset "utf-8"; ': xml.dom.SyntaxErr,
            
            # comments do not work in this rule!
            u'@charset "utf-8"/*1*//*2*/;': xml.dom.SyntaxErr
            }
        self.do_raise_r(tests)

    def test_repr(self):
        "CSSCharsetRule.__repr__()"
        self.r.encoding = 'utf-8'
        self.assert_('utf-8' in repr(self.r))

    def test_reprANDstr(self):
        "CSSCharsetRule.__repr__(), .__str__()"
        encoding='utf-8'

        s = cssutils.css.CSSCharsetRule(encoding=encoding)

        self.assert_(encoding in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(encoding == s2.encoding)

if __name__ == '__main__':
    import unittest
    unittest.main()
