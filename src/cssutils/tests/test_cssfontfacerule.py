"""testcases for cssutils.css.CSSFontFaceRule
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-10-18 19:38:15 +0200 (Do, 18 Okt 2007) $'
__version__ = '$LastChangedRevision: 500 $'

import xml.dom
import test_cssrule
import cssutils

class CSSFontFaceRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSFontFaceRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSFontFaceRule()
        self.rRO = cssutils.css.CSSFontFaceRule(readonly=True)
        self.r_type = cssutils.css.CSSFontFaceRule.FONT_FACE_RULE#
        self.r_typeString = 'FONT_FACE_RULE'

    def test_init(self):
        "CSSFontFaceRule.__init__()"
        super(CSSFontFaceRuleTestCase, self).test_init()

        r = cssutils.css.CSSFontFaceRule()
        self.assertEqual(cssutils.css.CSSStyleDeclaration, type(r.style))
        self.assertEqual(r, r.style.parentRule)

        # until any properties
        self.assertEqual(u'', r.cssText)

    def test_InvalidModificationErr(self):
        "CSSFontFaceRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@font-face')
        tests = {
            u'@font-fac {}': xml.dom.InvalidModificationErr,
            }
        self.do_raise_r(tests)

    def test_incomplete(self):
        "CSSFontFaceRule (incomplete)"
        tests = {
            # TODO: with no { this should work too???
            u'@font-face{':
                u'', # no } and no content
            u'@font-face { ':
                u'', # no } and no content
            u'@font-face { color: red':
                u'@font-face {\n    color: red\n    }', # no }
        }
        self.do_equal_p(tests) # parse

    def test_cssText(self):
        "CSSFontFaceRule.cssText"
        tests = {
            u'@font-face {margin:0;}': u'@font-face {\n    margin: 0\n    }',
            u'@font-face{margin:0;}': u'@font-face {\n    margin: 0\n    }',
            u'@f\\ont\\-face{margin:0;}': u'@font-face {\n    margin: 0\n    }',
            u'@font-face/*1*//*2*/{margin:0;}':
                u'@font-face /*1*/ /*2*/ {\n    margin: 0\n    }',
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        tests = {
            u'@font-face;': xml.dom.SyntaxErr,
            u'@font-face }': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@font-face {': xml.dom.SyntaxErr, # no }
            })
        self.do_raise_r(tests) # set cssText

    def test_style(self):
        "CSSFontFaceRule.style"
        d = cssutils.css.CSSStyleDeclaration()
        self.r.style = d
        self.assertEqual(d, self.r.style)
        self.assertEqual(self.r, d.parentRule)

    def test_properties(self):
        "CSSFontFaceRule.style properties"
        r = cssutils.css.CSSFontFaceRule()
        r.style.cssText = '''
        src: url(x)
        '''
        exp = u'''@font-face {
    src: url(x)
    }'''
        self.assertEqual(exp, r.cssText)

    def test_reprANDstr(self):
        "CSSFontFaceRule.__repr__(), .__str__()"
        style='src: url(x)'        
        s = cssutils.css.CSSFontFaceRule(style=style)
        
        self.assert_(style in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(style == s2.style.cssText)


if __name__ == '__main__':
    import unittest
    unittest.main()
