"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2 $LastChangedRevision$'

import xml.dom

from tokenize import Tokenizer

import cssutils


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
    __tokenizer = Tokenizer()

    _log = __tokenizer.log
    _ttypes = __tokenizer.ttypes

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

##        print '--- %s ---\n' % (str(ends))
##        print u''.join([x.value for x in tokens])
##        print u''.join([x.value for x in resulttokens])
##        print

        return resulttokens, i


    def _valuestr(self, t):
        """
        returns string value of t (t may be string of tokenlist)
        """
        if t is None:
            return u''
        elif isinstance(t, basestring):
            return t
        else:
            return u''.join([x.value for x in t])
