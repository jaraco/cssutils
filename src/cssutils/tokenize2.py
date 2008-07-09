#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""New CSS Tokenizer (a generator)
"""
__all__ = ['Tokenizer', 'CSSProductions']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'
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
    _atkeywords = {
        u'@font-face': 'FONT_FACE_SYM',
        u'@import': 'IMPORT_SYM',
        u'@media': 'MEDIA_SYM',        
        u'@namespace': 'NAMESPACE_SYM',
        u'@page': 'PAGE_SYM'
        }
    _linesep = u'\n'
    
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
                self._expand_macros(macros, 
                                    productions))
        self.commentmatcher = [x[1] for x in self.tokenmatches if x[0] == 'COMMENT'][0]
        self.urimatcher = [x[1] for x in self.tokenmatches if x[0] == 'URI'][0]
        self.unicodesub = re.compile(r'\\[0-9a-fA-F]{1,6}(?:\r\n|[\t|\r|\n|\f|\x20])?').sub

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

    def tokenize(self, text, fullsheet=False):
        """Generator: Tokenize text and yield tokens, each token is a tuple 
        of::
        
            (nname, value, line, col)
        
        The token value will contain a normal string, meaning CSS unicode 
        escapes have been resolved to normal characters. The serializer
        escapes needed characters back to unicode escapes depending on
        the stylesheet target encoding.

        text
            to be tokenized
        fullsheet
            if ``True`` appends EOF token as last one and completes incomplete
            COMMENT tokens
        """
        def repl(m):
            "used by unicodesub"
            num = int(m.group(0)[1:], 16)
            if num < 0x10000:
                return unichr(num)
            else:
                return m.group(0)

        def normalize(value):
            "normalize and do unicodesub"
            return util.Base._normalize(self.unicodesub(repl, value))

        line = col = 1
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

                match = matcher(text) # if no match next one is tried
                if match:
                    found = match.group(0) # needed later for line/col

                    if fullsheet:                        
                        # check if tokens may be completed for a full token
                        if 'INVALID' == name and text == found:
                            # complete INVALID to STRING with start char " or '
                            name, found = 'STRING', '%s%s' % (found, found[0])
                        
                        elif 'FUNCTION' == name and\
                             u'url(' == normalize(found):
                            # FUNCTION url( is fixed to URI if fullsheet
                            # FUNCTION production MUST BE after URI production!
                            for end in (u"')", u'")', u')'):
                                possibleuri = '%s%s' % (text, end)
                                match = self.urimatcher(possibleuri)
                                if match:
                                    name, found = 'URI', match.group(0)
                                    break

                    if name in ('DIMENSION', 'IDENT', 'STRING', 'URI', 
                                'HASH', 'COMMENT', 'FUNCTION', 'INVALID'):
                        # may contain unicode escape, replace with normal char
                        # but do not normalize (?)
                        value = self.unicodesub(repl, found)

                    else:
                        if 'ATKEYWORD' == name:
                            # all @x are ATKEYWORD upto here
                            # but do no normalize value!
                            name = self._atkeywords.get(normalize(found), 'ATKEYWORD')

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
