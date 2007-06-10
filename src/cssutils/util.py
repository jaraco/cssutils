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

    
    def _tokenize(self, textortokens):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if isinstance(textortokens, list):
            return textortokens # already tokenized
        elif isinstance(textortokens, cssutils.token.Token):
            return [textortokens] # comment is a single token
        elif isinstance(textortokens, basestring):
            return self.__tokenizer.tokenize(textortokens) # already string
        else:
            if textortokens is not None:
                textortokens = unicode(textortokens)
            return self.__tokenizer.tokenize(textortokens)


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

        blockendonly
            if True only looks for ending "}" else also for ending ";"
        """
        ends = (self._ttypes.SEMICOLON, self._ttypes.RBRACE)
        endvalues = ()
        blocklevel = 0 # check only for blockend }

        if blockstartonly: # { 
            ends = (self._ttypes.LBRACE,)
            blocklevel = -1 # end is { so blocklevel gets 0
        if blockendonly: # }
            ends = (self._ttypes.RBRACE,)
        elif propertynameendonly: # : and ; in case of an error
            ends = (self._ttypes.DELIM, self._ttypes.SEMICOLON)
            endvalues = u':'
        elif propertyvalueendonly: # ; or '!important'
            ends = (self._ttypes.SEMICOLON, self._ttypes.IMPORTANT_SYM)
        elif propertypriorityendonly: # ;
            ends = (self._ttypes.SEMICOLON,)
        elif selectorattendonly: # ]
            ends = (self._ttypes.RBRACKET,)
        elif funcendonly: # )
            ends = (self._ttypes.RPARANTHESIS,)
        
        resulttokens = []
        i = 0 # if no tokens
        
        for i, t in enumerate(tokens):
            if u'{' == t.value:
                blocklevel += 1
            elif u'}' == t.value:
                blocklevel -= 1

            resulttokens.append(t)            
                
            if t.type in ends and (
                  # ":" is special case: t.type == DELIM
                  # which is NOT in ends but used anyhow
                  t.type != self._ttypes.DELIM or
                  (t.type == self._ttypes.DELIM and t.value in endvalues)
                ) and (
                  # only closed blocks except }
                  blocklevel == 0 # OR: t.value != u'}'
                ):                    
                break
            
        return resulttokens, i


    def _valuestr(self, t):
        """
        returns string value of t (t may be string of tokenlist)
        """
        if isinstance(t, basestring):
            return t
        else:
            return u''.join([x.value for x in t])
