#!/usr/bin/env python
"""New CSS Tokenizer

CSS2_1_MACROS and CSS2_1_PRODUCTIONS are from both
http://www.w3.org/TR/CSS21/grammar.html and
http://www.w3.org/TR/css3-syntax/#grammar0

changes
    - numbers contain "-" if present
    - F is missing from spec

CSS3_MACROS and CSS3_PRODUCTIONS are from http://www.w3.org/TR/css3-syntax

    - numbers contain "-" if present
    - HASH: #aaa is, #000 is not anymore,
            CSS2.1: 'nmchar': r'[_a-z0-9-]|{nonascii}|{escape}',
            CSS3: 'nmchar': r'[_a-z-]|{nonascii}|{escape}',
        ???

TODO: check selectors module tokenizer


test:
    - r'\" \('
    - r'\1 \22 \333 \4444 \55555 \666666 \777777 7 \7777777'
    - r'#abc #123'

    - longer tokens before shorter
        1px -> 1

    - escapes
        c\olor is one token?
        1p\\x = 1PX = 1px?

    - num: -0 are two tokens?

"""
__all__ = ['Tokenizer', 'CSS3_MACROS', 'CSS3_PRODUCTIONS',
                        'CSS2_1_MACROS', 'CSS2_1_PRODUCTIONS']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:55:42 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 300 $'

import os
import re
import string
import xml.dom

# option case-insensitive
CSS2_1_MACROS = {
    'h': r'[0-9a-f]',
    #'nonascii': r'[\200-\377]',
    'nonascii': r'[^\0-\177]', # CSS3
    'unicode': r'\\{h}{1,6}(\r\n|[ \t\r\n\f])?',

    'escape': r'{unicode}|\\[^\r\n\f0-9a-f]',
    'nmstart': r'[_a-zA-Z]|{nonascii}|{escape}',
    'nmchar': r'[_a-zA-Z0-9-]|{nonascii}|{escape}',
    'string1': r'\"([^\n\r\f\\"]|\\{nl}|{escape})*\"',
    'string2': r"\'([^\n\r\f\\']|\\{nl}|{escape})*\'",
    'invalid1': r'\"([^\n\r\f\\"]|\\{nl}|{escape})*',
    'invalid2': r"\'([^\n\r\f\\']|\\{nl}|{escape})*",
    'comment': r'\/\*[^*]*\*+([^/*][^*]*\*+)*\/',

    'ident':  r'[-]?{nmstart}{nmchar}*',
    'name': r'{nmchar}+',
    # CHANGED TO SPEC: added "-?"
    'num': r'-?[0-9]*\.[0-9]+|[0-9]+',
    'string': r'{string1}|{string2}',
    'invalid': r'{invalid1}|{invalid2}',
    'url': r'([!#$%&*-~]|{nonascii}|{escape})*',
    's': r'[ \t\r\n\f]+',
    'w': r'{s}?',
    'nl': r'\n|\r\n|\r|\f',
    'range': r'\?{1,6}|{h}(\?{0,5}|{h}(\?{0,4}|{h}(\?{0,3}|{h}(\?{0,2}|{h}(\??|{h})))))',

    'A': r'a|\\0{0,4}(41|61)(\r\n|[ \t\r\n\f])?',
    'C': r'c|\\0{0,4}(43|63)(\r\n|[ \t\r\n\f])?',
    'D': r'd|\\0{0,4}(44|64)(\r\n|[ \t\r\n\f])?',
    'E': r'e|\\0{0,4}(45|65)(\r\n|[ \t\r\n\f])?',
    'F': r'f|\\0{0,4}(46|66)(\r\n|[ \t\r\n\f])?',
    'G': r'g|\\0{0,4}(47|67)(\r\n|[ \t\r\n\f])?|\\g',
    'H': r'h|\\0{0,4}(48|68)(\r\n|[ \t\r\n\f])?|\\h',
    'I': r'i|\\0{0,4}(49|69)(\r\n|[ \t\r\n\f])?|\\i',
    'K': r'k|\\0{0,4}(4b|6b)(\r\n|[ \t\r\n\f])?|\\k',
    'M': r'm|\\0{0,4}(4d|6d)(\r\n|[ \t\r\n\f])?|\\m',
    'N': r'n|\\0{0,4}(4e|6e)(\r\n|[ \t\r\n\f])?|\\n',
    'O': r'o|\\0{0,4}(51|71)(\r\n|[ \t\r\n\f])?|\\o',
    'P': r'p|\\0{0,4}(50|70)(\r\n|[ \t\r\n\f])?|\\p',
    'R': r'r|\\0{0,4}(52|72)(\r\n|[ \t\r\n\f])?|\\r',
    'S': r's|\\0{0,4}(53|73)(\r\n|[ \t\r\n\f])?|\\s',
    'T': r't|\\0{0,4}(54|74)(\r\n|[ \t\r\n\f])?|\\t',
    'X': r'x|\\0{0,4}(58|78)(\r\n|[ \t\r\n\f])?|\\x',
    'Z': r'z|\\0{0,4}(5a|7a)(\r\n|[ \t\r\n\f])?|\\z',
    }

CSS2_1_PRODUCTIONS = [
    ('URI', r'url\({w}{string}{w}\)'), #"url("{w}{string}{w}")"    {return URI;}
    ('URI', r'url\({w}{url}{w}\)'), #"url("{w}{url}{w}")"    {return URI;}
    ('FUNCTION', r'{ident}\('), #{ident}"("        {return FUNCTION;}

    ('IMPORT_SYM', r'@{I}{M}{P}{O}{R}{T}'), #"@import"        {return IMPORT_SYM;}
    ('PAGE_SYM', r'@{P}{A}{G}{E}'), #"@page"            {return PAGE_SYM;}
    ('MEDIA_SYM', r'@{M}{E}{D}{I}{A}'), #"@media"        {return MEDIA_SYM;}
    ('FONT_FACE_SYM', r'@{F}{O}{N}{T}\-{F}{A}{C}{E}'), #"@font-face"        {return FONT_FACE_SYM;}

    # CHANGED TO SPEC: only @charset
    ('CHARSET_SYM', r'@charset'), #"@charset"        {return CHARSET_SYM;}

    ('NAMESPACE_SYM', r'@{N}{A}{M}{E}{S}{P}{A}{C}{E}'), #"@namespace"        {return NAMESPACE_SYM;}

    # CHANGED TO SPEC: ATKEYWORD
    ('ATKEYWORD', r'\@{ident}'),

    ('IDENT', r'{ident}'), #{ident}            {return IDENT;}
    ('STRING', r'{string}'), #{string}        {return STRING;}
    ('INVALID', r'{invalid}'), #        {return INVALID; /* unclosed string */}
    ('HASH', r'\#{name}'), #"#"{name}        {return HASH;}
    ('PERCENTAGE', r'{num}%'), #{num}%            {return PERCENTAGE;}
    ('LENGTH', r'{num}{E}{M}'), #{num}em            {return EMS;}
    ('LENGTH', r'{num}{E}{X}'), #{num}ex            {return EXS;}
    ('LENGTH', r'{num}{P}{X}'), #{num}px            {return LENGTH;}
    ('LENGTH', r'{num}{C}{M}'), #{num}cm            {return LENGTH;}
    ('LENGTH', r'{num}{M}{M}'), #{num}mm            {return LENGTH;}
    ('LENGTH', r'{num}{I}{N}'), #{num}in            {return LENGTH;}
    ('LENGTH', r'{num}{P}{T}'), #{num}pt            {return LENGTH;}
    ('LENGTH', r'{num}{P}{C}'), #{num}pc            {return LENGTH;}
    ('ANGLE', r'{num}{D}{E}{G}'), #{num}deg        {return ANGLE;}
    ('ANGLE', r'{num}{R}{A}{D}'), #{num}rad        {return ANGLE;}
    ('ANGLE', r'{num}{G}{R}{A}{D}'), #{num}grad        {return ANGLE;}
    ('TIME', r'{num}{M}{S}'), #{num}ms            {return TIME;}
    ('TIME', r'{num}{S}'), #{num}s            {return TIME;}
    ('FREQ', r'{num}{H}{Z}'), #{num}Hz            {return FREQ;}
    ('FREQ', r'{num}{K}{H}{Z}'), #{num}kHz        {return FREQ;}
    ('DIMEN', r'{num}{ident}'), #{num}{ident}        {return DIMEN;}
    ('NUMBER', r'{num}'), #{num}            {return NUMBER;}
    #('UNICODERANGE', r'U\+{range}'), #U\+{range}        {return UNICODERANGE;}
    #('UNICODERANGE', r'U\+{h}{1,6}-{h}{1,6}'), #U\+{h}{1,6}-{h}{1,6}    {return UNICODERANGE;}
    # --- CSS3 ---
    ('UNICODE-RANGE', r'[0-9A-F?]{1,6}(\-[0-9A-F]{1,6})?'),
    ('CDO', r'\<\!\-\-'), #"<!--"            {return CDO;}
    ('CDC', r'\-\-\>'), #"-->"            {return CDC;}
    ('S', r'{s}'),#		{return S;}

    # \/\*[^*]*\*+([^/*][^*]*\*+)*\/		/* ignore comments */
    # {s}+\/\*[^*]*\*+([^/*][^*]*\*+)*\/	{unput(' '); /*replace by space*/}

    ('INCLUDES', r'\~\='), #"~="			{return INCLUDES;}
    ('DASHMATCH', r'\|\='), #"|="			{return DASHMATCH;}
    ('LBRACE', r'\{'), #{w}"{"			{return LBRACE;}
    ('PLUS', r'\+'), #{w}"+"			{return PLUS;}
    ('GREATER', r'\>'), #{w}">"			{return GREATER;}
    ('COMMA', r'\,'), #{w}","			{return COMMA;}
    ('IMPORTANT_SYM', r'\!({w}|{comment})*{I}{M}{P}{O}{R}{T}{A}{N}{T}'), #"!{w}important"        {return IMPORTANT_SYM;}
    ('COMMENT', '\/\*[^*]*\*+([^/][^*]*\*+)*\/'), #    /* ignore comments */
    ('CLASS', r'\.'), #.			{return *yytext;}

    # --- CSS3! ---
    ('CHAR', r'[^"\']'),
    ]

# ===== CSS 3 =====

# a complete list of css3 macros
CSS3_MACROS = {
    'ident': r'[-]?{nmstart}{nmchar}*',
    'name': r'{nmchar}+',
    'nmstart': r'[_a-zA-Z]|{nonascii}|{escape}',
    'nonascii': r'[^\0-\177]',
    'unicode': r'\\[0-9a-f]{1,6}{wc}?',
    'escape': r'{unicode}|\\[ -~\200-\777]',
    #   'escape': r'{unicode}|\\[ -~\200-\4177777]',
    'nmchar': r'[-_a-zA-Z0-9]|{nonascii}|{escape}',

    # CHANGED TO SPEC: added "-?"
    'num': r'-?[0-9]*\.[0-9]+|[0-9]+', #r'[-]?\d+|[-]?\d*\.\d+',
    'string':  r'''\'({stringchar}|\")*\'|\"({stringchar}|\')*\"''',
    'stringchar':  r'{urlchar}| |\\{nl}',
    'urlchar':  r'[\x09\x21\x23-\x26\x27-\x7E]|{nonascii}|{escape}',
    # what if \r\n, \n matches first?
    'nl': r'\n|\r\n|\r|\f',
    'w': r'{wc}*',
    'wc': r'\t|\r|\n|\f|\x20'
    }

# The following productions are the complete list of tokens in CSS3, the productions are **ordered**:
CSS3_PRODUCTIONS = [
    ('BOM', r'\xFEFF'),
    ('URI', r'url\({w}({string}|{urlchar}*){w}\)'),
    ('FUNCTION', r'{ident}\('),
    ('ATKEYWORD', r'\@{ident}'),
    ('IDENT', r'{ident}'),
    ('STRING', r'{string}'),
    ('HASH', r'\#{name}'),
    ('PERCENTAGE', r'{num}\%'),
    ('DIMENSION', r'{num}{ident}'),
    ('NUMBER', r'{num}'),
    #???
    ('UNICODE-RANGE', r'[0-9A-F?]{1,6}(\-[0-9A-F]{1,6})?'),
    ('CDO', r'\<\!\-\-'),
    ('CDC', r'\-\-\>'),
    ('S', r'{wc}+'),
    ('INCLUDES', '\~\='),
    ('DASHMATCH', r'\|\='),
    ('PREFIXMATCH', r'\^\='),
    ('SUFFIXMATCH', r'\$\='),
    ('SUBSTRINGMATCH', r'\*\='),
    ('COMMENT', r'\/\*[^*]*\*+([^/][^*]*\*+)*\/'),
    ('CHAR', r'[^"\']'),
    ]


class Tokenizer(object):
    """
    generates a list of Token tuples:
        (Tokenname, value, startline, startcolumn)
    """
    nl = os.linesep

    def __init__(self, macros=None, productions=None):
        """
        inits tokenizer with given macros and productions which default to CSS3_MACROS and
        CSS3_PRODUCTIONS
        """
        if not macros:
            macros = CSS3_MACROS
        if not productions:
            productions = CSS3_PRODUCTIONS
        self.tokenmatches = self._compile_productions(
                self._expand_macros(macros, productions))

    def _expand_macros(self, macros, productions):
        """returns macro expanded productions, order of productions is kept"""
        def macro_value(m):
            return '(?:%s)' % macros[m.groupdict()['macro']]
        expanded = []
        for key, value in productions:
            while re.search(r'{[a-zA-Z][a-zA-Z0-9-]*}', value):
                value = re.sub(r'{(?P<macro>[a-zA-Z][a-zA-Z0-9-]*)}',
                               macro_value, value)
            expanded.append((key, value))
        return expanded

    def _compile_productions(self, expanded_productions):
        """compile productions into callable match objects, order is kept"""
        compiled = []
        for key, value in expanded_productions:
            compiled.append((key, re.compile('^(?:%s)' % value, re.U).match))
        return compiled

    def tokenize(self, text, linesep=None, fullsheet=False):
        """
        returns a list of tokens, each token is a tuple of
            (tokenname, tokenvalue, line, col)

        text
            to be tokenized
        linesep
            used to detect the linenumber, defaults to os.linesep
        fullsheet
            if ``True`` appends EOF token as last one
        """
        if not linesep:
            linesep = os.linesep
        line = col = 1

        tokens = []
        while text:
            for name, matcher in self.tokenmatches:
                match = matcher(text)
                if match:
                    found = match.group(0)
                    tokens.append((name, found, line, col))
                    text = text[len(found):]

                    nls = found.count(linesep)
                    line += nls
                    if nls:
                        col = len(found[found.rfind(linesep):])
                    else:
                        col += len(found)
                    break

            else:
                raise Exception('no token match "%s(...)"' % text[:10])
                text = text[1:]

        if fullsheet:
            tokens.append(('EOF', None, line, col))

        return tokens


if __name__ == '__main__':
    from pprint import pprint
    css = u'''@charset "utf-8";
    a {
        color: red;
        left: 1px "a string" url("a") 'string';
    }
    /** / comment */
    @media all {
        x+b>c#a.f {
            color: #000;
            c\olor: rgb(1,2,3)
            }
        } '''
    css = '''@import ident" string "'string'
  #hash 0px0%0 0.0 1.0 url("a") url( "a  ") url('a')func(    <!-- --> \n\f\t~=|=^=$=*=/* * / /* */ ()[{}.
    #000
    '''
    css = r'\1 \22 \333 \4444 \55555 \666666 \777777 7 \7777777'
    css = '1.1'
    tokens = Tokenizer(CSS3_MACROS, CSS3_PRODUCTIONS
                       ).tokenize(css, '\n')
    pprint(tokens)
