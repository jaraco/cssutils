"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import types
import xml.dom
import cssutils
from tokenize2 import Tokenizer as Tokenizer2
# OLD
from tokenize import Tokenizer

class Seq(object):
    """
    (EXPERIMENTAL)
    a list like sequence of (value, type) used in almost all cssutils classes

    behaves almost like a list but keeps extra attribute "type" for
    each value in the list

    types are tokens types like e.g. "COMMENT" (value='/*...*/', all uppercase)
    or productions like e.g. "universal" (value='*', all lowercase)
    """
    def __init__(self):
        self.values = []
        self.types = []

    def __contains__(self, item):
        return item in self.values

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
        "returns an iterator of values only "
        return iter(self.values)

    def __len__(self):
        "same as len(list)"
        return len(self.values)

    def __repr__(self):
        "returns a repr same as a list of tuples of (value, type)"
        return u'[%s]' % u',\n '.join([u'(%r, %r)' % (value, self.types[i])
                                    for i, value in enumerate(self.values)])
    def __str__(self):
        "returns a concanated string of all values"
        items = []
        for i, value in enumerate(self.values):
            if self.types[i]:
                if self.types[i] != 'COMMENT':
                    items.append(value)
            items.append(value)
        return u''.join(items)

    def append(self, value, type=None):
        """
        same as list.append but not a simple value but a SeqItem is appended
        """
        self.values.append(value) # str(value)??? does not work if value is e.g. comment
        self.types.append(type)


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
    _prods = cssutils.tokenize2.CSSProductions

    def _newseq(self):
        return Seq()

    def _tokenize2(self, textortokens, aslist=False, fullsheet=False):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if not textortokens:
            return None
        if types.GeneratorType == type(textortokens) and not aslist:
            # already tokenized
            return textortokens
        if isinstance(textortokens, basestring):
            if aslist:
                return [t for t in self.__tokenizer2.tokenize(
                     textortokens, fullsheet=fullsheet)]
            else:
                return self.__tokenizer2.tokenize(
                     textortokens, fullsheet=fullsheet)
        elif isinstance(textortokens, tuple):
            # a single token (like a comment)
            return [textortokens]
        else:
            # already tokenized but return generator
            return (x for x in textortokens)

    def _type(self, token):
        "type of Tokenizer2 token"
        return token[0]

    def _tokenvalue(self, token, normalize=False):
        "value of Tokenizer2 token"
        if normalize:
            return Base._normalize(token[1])
        else:
            return token[1]

    def _nexttoken(self, tokenizer, default=None):
        "returns next token in generator tokenizer or the default value"
        try:
            return tokenizer.next()
        except (StopIteration, AttributeError):
            return default

    def _tokensupto2(self,
                     tokenizer,
                     starttoken=None, # not needed anymore?
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
            if self._tokenvalue(starttoken) == u'[':
                bracket = 1
        elif funcendonly: # )
            ends = u')'
            parant = 1
        elif listseponly: # ,
            ends = u','

        resulttokens = []

        # NEEDED?
        if starttoken:
            resulttokens.append(starttoken)

        if not tokenizer:
            return resulttokens
        else:
            for token in tokenizer:
                if self._type(token) == 'EOF':
                    if keepEOF and keepEnd:
                        resulttokens.append(token)
                    break
                val = self._tokenvalue(token)
                if u'{' == val: brace += 1
                elif u'}' == val: brace -= 1
                elif u'[' == val: bracket += 1
                elif u']' == val: bracket -= 1
                # function( or single (
                elif u'(' == val or \
                   Base._prods.FUNCTION == self._type(token): parant += 1
                elif u')' == val: parant -= 1
                if val in ends and (brace == bracket == parant == 0):
                    if keepEnd:
                        resulttokens.append(token)
                    break
                else:
                    resulttokens.append(token)

            return resulttokens

    def _getProductions(self, productions):
        """
        each production should return the next expected token
        normaly a name like "uri" or "EOF"
        some have no expectation like S or COMMENT, so simply return
        the current value of self.__expected
        """
        def _COMMENT(expected, seq, token, tokenizer=None):
            "default implementation for comment token"
            seq.append(cssutils.css.CSSComment([token]))
            return expected

        def _S(expected, seq, token, tokenizer=None):
            "default implementation for S token"
            return expected

        def _atrule(expected, seq, token, tokenizer=None):
            "TODO: add default impl for unexpected @rule"
            return expected

        def _EOF(expected=None, seq=None, token=None, tokenizer=None):
            "default implementation for EOF token"
            return 'EOF'

        p = {
            'COMMENT': _COMMENT,
            'S': _S,
            'ATKEYWORD': _atrule,
            'EOF': _EOF # only available if fullsheet
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

        returns (valid, expected) which the last prod might have set
        """
        valid = True

        if not tokenizer:
            return valid, expected

        prods = self._getProductions(productions)
        for token in tokenizer:
            typ, val, lin, col = token
            p = prods.get(typ, default)
            if p:
                expected = p(expected, seq, token, tokenizer)
            else:
                valid = False
                self._log.error(u'Unexpected token (%s, %s, %s, %s)' % token)

        return valid, expected

    # --- OLD ---
    __tokenizer = Tokenizer()
    _ttypes = __tokenizer.ttypes

    def _tokenize(self, textortokens, _fullSheet=False):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if isinstance(textortokens, list) and\
           isinstance(textortokens[0], tuple):
            # todo: convert tokenizer 2 list to tokenizer 1 list
            return textortokens # already tokenized


        elif isinstance(textortokens, list):
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
        normalizes x namely:

        - lowercase
        - removes any \ (TODO: check for escapes like \65)
          so for x=="c\olor\" return "color"
        """
        if x:
            return x.replace(u'\\', u'').lower()
        else:
            return x

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
        if not t:
            return u''
        elif isinstance(t, basestring):
            return t
        elif isinstance(t, list) and isinstance(t[0], tuple):
            return u''.join([x[1] for x in t])
        elif isinstance(t, tuple): # needed?
            return self._tokenvalue(t)
        else: # old
            return u''.join([x.value for x in t])


