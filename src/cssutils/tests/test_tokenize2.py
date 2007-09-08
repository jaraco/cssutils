# -*- coding: iso-8859-1 -*-
"""
testcases for new cssutils.tokenize.Tokenizer
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:56:36 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 302 $'

import xml.dom
import basetest
from cssutils.newtokenize import *
from cssutils.token import Token

class TokenizerTestCase(basetest.BaseTestCase):

    testsall = {
        # IDENT
        u' a ': [('S', u' ', 1, 1),
                 ('IDENT', u'a', 1, 2),
                 ('S', u' ', 1, 3)],
        u'_a': [('IDENT', u'_a', 1, 1)],
        u'-a': [('IDENT', u'-a', 1, 1)],
        u'aA-_\200\377': [('IDENT', u'aA-_\200\377', 1, 1)],
        u'a1': [('IDENT', u'a1', 1, 1)],
        # escapes must end with S or max 6 digits:
        u'\\1\nb': [('IDENT', u'\\1\nb', 1, 1)],
        u'\\1\rb': [('IDENT', u'\\1\rb', 1, 1)],
        u'\\1\fb': [('IDENT', u'\\1\fb', 1, 1)],

        # TODO: escape ends with explicit space but \r\n as single space
        #u'\\1\r\nb': [('IDENT', u'\\1\r\nb', 1, 1)],
        u'\\1 b': [('IDENT', u'\\1 b', 1, 1)],
        u'\\12 b': [('IDENT', u'\\12 b', 1, 1)],
        u'\\123 b': [('IDENT', u'\\123 b', 1, 1)],
        u'\\1234 b': [('IDENT', u'\\1234 b', 1, 1)],
        u'\\12345 b': [('IDENT', u'\\12345 b', 1, 1)],
        u'\\123456 b': [('IDENT', u'\\123456 b', 1, 1)],
        u'\\1234567 b': [('IDENT', u'\\1234567', 1, 1),
                         ('S', u' ', 1, 9),
                         ('IDENT', u'b', 1, 10)],
        u'\\{\\}\\(\\)\\[\\]\\#\\@\\.\\,':
            [('IDENT', u'\\{\\}\\(\\)\\[\\]\\#\\@\\.\\,', 1, 1)],

        # STRING
        u' "" ': [('S', u' ', 1, 1),
                 ('STRING', u'""', 1, 2),
                 ('S', u' ', 1, 4)],
        u' "\'" ': [('S', u' ', 1, 1),
                 ('STRING', u'"\'"', 1, 2),
                 ('S', u' ', 1, 5)],
        u" '' ": [('S', u' ', 1, 1),
                 ('STRING', u"''", 1, 2),
                 ('S', u' ', 1, 4)],
        # TODO:
        ##u'"\\""': [('STRING', u'"\\""', 1, 1)],

        u"'\\''": [('STRING', u"'\\''", 1, 1)],
        u"'\\\n'": [('STRING', u"'\\\n'", 1, 1)],
        u"'\\\n\\\n\\\n'": [('STRING', u"'\\\n\\\n\\\n'", 1, 1)],
        u"'\\\f'": [('STRING', u"'\\\f'", 1, 1)],
        u"'\\\r'": [('STRING', u"'\\\r'", 1, 1)],
        u"'\\\r\n'": [('STRING', u"'\\\r\n'", 1, 1)],
        u"'1\\\n2'": [('STRING', u"'1\\\n2'", 1, 1)],

        # HASH
        u' #a ': [('S', u' ', 1, 1),
                 ('HASH', u'#a', 1, 2),
                 ('S', u' ', 1, 4)],

        # NUMBER
        u' 0 ': [('S', u' ', 1, 1),
                 ('NUMBER', u'0', 1, 2),
                 ('S', u' ', 1, 3)],
        u' 0.1 ': [('S', u' ', 1, 1),
                 ('NUMBER', u'0.1', 1, 2),
                 ('S', u' ', 1, 5)],
        u' .0 ': [('S', u' ', 1, 1),
                 ('NUMBER', u'.0', 1, 2),
                 ('S', u' ', 1, 4)],

        # PERCENTAGE
        u' 0% ': [('S', u' ', 1, 1),
                 ('PERCENTAGE', u'0%', 1, 2),
                 ('S', u' ', 1, 4)],
        u' .5% ': [('S', u' ', 1, 1),
                 ('PERCENTAGE', u'.5%', 1, 2),
                 ('S', u' ', 1, 5)],

        # URI
        u' url() ': [('S', u' ', 1, 1),
                 ('URI', u'url()', 1, 2),
                 ('S', u' ', 1, 7)],
        u' url(a) ': [('S', u' ', 1, 1),
                 ('URI', u'url(a)', 1, 2),
                 ('S', u' ', 1, 8)],
        u' url("a") ': [('S', u' ', 1, 1),
                 ('URI', u'url("a")', 1, 2),
                 ('S', u' ', 1, 10)],
        u' url( a ) ': [('S', u' ', 1, 1),
                 ('URI', u'url( a )', 1, 2),
                 ('S', u' ', 1, 10)],

        # UNICODE-RANGE

        # CDO
        u' <!-- ': [('S', u' ', 1, 1),
                   ('CDO', u'<!--', 1, 2),
                   ('S', u' ', 1, 6)],
        u'"<!--""-->"': [('STRING', u'"<!--"', 1, 1),
                    ('STRING', u'"-->"', 1, 7)],

        # CDC
        u' --> ': [('S', u' ', 1, 1),
                  ('CDC', u'-->', 1, 2),
                  ('S', u' ', 1, 5)],

        # S
        u' ': [('S', u' ', 1, 1)],
        u'  ': [('S', u'  ', 1, 1)],
        u'\r': [('S', u'\r', 1, 1)],
        u'\n': [('S', u'\n', 1, 1)],
        u'\r\n': [('S', u'\r\n', 1, 1)],
        u'\f': [('S', u'\f', 1, 1)],
        u'\r': [('S', u'\r', 1, 1)],
        u'\t': [('S', u'\t', 1, 1)],
        u'\r\n\r\n\f\t ': [('S', u'\r\n\r\n\f\t ', 1, 1)],

        # COMMENT
        u'/*x*/ ': [('COMMENT', u'/*x*/', 1, 1),
                    ('S', u' ', 1, 6)],

        # FUNCTION
        u' x( ': [('S', u' ', 1, 1),
                  ('FUNCTION', u'x(', 1, 2),
                  ('S', u' ', 1, 4)],

        # INCLUDES
        u' ~= ': [('S', u' ', 1, 1),
                  ('INCLUDES', u'~=', 1, 2),
                  ('S', u' ', 1, 4)],
        u'~==': [('INCLUDES', u'~=', 1, 1), ('CHAR', u'=', 1, 3)],

        # DASHMATCH
        u' |= ': [('S', u' ', 1, 1),
                  ('DASHMATCH', u'|=', 1, 2),
                  ('S', u' ', 1, 4)],
        u'|==': [('DASHMATCH', u'|=', 1, 1), ('CHAR', u'=', 1, 3)],

        # CHAR
        u' @ ': [('S', u' ', 1, 1),
                  ('CHAR', u'@', 1, 2),
                  ('S', u' ', 1, 3)],
    }

    tests3 = {
        # ATKEYWORD
        u' @x ': [('S', u' ', 1, 1),
                  ('ATKEYWORD', u'@x', 1, 2),
                  ('S', u' ', 1, 4)],
        u'@X': [('ATKEYWORD', u'@X', 1, 1)],
        u'@\\x': [('ATKEYWORD', u'@\\x', 1, 1)],
        # -
        u'@1x': [('CHAR', u'@', 1, 1),
                  ('DIMENSION', u'1x', 1, 2)],

        # DIMENSION
        u' 0px ': [('S', u' ', 1, 1),
                 ('DIMENSION', u'0px', 1, 2),
                 ('S', u' ', 1, 5)],
        u' 1s ': [('S', u' ', 1, 1),
                 ('DIMENSION', u'1s', 1, 2),
                 ('S', u' ', 1, 4)],
        u'0.2EM': [('DIMENSION', u'0.2EM', 1, 1)],

        # PREFIXMATCH
        u' ^= ': [('S', u' ', 1, 1),
                  ('PREFIXMATCH', u'^=', 1, 2),
                  ('S', u' ', 1, 4)],
        u'^==': [('PREFIXMATCH', u'^=', 1, 1), ('CHAR', u'=', 1, 3)],

        # SUFFIXMATCH
        u' $= ': [('S', u' ', 1, 1),
                  ('SUFFIXMATCH', u'$=', 1, 2),
                  ('S', u' ', 1, 4)],
        u'$==': [('SUFFIXMATCH', u'$=', 1, 1), ('CHAR', u'=', 1, 3)],

        # SUBSTRINGMATCH
        u' *= ': [('S', u' ', 1, 1),
                  ('SUBSTRINGMATCH', u'*=', 1, 2),
                  ('S', u' ', 1, 4)],
        u'*==': [('SUBSTRINGMATCH', u'*=', 1, 1), ('CHAR', u'=', 1, 3)],

        # BOM
        u' \xFEFF ': [('S', u' ', 1, 1),
                  ('BOM', u'\xFEFF', 1, 2), # len=3
                  ('S', u' ', 1, 5)],

        # CHAR
        u' . ': [('S', u' ', 1, 1),
                  ('CHAR', u'.', 1, 2),
                  ('S', u' ', 1, 3)],
        }


    tests2_1 = {
        # IMPORT_SYM
        u' @import ': [('S', u' ', 1, 1),
                 ('IMPORT_SYM', u'@import', 1, 2),
                 ('S', u' ', 1, 9)],
        ##u'@IMport': [('IMPORT_SYM', u'@IM\\port', 1, 1)],

        # PAGE_SYM
        u' @page ': [('S', u' ', 1, 1),
                 ('PAGE_SYM', u'@page', 1, 2),
                 ('S', u' ', 1, 7)],
        # MEDIA_SYM
        u' @media ': [('S', u' ', 1, 1),
                 ('MEDIA_SYM', u'@media', 1, 2),
                 ('S', u' ', 1, 8)],
        # FONT_FACE_SYM
        u' @font-face ': [('S', u' ', 1, 1),
                 ('FONT_FACE_SYM', u'@font-face', 1, 2),
                 ('S', u' ', 1, 12)],
        # CHARSET_SYM
        u' @charset ': [('S', u' ', 1, 1),
                 ('CHARSET_SYM', u'@charset', 1, 2),
                 ('S', u' ', 1, 10)],
        u'@CHARSET': [('ATKEYWORD', u'@CHARSET', 1, 1)],
        u'@cha\\rset': [('ATKEYWORD', u'@cha\\rset', 1, 1)],

        # NAMESPACE_SYM
        u' @namespace ': [('S', u' ', 1, 1),
                 ('NAMESPACE_SYM', u'@namespace', 1, 2),
                 ('S', u' ', 1, 12)],
        # ATKEYWORD
        u' @unknown ': [('S', u' ', 1, 1),
                 ('ATKEYWORD', u'@unknown', 1, 2),
                 ('S', u' ', 1, 10)],

        # LBRACE
        u' { ': [('S', u' ', 1, 1),
                 ('LBRACE', u'{', 1, 2),
                 ('S', u' ', 1, 3)],
        # PLUS
        u' + ': [('S', u' ', 1, 1),
                 ('PLUS', u'+', 1, 2),
                 ('S', u' ', 1, 3)],
        # GREATER
        u' > ': [('S', u' ', 1, 1),
                 ('GREATER', u'>', 1, 2),
                 ('S', u' ', 1, 3)],
        # COMMA
        u' , ': [('S', u' ', 1, 1),
                 ('COMMA', u',', 1, 2),
                 ('S', u' ', 1, 3)],

        #{invalid}        {return INVALID; /* unclosed string */}

        # IMPORTANT_SYM
        u' !important ': [('S', u' ', 1, 1),
                 ('IMPORTANT_SYM', u'!important', 1, 2),
                 ('S', u' ', 1, 12)],
        u'! important': [('IMPORTANT_SYM', u'! important', 1, 1)],
        u'!\n\timportant': [('IMPORTANT_SYM', u'!\n\timportant', 1, 1)],

        # .
        u' . ': [('S', u' ', 1, 1),
                 ('CLASS', u'.', 1, 2),
                 ('S', u' ', 1, 3)],

        }


    def setUp(self):
        #log = cssutils.errorhandler.ErrorHandler()
        self.tokenizer = Tokenizer()

    def test_linenumbers(self):
        "Tokenizer line + col"
        pass

    def test_tokenizeCSS3(self):
        "Tokenizer(CSS3_MACROS, CSS3_PRODUCTIONS).tokenize()"
        tokenizer = Tokenizer(CSS3_MACROS, CSS3_PRODUCTIONS)
        tests = {}
        tests.update(self.testsall)
        tests.update(self.tests3)
        for css in tests:
            tokens = tokenizer.tokenize(css)
            for i, actual in enumerate(tokens):
                expected = tests[css][i]
                self.assertEqual(expected, actual)

    def test_tokenizeCSS2_1(self):
        "Tokenizer(CSS2_1_MACROS, CSS2_1_PRODUCTIONS).tokenize()"
        tokenizer = Tokenizer(CSS2_1_MACROS, CSS2_1_PRODUCTIONS)
        tests = {}
        tests.update(self.testsall)
        tests.update(self.tests2_1)
        for css in tests:
            tokens = tokenizer.tokenize(css)
            for i, actual in enumerate(tokens):
                expected = tests[css][i]
                self.assertEqual(expected, actual)

    def __old(self):

        tt = Token
        testsOLD = {
            u'x x1 -x .-x #_x -': [(1, 1, tt.IDENT, u'x'),
               (1, 2, 'S', u' '),
               (1, 3, tt.IDENT, u'x1'),
               (1, 5, 'S', u' '),
               (1, 6, tt.IDENT, u'-x'),
               (1, 8, 'S', u' '),
               (1, 9, tt.CLASS, u'.'),
               (1, 10, tt.IDENT, u'-x'),
               (1, 12, 'S', u' '),
               (1, 13, tt.HASH, u'#_x'),
               (1, 16, 'S', u' '),
               (1, 17, 'DELIM', u'-')],

            # num
            u'1 1.1 -1 -1.1 .1 -.1 1.': [(1, 1, tt.NUMBER, u'1'),
               (1, 2, 'S', u' '), (1, 3, tt.NUMBER, u'1.1'),
               (1, 6, 'S', u' '), (1, 7, tt.NUMBER, u'-1'),
               (1, 9, 'S', u' '), (1, 10, tt.NUMBER, u'-1.1'),
               (1, 14, 'S', u' '), (1, 15, tt.NUMBER, u'0.1'),
               (1, 17, 'S', u' '), (1, 18, tt.NUMBER, u'-0.1'),
               (1, 21, 'S', u' '),
               (1, 22, tt.NUMBER, u'1'), (1, 23, tt.CLASS, u'.')
                                         ],
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
            u'!%:&$|': [(1, 1, 'DELIM', u'!'),
               (1, 2, 'DELIM', u'%'),
               (1, 3, 'DELIM', u':'),
               (1, 4, 'DELIM', u'&'),
               (1, 5, 'DELIM', u'$'),
               (1, 6, 'DELIM', u'|')],


            # DIMENSION
            u'5em': [(1, 1, tt.DIMENSION, u'5em')],
            u' 5em': [(1, 1, 'S', u' '), (1, 2, tt.DIMENSION, u'5em')],
            u'5em ': [(1, 1, tt.DIMENSION, u'5em'), (1, 4, 'S', u' ')],

            u'-5em': [(1, 1, tt.DIMENSION, u'-5em')],
            u' -5em': [(1, 1, 'S', u' '), (1, 2, tt.DIMENSION, u'-5em')],
            u'-5em ': [(1, 1, tt.DIMENSION, u'-5em'), (1, 5, 'S', u' ')],

            u'.5em': [(1, 1, tt.DIMENSION, u'0.5em')],
            u' .5em': [(1, 1, 'S', u' '), (1, 2, tt.DIMENSION, u'0.5em')],
            u'.5em ': [(1, 1, tt.DIMENSION, u'0.5em'), (1, 5, 'S', u' ')],

            u'-.5em': [(1, 1, tt.DIMENSION, u'-0.5em')],
            u' -.5em': [(1, 1, 'S', u' '), (1, 2, tt.DIMENSION, u'-0.5em')],
            u'-.5em ': [(1, 1, tt.DIMENSION, u'-0.5em'), (1, 6, 'S', u' ')],

            u'5em5_-': [(1, 1, tt.DIMENSION, u'5em5_-')],

            u'a a5 a5a 5 5a 5a5': [(1, 1, tt.IDENT, u'a'),
               (1, 2, 'S', u' '),
               (1, 3, tt.IDENT, u'a5'),
               (1, 5, 'S', u' '),
               (1, 6, tt.IDENT, u'a5a'),
               (1, 9, 'S', u' '),
               (1, 10, tt.NUMBER, u'5'),
               (1, 11, 'S', u' '),
               (1, 12, tt.DIMENSION, u'5a'),
               (1, 14, 'S', u' '),
               (1, 15, tt.DIMENSION, u'5a5')],

            # URI
            u'url()': [(1, 1, tt.URI, u'url()')],
            u'url();': [(1, 1, tt.URI, u'url()'), (1, 6, tt.SEMICOLON, ';')],
            u'url("x")': [(1, 1, tt.URI, u'url("x")')],
            u'url( "x")': [(1, 1, tt.URI, u'url("x")')],
            u'url("x" )': [(1, 1, tt.URI, u'url("x")')],
            u'url( "x" )': [(1, 1, tt.URI, u'url("x")')],
            u' url("x")': [
                (1, 1, 'S', u' '),
                (1, 2, tt.URI, u'url("x")')],
            u'url("x") ': [
                (1, 1, tt.URI, u'url("x")'),
                (1, 9, 'S', u' '),
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
                (1, 6, 'S', u' '),
                (1, 7, tt.IDENT, u'b'),
                (1, 8, tt.RPARANTHESIS, u')'),
                ],

            # FUNCTION
            u' counter("x")': [
               (1,1, 'S', u' '),
               (1, 2, tt.FUNCTION, u'counter('),
               (1, 10, tt.STRING, u'"x"'),
               (1, 13, tt.RPARANTHESIS, u')')],
            # HASH
            u'# #a #_a #-a #1': [
                (1, 1, 'DELIM', u'#'),
                (1, 2, 'S', u' '),
                (1, 3, tt.HASH, u'#a'),
                (1, 5, 'S', u' '),
                (1, 6, tt.HASH, u'#_a'),
                (1, 9, 'S', u' '),
                (1, 10, tt.HASH, u'#-a'),
                (1, 13, 'S', u' '),
                (1, 14, tt.HASH, u'#1')
                ],
            u'#1a1 ': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u' '),
                ],
            u'#1a1\n': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u'\n'),
                ],
            u'#1a1{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, tt.LBRACE, u'{'),
                ],
            u'#1a1 {': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u' '),
                (1, 6, tt.LBRACE, u'{'),
                ],
            u'#1a1\n{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u'\n'),
                (2, 1, tt.LBRACE, u'{'),
                ],
            u'#1a1\n {': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u'\n '),
                (2, 2, tt.LBRACE, u'{'),
                ],
            u'#1a1 \n{': [
                (1, 1, tt.HASH, u'#1a1'),
                (1, 5, 'S', u' \n'),
                (2, 1, tt.LBRACE, u'{'),
                ],
            # STRINGS with NL
            u'"x\n': [(1,1, tt.INVALID, u'"x\n')],
            u'"x\r': [(1,1, tt.INVALID, u'"x\r')],
            u'"x\f': [(1,1, tt.INVALID, u'"x\f')],
            u'"x\n ': [
               (1,1, tt.INVALID, u'"x\n'),
               (2,1, 'S', u' ')
               ]

            }



#        tests = {
#            u'/*a': xml.dom.SyntaxErr,
#            u'"a': xml.dom.SyntaxErr,
#            u"'a": xml.dom.SyntaxErr,
#            u"\\0 a": xml.dom.SyntaxErr,
#            u"\\00": xml.dom.SyntaxErr,
#            u"\\000": xml.dom.SyntaxErr,
#            u"\\0000": xml.dom.SyntaxErr,
#            u"\\00000": xml.dom.SyntaxErr,
#            u"\\000000": xml.dom.SyntaxErr,
#            u"\\0000001": xml.dom.SyntaxErr
#            }
#        self.tokenizer.log.raiseExceptions = True #!!
#        for css, exception in tests.items():
#            self.assertRaises(exception, self.tokenizer.tokenize, css)


if __name__ == '__main__':
    import unittest
    unittest.main()
