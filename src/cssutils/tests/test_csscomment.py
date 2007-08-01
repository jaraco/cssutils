# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.css.CSSComment
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a5, $LastChangedRevision$'


import xml

import test_cssrule

import cssutils.css


class CSSCommentTestCase(test_cssrule.CSSRuleTestCase):

    def setUp(self):
        super(CSSCommentTestCase, self).setUp()
        self.r = cssutils.css.CSSComment()
        self.rRO = cssutils.css.CSSComment(readonly=True)
        self.r_type = cssutils.css.CSSComment.COMMENT

    def test_init(self):
        "CSSComment.type and init"
        super(CSSCommentTestCase, self).test_init()


    def test_InvalidModificationErr(self):
        "CSSComment.cssText InvalidModificationErr"
        self._test_InvalidModificationErr(u'/* comment */')        


    def test_csstext(self):
        "CSSComment.cssText"
        tests = {
            u'/*öäüß€ÖÄÜ*/': None,

            u'/*x*/': None,
            u'/* x */': None,
            u'/*\t12\n*/': None,
            u'/* /* */': None,
            u'/* \\*/': None,
            u'/*"*/': None,
            u'''/*"
            */''': None,            
            u'/** / ** //*/': None
            }
        self.do_equal_r(tests) # set cssText
        tests.update({
            u'/*x': u'/*x*/',
            u'\n /*': u'/**/',
            })
        self.do_equal_p(tests) # parse
        
        tests = {
            u'/* */ */': xml.dom.SyntaxErr,
            u'  */ /* ': xml.dom.SyntaxErr
            }
        self.do_raise_p(tests) # parse
        tests.update({
            u'*/': xml.dom.InvalidModificationErr,
            u'@x /* x */': xml.dom.InvalidModificationErr
            })
        self.do_raise_r(tests) # set cssText



if __name__ == '__main__':
    import unittest
    unittest.main()