#!/usr/bin/env python
"""
Classes used by Tokenizer and Parser
"""
__all__ = ['Token', 'Tokenre']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2 $LastChangedRevision$'

import re
import util


class Token(object):
    """
    constants for Tokenizer and Parser to use
    values are just identifiers!

    a CSS Token consisting of
    
    line
        startline of the token
    col
        startcol of the token
    type
        of the token
    value
        literal value of the token including backslashes
    normalvalue
        normalized value of the token

        - no ``\`` like ``c\olor``
        - for type Token.S normalvalue is always u' ' - a single space
        - lowercase
        
    literal
        REMOVED in 0.9.1 (literal value of the token including backslashes)

    So e.g. a token t might initialized with::

        t = Token(1, 1, Token.IDENT, u'c\olor')

    resulting in a token with attributes::

        t.line == 1 
        t.col == 1
        t.type == Token.IDENT
        t.value == u'c\olor'
        t.normalvalue == u'color'

    includes some CSS3 parts
        http://www.w3.org/TR/css3-selectors/
    """
    IDENT = u'{ident}'

    ATKEYWORD = u'@{ident}'
    IMPORT_SYM = u'@import'
    PAGE_SYM = u'@page' # not used
    MEDIA_SYM = u'@media'
    CHARSET_SYM = u'@charset'
    NAMESPACE_SYM = u'@namespace'
    
    STRING = u'{string}'
    HASH = u'HASH #{name}'  
    NUMBER = u'{num}'
    PERCENTAGE = u'PERCENTAGE {num}%'
    DIMENSION = u'DIMENSION {num}{ident}'
    # TODO
    URI = u'url\({w}{string}{w}\)|url\({w}([!#$%&*-~]|{nonascii}|{escape})*{w}\)'
    # TODO?
    UNICODE_RANGE = u'U\+[0-9A-F?]{1,6}(-[0-9A-F]{1,6})?'
    CDO = u'<!--'
    CDC = u'-->'
    SEMICOLON = u';'
    LBRACE = u'{'
    RBRACE = u'}'
    LBRACKET = u'['
    RBRACKET = u']'
    LPARANTHESIS = u'('
    RPARANTHESIS = u')'
    S = u'[ \t\r\n\f]+'
    COMMENT = u'COMMENT' # no comment between !important but S ist handled
    FUNCTION = u'{ident}\('

    IMPORTANT_SYM = u'!{w}important'

    DELIM = u'DELIM'   

    UNIVERSAL = u'*'
    CLASS = u'.'

    # combinators
    GREATER = u'>'
    PLUS = u'+'
    TILDE = u'~'

    # atts:
    INCLUDES = u'~='
    DASHMATCH = u'|='
    # CSS3
    PREFIXMATCH = u'^=' 
    SUFFIXMATCH = u'$='
    SUBSTRINGMATCH = u'*='
    PSEUDO_ELEMENT = u'::'

    # TODO?
    INVALID = u'INVALID'
    #{invalid}        return INVALID;

    COMMA = u',' # TODO!
    #EQUALS = u'='
    #DASH = u'-'
    #PIPE = u'|'
    #":not("          return NOT;


    def __init__(self, line=1, col=1, type=None, value=u''):
        self.line = line
        self.col = col
        self.type = type
        self.value = value


    def _getvalue(self):
        return self._value
    
    def _setvalue(self, value):
        if self.type == Token.S:
            self.normalvalue = u' '
            self._value = value
            
        elif self.type == Token.IDENT:
            self.normalvalue = util.Base._normalize(value)
            self._value = value
            
        else:
            self.normalvalue = self._value = value

    value = property(_getvalue, _setvalue,
                     doc='value and normalized value')

    
    def __eq__(self, token):
        """ 
        how to compare a token to another 
        """
        if self.line == token.line and\
                       self.col == token.col and\
                       self.type == token.type and\
                       self.value == token.value:
            return True
        else:
            return False

    def __repr__(self):
        """ 
        string representation of Token 
        """
        return u'%03d:%03d %s: %s' % (
            self.line, self.col, self.type, self.value)



class Tokenre(object):
    """
    regexes for CSS tokens, on initialization all attributes will
    be compiled to re.match objects
    """
    # custom
    DIMENSION = r'{num}{ident}'
    HASH = r'#{name}'
    URI = u'url\({w}{string}{w}\)|url\({w}([!#$%&*-~]|{nonascii}|{escape})*{w}\)'
    
    # see spec
    atkeyword = r'^@[-]?{nmstart}{nmchar}*' #?
    ident = r'[-]?{nmstart}{nmchar}*'
    name = r'{nmchar}+'
    nmstart = r'[_a-z]|{nonascii}|{escape}'
    nonascii = r'[^\0-\177]'
    unicode = r'\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?'
    escape = r'{unicode}|\\[ -~\200-\777]'
    #    escape = r'{unicode}|\\[ -~\200-\4177777]'
    int = r'[-]?\d+'
    nmchar = r'[\w-]|{nonascii}|{escape}'
    num = r'[-]?\d+|\d*\.\d+'
    number = r'{num}'
    string = r'{string1}|{string2}'
    string1 = r'"(\\\"|[^\"])*"'
    string2 = r"'(\\\'|[^\'])*'"
    nl = r'\n|\r\n|\r|\f'
    w = r'\s*'

    def __init__(self):
        """ 
        compile class attribute values to re.match objects 
        """
        res = {}
        for x in dir(self):
            v = self.__getattribute__(x)
            if isinstance(v, basestring) and not x.startswith('_'):
                res[x] = v
            
        self._compile_regexes(self._expand_macros(res))
        
    def _expand_macros(self, tokdict):
        """ 
        Expand macros in token dictionary 
        """
        def macro_value(m):
            return '(?:%s)' % res[m.groupdict()['macro']]

        # copy for macros
        res = tokdict.copy() 
        for key, value in tokdict.items():
            while re.search(r'{[a-z][a-z0-9-]*}', value):
                value = re.sub(r'{(?P<macro>[a-z][a-z0-9-]*)}', 
                               macro_value, value)
            tokdict[key] = value
        return tokdict

    def _compile_regexes(self, tokdict):
        """ 
        Compile all regular expressions into callable objects 
        """
        for key, value in tokdict.items():
            self.__setattr__(key, re.compile('^%s$' % value, re.I).match)


if __name__ == '__main__':
    t = Token()
    print t
