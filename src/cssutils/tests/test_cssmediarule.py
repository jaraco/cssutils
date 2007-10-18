"""
testcases for cssutils.css.CSSMediaRule
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import test_cssrule
import cssutils

class CSSMediaRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSMediaRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSMediaRule()
        self.rRO = cssutils.css.CSSMediaRule(readonly=True)
        self.r_type = cssutils.css.CSSMediaRule.MEDIA_RULE
        self.r_typeString = 'MEDIA_RULE'
        # for tests
        self.stylerule = cssutils.css.CSSStyleRule()
        self.stylerule.cssText = u'a {}'

    def test_init(self):
        "CSSMediaRule.__init__()"
        super(CSSMediaRuleTestCase, self).test_init()

        r = cssutils.css.CSSMediaRule()
        self.assertEqual(cssutils.css.CSSRuleList, type(r.cssRules))
        self.assertEqual([], r.cssRules)

        self.assertEqual(cssutils.stylesheets.MediaList, type(r.media))
        self.assertEqual('all', r.media.mediaText)

        # until any rules
        self.assertEqual(u'', r.cssText)

    def test_InvalidModificationErr(self):
        "CSSMediaRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@media')

    def test_incomplete(self):
        "CSSMediaRule (incomplete)"
        tests = {
            u'@media all { @unknown;': # no }
                u'@media all {\n    @unknown;\n    }',
            u'@media all { a {}': # no }
                u'@media all {\n    a {}\n    }',
        }
        self.do_equal_p(tests) # parse

    def test_cssRules(self):
        "CSSMediaRule.cssRules"
        r = cssutils.css.CSSMediaRule()
        self.assertEqual([], r.cssRules)
        ir = cssutils.css.CSSImportRule()
        r.cssRules.append(ir)
        self.assertEqual([ir], r.cssRules)

    def test_cssText(self):
        "CSSMediaRule.cssText"
        tests = {
            u'''@media all {}''': u'',
            u'''@media all{}''': u'',
            u'''@media/*x*/all{}''': u'',
            # TODO: u'@media all { @x{': u'@media all {\n    @x{}\n    }',
            u'''@media all { a{} }''': u'''@media all {\n    a {}\n    }''',
            u'''@MEDIA all { a{} }''': u'''@media all {\n    a {}\n    }''',
            u'''@\\media all { a{} }''': u'''@media all {\n    a {}\n    }''',
            u'''@media all {@x some;a{color: red;}b{color: green;}}''':
                u'''@media all {
    @x some;
    a {
        color: red
        }
    b {
        color: green
        }
    }''',
            }
        self.do_equal_p(tests)
        self.do_equal_r(tests)

        tests = {
            u'@media;': xml.dom.SyntaxErr,
            u'@media all;': xml.dom.SyntaxErr,
            u'@media all; @x{}': xml.dom.SyntaxErr,
            # no medialist
            u'@media {}': xml.dom.SyntaxErr,
            u'@media/*only comment*/{}': xml.dom.SyntaxErr,

            u'@media all { @charset "x"; a{}}': xml.dom.HierarchyRequestErr,
            u'@media all { @import "x"; a{}}': xml.dom.HierarchyRequestErr,
            u'@media all { @media all {} }': xml.dom.HierarchyRequestErr,
            }
        self.do_raise_p(tests)
        self.do_raise_r(tests)

        tests = {
            # extra stuff
            u'@media all { , }': xml.dom.SyntaxErr,
            u'@media all { x{} } a{}': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests)

        m = cssutils.css.CSSMediaRule()
        m.cssText = u'''@media all {@x; /*1*/a{color: red;}}'''
        for r in m.cssRules:
            self.assertEqual(m, r.parentRule)

    def test_deleteRule(self):
        "CSSMediaRule.deleteRule"
        # see CSSStyleSheet.deleteRule
        m = cssutils.css.CSSMediaRule()
        m.cssText = u'''@media all {
            a {}
            /* x */
            b {}
            c {}
            d {}
        }'''
        self.assertEqual(5, m.cssRules.length)
        self.assertRaises(xml.dom.IndexSizeErr, m.deleteRule, 5)

        # end -1
        # check parentRule
        r = m.cssRules[-1]
        self.assertEqual(m, r.parentRule)
        m.deleteRule(-1)
        self.assertEqual(None, r.parentRule)

        self.assertEqual(4, m.cssRules.length)
        self.assertEqual(
            u'@media all {\n    a {}\n    /* x */\n    b {}\n    c {}\n    }', m.cssText)
        # beginning
        m.deleteRule(0)
        self.assertEqual(3, m.cssRules.length)
        self.assertEqual(u'@media all {\n    /* x */\n    b {}\n    c {}\n    }', m.cssText)
        # middle
        m.deleteRule(1)
        self.assertEqual(2, m.cssRules.length)
        self.assertEqual(u'@media all {\n    /* x */\n    c {}\n    }', m.cssText)
        # end
        m.deleteRule(1)
        self.assertEqual(1, m.cssRules.length)
        self.assertEqual(u'@media all {\n    /* x */\n    }', m.cssText)

    def test_insertRule(self):
        "CSSMediaRule.insertRule"
        # see CSSStyleSheet.insertRule
        r = cssutils.css.CSSMediaRule()
        charsetrule = cssutils.css.CSSCharsetRule('ascii')
        importrule = cssutils.css.CSSImportRule('x')
        namespacerule = cssutils.css.CSSNamespaceRule()
        pagerule = cssutils.css.CSSPageRule()
        mediarule = cssutils.css.CSSMediaRule()
        unknownrule = cssutils.css.CSSUnknownRule('@x;')
        stylerule = cssutils.css.CSSStyleRule('a')
        comment1 = cssutils.css.CSSComment(u'/*1*/')
        comment2 = cssutils.css.CSSComment(u'/*2*/')

        # hierarchy
        self.assertRaises(xml.dom.HierarchyRequestErr,
                          r.insertRule, charsetrule, 0)
        self.assertRaises(xml.dom.HierarchyRequestErr,
                          r.insertRule, importrule, 0)
        self.assertRaises(xml.dom.HierarchyRequestErr,
                          r.insertRule, namespacerule, 0)
        self.assertRaises(xml.dom.HierarchyRequestErr,
                          r.insertRule, pagerule, 0)
        self.assertRaises(xml.dom.HierarchyRequestErr,
                          r.insertRule, mediarule, 0)

        # start insert
        r.insertRule(stylerule, 0)
        self.assertEqual(r, stylerule.parentRule)
        # before
        r.insertRule(comment1, 0)
        self.assertEqual(r, comment1.parentRule)
        # end explicit
        r.insertRule(unknownrule, 2)
        self.assertEqual(r, unknownrule.parentRule)
        # end implicit
        r.insertRule(comment2)
        self.assertEqual(r, comment2.parentRule)
        self.assertEqual(
            '@media all {\n    /*1*/\n    a {}\n    @x;\n    /*2*/\n    }',
            r.cssText)

        # index
        self.assertRaises(xml.dom.IndexSizeErr,
                  r.insertRule, stylerule, -1)
        self.assertRaises(xml.dom.IndexSizeErr,
                  r.insertRule, stylerule, r.cssRules.length + 1)

    def test_media(self):
        "CSSMediaRule.media"
        # see CSSImportRule.media

        # setting not allowed
        self.assertRaises(AttributeError,
                          self.r.__setattr__, 'media', None)
        self.assertRaises(AttributeError,
                          self.r.__setattr__, 'media', 0)

        # set mediaText instead
        self.r.media.mediaText = 'print'
        self.r.insertRule(self.stylerule)
        self.assertEqual(u'@media print {\n    a {}\n    }', self.r.cssText)

    def test_reprANDstr(self):
        "CSSMediaRule.__repr__(), .__str__()"
        mediaText='tv, print'
        
        s = cssutils.css.CSSMediaRule(mediaText=mediaText)
        
        self.assert_(mediaText in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(mediaText == s2.media.mediaText)


if __name__ == '__main__':
    import unittest
    unittest.main()
