#!/usr/bin/env python
"""New CSS Tokenizer (a generator)

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
__all__ = ['Tokenizer', 'CSSProductions']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:55:42 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 300 $'

import os
import re
import string
import xml.dom
import cssutils
from cssproductions import *

class Tokenizer(object):
    """
    generates a list of Token tuples:
        (Tokenname, value, startline, startcolumn)
    """
    nl = os.linesep

    def __init__(self, macros=None, productions=None):
        """
        inits tokenizer with given macros and productions which default to
        cssutils own macros and productions
        """
        self.log = cssutils.log
        if not macros:
            macros = MACROS
        if not productions:
            productions = PRODUCTIONS
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
        generator: tokenizes text and yiels tokens, each token is a tuple of
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
                    yield (name, found, line, col)
                    text = text[len(found):]
                    nls = found.count(linesep)
                    line += nls
                    if nls:
                        col = len(found[found.rfind(linesep):])
                    else:
                        col += len(found)
                    break

            else:
                if text.startswith('"') or text.startswith("'"):
                    yield ('STRING', text + text[0], line, col)
                    text = ''
                else:
                    raise xml.dom.SyntaxErr('no token match "%s(...)"' % text[:10])
                    text = text[1:]

        if fullsheet:
            yield ('EOF', None, line, col)


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
    from css2productions import *
    tokens = Tokenizer(MACROS, PRODUCTIONS).tokenize(css, '\n')
    for token in tokens:
        print token
