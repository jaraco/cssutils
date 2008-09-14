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
__all__ = ['ProdsParser', 'Sequence', 'Choice', 'Prod']
__docformat__ = 'restructuredtext'
__version__ = '$Id: parse.py 1418 2008-08-09 19:27:50Z cthedot $'

import cssutils

class ParseError(Exception):
    """Raised during ProdParser run internally."""
    pass


class Choice(object):
    """A Choice of productions (Sequence or single Prod)."""
    def __init__(self, prods):
        """
        prods
            Prod or Sequence objects
        """
        self._prods = prods
        self._exhausted = False

    def nextProd(self, token=None):
        """Return next matching prod or sequence or raise ParseError.
        Any one in prod may match.

        ``token`` may be None but this occurs when no tokens left."""
        if not token:
            return None

        elif not self._exhausted:
            for x in self._prods:
                if isinstance(x, Prod):
                    test = x
                else:
                    # nested Sequence matches if 1st prod matches
                    test = x.first()
                try:
                    if test.matches(token):
                        self._exhausted = True
                        return x
                except ParseError, e:
                    # do not raise if other my match
                    continue
            else:
                # None matched
                raise ParseError('No match in choice')
        else:
            # Choice is exhausted
            raise ParseError('Extra token.')


class Sequence(object):
    """A Sequence of productions (Choice or single Prod)."""
    def __init__(self, prods, minmax=None):
        """
        prods
            Prod or Sequence objects
        minmax = lambda: (1, 1)
            callback returning number of times this sequence may run
        """
        self._prods = prods
        if not minmax:
            minmax = lambda: (1, 1)
        self._min, self._max = minmax()

        self._number = len(self._prods)
        self._round = 1 # 1 based!
        self._pos = 0

    def first(self):
        """Return 1st element of Sequence, used by Choice"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self._prods:
            if not prod.optional:
                return prod

    def _currentName(self):
        """Return current element of Sequence, used by name"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self._prods[self._pos:]:
            if not prod.optional:
                return prod.name
        else:
            return 'Unknown'

    name = property(_currentName, doc='Used for Error reporting')

    def nextProd(self, token=None):
        """Return next matching prod or raise ParseError."""
        if not token:
            return None

        else:
            while self._pos < self._number:
                x = self._prods[self._pos]
                self._pos += 1

                if self._pos == self._number and self._round < self._max:
                    # new round
                    self._pos = 0
                    self._round += 1

                if isinstance(x, Prod):
                    if not token or x.matches(token):
                        # not token is probably done
                        return x
                else:
                    # nested Sequence or Choice
                    return x
            else:
                # Sequence is exhausted
                if not self._min <= self._round <= self._max:
                    raise ParseError('Extra token.')


class Prod(object):
    """Single Prod in Sequence or Choice."""
    def __init__(self, name, match=None, toSeq=None, toStore=None,
                 optional=False):
        """
        name
            name used for error reporting
        match callback
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseError
        toStore (optional)
            key to save (type, value) to store or callback(store, util.Item)
        toSeq callback (optional)
            if given calling toSeq(val) will be appended to seq
            else simply seq
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

        if callable(toStore):
            self.toStore = toStore
        elif toStore:
            self.toStore = makeToStore(toStore)
        else:
            # always set!
            self.toStore = None

        if toSeq:
            # called: seq.append(toSeq(value))
            self.toSeq = toSeq
        else:
            self.toSeq = lambda val: val

    def matches(self, token):
        """Return True, False or raise ParseError."""
        type_, val, line, col = token

        msg = None
        if not self.match(type_, val): # check type and value
            msg = u'Expected %s, wrong type or value' % self.name

        if msg and self.optional:
            return False # try next in Sequence
        elif msg:
            raise ParseError(msg)
        else:
            return True


class ProdsParser(object):
    """Productions parser."""
    def __init__(self):
        self.types = cssutils.cssproductions.CSSProductions
        self._log = cssutils.log
        self._tokenizer = cssutils.tokenize2.Tokenizer()

    def parse(self, text, name, productions, store=None):
        """
        text (or token generator)
            to parse, will be tokenized if not a generator yet
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
            :unusedtokens: token generator containing tokens not used yet
        """
        # tokenize if needed
        if isinstance(text, basestring):
            tokens = self._tokenizer.tokenize(text)
        else:
            # already tokenized, assume generator
            tokens = text

        # a new seq to append all Items to
        seq = cssutils.util.Seq(readonly=False)

        # store for specific values
        if not store:
            store = {}
        store['_raw'] = []

        # stack of productions
        prods = [productions]

        wellformed = True
        for token in tokens:
            type_, val, line, col = token
            store['_raw'].append(val)

            # default productions
            if type_ == self.types.S:
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
                        prod = prods[-1].nextProd(token)
                        if isinstance(prod, Prod):
                            break
                        elif not prod:
                            if len(prods) > 1:
                                # nested exhausted, next in parent
                                prods.pop()
                            else:
                                raise ParseError('No match found')
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
            # productions exhausted?
            prod = prods[-1].nextProd()
            try:
                if prod.optional:
                    # ignore optional ones
                    continue
            except AttributeError:
                pass

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
        return wellformed, seq, tokens
