"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
from tokenize import Tokenizer
from tokenize2 import Tokenizer as Tokenizer2

class Base(object):
    """
    Base class for most CSS and StyleSheets classes

    contains helper objects
        * _log
        * _ttypes

    and functions
        * staticmethod: _normalize(x)
        * _checkReadonly()
        * _tokenize()
        * _tokensupto()
        * _valuestr()

    for inheriting classes helping parsing
    """
    _log = cssutils.log

    __tokenizer2 = Tokenizer2()
    _pds = cssutils.tokenize2.CSSProductions

    def _tokenize2(self, textortokens, fullsheet=False):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if isinstance(textortokens, basestring):
            return self.__tokenizer2.tokenize(
                     textortokens, fullsheet=fullsheet)
        else:
            return textortokens # already tokenized

    def _type(self, token):
        "type of Tokenizer2 token"
        return token[0]

    def _value(self, token):
        "value of Tokenizer2 token"
        return token[1]

    # ----

    def _lex(self, seq, tokens, productions, default=None):
        for token in tokens:
            typ, val, lin, col = token
            p = productions.get(typ, default)
            if p is None:
                self._log.Error('Unexpected token (%s, %s, %s, %s)' % token)
            else:
                p(seq, token)

    def _S(self, seq, token):
        "default implementation for S token"
        pass

    def _COMMENT(self, seq, token):
        "default implementation for comment token"
        seq.append(cssutils.css.CSSComment([token]))

    def _EOF(self, seq, token):
        "default implementation for EOF token"
        print token

    # --- OLD ---
    __tokenizer = Tokenizer()
    _ttypes = __tokenizer.ttypes

    def _tokenize(self, textortokens, _fullSheet=False):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if isinstance(textortokens, list):
            return textortokens # already tokenized
        elif isinstance(textortokens, cssutils.token.Token):
            return [textortokens] # comment is a single token
        elif isinstance(textortokens, basestring): # already string
            return self.__tokenizer.tokenize(textortokens, _fullSheet)
        else:
            if textortokens is not None:
                textortokens = unicode(textortokens)
            return self.__tokenizer.tokenize(textortokens, _fullSheet)

    @staticmethod
    def _normalize(x):
        """
        normalizes x namely replaces any \ with the empty string
        so for x=="c\olor\" return "color"

        used in Token for normalized value and CSSStyleDeclaration
        currently
        """
        return x.replace(u'\\', u'').lower()

    def _checkReadonly(self):
        "raises xml.dom.NoModificationAllowedErr if rule/... is readonly"
        if hasattr(self, '_readonly') and self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'%s is readonly.' % self.__class__)
            return True
        return False

    def _tokensupto(self, tokens,
                    blockstartonly=False,
                    blockendonly=False,
                    propertynameendonly=False,
                    propertyvalueendonly=False,
                    propertypriorityendonly=False,
                    selectorattendonly=False,
                    funcendonly=False):
        """
        returns tokens upto end of atrule and end index
        end is defined by parameters, might be ; } ) or other

        default looks for ending "}" and ";"
        """
        ends = u';}'

        if blockstartonly: # {
            ends = u'{'
        if blockendonly: # }
            ends = u'}'
        elif propertynameendonly: # : and ; in case of an error
            ends = u':;'
        elif propertyvalueendonly: # ; or !important
            ends = (u';', u'!important')
        elif propertypriorityendonly: # ;
            ends = u';'
        elif selectorattendonly: # ]
            ends = u']'
        elif funcendonly: # )
            ends = u')'

        brace = bracket = parant = 0 # {}, [], ()
        if blockstartonly:
            brace = -1 # set to 0 with first {
        resulttokens = []
        i, imax = 0, len(tokens)
        while i < imax:
            t = tokens[i]

            if u'{' == t.value: brace += 1
            elif u'}' == t.value: brace -= 1
            if u'[' == t.value: bracket += 1
            elif u']' == t.value: bracket -= 1
            # function( or single (
            if u'(' == t.value or \
               Base._ttypes.FUNCTION == t.type: parant += 1
            elif u')' == t.value: parant -= 1

            resulttokens.append(t)

            if t.value in ends and (brace == bracket == parant == 0):
                break

            i += 1

        return resulttokens, i

    def _valuestr(self, t):
        """
        returns string value of t (t may be a string, a list of token tuples
        or a single tuple in format (type, value, line, col) or a
        tokenlist[old])
        """
        if t is None:
            return u''
        elif isinstance(t, basestring):
            return t
        elif isinstance(t, list) and isinstance(t[0], tuple):
            return u''.join([x[1] for x in t])
        elif isinstance(t, tuple): # needed?
            return self._value(t)
        else: # old
            return u''.join([x.value for x in t])

