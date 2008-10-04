# -*- coding: utf-8 -*-
"""Productions parser used by css and stylesheets classes to parse
test into a cssutils.util.Seq and at the same time retrieving
additional specific cssutils.util.Item objects for later use.

TODO:
    - ProdsParser
        - handle EOF or STOP?
        - handle unknown @rules
        - handle S: maybe save to Seq? parameterized?
        - store['_raw']: always?

    - Sequence:
        - opt first(), naive impl for now

"""
__all__ = ['ProdParser', 'Sequence', 'Choice', 'Prod', 'PreDef']
__docformat__ = 'restructuredtext'
__version__ = '$Id: parse.py 1418 2008-08-09 19:27:50Z cthedot $'

import sys
import cssutils


class ParseError(Exception):
    """Base Exception class for ProdParser (used internally)."""
    pass

class Exhausted(ParseError):
    """Raised if Sequence or Choice is done."""
    pass

class NoMatch(ParseError):
    """Raised if Sequence or Choice do not match."""
    pass

class MissingToken(ParseError):
    """Raised if Sequence or Choice are not exhausted."""
    pass


class Choice(object):
    """A Choice of productions (Sequence or single Prod)."""
    
    optional = False
    
    def __init__(self, *prods, **options):
        """
        *prods
            Prod or Sequence objects
        """
        self._prods = prods
        self.reset()

    name = property(lambda self: u'choice of (%s)' % 
                    u', '.join([x.name for x in self._prods]),
                    doc="Name shows all possible options in this choice.")

    def reset(self):
        """Start Choice from zero"""
        self._exhausted = False

    def matches(self, token):
        """Check if token matches"""
        for prod in self._prods:
            if prod.matches(token):
                return True
        return False            

    def nextProd(self, token):
        """
        Return:
        
        - next matching Prod or Sequence 
        - raises ParseError if nothing matches
        - raises Exhausted if choice already done

        ``token`` may be None but this occurs when no tokens left."""
        if not self._exhausted:
            for x in self._prods:
                if x.matches(token):
                    self._exhausted = True
                    x.reset()
                    return x
            else:
                # None matched
                raise ParseError(u'No match in choice')
        else:
            raise Exhausted(u'Extra token')


class Sequence(object):
    """A Sequence of productions (Choice or single Prod)."""
    def __init__(self, *prods, **options):
        """
        *prods
            Prod or Sequence objects
        **options:
            minmax = lambda: (1, 1)
                callback returning number of times this sequence may run
        """
        self._prods = prods
        try:
            minmax = options['minmax']
        except KeyError:
            minmax = lambda: (1, 1)

        self._min, self._max = minmax()
        if self._max is None:
            # unlimited
            self._max = sys.maxint 

        self._number = len(self._prods)
        self.reset()

    def matches(self, token):
        """Called by Choice to try to find if Sequence matches."""
        for prod in self._prods:
            if prod.matches(token):
                return True
            try:
                if not prod.optional:
                    break
            except AttributeError:
                pass
        return False
        
    def reset(self):
        """Reset this Sequence if it is nested."""
        self._round = 1 # 1 based!
        self._pos = 0

    def _currentName(self):
        """Return current element of Sequence, used by name"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self._prods[self._pos:]:
            if not prod.optional:
                return prod.name
        else:
            return 'Unknown'

    name = property(_currentName, doc='Used for Error reporting')

    optional = property(lambda self: self._min == 0)

    def nextProd(self, token):
        """Return
        
        - next matching Prod or Choice 
        - raises ParseError if nothing matches
        - raises Exhausted if sequence already done
        """
        while self._pos < self._number:
            x = self._prods[self._pos]
            thisround = self._round
            
            self._pos += 1
            if self._pos == self._number:
                if self._round < self._max:
                    # new round?
                    self._pos = 0
                    self._round += 1

            if isinstance(x, Prod):
                if not token and (x.optional or thisround > self._min):
                    # token is None if nothing expected
                    raise Exhausted()
                elif not token and not x.optional:
                    raise MissingToken(u'Missing token for production %s'
                                       % x.name)
                elif x.matches(token):
                    return x
                elif x.optional:
                    # try next 
                    continue
#                elif thisround > self._min:
#                    # minimum done
#                    self._round = self._max
#                    self._pos = self._number
#                    return None
                else:
                    # should have matched
                    raise NoMatch(u'No matching production for token')
                    
            else:
                # nested Sequence or Choice
                x.reset() # start Sequence or Choice from start
                return x
        
        # Sequence is exhausted
        if self._round >= self._max:
            raise Exhausted(u'Extra token')


class Prod(object):
    """Single Prod in Sequence or Choice."""
    def __init__(self, name, match, toSeq=None, toStore=None,
                 optional=False):
        """
        name
            name used for error reporting
        match callback
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseError
        toSeq callback (optional)
            if given calling toSeq(token) will be appended to seq
            else simply seq
        toStore (optional)
            key to save util.Item to store or callback(store, util.Item)
        optional = False
            wether Prod is optional or not
        """
        self.name = name
        self.match = match
        self.optional=optional

        def makeToStore(key):
            "Return a function used by toStore."
            def toStore(store, item):
                "Set or append store item."
                if key in store:
                    store[key].append(item)
                else:
                    store[key] = item
            return toStore

        if toSeq:
            # called: seq.append(toSeq(value))
            self.toSeq = toSeq
        else:
            self.toSeq = lambda val: val

        if callable(toStore):
            self.toStore = toStore
        elif toStore:
            self.toStore = makeToStore(toStore)
        else:
            # always set!
            self.toStore = None

    def matches(self, token):
        """Return if token matches."""
        type_, val, line, col = token
        return self.match(type_, val)

    def reset(self):
        pass

    def __repr__(self):
        return "<cssutils.prodsparser.%s object name=%r at 0x%x>" % (
                self.__class__.__name__, self.name, id(self))


class ProdParser(object):
    """Productions parser."""
    def __init__(self):
        self.types = cssutils.cssproductions.CSSProductions
        self._log = cssutils.log
        self._tokenizer = cssutils.tokenize2.Tokenizer()

    def parse(self, text, name, productions, store=None,
              defaultS=True):
        """
        text (or token generator)
            to parse, will be tokenized if not a generator yet
            
            may be:
            - a string to be tokenized
            - a single token, a tuple
            - a tuple of (token, tokensGenerator)
            - already tokenized so a tokens generator 
            
        name
            used for logging
        productions
            used to parse tokens
        store  UPDATED
            If a Prod defines ``toStore`` the key defined there
            is a key in store to be set or if store[key] is a list
            the next Item is appended here.

            TODO: NEEDED? :
            Key ``raw`` is always added and holds all unprocessed
            values found

        returns
            :wellformed: True or False
            :seq: a filled cssutils.util.Seq object which is NOT readonly yet
            :store: filled keys defined by Prod.toStore
            :unusedtokens: token generator containing tokens not used yet
        """
        if isinstance(text, basestring):
            # to tokenize
            tokens = self._tokenizer.tokenize(text)
        elif isinstance(text, tuple):
            # (token, tokens) or a single token
            if len(text) == 2:
                # (token, tokens)
                def gen(token, tokens):
                    "new generator appending token and tokens"
                    yield token
                    for t in tokens:
                        yield t
                        
                tokens = (t for t in gen(*text))
                
            else:
                # single token
                tokens = [text]
        else:
            # already tokenized, assume generator
            tokens = text

        # a new seq to append all Items to
        seq = cssutils.util.Seq(readonly=False)

        # store for specific values
        if not store:
            store = {}
#        store['_raw'] = []

        # stack of productions
        prods = [productions]

        wellformed = True
        for token in tokens:
            type_, val, line, col = token
#            store['_raw'].append(val)
            # default productions
            if defaultS and type_ == self.types.S:
                # always append S?
                seq.append(val, type_, line, col)
            elif type_ == self.types.COMMENT:
                # always append COMMENT
                seq.append(val, type_, line, col)
#            elif type_ == self.types.ATKEYWORD:
#                # @rule
#                r = cssutils.css.CSSUnknownRule(cssText=val)
#                seq.append(r, type(r), line, col)
            elif type_ == self.types.EOF:
                # do nothing
                pass
#               next = 'EOF'
            else:
                # check prods
                try:
                    while True:
                        # find next matching production
                        try:
                            prod = prods[-1].nextProd(token)
                        except (NoMatch, Exhausted), e:
                            # try next
                            prod = None
                            
                        if isinstance(prod, Prod):
                            break
                        elif not prod:
                            if len(prods) > 1:
                                # nested exhausted, next in parent
                                prods.pop()
                            else:
                                raise Exhausted('Extra token')
                        else:
                            # nested Sequence, Choice
                            prods.append(prod)

                except ParseError, e:
                    wellformed = False
                    self._log.error(u'%s: %s: %r' % (name, e, token))

                else:
                    # process prod
                    if prod.toSeq:
                        seq.append(prod.toSeq(val), type_, line, col)
                    else:
                        seq.append(val, type_, line, col)

                    if prod.toStore:
                        prod.toStore(store, seq[-1])
                        
#                    if 'STOP' == next: # EOF?
#                        # stop here and ignore following tokens
#                        break

        while True:
            # all productions exhausted?
            try:
                prod = prods[-1].nextProd(token=None)
            except Exhausted, e:
                prod = None # ok
            except (MissingToken, NoMatch), e:
                wellformed = False
                self._log.error(u'%s: %s'
                                % (name, e))
            else:
                if prod.optional:
                    # ignore optional ones
                    continue

            if prod:
                wellformed = False
                self._log.error(u'%s: Missing token for production %r'
                                % (name, prod.name))
            elif len(prods) > 1:
                # nested exhausted, next in parent
                prods.pop()
            else:
                break

        # bool, Seq, None or generator
        
        # or tokenizer.push(tokens)????
        
        return wellformed, seq, store, tokens


class PreDef(object):
    """Predefined Prod definition for use in productions definition
    for ProdParser instances.
    """ 
    types = cssutils.cssproductions.CSSProductions
    
    @staticmethod
    def CHAR(name='char', char=u','):
        "any CHAR"
        return Prod(name=name, match=lambda t, v: v in char)

    @staticmethod
    def comma():
        return PreDef.CHAR(u'comma', u',')

    @staticmethod
    def dimension():
        return Prod(name=u'dimension', 
                    match=lambda t, v: t == PreDef.types.DIMENSION)

    @staticmethod
    def function():
        return Prod(name=u'function', 
                    match=lambda t, v: t == PreDef.types.FUNCTION)

    @staticmethod
    def funcEnd():
        ")"
        return PreDef.CHAR(u'end FUNC ")"', u')')
    
    @staticmethod
    def ident():
        return Prod(name=u'ident', 
                    match=lambda t, v: t == PreDef.types.IDENT)

    @staticmethod
    def number():
        return Prod(name=u'number', 
                    match=lambda t, v: t == PreDef.types.NUMBER)

    @staticmethod
    def string():
        return Prod(name=u'string', 
                    match=lambda t, v: t == PreDef.types.STRING)

    @staticmethod
    def percentage():
        return Prod(name=u'percentage', 
                    match=lambda t, v: t == PreDef.types.PERCENTAGE)

    @staticmethod
    def S(optional=True):
        return Prod(name=u'whitespace', 
                    match=lambda t, v: t == PreDef.types.S,
                    optional=True)

    @staticmethod
    def unary(optional=True):
        "+ or -"
        return Prod(name=u'unary +-', match=lambda t, v: v in u'+-', 
                    optional=optional)            

    @staticmethod
    def uri():
        return Prod(name=u'URI', 
                    match=lambda t, v: t == PreDef.types.URI)

    @staticmethod
    def hexcolor(toStore=None):
        return Prod(name='HEX color', 
                    match=lambda t, v: t == PreDef.types.HASH and 
                                       len(v) == 4 or len(v) == 7,
                    toStore=toStore
                    )
        


