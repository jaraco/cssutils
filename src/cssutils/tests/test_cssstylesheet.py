# -*- coding: utf-8 -*-
"""
tests for css.CSSStyleSheet
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

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
        self.assertEqual('text/css', self.s.type)
        self.assertEqual(False, self.s._readonly)
        self.assertEqual([], self.s.cssRules)
        self.assertEqual(False, self.s.disabled)
        self.assertEqual(None, self.s.href)
        self.assertEqual(None, self.s.media)
        self.assertEqual(None, self.s.ownerNode)
        self.assertEqual(None, self.s.parentStyleSheet)
        self.assertEqual(u'', self.s.title)

    def test_encoding(self):
        "CSSStyleSheet.encoding"
        self.s.cssText=''
        self.assertEqual('utf-8', self.s.encoding)
        
        self.s.encoding = 'ascii'
        self.assertEqual('ascii', self.s.encoding)
        self.assertEqual(1, self.s.cssRules.length)
        self.assertEqual('ascii', self.s.cssRules[0].encoding)

        self.s.encoding = None
        self.assertEqual('utf-8', self.s.encoding)
        self.assertEqual(0, self.s.cssRules.length)

        self.s.encoding = 'UTF-8'
        self.assertEqual('utf-8', self.s.encoding)
        self.assertEqual(1, self.s.cssRules.length)

        self.assertRaises(xml.dom.SyntaxErr, self.s._setEncoding, 
                          'INVALID ENCODING')
        self.assertEqual('utf-8', self.s.encoding)
        self.assertEqual(1, self.s.cssRules.length)
    
    def test_namespaces(self):
        "CSSStyleSheet.namespaces"
        s = cssutils.css.CSSStyleSheet()
        self.assertEqual(0, len(s.namespaces))
        css = u'@namespace "default";\n@namespace ex "example";'
        s.cssText = css
        self.assertEqual(s.cssText, css)
        self.assertEqual({ u'': u'default', u'ex': u'example'}, 
                         s.namespaces._namespaces)
        s.insertRule('@namespace n "new";')
        self.assertEqual({ u'': u'default', u'n': 'new', u'ex': u'example'}, 
                         s.namespaces._namespaces)
        css = '''@namespace "default";\n@namespace ex "example";
@namespace n "new";'''
        self.assertEqual(s.cssText, css)
        
        def _do():
            s.namespaces['ex'] = 'OTHER'
        self.assertEqual(set([u'', u'ex', u'n']), 
                         set(s.namespaces.keys()))
        def do(self):
            s.namespaces['n'] = 'OTHER'
        self.assertRaises(xml.dom.NoModificationAllowedErr, _do)

        self.assertEqual(s.cssText, css)

        
        s.cssText = '@namespace p "u"; p|x {a:1}'

        # len, __iter__ and keys
        self.assert_(1, len(s.namespaces))
        self.assert_(['p'], s.namespaces.keys())
        keys = [k for k in s.namespaces] 
        self.assert_(['p'], keys)

        # getitem
        self.assert_('u', s.namespaces['p'])
        self.assertRaises(KeyError, s.namespaces.__getitem__, 'x')

        # prefix in namespaces 
        self.assertTrue('p' in s.namespaces)
        self.assertFalse('no' in s.namespaces)
        
        # del namespaces[prefix]
        self.assertRaises(IndexError, 
                          s.namespaces.__delitem__, 'x')
        self.assertRaises(xml.dom.NamespaceErr, 
                          s.namespaces.__delitem__, 'p')
        s.cssRules[1].selectorText = 'x'
        del s.namespaces['p']
        self.assertEqual(s.cssText, 'x {\n    a: 1\n    }')
        


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
            u'@charset "ascii";@charset "ascii";': xml.dom.HierarchyRequestErr,            u'/*c*/@charset "ascii";': xml.dom.HierarchyRequestErr,
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

    def test_incomplete(self):
        "CSSStyleRule (incomplete)"
        tests = {
            u'@import "a': u'@import "a";', # no }
            u'a { x: 1': u'a {\n    x: 1\n    }', # no }
            u'a { font-family: "arial sans': # no "
                u'a {\n    font-family: "arial sans"\n    }',
        }
        self.do_equal_p(tests) # parse

    def test_cssText(self):
        "CSSStyleSheet.cssText"
        tests = {
            u'': None,
            # @charset
            u'@charset "ascii";\n@import "x";': None,
            u'@charset "ascii";\n@media all {}': u'@charset "ascii";',
            u'@charset "ascii";\n@x;': None,
            u'@charset "ascii";\na {\n    x: 1\n    }': None,
            # @import
            u'@x;\n@import "x";': None,
            u'@import "x";\n@import "y";': None,
            u'@import "x";\n@media all {}': u'@import "x";',
            u'@import "x";\n@x;': None,
            u'@import "x";\na {\n    x: 1\n    }': None,
            # @namespace
            u'@x;\n@namespace a "x";': None,
#            u'@namespace a "x";\n@namespace b "y";': None,
#            u'@import "x";\n@namespace a "x";\n@media all {}': u'@import "x";\n@namespace a "x";',
#            u'@namespace a "x";\n@x;': None,
#            u'@namespace a "x";\na {\n    x: 1\n    }': None,
#            ur'\1 { \2: \3 }': ur'''\1 {
#    \2: \3
#    }''',
#            ur'''
#            \@ { \@: \@ }
#            \1 { \2: \3 }
#            \{{\::\;;}
#            ''': ur'''\@ {
#    \@: \@
#    }
#\1 {
#    \2: \3
#    }
#\{
#    {\:: \;
#    }'''
            }
        self.do_equal_r(tests)
        self.do_equal_p(tests)

        s = cssutils.css.CSSStyleSheet()
        s.cssText = u'''@charset "ascii";@import "x";@namespace a "x";
        @media all {/*1*/}@page {margin: 0}a {\n    x: 1\n    }@unknown;/*comment*/'''
        for r in s.cssRules:
            self.assertEqual(s, r.parentStyleSheet)

    def test_HTMLComments(self):
        "CSSStyleSheet CDO CDC"
        css = u'''body { color: red }
<!-- comment -->
body { color: blue }
body { color: pink }
<!-- comment -->
body { color: green }
'''
        exp = u'''body {
    color: red
    }
body {
    color: pink
    }'''
        sheet = cssutils.parseString(css)
        self.assertEqual(sheet.cssText, exp)

    def test_deleteRule(self):
        "CSSStyleSheet.deleteRule()"
        self.s.cssText = u'@charset "ascii"; @import "x"; @x; a {\n    x: 1\n    }@y;'
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
            u'@charset "ascii";\n@import "x";\n@x;\na {\n    x: 1\n    }', self.s.cssText)
        # beginning
        self.s.deleteRule(0)
        self.assertEqual(3, self.s.cssRules.length)
        self.assertEqual(u'@import "x";\n@x;\na {\n    x: 1\n    }', self.s.cssText)
        # middle
        self.s.deleteRule(1)
        self.assertEqual(2, self.s.cssRules.length)
        self.assertEqual(u'@import "x";\na {\n    x: 1\n    }', self.s.cssText)
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
        self.mr.cssText = u'@media all { @m; }'
        self.pr = cssutils.css.CSSPageRule()
        self.pr.style = u'margin: 0;'
        self.sr = cssutils.css.CSSStyleRule()
        self.sr.cssText = 'a {\n    x: 1\n    }'

        s = cssutils.css.CSSStyleSheet()
        s.insertRule(self.cr) # 0
        s.insertRule(self.ir) # 1
        s.insertRule(self.nr) # 2
        s.insertRule(self.mr) # 3
        s.insertRule(self.sr) # 4
        s.insertRule(self.mr) # 5
        s.insertRule(self.pr) # 6
        s.insertRule(self.sr) # 7
        self.assertEqual(u'@charset "ascii";\n@import url(x);\n@namespace "uri";\n@media all {\n    @m;\n    }\na {\n    x: 1\n    }\n@media all {\n    @m;\n    }\n@page {\n    margin: 0\n    }\na {\n    x: 1\n    }', s.cssText)
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
        
        # insert string
        s.insertRule('a {}')
        self.assertEqual(L+1, s.cssRules.length)
        # insert rule
        s.insertRule(self.sr)
        self.assertEqual(L+2, s.cssRules.length)
        # insert rulelist
        s2, L2 = self._gets()
        rulelist = s2.cssRules
        del rulelist[:-2]
        s.insertRule(rulelist)
        self.assertEqual(L+2 + 2, s.cssRules.length)

    def test_add(self):
        "CSSStyleSheet.add()"
        full = cssutils.css.CSSStyleSheet()
        sheet = cssutils.css.CSSStyleSheet()
        css = ['@charset "ascii";',
               '@import "x";',
               '@namespace p "u";',
               '@page {\n    left: 0\n    }',
               '@font-face {\n    color: red\n    }',
               '@media all {\n    a {\n        color: red\n        }\n    }',
               'a {\n    color: green\n    }',
               '/*comment*/',
               '@x;'
               ]
        fullcss = u'\n'.join(css)
        full.cssText = fullcss
        self.assertEqual(full.cssText, fullcss)
        for i, line in enumerate(css):
            # sheet with no same rule
            before = css[:i]
            after = css[i+1:]
            sheet.cssText = u''.join(before + after)
            index = sheet.add(line)
            if i < 3:
                self.assertEqual(fullcss, sheet.cssText)
                self.assertEqual(i, index) # no same rule present
            else: 
                expected = before
                expected.extend(after)
                expected.append(line)
                self.assertEqual(u'\n'.join(expected), sheet.cssText)
                self.assertEqual(8, index) # no same rule present

            # sheet with one same rule
            if i == 1: line = '@import "x2";'
            if i == 2: line = '@namespace p2 "u2";'
            full.cssText = fullcss
            index = full.add(line)
            if i < 1:
                self.assertEqual(fullcss, sheet.cssText)
                self.assertEqual(i, index) # no same rule present
            else: 
                expected = css[:i+1] # including same rule
                expected.append(line)
                expected.extend(css[i+1:])
                self.assertEqual(u'\n'.join(expected), full.cssText)
                self.assertEqual(i+1, index) # no same rule present

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
                s = cssutils.css.CSSStyleSheet()
                s.add(r)
                self.assertRaises(xml.dom.HierarchyRequestErr,
                                  s.insertRule, rule, 0)
            for r in notafter:
                s = cssutils.css.CSSStyleSheet()
                s.insertRule(r)
                self.assertRaises(xml.dom.HierarchyRequestErr,
                                  s.insertRule, rule, 1)
                s = cssutils.css.CSSStyleSheet()
                s.add(r)
                s.add(rule) # never raises

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

    def test_replaceUrls(self):
        "CSSStyleSheet.replaceUrls()"
        cssutils.ser.prefs.keepAllProperties = True

        css='''
        @import "im1";
        @import url(im2);
        a { 
            background-image: url(c) !important;
            background-\image: url(b);
            background: url(a) no-repeat !important;    
            }'''
        s = cssutils.parseString(css)
        s.replaceUrls(lambda old: "NEW" + old)
        self.assertEqual(u'@import "NEWim1";', s.cssRules[0].cssText)
        self.assertEqual(u'NEWim2', s.cssRules[1].href)
        self.assertEqual(u'''background-image: url(NEWc) !important;
background-\\image: url(NEWb);
background: url(NEWa) no-repeat !important''', s.cssRules[2].style.cssText)

        cssutils.ser.prefs.keepAllProperties = False

    def test_reprANDstr(self):
        "CSSStyleSheet.__repr__(), .__str__()"
        href = 'file:foo.css'
        title = 'title-of-css'
        
        s = cssutils.css.CSSStyleSheet(href=href, title=title)
        
        self.assert_(href in str(s))
        self.assert_(title in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(href == s2.href)
        self.assert_(title == s2.title)


if __name__ == '__main__':
    import unittest
    unittest.main()
