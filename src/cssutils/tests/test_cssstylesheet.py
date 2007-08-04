"""
tests for css.CSSStyleSheet
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2, $LastChangedRevision$'

import xml.dom

import basetest

import cssutils.css


class CSSStyleSheetTestCase(basetest.BaseTestCase):

    def setUp(self):
        super(CSSStyleSheetTestCase, self).setUp()

        self.r = cssutils.css.CSSStyleSheet() # used by basetest
        self.s = self.r # used here

        self.rule = cssutils.css.CSSStyleRule()


    def test_init(self):
        "CSSStyleSheet.__init__()"
        self.assertEqual(False, self.s._readonly)
        self.assertEqual([], self.s.cssRules)
        self.assertEqual('text/css', self.s.type)

        self.assertEqual(False, self.s.disabled)
        self.assertEqual(None, self.s.href)
        self.assertEqual(None, self.s.media)
        self.assertEqual(None, self.s.ownerNode)
        self.assertEqual(None, self.s.parentStyleSheet)
        self.assertEqual(u'', self.s.title)


    def test_NoModificationAllowedErr(self):
        "CSSStyleSheet NoModificationAllowedErr"
        css = cssutils.css.CSSStyleSheet(readonly=True)

        self.assertEqual(True, css._readonly) # internal...

        self.assertRaises(xml.dom.NoModificationAllowedErr,
                          css._setCssText, u'@x;')
        self.assertRaises(xml.dom.NoModificationAllowedErr,
                          css.insertRule, self.rule)
        self.assertRaises(xml.dom.NoModificationAllowedErr,
                          css.insertRule, self.rule, 0)
        self.assertRaises(xml.dom.NoModificationAllowedErr,
                          css.deleteRule, 0)


    def test_cssText_HierarchyRequestErr(self):
        "CSSStyleSheet.cssText HierarchyRequestErr"
        tests = {
            # @charset: only one and always 1st
            u' @charset "utf-8";': xml.dom.HierarchyRequestErr,
            u'@charset "ascii";@charset "ascii";': xml.dom.HierarchyRequestErr,
            u'/*c*/@charset "ascii";': xml.dom.HierarchyRequestErr,
            u'@import "x"; @charset "ascii";': xml.dom.HierarchyRequestErr,
            u'@namespace a "x"; @charset "ascii";': xml.dom.HierarchyRequestErr,
            u'@media all {} @charset "ascii";': xml.dom.HierarchyRequestErr,
            u'@page {} @charset "ascii";': xml.dom.HierarchyRequestErr,
            u'a {} @charset "ascii";': xml.dom.HierarchyRequestErr,

            # @import: before @namespace, @media, @page, sr
            u'@namespace a "x"; @import "x";': xml.dom.HierarchyRequestErr,
            u'@media all {} @import "x";': xml.dom.HierarchyRequestErr,
            u'@page {} @import "x";': xml.dom.HierarchyRequestErr,
            u'a {} @import "x";': xml.dom.HierarchyRequestErr,

            # @namespace: before @media, @page, sr
            u'@media all {} @namespace a "x";': xml.dom.HierarchyRequestErr,
            u'@page {} @namespace a "x";': xml.dom.HierarchyRequestErr,
            u'a {} @namespace a "x";': xml.dom.HierarchyRequestErr,
            }
        self.do_raise_r(tests)
        self.do_raise_p(tests)


    def test_cssText_SyntaxErr(self):
        """CSSStyleSheet.cssText SyntaxErr

        for single {, } or ;
        """
        tests = {
            u'{': xml.dom.SyntaxErr,
            u'}': xml.dom.SyntaxErr,
            u';': xml.dom.SyntaxErr,
            u'@charset "ascii";{': xml.dom.SyntaxErr,
            u'@charset "ascii";}': xml.dom.SyntaxErr,
            u'@charset "ascii";;': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests)
        self.do_raise_p(tests)


    def test_cssText(self):
        "CSSStyleSheet.cssText"
        tests = {
            u'': None,
            # @charset
            u'@charset "ascii";\n@import "x";': None,
            u'@charset "ascii";\n@media all {}': u'@charset "ascii";',
            u'@charset "ascii";\n@x;': None,
            u'@charset "ascii";\na {}': None,
            # @import
            u'@x;\n@import "x";': None,
            u'@import "x";\n@import "y";': None,
            u'@import "x";\n@media all {}': u'@import "x";',
            u'@import "x";\n@x;': None,
            u'@import "x";\na {}': None,
            # @namespace
            u'@x;\n@namespace a "x";': None,
            u'@namespace a "x";\n@namespace b "y";': None,
            u'@import "x";\n@namespace a "x";\n@media all {}': u'@import "x";\n@namespace a "x";',
            u'@namespace a "x";\n@x;': None,
            u'@namespace a "x";\na {}': None,
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        s = cssutils.css.CSSStyleSheet()
        s.cssText = u'''@charset "ascii";@import "x";@namespace a "x";
        @media all {/*1*/}@page {margin: 0}a {}@unknown;/*comment*/'''
        for r in s.cssRules:
            self.assertEqual(s, r.parentStyleSheet)


    def test_deleteRule(self):
        "CSSStyleSheet.deleteRule()"
        self.s.cssText = u'@charset "ascii"; @import "x"; @x; a {}@y;'
        self.assertEqual(5, self.s.cssRules.length)

        self.assertRaises(xml.dom.IndexSizeErr, self.s.deleteRule, 5)

        # end -1
        # check parentStyleSheet
        r = self.s.cssRules[-1]
        self.assertEqual(self.s, r.parentStyleSheet)
        self.s.deleteRule(-1)
        self.assertEqual(None, r.parentStyleSheet)

        self.assertEqual(4, self.s.cssRules.length)
        self.assertEqual(
            u'@charset "ascii";\n@import "x";\n@x;\na {}', self.s.cssText)
        # beginning
        self.s.deleteRule(0)
        self.assertEqual(3, self.s.cssRules.length)
        self.assertEqual(u'@import "x";\n@x;\na {}', self.s.cssText)
        # middle
        self.s.deleteRule(1)
        self.assertEqual(2, self.s.cssRules.length)
        self.assertEqual(u'@import "x";\na {}', self.s.cssText)
        # end
        self.s.deleteRule(1)
        self.assertEqual(1, self.s.cssRules.length)
        self.assertEqual(u'@import "x";', self.s.cssText)


    def _gets(self):
        # complete
        self.cr = cssutils.css.CSSCharsetRule('ascii')
        self.c = cssutils.css.CSSComment(u'/*c*/')
        self.ur = cssutils.css.CSSUnknownRule('@x;')
        self.ir = cssutils.css.CSSImportRule('x')
        self.nr = cssutils.css.CSSNamespaceRule('uri')
        self.mr = cssutils.css.CSSMediaRule()
        self.pr = cssutils.css.CSSPageRule()
        self.pr.style = u'margin: 0;'
        self.sr = cssutils.css.CSSStyleRule('a')
        self.mr.cssText = u'@media all { m {} }'

        s = cssutils.css.CSSStyleSheet()
        s.insertRule(self.cr) # 0
        s.insertRule(self.ir) # 1
        s.insertRule(self.nr) # 2
        s.insertRule(self.mr) # 3
        s.insertRule(self.sr) # 4
        s.insertRule(self.mr) # 5
        s.insertRule(self.pr) # 6
        s.insertRule(self.sr) # 7
        self.assertEqual(u'@charset "ascii";\n@import url(x);\n@namespace "uri";\n@media all {\n    m {}\n    }\na {}\n@media all {\n    m {}\n    }\n@page {\n    margin: 0\n    }\na {}', s.cssText)
        return s, s.cssRules.length


    def test_insertRule(self):
        "CSSStyleSheet.insertRule()"
        s, L = self._gets()

        # INVALID index
        self.assertRaises(xml.dom.IndexSizeErr,
                  s.insertRule, self.sr, -1)
        self.assertRaises(xml.dom.IndexSizeErr,
                  s.insertRule, self.sr, s.cssRules.length + 1)
        #   check if rule is really not in
        self.assertEqual(L, s.cssRules.length)


    def _insertRule(self, rules, notbefore, notafter, anywhere):
        """
        helper
        test if any rule in rules cannot be inserted before rules in before
        or after rules in after but before and after rules in anywhere
        """
        for rule in rules:
            for r in notbefore:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                self.assertRaises(xml.dom.HierarchyRequestErr,
                                  s.insertRule, rule, 0)
            for r in notafter:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                self.assertRaises(xml.dom.HierarchyRequestErr,
                                  s.insertRule, rule, 1)
            for r in anywhere:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                s.insertRule(rule, 0) # before
                s.insertRule(rule) # after
                self.assertEqual(s.cssRules.length, 3)
                self.assertEqual(s, r.parentStyleSheet)

    def test_insertRule_charset(self):
        "CSSStyleSheet.insertRule(@charset)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = (self.cr, self.ir, self.nr, self.mr, self.pr, self.sr,
                    self.c, self.ur)
        anywhere = ()
        self._insertRule((self.cr,),
                         notbefore, notafter, anywhere)

    def test_insertRule_import(self):
        "CSSStyleSheet.insertRule(@import)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = (self.nr, self.pr, self.mr, self.sr)
        anywhere = (self.c, self.ur, self.ir)
        self._insertRule((self.ir,),
                         notbefore, notafter, anywhere)

    def test_insertRule_namespace(self):
        "CSSStyleSheet.insertRule(@namespace)"
        s, L = self._gets()
        notbefore = (self.cr, self.ir)
        notafter = (self.pr, self.mr, self.sr)
        anywhere = (self.c, self.ur, self.nr)
        self._insertRule((self.nr,), notbefore, notafter, anywhere)

    def test_insertRule_media_page_style(self):
        "CSSStyleSheet.insertRule(@media, @page, stylerule)"
        s, L = self._gets()
        notbefore = (self.cr, self.ir, self.nr)
        notafter = ()
        anywhere = (self.c, self.ur, self.mr, self.pr, self.sr)
        self._insertRule((self.pr, self.mr, self.sr),
                         notbefore, notafter, anywhere)

    def test_insertRule_unknownandcomment(self):
        "CSSStyleSheet.insertRule(@ unknown, comment)"
        s, L = self._gets()
        notbefore = (self.cr,)
        notafter = ()
        anywhere = (self.c, self.ur, self.ir, self.nr, self.mr, self.pr,
                    self.sr)
        self._insertRule((self.ur,),
                         notbefore, notafter, anywhere)

    def test_repr(self):
        s = cssutils.css.CSSStyleSheet()
        s.href = 'file:foo.css'
        self.assert_('file:foo.css' in repr(s))


if __name__ == '__main__':
    import unittest
    unittest.main()
