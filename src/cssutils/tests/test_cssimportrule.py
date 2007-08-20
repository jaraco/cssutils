"""
testcases for cssutils.css.CSSImportRule
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import test_cssrule
import cssutils

class CSSImportRuleTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSImportRuleTestCase, self).setUp()
        self.r = cssutils.css.CSSImportRule()
        self.rRO = cssutils.css.CSSImportRule(readonly=True)
        self.r_type = cssutils.css.CSSImportRule.IMPORT_RULE
        self.r_typeString = 'IMPORT_RULE'

    def test_init(self):
        "CSSImportRule.__init__()"
        super(CSSImportRuleTestCase, self).test_init()

        self.assertEqual(None, self.r.href)
        self.assertEqual(None, self.r.hreftype)
        self.assertEqual(
            cssutils.stylesheets.MediaList, type(self.r.media))
        self.assertEqual(u'all', self.r.media.mediaText)
        self.assertEqual(None, self.r.styleSheet)
        self.assertEqual(u'', self.r.cssText)

    def test_InvalidModificationErr(self):
        "CSSImportRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@import')

    def test_incomplete(self):
        "CSSImportRule (incomplete)"
        tests = {
            u'@import "x.css': u'@import "x.css";',
            u"@import 'x": u'@import "x";',
            u"@import url(x": u'@import url(x);',
            u"@import url('x": u'@import url(\'x\');',
            u'@import url("x;': u'@import url("x;");',
            u'@import url("x ': u'@import url("x ");',
            u'@import url(x ': u'@import url(x);',
        }
        self.do_equal_p(tests) # parse

    def test_initparameter(self):
        "CSSImportRule.__init__(href, media, hreftype)"
        r = cssutils.css.CSSImportRule(u'x', u'print')
        self.assertEqual(None, r.hreftype)
        self.assertEqual(u'@import url(x) print;', r.cssText)

        r = cssutils.css.CSSImportRule(
            u'x', u'print, tv', hreftype='string')
        self.assertEqual('string', r.hreftype)
        self.assertEqual(u'@import "x" print, tv;', r.cssText)

        r = cssutils.css.CSSImportRule(u'x', u'print, tv', hreftype='uri')
        self.assertEqual('uri', r.hreftype)
        self.assertEqual(u'@import url(x) print, tv;', r.cssText)

        # media but no href
        self.r = cssutils.css.CSSImportRule(mediaText=u'tv, screen')
        self.assertEqual(cssutils.stylesheets.MediaList,
                         type(self.r.media))
        self.assertEqual(u'tv, screen', self.r.media.mediaText)
        self.assertEqual(None, self.r.href)
        self.assertEqual(u'', self.r.cssText)

    def test_href(self):
        "CSSImportRule.href"
        # set
        self.r.href = 'x'
        self.assertEqual('x' , self.r.href)
        self.assertEqual(
            u'@import url(x);', self.r.cssText)

        # http
        self.r.href = 'http://www.example.com/x?css=z&v=1'
        self.assertEqual(
            'http://www.example.com/x?css=z&v=1' , self.r.href)
        self.assertEqual(
            u'@import url(http://www.example.com/x?css=z&v=1);',
            self.r.cssText)

        # also if hreftype changed
        self.r.hreftype='string'
        self.assertEqual(
            'http://www.example.com/x?css=z&v=1' , self.r.href)
        self.assertEqual(
            u'@import "http://www.example.com/x?css=z&v=1";',
            self.r.cssText)
        # strange and probably invalid uri with "
        self.r.href = 'XXX"123'
        self.assertEqual(
            u'@import "XXX\\"123";',
            self.r.cssText)

    def test_hreftype(self):
        "CSSImportRule.hreftype"
        self.r = cssutils.css.CSSImportRule()

        self.r.cssText = '@import /*1*/url(org) /*2*/;'
        self.assertEqual('uri', self.r.hreftype)
        self.assertEqual(u'@import /*1*/url(org) /*2*/;', self.r.cssText)

        self.r.cssText = '@import /*1*/"org" /*2*/;'
        self.assertEqual('string', self.r.hreftype)
        self.assertEqual(u'@import /*1*/"org" /*2*/;', self.r.cssText)

        self.r.href = 'new'
        self.assertEqual(u'@import /*1*/"new" /*2*/;', self.r.cssText)

        self.r.hreftype='uri'
        self.assertEqual(u'@import /*1*/url(new) /*2*/;', self.r.cssText)

    def test_media(self):
        "CSSImportRule.media"
        self.r.href = 'x' # @import url(x)

        # only medialist allowed
        self.assertRaises(AttributeError,
                          self.r.__setattr__, 'media', None)

        # set mediaText instead
        self.r.media.mediaText = 'print'
        self.assertEqual(u'@import url(x) print;', self.r.cssText)

    def test_cssText1(self):
        "CSSImportRule.cssText 1"
        tests = {
            u'''@import "str";''': None,
            u'''@\\import "str";''': u'''@import "str";''',
            u'''@IMPORT "str";''': u'''@import "str";''',

            u'''@import 'str';''': u'''@import "str";''',
            u'''@import 'str' ;''': u'''@import "str";''',
            u'''@import "str";''': None,
            u'''@import "str"  ;''': u'''@import "str";''',

            u'''@import /*1*/"str" /*2*/;''': None,
            u'''@import/*1*/ "str"/*2*/ ;''':
                u'''@import /*1*/"str" /*2*/;''',

            u'''@import "str";''': None,
            u'''@import "str" tv, print;''': None,
            u'''@import "str" tv, print, all;''': u'''@import "str";''',
            u'''@import "str" handheld, all;''': None,
            u'''@import "str" all, handheld;''': None,

            u'''@import url(x.css);''': None,
            }
        self.do_equal_r(tests) # set cssText
        tests.update({
            u'@import "x.css"': '@import "x.css";', # no ;
            u"@import 'x.css'": '@import "x.css";', # no ;
            u'@import url(x.css)': '@import url(x.css);', # no ;
            u'@import "x.css" tv': '@import "x.css" tv;',
            u'@import "x;': '@import "x;";', # no "!
            })
        self.do_equal_p(tests) # parse

        tests = {
            u'''@import;''': xml.dom.SyntaxErr,
            u'''@import all;''': xml.dom.SyntaxErr,
            u'''@import;''': xml.dom.SyntaxErr,

            u'''@import x";''': xml.dom.SyntaxErr,

            u'''@import "str" ,all;''': xml.dom.SyntaxErr,
            u'''@import "str" all,;''': xml.dom.SyntaxErr,
            u'''@import "str" all tv;''': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@import "x.css"': xml.dom.SyntaxErr,
            u"@import 'x.css'": xml.dom.SyntaxErr,
            u'@import url(x.css)': xml.dom.SyntaxErr,
            u'@import "x.css" tv': xml.dom.SyntaxErr,
            u'@import "x;': xml.dom.SyntaxErr,
            u'''@import url("x);''': xml.dom.SyntaxErr,
            })
        self.do_raise_r(tests) # set cssText

    def test_reprANDstr(self):
        "CSSImportRule.__repr__(), .__str__()"
        href='x.css'
        mediaText='tv, print'
        
        s = cssutils.css.CSSImportRule(href=href, mediaText=mediaText)
        
        self.assert_(href in str(s))
        # mediaText is not present in str(s)

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(href == s2.href)
        self.assert_(mediaText == s2.media.mediaText)
        

if __name__ == '__main__':
    import unittest
    unittest.main()
