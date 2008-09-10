# -*- coding: utf-8 -*-
"""a validating CSSParser
"""
__all__ = ['ProdsParser', 'Sequence', 'Choice', 'Prod']
__docformat__ = 'restructuredtext'
__version__ = '$Id: parse.py 1418 2008-08-09 19:27:50Z cthedot $'

from pprint import pprint as pp
import cssutils

class ParseException(Exception):
    """Raised during ProdParser run"""
    pass

class ParseBase(object):
    """Base class for parsing classes"""
    def __repr__(self):
        props = []
        for k in self.__dict__:
            props.append('%s=%r' % (k, self.__getattribute__(k)))
        return u'%s(%s)' % (self.__class__.__name__, u', '.join(props))

class Choice(ParseBase):
    """A Choice of productions (Sequence or single Prod)."""
    def __init__(self, choice=None):
        """
        prods
            Prod or Sequence objects
        """
        self._choice = choice
        self._exhausted = False

    def nextProd(self, token=None):
        """Return next matching prod or sequence or raise ParseException.
        Any one in prod may match."""
        if not token:
            # called when probably done
            return None
        elif not self._exhausted:
            for x in self._choice:
                if isinstance(x, Prod):
                    test = x
                else:
                    # nested Sequence matches if 1st prod matches
                    test = x.first()
                try:
                    if test.matches(token):
                        self._exhausted = True
                        return x
                except ParseException, e:
                    # do not raise if other my match
                    continue
            else:
                # None matched
                raise ParseException('No match in choice')
        else:
            # Choice is exhausted
            raise ParseException('Extra token.')

class Sequence(object):
    """A Sequence of productions (Choice or single Prod)."""
    def __init__(self, sequence, minmax=None):
        """
        minmax = lambda: (1, 1)
            callback returning number of times this sequence may run
        """
        self._sequence = sequence       
        if not minmax:
            minmax = lambda: (1, 1)
        self._min, self._max = minmax()
        
        self._number = len(self._sequence)
        self._round = 1 # 1 based!    
        self._pos = 0

    def first(self):
        """Return 1st element of Sequence, used by Choice"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self._sequence:
            if not prod.optional:
                return prod

    def currentName(self):
        """Return current element of Sequence, used by name"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self._sequence[self._pos:]:
            if not prod.optional:
                return prod.name
        else:
            return 'Unknown'

    name = property(currentName, doc='Used for Error reporting')

    def nextProd(self, token=None):
        """Return next matching prod or raise ParseException."""
        while self._pos < self._number:
            x = self._sequence[self._pos]
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
                raise ParseException('Extra token.')
   
   
class Prod(ParseBase):
    """Single Prod in Sequence or Choice"""
    def __init__(self, name, match=None, toSeq=None, toStore=None, 
                 optional=False):
        """
        name
            name used for error reporting
        match callback
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseException
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
        
        if callable(toStore):
            self.toStore = toStore
        elif toStore:
            self.toStore = self._makeToStore(toStore)
        else:
            self.toStore = None
            
        if toSeq:
            self.toSeq = toSeq # call seq.append(toSeq(value))
        else:
            self.toSeq = lambda val: val
       
    def _makeToStore(self, key):
        "Return a function used by toStore"
        def toStore(store, item):
            "Set or append item in store"
            if key in store:
                store[key].append(item)
            else:
                store[key] = item
                
        return toStore
    
    def matches(self, token):
        """Return True, False or raise ParseException."""
        type_, val, line, col = token

        msg = None 
        if not self.match(type_, val): # check type and value
            msg = u'Expected %s, wrong type or value' % self.name

        if msg and self.optional:
            return False # try next in Sequence
        elif msg:
            raise ParseException(msg)
        else:
            return True

class ProdsParser(object):
    """Productions parser"""
    def __init__(self):
        self.types = cssutils.cssproductions.CSSProductions
        self._log = cssutils.log
        self._tokenizer = cssutils.tokenize2.Tokenizer()
    
    def parse(self, text, name, productions, store=None):
        """
        text
            to parse, will be tokenized
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
            
        seq (optional) UPDATED
            append prods' value here
          
        returns
            :wellformed: True or False
            :seq: a filled cssutils.util.Seq object which is NOT readonly yet
            :unusedtokens: token generator containing tokens not used yet
        """
        # tokenize if needed
        if isinstance(text, basestring):
            tokens = self._tokenizer.tokenize(text)
        else:
            # already tokenized, should be a generator
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
                # ignore S
                continue
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
                                raise ParseException('No match found')
                        else:
                            # nested Sequence, Choice
                            prods.append(prod)                    
                
                except ParseException, e:
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
            # not all needed productions done?
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


#
#
## PRODUCTION FOR CSSColor
#types = cssutils.cssproductions.CSSProductions
#
#sign = Prod(name='sign +-', match=lambda t, v: v in u'+-',
#            optional=True)
#value = Prod(name='value', 
#             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
#             toSeq=cssutils.css.CSSPrimitiveValue,
#             toStore='test'
#             )
#comma = Prod(name='comma', match=lambda t, v: v == u',')
#endfunc = Prod(name='end FUNC ")"', match=lambda t, v: v == u')')
#
## COLOR PRODUCTION
#_funccolor = Sequence([
#    Prod(name='FUNC', match=lambda t, v: v in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION, 
#         toStore='colorType' ),
#    sign,
#    value,
#    # more values starting with Comma
#    Sequence([# comma , 
#              comma,
#              sign, 
#              value
#             ], 
#             # should use store where colorType is saved to 
#             # define min and may, closure?
#             minmax=lambda: (2, 2)
#    ),
#    # end of FUNCTION )
#    endfunc
# ])
#colorproductions = Choice([_funccolor,
#                      Prod(name='HEX color', 
#                           match=lambda t, v: t == types.HASH and 
#                            len(v) == 4 or len(v) == 7,
#                            toSeq=cssutils.css.CSSPrimitiveValue,
#                            toStore='colorType'
#                           ),
#                      Prod(name='named color', match=lambda t, v: t == types.IDENT,
#                           toSeq=cssutils.css.CSSPrimitiveValue,
#                           toStore='colorType'),
#                      ]
#    )
#
## ----
#
## PRODUCTION FOR Rect
#rectvalue = Prod(name='value in rect()', 
#                 match=lambda t, v: t in (types.DIMENSION,) or\
#                    str(v) in ('auto', '0'), 
#                 toSeq=cssutils.css.CSSPrimitiveValue)
#rectproductions = Sequence([Prod(name='FUNC rect(', 
#                                 match=lambda t, v: v == u'rect('),  #normalized!
#                            rectvalue,
#                            Sequence([comma, 
#                                      rectvalue], minmax=lambda: (3,3)),
#                            endfunc 
#                            ])
#
## EXAMPLE
#name, productions = u'CSSColor', colorproductions
#text = 'rgb(1%,   \n2% , -3.0%)' 
## RESULT: colorType filled, in test all values
#store = {'test': [] }
#
#wellformed, seq, unusedtokens = ProdsParser().parse(text, name, productions,  
#                                                    store=store)
#
#print '- WELLFORMED:', wellformed
#print '- STORE:', store
#print '- TOKENS:', list(unusedtokens) 
#pp(seq)
