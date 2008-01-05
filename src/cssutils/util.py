"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import re
import types
import xml.dom
import cssutils
from tokenize2 import Tokenizer

class Seq(object):
    """
    (EXPERIMENTAL)
    a list like sequence of (value, type) used in some cssutils classes
    as property ``seq``

    behaves almost like a list but keeps extra attribute "type" for
    each value in the list

    types are token types like e.g. "COMMENT" (all uppercase, value='/*...*/')
    or productions like e.g. "universal" (all lowercase, value='*')
    """
    def __init__(self):
        self.values = []
        self.types = []

    def __contains__(self, item):
        return item in self.values

    def __delitem__(self, index):
        del self.values[index]

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value_type):
        "might be set with tuple (value, type) or a single value"
        if type(value_type) == tuple:
            val = value_type[0]
            typ = value_type[1]
        else:
            val = value_type
            typ = None
        self.values[index] = val
        self.types[index] = typ

    def __iter__(self):
        "returns an iterator for values"
        return iter(self.values)

    def __len__(self):
        "same as len(list)"
        return len(self.values)

    def __repr__(self):
        "returns a repr same as a list of tuples of (value, type)"
        return u'[%s]' % u',\n '.join([u'(%r, %r)' % (value, self.types[i])
                                    for i, value in enumerate(self.values)])
    def __str__(self):
        "returns a concatated string of all values"
        items = []
        for i, value in enumerate(self.values):
            if self.types[i]:
                if self.types[i] != 'COMMENT':
                    items.append(value)
            # items.append(value)
        return u''.join(str(items))

    def _append(self, value, type=None):
        """
        same as list.append but not a simple value but a SeqItem is appended
        """
        self.values.append(value) # str(value)??? does not work if value is e.g. comment
        self.types.append(type)

    # TODO: should this be the default and the list the special case???
    def _get_values_types(self):
        return ((self.values[i], self.types[i]) for i in range(0, len(self)))
    
    _items = property(_get_values_types, 
        doc="EXPERIMENTAL: returns an iterator for (value, type) tuples")


class ListSeq(object):
    """
    (EXPERIMENTAL)
    A base class used for list classes like css.SelectorList or 
    stylesheets.MediaList

    adds list like behaviour running on inhering class' property ``seq``
    
    - item in x => bool
    - len(x) => integer
    - get, set and del x[i]
    - for item in x
    - append(item)
    
    some methods must be overwritten in inheriting class
    """
    def __init__(self):
        self.seq = [] # does not need to use ``Seq`` as simple list only

    def __contains__(self, item):
        return item in self.seq

    def __delitem__(self, index):
        del self.seq[index]

    def __getitem__(self, index):
        return self.seq[index]

    def __iter__(self):
        return iter(self.seq)

    def __len__(self):
        return len(self.seq)

    def __setitem__(self, index, item):
        "must be overwritten"
        raise NotImplementedError

    def append(self, item):
        "must be overwritten"
        raise NotImplementedError


class Base(object):
    """
    Base class for most CSS and StyleSheets classes

    Contains helper methods for inheriting classes helping parsing
    
    ``_normalize`` is static as used be Preferences.
    """
    __tokenizer2 = Tokenizer()
    _log = cssutils.log
    _prods = cssutils.tokenize2.CSSProductions

    # for more on shorthand properties see 
    # http://www.dustindiaz.com/css-shorthand/
    # format: shorthand: [(propname, mandatorycheck?)*]
    _SHORTHANDPROPERTIES = {
            u'background': [],
            u'border': [],
            u'border-left': [], 
            u'border-right': [],
            u'border-top': [], 
            u'border-bottom': [],
            u'border-color': [], 
            u'border-style': [], 
            u'border-width': [],
            u'cue': [],
            u'font': [('font-weight', True), 
                      ('font-size', True),
                      ('line-height', False), 
                      ('font-family', True)],
            u'list-style': [],
            u'margin': [],
            u'outline': [],
            u'padding': [],
            u'pause': []
            }
    
    def _newseq(self):
        # TODO: replace with data [{type, value}]
        # used by Selector but should be used by most classes
        return Seq()

    # simple escapes, all non unicodes
    __escapes = re.compile(ur'(\\[^0-9a-fA-F])').sub
    # all unicode (see cssproductions "unicode")
    __unicodes = re.compile(ur'\\[0-9a-fA-F]{1,6}[\t|\r|\n|\f|\x20]?').sub

    @staticmethod
    def _normalize(x):
        """
        normalizes x, namely:

        - remove any \ before non unicode sequences (0-9a-zA-Z) so for 
          x=="c\olor\" return "color" (unicode escape sequences should have
          been resolved by the tokenizer already)
        - lowercase
        """
        if x:
            def removeescape(matchobj):
                return matchobj.group(0)[1:]
            x = Base.__escapes(removeescape, x)
            return x.lower()        
        else:
            return x

    def _checkReadonly(self):
        "raises xml.dom.NoModificationAllowedErr if rule/... is readonly"
        if hasattr(self, '_readonly') and self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'%s is readonly.' % self.__class__)
            return True
        return False

    def _tokenize2(self, textortokens):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if not textortokens:
            return None
        elif isinstance(textortokens, basestring):
            # needs to be tokenized
            return self.__tokenizer2.tokenize(
                 textortokens)
        elif types.GeneratorType == type(textortokens):
            # already tokenized
            return textortokens
        elif isinstance(textortokens, tuple):
            # a single token (like a comment)
            return [textortokens]
        else:
            # already tokenized but return generator
            return (x for x in textortokens)

    def _nexttoken(self, tokenizer, default=None):
        "returns next token in generator tokenizer or the default value"
        try:
            return tokenizer.next()
        except (StopIteration, AttributeError):
            return default

    def _type(self, token):
        "returns type of Tokenizer token"
        if token:
            return token[0]
        else:
            return None

    def _tokenvalue(self, token, normalize=False):
        "returns value of Tokenizer token"
        if token and normalize:
            return Base._normalize(token[1])
        elif token:
            return token[1]
        else:
            return None

    def _tokensupto2(self,
                     tokenizer,
                     starttoken=None,
                     blockstartonly=False,
                     blockendonly=False,
                     mediaendonly=False,
                     semicolon=False,
                     propertynameendonly=False,
                     propertyvalueendonly=False,
                     propertypriorityendonly=False,
                     selectorattendonly=False,
                     funcendonly=False,
                     listseponly=False, # ,
                     keepEnd=True,
                     keepEOF=True):
        """
        returns tokens upto end of atrule and end index
        end is defined by parameters, might be ; } ) or other

        default looks for ending "}" and ";"
        """
        ends = u';}'
        brace = bracket = parant = 0 # {}, [], ()

        if blockstartonly: # {
            ends = u'{'
            brace = -1 # set to 0 with first {
        elif blockendonly: # }
            ends = u'}'
        elif mediaendonly: # }
            ends = u'}'
            brace = 1 # rules } and mediarules }
        elif semicolon:
            ends = u';'
        elif propertynameendonly: # : and ; in case of an error
            ends = u':;'
        elif propertyvalueendonly: # ; or !important
            ends = (u';', u'!')
        elif propertypriorityendonly: # ;
            ends = u';'
        elif selectorattendonly: # ]
            ends = u']'
            if starttoken and self._tokenvalue(starttoken) == u'[':
                bracket = 1
        elif funcendonly: # )
            ends = u')'
            parant = 1
        elif listseponly: # ,
            ends = u','

        resulttokens = []
        if starttoken:
            resulttokens.append(starttoken)
        if tokenizer:
            for token in tokenizer:
                typ, val, line, col = token
                if 'EOF' == typ:
                    if keepEOF and keepEnd:
                        resulttokens.append(token)
                    break
                if u'{' == val: 
                    brace += 1
                elif u'}' == val: 
                    brace -= 1
                elif u'[' == val: 
                    bracket += 1
                elif u']' == val: 
                    bracket -= 1
                # function( or single (
                elif u'(' == val or \
                     Base._prods.FUNCTION == typ: 
                    parant += 1
                elif u')' == val: 
                    parant -= 1
                    
                if val in ends and (brace == bracket == parant == 0):
                    if keepEnd:
                        resulttokens.append(token)
                    break
                else:
                    resulttokens.append(token)

        return resulttokens

    def _valuestr(self, t):
        """
        returns string value of t (t may be a string, a list of token tuples
        or a single tuple in format (type, value, line, col).
        Mainly used to get a string value of t for error messages.
        """
        if not t:
            return u''
        elif isinstance(t, basestring):
            return t
        else:
            return u''.join([x[1] for x in t])

    def __adddefaultproductions(self, productions):
        """
        adds default productions if not already present, used by 
        _parse only
        
        each production should return the next expected token
        normaly a name like "uri" or "EOF"
        some have no expectation like S or COMMENT, so simply return
        the current value of self.__expected
        """
        def ATKEYWORD(expected, seq, token, tokenizer=None):
            "TODO: add default impl for unexpected @rule?"
            return expected

        def COMMENT(expected, seq, token, tokenizer=None):
            "default implementation for COMMENT token adds CSSCommentRule"
            seq.append(cssutils.css.CSSComment([token]))
            return expected

        def S(expected, seq, token, tokenizer=None):
            "default implementation for S token, does nothing"
            return expected

        def EOF(expected=None, seq=None, token=None, tokenizer=None):
            "default implementation for EOF token"
            return 'EOF'

        p = {'ATKEYWORD': ATKEYWORD,
             'COMMENT': COMMENT,
             'S': S,
             'EOF': EOF # only available if fullsheet
             }
        p.update(productions)
        return p

    def _parse(self, expected, seq, tokenizer, productions, default=None):
        """
        puts parsed tokens in seq by calling a production with
            (seq, tokenizer, token)

        expected
            a name what token or value is expected next, e.g. 'uri'
        seq
            to add rules etc to
        tokenizer
            call tokenizer.next() to get next token
        productions
            callbacks {tokentype: callback}
        default
            default callback if tokentype not in productions

        returns (wellformed, expected) which the last prod might have set
        """
        wellformed = True
        if tokenizer:
            prods = self.__adddefaultproductions(productions)
            for token in tokenizer:
                p = prods.get(token[0], default)
                if p:
                    expected = p(expected, seq, token, tokenizer)
                else:
                    wellformed = False
                    self._log.error(u'Unexpected token (%s, %s, %s, %s)' % token)
                    
        return wellformed, expected


class Deprecated(object):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    It accepts a single paramter ``msg`` which is shown with the warning.
    It should contain information which function or method to use instead.
    """
    def __init__(self, msg):
        self.msg = msg

    def __call__(self, func):
        def newFunc(*args, **kwargs):
            import warnings
            warnings.warn("Call to deprecated method %r. %s" %
                            (func.__name__, self.msg),
                            category=DeprecationWarning,
                            stacklevel=2)
            return func(*args, **kwargs)
        newFunc.__name__ = func.__name__
        newFunc.__doc__ = func.__doc__
        newFunc.__dict__.update(func.__dict__)
        return newFunc
