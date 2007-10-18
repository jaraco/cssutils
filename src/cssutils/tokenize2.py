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
        self.commentmatcher = [x[1] for x in self.tokenmatches if x[0] == 'COMMENT'][0]
        self.urimatcher = [x[1] for x in self.tokenmatches if x[0] == 'URI'][0]

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
            if ``True`` appends EOF token as last one and completes incomplete
            COMMENT tokens
        """
        if not linesep:
            linesep = os.linesep
        line = col = 1

        tokens = []
        while text:
            for name, matcher in self.tokenmatches:

                if fullsheet and name == 'CHAR' and text.startswith(u'/*'):
                    # after all tokens except CHAR have been tested
                    # test for incomplete comment
                    possiblecomment = '%s*/' % text
                    match = self.commentmatcher(possiblecomment)
                    if match:
                        yield ('COMMENT', possiblecomment, line, col)
                        text = None
                        break

                # default
                match = matcher(text)
                if match:
                    found = match.group(0)

                    if fullsheet:
                        if 'FUNCTION' == name:
                            f = found.replace('\\', '')
                            if f.startswith(u'url('):
                                # "url(" is literaland my not be URL( but u\\rl(
                                # FUNCTION url( is fixed to URI
                                # FUNCTION production MUST BE after URI production!
                                for end in (u"')", u'")', u')'):
                                    possibleuri = '%s%s' % (text, end)
                                    match = self.urimatcher(possibleuri)
                                    if match:
                                        name = 'URI'
                                        found = match.group(0)
                                        break

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
                # should not happen at all
                raise xml.dom.SyntaxErr('no token match "%s(...)"' % text[:10])
                text = text[1:]

        if fullsheet:
            yield ('EOF', u'', line, col)
