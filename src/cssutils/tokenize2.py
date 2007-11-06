#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""New CSS Tokenizer (a generator)
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
import util
from cssproductions import *

class Tokenizer(object):
    """
    generates a list of Token tuples:
        (Tokenname, value, startline, startcolumn)
    """
    _linesep = u'\n'
    
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
        self.unicodesub = re.compile(RE_UNICODE).sub

    def tokenize(self, text, fullsheet=False):
        """
        generator: tokenizes text and yiels tokens, each token is a tuple of::
        
            (tokenname, tokenvalue, line, col)
        
        The tokenvalue will contain a normal string, meaning CSS unicode 
        escapes have been resolved to normal characters. The serializer
        escapes needed characters back to unicode escapes depending of
        the stylesheet target encoding.

        text
            to be tokenized
        fullsheet
            if ``True`` appends EOF token as last one and completes incomplete
            COMMENT tokens
        """
        line = col = 1

        tokens = []
        while text:
            for name, matcher in self.tokenmatches:

                if fullsheet and name == 'CHAR' and text.startswith(u'/*'):
                    # after all tokens except CHAR have been tested
                    # test for incomplete comment
                    possiblecomment = u'%s*/' % text
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
                        # check if tokens may be completed
                        if 'INVALID' == name and text == found:
                            # complete INVALID to STRING
                            name = 'STRING'
                            found = '%s%s' % (found, found[0])
                        
                        elif 'FUNCTION' == name and\
                             u'url(' == util.Base._normalize(found):
                            # FUNCTION url( is fixed to URI if fullsheet
                            # FUNCTION production MUST BE after URI production!
                            for end in (u"')", u'")', u')'):
                                possibleuri = '%s%s' % (text, end)
                                match = self.urimatcher(possibleuri)
                                if match:
                                    name = 'URI'
                                    found = match.group(0)
                                    break

                    if name in ('URI', 'FUNCTION', 'ATKEYWORD', 'IDENT', 'STRING', 
                                'INVALID', 'HASH', 'DIMENSION', 'COMMENT'):
                        # may contain unicode escape, replace with normal char
                        def repl(m):
                            num = int(m.group(0)[1:], 16)
                            if num < 0x10000:
                                return unichr(num)
                            else:
                                return m.group(0)
                        value = self.unicodesub(repl, found)
                    else:
                        # should not contain unicodes
                        value = found

                    yield (name, value, line, col)
                    text = text[len(found):]
                    nls = found.count(self._linesep)
                    line += nls
                    if nls:
                        col = len(found[found.rfind(self._linesep):])
                    else:
                        col += len(found)
                    break

            else:
                # should not happen at all
                raise xml.dom.SyntaxErr('no token match "%s(...)"' % text[:10])
                text = text[1:]

        if fullsheet:
            yield ('EOF', u'', line, col)
