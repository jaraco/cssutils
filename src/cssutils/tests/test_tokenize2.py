# -*- coding: utf-8 -*-
"""testcases for new cssutils.tokenize.Tokenizer

TODO:
    - escape ends with explicit space but \r\n as single space
    - ur'"\""': [('STRING', ur'"\""', 1, 1)],
    - font-face with escaped "-"

    + old tests as new ones are **not complete**!
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:56:36 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 302 $'

import xml.dom
import basetest
from cssutils.tokenize2 import *
from cssutils.token import Token

class TokenizerTestCase(basetest.BaseTestCase):

    testsall = {
        u'äöüß€': [('IDENT', u'äöüß€', 1, 1)],

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
        u" '' ": [('S', u' ', 1, 1),
                 ('STRING', u"''", 1, 2),
                 ('S', u' ', 1, 4)],
        # TODO:
        #u'"\\" "': [('STRING', u'"\\" "', 1, 1)],

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

        u' -0 ': [('S', u' ', 1, 1),
                 ('CHAR', u'-', 1, 2),
                 ('NUMBER', u'0', 1, 3),
                 ('S', u' ', 1, 4)],
        # for plus see CSS3


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

        # --- overwritten for CSS 2.1 ---
        # LBRACE
        u' { ': [('S', u' ', 1, 1),
                 ('CHAR', u'{', 1, 2),
                 ('S', u' ', 1, 3)],
        # PLUS
        u' + ': [('S', u' ', 1, 1),
                 ('CHAR', u'+', 1, 2),
                 ('S', u' ', 1, 3)],
        # GREATER
        u' > ': [('S', u' ', 1, 1),
                 ('CHAR', u'>', 1, 2),
                 ('S', u' ', 1, 3)],
        # COMMA
        u' , ': [('S', u' ', 1, 1),
                 ('CHAR', u',', 1, 2),
                 ('S', u' ', 1, 3)],

        # class
        u' . ': [('S', u' ', 1, 1),
                  ('CHAR', u'.', 1, 2),
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

        # NUMBER
        u' - 0 ': [('S', u' ', 1, 1),
                 ('CHAR', u'-', 1, 2),
                 ('S', u' ', 1, 3),
                 ('NUMBER', u'0', 1, 4),
                 ('S', u' ', 1, 5)],
        u' + 0 ': [('S', u' ', 1, 1),
                 ('CHAR', u'+', 1, 2),
                 ('S', u' ', 1, 3),
                 ('NUMBER', u'0', 1, 4),
                 ('S', u' ', 1, 5)],

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

        }

    tests2 = {
        # escapes work not for a-f!
        # IMPORT_SYM
        u' @import ': [('S', u' ', 1, 1),
                 ('IMPORT_SYM', u'@import', 1, 2),
                 ('S', u' ', 1, 9)],
        u'@IMPORT': [('IMPORT_SYM', u'@IMPORT', 1, 1)],
        ur'@\i\m\p\o\r\t': [('IMPORT_SYM', ur'@\i\m\p\o\r\t', 1, 1)],
        ur'@\I\M\P\O\R\T': [('IMPORT_SYM', ur'@\I\M\P\O\R\T', 1, 1)],
        ur'@\49 \04d\0050\0004f\000052\54': [('IMPORT_SYM',
                                        ur'@\49 \04d\0050\0004f\000052\54',
                                        1, 1)],
        ur'@\69 \06d\0070\0006f\000072\74': [('IMPORT_SYM',
                                        ur'@\69 \06d\0070\0006f\000072\74',
                                        1, 1)],

        # PAGE_SYM
        u' @page ': [('S', u' ', 1, 1),
                 ('PAGE_SYM', u'@page', 1, 2),
                 ('S', u' ', 1, 7)],
        u'@PAGE': [('PAGE_SYM', u'@PAGE', 1, 1)],
        ur'@\pa\ge': [('PAGE_SYM', ur'@\pa\ge', 1, 1)],
        ur'@\PA\GE': [('PAGE_SYM', ur'@\PA\GE', 1, 1)],
        ur'@\50\41\47\45': [('PAGE_SYM', ur'@\50\41\47\45', 1, 1)],
        ur'@\70\61\67\65': [('PAGE_SYM', ur'@\70\61\67\65', 1, 1)],

        # MEDIA_SYM
        u' @media ': [('S', u' ', 1, 1),
                 ('MEDIA_SYM', u'@media', 1, 2),
                 ('S', u' ', 1, 8)],
        u'@MEDIA': [('MEDIA_SYM', u'@MEDIA', 1, 1)],
        ur'@\med\ia': [('MEDIA_SYM', ur'@\med\ia', 1, 1)],
        ur'@\MED\IA': [('MEDIA_SYM', ur'@\MED\IA', 1, 1)],
        u'@\\4d\n\\45\r\\44\t\\49\r\n\\41\f': [('MEDIA_SYM',
                                        u'@\\4d\n\\45\r\\44\t\\49\r\n\\41\f',
                                        1, 1)],
        u'@\\6d\n\\65\r\\64\t\\69\r\n\\61\f': [('MEDIA_SYM',
                                        u'@\\6d\n\\65\r\\64\t\\69\r\n\\61\f',
                                        1, 1)],

        # FONT_FACE_SYM
        u' @font-face ': [('S', u' ', 1, 1),
                 ('FONT_FACE_SYM', u'@font-face', 1, 2),
                 ('S', u' ', 1, 12)],
        u'@FONT-FACE': [('FONT_FACE_SYM', u'@FONT-FACE', 1, 1)],
        ur'@f\o\n\t\-face': [('FONT_FACE_SYM', ur'@f\o\n\t\-face', 1, 1)],
        ur'@F\O\N\T\-FACE': [('FONT_FACE_SYM', ur'@F\O\N\T\-FACE', 1, 1)],
        # TODO: "-" as hex!
        ur'@\46\4f\4e\54\-\46\41\43\45': [('FONT_FACE_SYM',
            ur'@\46\4f\4e\54\-\46\41\43\45', 1, 1)],
        ur'@\66\6f\6e\74\-\66\61\63\65': [('FONT_FACE_SYM',
            ur'@\66\6f\6e\74\-\66\61\63\65', 1, 1)],

        # CHARSET_SYM only if "@charset"!
        u' @charset ': [('S', u' ', 1, 1),
                 ('CHARSET_SYM', u'@charset', 1, 2),
                 ('S', u' ', 1, 10)],
        u'@CHARSET': [('ATKEYWORD', u'@CHARSET', 1, 1)],
        u'@cha\\rset': [('ATKEYWORD', u'@cha\\rset', 1, 1)],

        # NAMESPACE_SYM
        u' @namespace ': [('S', u' ', 1, 1),
                 ('NAMESPACE_SYM', u'@namespace', 1, 2),
                 ('S', u' ', 1, 12)],
        ur'@NAMESPACE': [('NAMESPACE_SYM', ur'@NAMESPACE', 1, 1)],
        ur'@\na\me\s\pace': [('NAMESPACE_SYM', ur'@\na\me\s\pace', 1, 1)],
        ur'@\NA\ME\S\PACE': [('NAMESPACE_SYM', ur'@\NA\ME\S\PACE', 1, 1)],
        ur'@\4e\41\4d\45\53\50\41\43\45': [('NAMESPACE_SYM',
            ur'@\4e\41\4d\45\53\50\41\43\45', 1, 1)],
        ur'@\6e\61\6d\65\73\70\61\63\65': [('NAMESPACE_SYM',
            ur'@\6e\61\6d\65\73\70\61\63\65', 1, 1)],

        # ATKEYWORD
        u' @unknown ': [('S', u' ', 1, 1),
                 ('ATKEYWORD', u'@unknown', 1, 2),
                 ('S', u' ', 1, 10)],

        # STRING
        # strings with linebreak in it
        u' "\\na"\na': [('S', u' ', 1, 1),
                   ('STRING', u'"\\na"', 1, 2),
                   ('S', u'\n', 1, 7),
                   ('IDENT', u'a', 1, 8)],
        u" '\\na'\na": [('S', u' ', 1, 1),
                   ('STRING', u"'\\na'", 1, 2),
                   ('S', u'\n', 1, 7),
                   ('IDENT', u'a', 1, 8)],
        u' "\\r\\n\\t\\f\\n\\ra"a': [('S', u' ', 1, 1),
                   ('STRING', u'"\\r\\n\\t\\f\\n\\ra"', 1, 2),
                   ('IDENT', u'a', 1, 17)],

        # INVALID (STRING)
        u' " ': [('S', u' ', 1, 1),
                 ('INVALID', u'" ', 1, 2)],
        u" 'abc\"with quote\" in it": [('S', u' ', 1, 1),
                 ('INVALID', u"'abc\"with quote\" in it", 1, 2)],
        u' "\na': [('S', u' ', 1, 1),
                   ('INVALID', u'"', 1, 2),
                   ('S', u'\n', 1, 3),
                   ('IDENT', u'a', 1, 4)],
        # strings with linebreak in it
        u' "\\na\na': [('S', u' ', 1, 1),
                   ('INVALID', u'"\\na', 1, 2),
                   ('S', u'\n', 1, 6),
                   ('IDENT', u'a', 1, 7)],
        u' "\\r\\n\\t\\f\\n\\ra\na': [('S', u' ', 1, 1),
                   ('INVALID', u'"\\r\\n\\t\\f\\n\\ra', 1, 2),
                   ('S', u'\n', 1, 16),
                   ('IDENT', u'a', 1, 17)],

        # IMPORTANT_SYM is not IDENT!!!
        u' !important ': [('S', u' ', 1, 1),
                ('CHAR', u'!', 1, 2),
                 ('IDENT', u'important', 1, 3),
                 ('S', u' ', 1, 12)],
        u'! /*1*/ important ': [
                ('CHAR', u'!', 1, 1),
                ('S', u' ', 1, 2),
                ('COMMENT', u'/*1*/', 1, 3),
                ('S', u' ', 1, 8),
                 ('IDENT', u'important', 1, 9),
                 ('S', u' ', 1, 18)],
        u'! important': [('CHAR', u'!', 1, 1),
                         ('S', u' ', 1, 2),
                         ('IDENT', u'important', 1, 3)],
        u'!\n\timportant': [('CHAR', u'!', 1, 1),
                            ('S', u'\n\t', 1, 2),
                            ('IDENT', u'important', 1, 4)],
        u'!IMPORTANT': [('CHAR', u'!', 1, 1),
                        ('IDENT', u'IMPORTANT', 1, 2)],
        ur'!\i\m\p\o\r\ta\n\t': [('CHAR', u'!', 1, 1),
                                 ('IDENT',
                                  ur'\i\m\p\o\r\ta\n\t', 1, 2)],
        ur'!\I\M\P\O\R\Ta\N\T': [('CHAR', u'!', 1, 1),
                                 ('IDENT',
                                  ur'\I\M\P\O\R\Ta\N\T', 1, 2)],
        ur'!\49\4d\50\4f\52\54\41\4e\54': [('CHAR', u'!', 1, 1),
                                           ('IDENT',
                                            ur'\49\4d\50\4f\52\54\41\4e\54',
                                            1, 2)],
        ur'!\69\6d\70\6f\72\74\61\6e\74': [('CHAR', u'!', 1, 1),
                                           ('IDENT',
                                            ur'\69\6d\70\6f\72\74\61\6e\74',
                                            1, 2)],
        }

    tests2only = {
        # --- overwriting ---
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
        # class
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

    def test_tokenize(self):
        "cssutils Tokenizer().tokenize()"
        import cssutils.cssproductions
        tokenizer = Tokenizer(cssutils.cssproductions.MACROS,
                              cssutils.cssproductions.PRODUCTIONS)
        tests = {}
        tests.update(self.testsall)
        tests.update(self.tests2)
        tests.update(self.tests3)
        for css in tests:
            # check token format
            tokens = tokenizer.tokenize(css)
            for i, actual in enumerate(tokens):
                expected = tests[css][i]
                self.assertEqual(expected, actual)

            # check if all same number of tokens
            tokens = [t for t in tokenizer.tokenize(css)]
            self.assertEqual(len(tokens), len(tests[css]))

    def test_tokenizeCSS3(self):
        "CSS3 Tokenizer().tokenize()"
        import cssutils.css3productions
        tokenizer = Tokenizer(cssutils.css3productions.MACROS,
                              cssutils.css3productions.PRODUCTIONS)
        tests = {}
        tests.update(self.testsall)
        tests.update(self.tests3)
        for css in tests:
            tokens = tokenizer.tokenize(css)
            for i, actual in enumerate(tokens):
                expected = tests[css][i]
                self.assertEqual(expected, actual)

    def test_tokenizeCSS2_1(self):
        "CSS2 Tokenizer().tokenize()"
        import cssutils.css2productions
        tokenizer = Tokenizer(cssutils.css2productions.MACROS,
                              cssutils.css2productions.PRODUCTIONS)
        tests = {}
        tests.update(self.testsall)
        #tests.update(self.tests2)
        tests.update(self.tests2only)
        for css in tests:
            tokens = tokenizer.tokenize(css)
            for i, actual in enumerate(tokens):
                expected = tests[css][i]
                self.assertEqual(expected, actual)

    # --------------

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
