"""Testcases for cssutils.css.CSSImportRule"""
__version__ = '$Id$'

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

        # no init param
        self.assertEqual(None, self.r.href)
        self.assertEqual(None, self.r.hreftype)
        self.assertEqual(u'all', self.r.media.mediaText)
        self.assertEqual(
            cssutils.stylesheets.MediaList, type(self.r.media))
        self.assertEqual(None, self.r.name)
        self.assertEqual(None, self.r.styleSheet)
        self.assertEqual(u'', self.r.cssText)

        # all
        r = cssutils.css.CSSImportRule(href='href', mediaText='tv', name='name')
        self.assertEqual(u'@import url(href) tv "name";', r.cssText)
        self.assertEqual("href", r.href)
        self.assertEqual(None, r.hreftype)
        self.assertEqual(u'tv', r.media.mediaText)
        self.assertEqual(
            cssutils.stylesheets.MediaList, type(r.media))
        self.assertEqual('name', r.name)
        self.assertEqual(None, r.parentRule) # see CSSRule
        self.assertEqual(None, r.parentStyleSheet) # see CSSRule
        
        # href
        r = cssutils.css.CSSImportRule(u'x')
        self.assertEqual(u'@import url(x);', r.cssText)
        self.assertEqual('x', r.href)
        self.assertEqual(None, r.hreftype)

        # href + mediaText
        r = cssutils.css.CSSImportRule(u'x', u'print')
        self.assertEqual(u'@import url(x) print;', r.cssText)
        self.assertEqual('x', r.href)
        self.assertEqual('print', r.media.mediaText)

        # href + name
        r = cssutils.css.CSSImportRule(u'x', name=u'n')
        self.assertEqual(u'@import url(x) "n";', r.cssText)
        self.assertEqual('x', r.href)
        self.assertEqual('n', r.name)

        # href + mediaText + name
        r = cssutils.css.CSSImportRule(u'x', u'print', 'n')
        self.assertEqual(u'@import url(x) print "n";', r.cssText)
        self.assertEqual('x', r.href)
        self.assertEqual('print', r.media.mediaText)
        self.assertEqual('n', r.name)

        # media +name only
        self.r = cssutils.css.CSSImportRule(mediaText=u'print', name="n")
        self.assertEqual(cssutils.stylesheets.MediaList,
                         type(self.r.media))
        self.assertEqual(u'', self.r.cssText)
        self.assertEqual(u'print', self.r.media.mediaText)
        self.assertEqual(u'n', self.r.name)

    def test_cssText(self):
        "CSSImportRule.cssText"
        tests = {
            # href string
            u'''@import "str";''': None,
            u'''@import"str";''': u'''@import "str";''',
            u'''@\\import "str";''': u'''@import "str";''',
            u'''@IMPORT "str";''': u'''@import "str";''',
            u'''@import 'str';''': u'''@import "str";''',
            u'''@import 'str' ;''': u'''@import "str";''',
            u'''@import "str";''': None,
            u'''@import "str"  ;''': u'''@import "str";''',
            ur'''@import "\""  ;''': ur'''@import "\"";''',
            u'''@import '\\'';''': ur'''@import "'";''',
            u'''@import '"';''': ur'''@import "\"";''',
            # href url
            u'''@import url(x.css);''': None,
            # nospace
            u'''@importurl(x.css);''': u'''@import url(x.css);''',
            u'''@import url(")");''': u'''@import url(")");''',
            u'''@import url("\\"");''': u'''@import url(");''',
            u'''@import url('\\'');''': u'''@import url(');''',

            # href + media
            # all is removed
            u'''@import "str" all;''': u'''@import "str";''',
            u'''@import "str" tv, print;''': None,
            u'''@import"str"tv,print;''': u'''@import "str" tv, print;''',
            u'''@import "str" tv, print, all;''': u'''@import "str";''',
            u'''@import "str" handheld, all;''': u'''@import "str" all, handheld;''',
            u'''@import "str" all, handheld;''': None,
            u'''@import "str" not tv;''': None,
            u'''@import "str" only tv;''': None,
            u'''@import "str" only tv and (color: 2);''': None,

            # href + name
            u'''@import "str" "name";''': None,
            u'''@import "str" 'name';''': u'''@import "str" "name";''',
            u'''@import url(x) "name";''': None,
            u'''@import "str" "\\"";''': None,
            u'''@import "str" '\\'';''': u'''@import "str" "'";''',

            # href + media + name
            u'''@import"str"tv"name";''': u'''@import "str" tv "name";''',
            u'''@import\t\r\f\n"str"\t\t\r\f\ntv\t\t\r\f\n"name"\t;''': 
                u'''@import "str" tv "name";''',

            # comments
            u'''@import /*1*/ "str" /*2*/;''': None,
            u'@import/*1*//*2*/"str"/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': 
                u'@import /*1*/ /*2*/ "str" /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            u'@import/*1*//*2*/url(u)/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': 
                u'@import /*1*/ /*2*/ url(u) /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            u'@import/*1*//*2*/url("u")/*3*//*4*/all/*5*//*6*/"name"/*7*//*8*/ ;': 
                u'@import /*1*/ /*2*/ url(u) /*3*/ /*4*/ all /*5*/ /*6*/ "name" /*7*/ /*8*/;',
            # WS
            u'@import\n\t\f "str"\n\t\f tv\n\t\f "name"\n\t\f ;': 
                u'@import "str" tv "name";',
            u'@import\n\t\f url(\n\t\f u\n\t\f )\n\t\f tv\n\t\f "name"\n\t\f ;': 
                u'@import url(u) tv "name";',
            u'@import\n\t\f url("u")\n\t\f tv\n\t\f "name"\n\t\f ;': 
                u'@import url(u) tv "name";',
            u'@import\n\t\f url(\n\t\f "u"\n\t\f )\n\t\f tv\n\t\f "name"\n\t\f ;': 
                u'@import url(u) tv "name";',
            }
        self.do_equal_r(tests) # set cssText
        tests.update({
            u'@import "x.css" tv': '@import "x.css" tv;',
            u'@import "x.css"': '@import "x.css";', # no ;
            u"@import 'x.css'": '@import "x.css";', # no ;
            u'@import url(x.css)': '@import url(x.css);', # no ;
            u'@import "x;': '@import "x;";', # no "!
            })
        self.do_equal_p(tests) # parse

        tests = {
            u'''@import;''': xml.dom.SyntaxErr,
            u'''@import all;''': xml.dom.SyntaxErr,
            u'''@import all"name";''': xml.dom.SyntaxErr,
            u'''@import;''': xml.dom.SyntaxErr,
            u'''@import x";''': xml.dom.SyntaxErr,
            u'''@import "str" ,all;''': xml.dom.SyntaxErr,
            u'''@import "str" all,;''': xml.dom.SyntaxErr,
            u'''@import "str" all tv;''': xml.dom.SyntaxErr,
            u'''@import "str" "name" all;''': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'@import "x.css"': xml.dom.SyntaxErr,
            u"@import 'x.css'": xml.dom.SyntaxErr,
            u'@import url(x.css)': xml.dom.SyntaxErr,
            u'@import "x.css" tv': xml.dom.SyntaxErr,
            u'@import "x;': xml.dom.SyntaxErr,
            u'''@import url("x);''': xml.dom.SyntaxErr,
            # trailing
            u'''@import "x";"a"''': xml.dom.SyntaxErr,
            # trailing S or COMMENT
            u'''@import "x";/**/''': xml.dom.SyntaxErr,
            u'''@import "x"; ''': xml.dom.SyntaxErr,
            })
        self.do_raise_r(tests) # set cssText

    def test_href(self):
        "CSSImportRule.href"
        # set
        self.r.href = 'x'
        self.assertEqual('x', self.r.href)
        self.assertEqual(u'@import url(x);', self.r.cssText)

        # http
        self.r.href = 'http://www.example.com/x?css=z&v=1'
        self.assertEqual('http://www.example.com/x?css=z&v=1' , self.r.href)
        self.assertEqual(u'@import url(http://www.example.com/x?css=z&v=1);',
                         self.r.cssText)

        # also if hreftype changed
        self.r.hreftype='string'
        self.assertEqual('http://www.example.com/x?css=z&v=1' , self.r.href)
        self.assertEqual(u'@import "http://www.example.com/x?css=z&v=1";',
                         self.r.cssText)
        
        # string escaping?
        self.r.href = '"'
        self.assertEqual(u'@import "\\"";', self.r.cssText)
        self.r.hreftype='url'
        self.assertEqual(u'@import url(");', self.r.cssText)
        
        # url escaping?
        self.r.href = ')'
        self.assertEqual(u'@import url(")");', self.r.cssText)

        self.r.hreftype = 'NOT VALID' # using default
        self.assertEqual(u'@import url(")");', self.r.cssText)

    def test_hreftype(self):
        "CSSImportRule.hreftype"
        self.r = cssutils.css.CSSImportRule()

        self.r.cssText = '@import /*1*/url(org) /*2*/;'
        self.assertEqual('uri', self.r.hreftype)
        self.assertEqual(u'@import /*1*/ url(org) /*2*/;', self.r.cssText)

        self.r.cssText = '@import /*1*/"org" /*2*/;'
        self.assertEqual('string', self.r.hreftype)
        self.assertEqual(u'@import /*1*/ "org" /*2*/;', self.r.cssText)

        self.r.href = 'new'
        self.assertEqual(u'@import /*1*/ "new" /*2*/;', self.r.cssText)

        self.r.hreftype='uri'
        self.assertEqual(u'@import /*1*/ url(new) /*2*/;', self.r.cssText)

    def test_media(self):
        "CSSImportRule.media"
        self.r.href = 'x' # @import url(x)

        # media is readonly
        self.assertRaises(AttributeError, self.r.__setattr__, 'media', None)

        # but not static
        self.r.media.mediaText = 'print'
        self.assertEqual(u'@import url(x) print;', self.r.cssText)

    def test_name(self):
        "CSSImportRule.name"
        r = cssutils.css.CSSImportRule('x')

        r.name = "n"
        self.assertEqual('n', r.name)
        self.assertEqual(u'@import url(x) "n";', r.cssText)
        r.name = '"'
        self.assertEqual('"', r.name)
        self.assertEqual(u'@import url(x) "\\"";', r.cssText)

    def test_incomplete(self):
        "CSSImportRule (incomplete)"
        tests = {
            u'@import "x.css': u'@import "x.css";',
            u"@import 'x": u'@import "x";',
            # TODO:
            u"@import url(x": u'@import url(x);',
            u"@import url('x": u'@import url(x);',
            u'@import url("x;': u'@import url("x;");',
            u'@import url( "x;': u'@import url("x;");',
            u'@import url("x ': u'@import url("x ");',
            u'@import url(x ': u'@import url(x);',
            u'''@import "a
                @import "b";
                @import "c";''': u'@import "c";'
        }
        self.do_equal_p(tests, raising=False) # parse
        
    def test_InvalidModificationErr(self):
        "CSSImportRule.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'@import')

    def test_reprANDstr(self):
        "CSSImportRule.__repr__(), .__str__()"
        href = 'x.css'
        mediaText = 'tv, print'
        name = 'name'
        s = cssutils.css.CSSImportRule(href=href, mediaText=mediaText, name=name)

        # str(): mediaText nor name are present here
        self.assert_(href in str(s))
        
        # repr()
        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(href == s2.href)
        self.assert_(mediaText == s2.media.mediaText)
        self.assert_(name == s2.name)


if __name__ == '__main__':
    import unittest
    unittest.main()
