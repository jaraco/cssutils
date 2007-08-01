# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.tokenize.Tokenizer
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2b2, $LastChangedRevision$'

import xml.dom

import basetest

from cssutils.tokenize import Tokenizer
from cssutils.token import Token


class TokenizerTestCase(basetest.BaseTestCase):

    def setUp(self):
        #log = cssutils.errorhandler.ErrorHandler() 
        self.tokenizer = Tokenizer()
        self.ttype = Token


    def test_tokenize(self):
        "Tokenizer tests"

        # testcss: expected token list with
        #   (line, col, type, value[, normalvalue])

        tt = self.ttype
        tests = {
            # SPACES are condensed to 1 SPACE only!
            u' ': [(1, 1, tt.S, u' ', u' ')],
            u'  ': [(1, 1, tt.S, u'  ', u' ')],
            u'\r': [(1, 1, tt.S, u'\r', u' ')],
            u'\n': [(1, 1, tt.S, u'\n', u' ')],
            u'\r\n': [(1, 1, tt.S, u'\r\n', u' ')],
            u'\f': [(1, 1, tt.S, u'\f', u' ')],
            u'\t': [(1, 1, tt.S, u'\t', u' ')],
            u'\r\n\r\n\f\t ': [(1, 1, tt.S, u'\r\n\r\n\f\t ', u' ')],

            # IDENT
            u'a': [(1, 1, tt.IDENT, u'a')],
            u'a-b': [(1, 1, tt.IDENT, u'a-b')],
            u'a-': [(1, 1, tt.IDENT, u'a-')],
            u'-b': [(1, 1, tt.IDENT, u'-b')],

            # ATKEYWORD
            u'@a @_ @ab1 @-ab @1': [(1, 1, tt.ATKEYWORD, u'@a'),
               (1, 3, tt.S, u' '), (1, 4, tt.ATKEYWORD, u'@_'),
               (1, 6, tt.S, u' '), (1, 7, tt.ATKEYWORD, u'@ab1'),
               (1, 11, tt.S, u' '), (1, 12, tt.ATKEYWORD, u'@-ab'),
               (1, 16, tt.S, u' '), (1, 17, tt.DELIM, u'@'),
               (1, 18, tt.NUMBER, u'1')],
            u'x x1 -x .-x #_x -': [(1, 1, tt.IDENT, u'x'),
               (1, 2, tt.S, u' '),
               (1, 3, tt.IDENT, u'x1'),
               (1, 5, tt.S, u' '),
               (1, 6, tt.IDENT, u'-x'),
               (1, 8, tt.S, u' '),
               (1, 9, tt.CLASS, u'.'),
               (1, 10, tt.IDENT, u'-x'),
               (1, 12, tt.S, u' '),
               (1, 13, tt.HASH, u'#_x'),
               (1, 16, tt.S, u' '),
               (1, 17, tt.DELIM, u'-')],
            u'@import': [(1, 1, tt.IMPORT_SYM, u'@import')],
            u'@page': [(1, 1, tt.PAGE_SYM, u'@page')],
            u'@media': [(1, 1, tt.MEDIA_SYM, u'@media')],
            u'@charset': [(1, 1, tt.CHARSET_SYM, u'@charset')],
            # simple escapes, should \ be removed???
            u'\\{\\}\\(\\)\\;\\}\\:\\,': [
              (1, 1, u'{ident}', u'\\{\\}\\(\\)\\;\\}\\:\\,')],

            # comment
            u'/*x*//': [(1, 1, tt.COMMENT, u'/*x*/'), (1, 6, tt.DELIM, u'/')],
            u'/* */ */': [(1, 1, tt.COMMENT, u'/* */'), (1, 6, tt.S, u' '),
                          (1, 7, tt.UNIVERSAL, u'*'), (1, 8, tt.DELIM, u'/')],
            u'1/*\\*/2': [(1, 1, tt.NUMBER, u'1'),
                          (1, 2, tt.COMMENT, u'/*\\*/'),
                             (1, 7, tt.NUMBER, u'2')],

            # STRING
            u'"x"': [(1, 1, tt.STRING, u'"x"')],
            u'"\\""': [(1, 1, tt.STRING, u'"\\""')],
            u'"x\\""a': [(1, 1, tt.STRING, u'"x\\""'), (1, 6, tt.IDENT, u'a')],
            u"'x'": [(1, 1, tt.STRING, u"'x'")],
            u"'\\''": [(1, 1, tt.STRING, u"'\\''")],
            u'''"1\\\n2"''': [(1, 1, tt.STRING, u'"12"')],
            u'''"1\\\r2"''': [(1, 1, tt.STRING, u'"12"')],
            u'''"1\\\r\n2"''': [(1, 1, tt.STRING, u'"12"')],
            u'''"1\\\f2"''': [(1, 1, tt.STRING, u'"12"')],
            u'''"\\"1\\\n\\\r\\\f\\\r\n2"''': [(1, 1, tt.STRING, u'"\\"12"')],

            # ESCAPES
            # full length 6 digit escape
            u'\\000029a': [(1, 1, tt.IDENT, u'\\000029a')],
            # escape short form
            u'\\29': [(1, 1, tt.IDENT, u'\\29')],
            # escape ends as non hexdigit follows
            u'\\29x': [(1, 1, tt.IDENT, u'\\29x')],
            # escape ends with explicit space
            u'\\29 a': [(1, 1, tt.IDENT, u'\\29 a')],
            # escape ends with explicit space but \r\n as single space
            u'\\29\r\na': [(1, 1, tt.IDENT, u'\\29 a')],
            # escape ends, double space becomes single
            u'\\1  ': [(1, 1, tt.IDENT, u'\\1 '), (1, 4, tt.S, u' ')],
            u'\\12  ': [(1, 1, tt.IDENT, u'\\12 '), (1, 5, tt.S, u' ')],
            u'\\123  ': [(1, 1, tt.IDENT, u'\\123 '), (1, 6, tt.S, u' ')],
            u'\\1234  ': [(1, 1, tt.IDENT, u'\\1234 '), (1, 7, tt.S, u' ')],
            u'\\12345  ': [(1, 1, tt.IDENT, u'\\12345 '), (1, 8, tt.S, u' ')],
            u'\\123456 ': [(1, 1, tt.IDENT, u'\\123456'), (1, 8, tt.S, u' ')],
            u'\\123456  ': [(1, 1, tt.IDENT, u'\\123456'), (1, 8, tt.S, u'  ')],
            # escape ends with space but space stays as escaped itself
            u'\\29\\ ': [(1, 1, tt.IDENT, u'\\29\\ ')],
            # escape inside string, escape end removed!
            u'"\\29 a "': [(1, 1, tt.STRING, u'"\\29 a "')],

            # HTML CDO and CDC
            u'1 <!-- x --> 2': [(1, 1, tt.NUMBER, u'1'), (1, 2, tt.S, u' '),
                                (1, 3, tt.CDO, u'<!--'), (1, 7, tt.S, u' '),
                                (1, 8, tt.IDENT, u'x'), (1, 9, tt.S, u' '),
                                (1, 10, tt.CDC, u'-->'), (1, 13, tt.S, u' '),
                                (1, 14, tt.NUMBER, u'2')],
            u'<!--"--><!--"-->': [(1, 1, tt.CDO, u'<!--'),
                                  (1, 5, tt.STRING, u'"--><!--"'),
                                  (1, 14, tt.CDC, u'-->')],

            # PERCENTAGE
            u'1 2% 3': [(1, 1, tt.NUMBER, u'1'),
             (1, 2, tt.S, u' '),
             (1, 3, tt.PERCENTAGE, u'2%'),
             (1, 5, tt.S, u' '),
             (1, 6, tt.NUMBER, u'3')],
            u'"2%"': [(1, 1, tt.STRING, u'"2%"')],

            # IMPORTANT_SYM
            u' !important ': [(1, 1, tt.S, u' '),
                              (1, 2, tt.IMPORTANT_SYM, u'!important'),
                              (1, 12, tt.S, u' ')],
            u'x !important': [(1,1, tt.IDENT, u'x'),
                              (1, 2, tt.S, u' '),
                              (1, 3, tt.IMPORTANT_SYM, u'!important')],
            u' ! ': [(1, 1, tt.S, u' '), (1, 2, tt.DELIM, u'!'),
                     (1, 3, tt.S, u' ')],
            u'!important': [(1,1, tt.IMPORTANT_SYM, u'!important')],
            u' !important': [
                (1,1, tt.S, u' '),
                (1,2, tt.IMPORTANT_SYM, u'!important')
                ],
            u' ! x important !/*important*/important': [
                (1,1, tt.S, u' '),
                (1,2, tt.DELIM, u'!'),
                (1,3, tt.S, u' '),
                (1,4, tt.IDENT, u'x'),
                (1,5, tt.S, u' '),
                (1,6, tt.IDENT, u'important'),
                (1,15, tt.S, u' '),
                (1,16, tt.DELIM, u'!'),
                (1,17, tt.COMMENT, u'/*important*/'),
                (1,30, tt.IDENT, u'important')
                ],

            # num
            u'1 1.1 -1 -1.1 .1 -.1 1.': [(1, 1, tt.NUMBER, u'1'),
               (1, 2, tt.S, u' '), (1, 3, tt.NUMBER, u'1.1'),
               (1, 6, tt.S, u' '), (1, 7, tt.NUMBER, u'-1'),
               (1, 9, tt.S, u' '), (1, 10, tt.NUMBER, u'-1.1'),
               (1, 14, tt.S, u' '), (1, 15, tt.NUMBER, u'0.1'),
               (1, 17, tt.S, u' '), (1, 18, tt.NUMBER, u'-0.1'),
               (1, 21, tt.S, u' '), 
               (1, 22, tt.NUMBER, u'1'), (1, 23, tt.CLASS, u'.')
                                         ],
            # Attribute INCLUDES & DASHMATCH + CSS3
            u'a=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.DELIM, u'='),
                      (1, 3, tt.NUMBER, u'1')],
            u'a~=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.INCLUDES, u'~='),
                      (1, 4, tt.NUMBER, u'1')],
            u'a|=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.DASHMATCH, u'|='),
                      (1, 4, tt.NUMBER, u'1')],
            u'a^=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.PREFIXMATCH, u'^='),
                      (1, 4, tt.NUMBER, u'1')],
            u'a$=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.SUFFIXMATCH, u'$='),
                      (1, 4, tt.NUMBER, u'1')],
            u'a*=1': [(1, 1, tt.IDENT, u'a'), (1, 2, tt.SUBSTRINGMATCH, u'*='),
                      (1, 4, tt.NUMBER, u'1')],

            # CSS3 pseudo
            u'::': [(1, 1, tt.PSEUDO_ELEMENT, u'::')],

            # SPECIALS
            u'*+>~{},': [(1, 1, tt.UNIVERSAL, u'*'),
               (1, 2, tt.PLUS, u'+'),
               (1, 3, tt.GREATER, u'>'),
               (1, 4, tt.TILDE, u'~'),
               (1, 5, tt.LBRACE, u'{'),
               (1, 6, tt.RBRACE, u'}'),
               (1, 7, tt.COMMA, u',')],

            # DELIM
            u'!%:&$|': [(1, 1, tt.DELIM, u'!'),
               (1, 2, tt.DELIM, u'%'),
               (1, 3, tt.DELIM, u':'),
               (1, 4, tt.DELIM, u'&'),
               (1, 5, tt.DELIM, u'$'),
               (1, 6, tt.DELIM, u'|')],


            # DIMENSION
            u'5em': [(1, 1, tt.DIMENSION, u'5em')],
            u' 5em': [(1, 1, tt.S, u' '), (1, 2, tt.DIMENSION, u'5em')],
            u'5em ': [(1, 1, tt.DIMENSION, u'5em'), (1, 4, tt.S, u' ')],

            u'-5em': [(1, 1, tt.DIMENSION, u'-5em')],
            u' -5em': [(1, 1, tt.S, u' '), (1, 2, tt.DIMENSION, u'-5em')],
            u'-5em ': [(1, 1, tt.DIMENSION, u'-5em'), (1, 5, tt.S, u' ')],

            u'.5em': [(1, 1, tt.DIMENSION, u'0.5em')],
            u' .5em': [(1, 1, tt.S, u' '), (1, 2, tt.DIMENSION, u'0.5em')],
            u'.5em ': [(1, 1, tt.DIMENSION, u'0.5em'), (1, 5, tt.S, u' ')],

            u'-.5em': [(1, 1, tt.DIMENSION, u'-0.5em')],
            u' -.5em': [(1, 1, tt.S, u' '), (1, 2, tt.DIMENSION, u'-0.5em')],
            u'-.5em ': [(1, 1, tt.DIMENSION, u'-0.5em'), (1, 6, tt.S, u' ')],

            u'5em5_-': [(1, 1, tt.DIMENSION, u'5em5_-')],

            u'a a5 a5a 5 5a 5a5': [(1, 1, tt.IDENT, u'a'),
               (1, 2, tt.S, u' '),
               (1, 3, tt.IDENT, u'a5'),
               (1, 5, tt.S, u' '),
               (1, 6, tt.IDENT, u'a5a'),
               (1, 9, tt.S, u' '),
               (1, 10, tt.NUMBER, u'5'),
               (1, 11, tt.S, u' '),
               (1, 12, tt.DIMENSION, u'5a'),
               (1, 14, tt.S, u' '),
               (1, 15, tt.DIMENSION, u'5a5')],

            # URI            
            u'url("x")': [(1, 1, tt.URI, u'url("x")')],
            u'url( "x")': [(1, 1, tt.URI, u'url("x")')],
            u'url("x" )': [(1, 1, tt.URI, u'url("x")')],
            u'url( "x" )': [(1, 1, tt.URI, u'url("x")')],
            u' url("x")': [
                (1, 1, tt.S, u' '),
                (1, 2, tt.URI, u'url("x")')],
            u'url("x") ': [
                (1, 1, tt.URI, u'url("x")'),
                (1, 9, tt.S, u' '),
                ],
            u'url(ab)': [(1, 1, tt.URI, u'url(ab)')],
            u'url($#/ab)': [(1, 1, tt.URI, u'url($#/ab)')],
            u'url(\1233/a/b)': [(1, 1, tt.URI, u'url(\1233/a/b)')],
            # not URI
            u'url("1""2")': [
                (1, 1, tt.FUNCTION, u'url('),
                (1, 5, tt.STRING, u'"1"'),
                (1, 8, tt.STRING, u'"2"'),
                (1, 11, tt.RPARANTHESIS, u')'),
                ],
            u'url(a"2")': [
                (1, 1, tt.FUNCTION, u'url('),
                (1, 5, tt.IDENT, u'a'),
                (1, 6, tt.STRING, u'"2"'),
                (1, 9, tt.RPARANTHESIS, u')'),
                ],
            u'url(a b)': [
                (1, 1, tt.FUNCTION, u'url('),
                (1, 5, tt.IDENT, u'a'),
                (1, 6, tt.S, u' '),
                (1, 7, tt.IDENT, u'b'),
                (1, 8, tt.RPARANTHESIS, u')'),
                ],

            # FUNCTION
            u' counter("x")': [
               (1,1, tt.S, u' '),
               (1, 2, tt.FUNCTION, u'counter('),
               (1, 10, tt.STRING, u'"x"'),
               (1, 13, tt.RPARANTHESIS, u')')],
            # HASH
            u'# #a #_a #-a #1': [
                (1, 1, tt.DELIM, u'#'),
                (1, 2, tt.S, u' '),
                (1, 3, tt.HASH, u'#a'),
                (1, 5, tt.S, u' '),
                (1, 6, tt.HASH, u'#_a'),
                (1, 9, tt.S, u' '),
                (1, 10, tt.HASH, u'#-a'),
                (1, 13, tt.S, u' '),
                (1, 14, tt.HASH, u'#1')                            
                ],
            u'#1a1 ': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u' '),
                ],
            u'#1a1\n': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u'\n'),
                ],
            u'#1a1{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.LBRACE, u'{'),
                ],
            u'#1a1 {': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u' '),
                (1, 6, tt.LBRACE, u'{'),
                ],
            u'#1a1\n{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u'\n'),
                (2, 1, tt.LBRACE, u'{'),
                ],
            u'#1a1\n {': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u'\n '),
                (2, 2, tt.LBRACE, u'{'),
                ],
            u'#1a1 \n{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.S, u' \n'),
                (2, 1, tt.LBRACE, u'{'),
                ],
            # STRINGS with NL
            u'"x\n': [(1,1, tt.INVALID, u'"x\n')],
            u'"x\r': [(1,1, tt.INVALID, u'"x\r')],
            u'"x\f': [(1,1, tt.INVALID, u'"x\f')],
            u'"x\n ': [
               (1,1, tt.INVALID, u'"x\n'),
               (2,1, tt.S, u' ')
               ]

            }

        for css in tests:
            tokens = self.tokenizer.tokenize(css)
            expected = [Token(x[0], x[1], x[2], x[3]) for x in tests[css]]
            self.assertEqual(expected, tokens)
            # check normalvalue for single tokens
            if len(tests[css][0]) > 4:
                expectednv = tests[css][0][4]
                self.assertEqual(expected[0].normalvalue, expectednv)

        tests = {
            u'/*a': xml.dom.SyntaxErr,
            u'"a': xml.dom.SyntaxErr,
            u"'a": xml.dom.SyntaxErr,
            u"\\0 a": xml.dom.SyntaxErr,
            u"\\00": xml.dom.SyntaxErr,
            u"\\000": xml.dom.SyntaxErr,
            u"\\0000": xml.dom.SyntaxErr,
            u"\\00000": xml.dom.SyntaxErr,
            u"\\000000": xml.dom.SyntaxErr,
            u"\\0000001": xml.dom.SyntaxErr
            }
        self.tokenizer.log.raiseExceptions = True #!!
        for css, exception in tests.items():
            self.assertRaises(exception, self.tokenizer.tokenize, css)


if __name__ == '__main__':
    import unittest
    unittest.main() 
