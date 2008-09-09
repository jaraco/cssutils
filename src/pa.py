# -*- coding: utf-8 -*-
from pprint import pprint as pp
import logging
import sys
import cssutils


class ParseException(Exception):
    pass

class ParseBase(object):
    """Base class for parsing classes"""
    def __repr__(self):
        props = []
        for k in self.__dict__:
            props.append('%s=%r' % (k, self.__getattribute__(k)))
        return u'%s(%s)' % (self.__class__.__name__, u', '.join(props))

class Choice(ParseBase):
    """Choice of different productions"""
    def __init__(self, prods=None):
        """
        prods
            Prod or Sequence objects
        """
        self.prods = prods

    def nextProd(self, token=None):
        """Return next matching prod or sequence or raise ParseException.
        Any one in prod may match."""
        if not token:
            # called when probably done
            return None
        for x in self.prods:
            if isinstance(x, Prod):
                test = x
            else:
                # nested Sequence matches if 1st prod matches
                test = x.first()
            try:
                if test.matches(token):
                    return x
            except ParseException, e:
                # do not raise if other my match
                continue
        else:
            # None matched
            raise ParseException('No match in choice')


class Sequence(object):
    """Sequence of Choice or Prod objects"""
    def __init__(self, sequence, minmax=None):
        """
        minmax = lambda: (1, 1)
            number of times this sequence may occur
        """
        self.sequence = sequence       
        if not minmax:
            minmax = lambda: (1, 1)
        self._min, self._max = minmax()
        
        self._number = len(self.sequence)
        self._round = 1 # 1 based!    
        self._pos = 0

    def first(self):
        """Return 1st element of Sequence, used by Choice"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self.sequence:
            if not prod.optional:
                return prod

    def currentName(self):
        """Return current element of Sequence, used by name"""
        # TODO: current impl first only if 1st if an prod!
        for prod in self.sequence[self._pos:]:
            if not prod.optional:
                return prod.name
        else:
            return 'Unknown'

    name = property(currentName, doc='Used for Error reporting')

    def nextProd(self, token=None):
        """Return next matching prod or raise ParseException."""
        while self._pos < self._number:
            x = self.sequence[self._pos]
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
            if not self._min <= self._round <= self._max: 
                raise ParseException(msg)
   
   
class Prod(ParseBase):
    """Single Prod in Sequence or Choice"""
    def __init__(self, name, match=None, toStore=None, toSeq=None,
                 optional=False):
        """
        name
            name used for error reporting
        match callback
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseException
        toStore (optional)
            key to save val to store or callback(store, val)
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
            self.toStore = toStore # toStore(store, val)
        else:
            self.toStore = self._makeSetStore(toStore)
            
        if toSeq:
            self.toSeq = toSeq # call seq.append(toSeq(value))
        else:
            self.toSeq = lambda val: val
       
    def _makeSetStore(self, key):
        "helper"
        def setStore(store, val):
            store[key] = val
        return setStore
        
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
    
    def parse(self, name, tokenizer, productions, store=None, seq=None):
        """
        tokenizer
            generating tokens
        productions
            used to parse tokens
        store  UPDATED
            prod.store should be a dict. 
            
            TODO: NEEDED? 
            Key ``raw`` is always added and holds all unprocessed 
            values found
            
        seq (optional) UPDATED
            append prods' value here
          
        returns
            :wellformed: True or False
            :token: Last token if not used to be used for new tokenizer
        """
        # contains always raw values?
        store['_raw'] = []
        prods = [productions] # a stack

        wellformed = True
        next, token = None, None # if no tokens at all
        for token in tokenizer:
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
                next = 'EOF'
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
                        prod.toStore(store, val)
                        
                    if 'STOP' == next:
                        # stop here and ignore following tokens
                        token = None
                        break
        while True:
            # not all needed productions done?
            prod = prods[-1].nextProd()
            if hasattr(prod, 'optional') and prod.optional:
                # ignore optional ones
                continue
            
            if prod:
                self._log.error(u'%s: Missing token for production %r' 
                                % (name, prod.name)) 
            elif not prod:
                if len(prods) > 1:
                    # nested exhausted, next in parent
                    prods.pop()
                else:
                    break
    
        return wellformed, token    




types = cssutils.cssproductions.CSSProductions

# PRODUCTION FOR CSSColor
# sign + or -
sign = Prod(name='sign +-', match=lambda t, v: v in u'+-',
            optional=True)

def makeAppendStore(key):
    def appendStore(store, val):
        "helper"
        store[key].append(val)
    return appendStore

# value NUMBER or PERCENTAGE
value = Prod(name='value', 
             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
             toSeq=cssutils.css.CSSPrimitiveValue,
             toStore=makeAppendStore('test'))
comma = Prod(name='comma', match=lambda t, v: v == u',')
endfunc = Prod(name='end FUNC ")"', match=lambda t, v: v == u')')

# COLOR PRODUCTION
_funccolor = Sequence([
    Prod(name='FUNC', match=lambda t, v: v in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION, 
         toStore='colorType' ),
    sign,
    value,
    # more values starting with Comma
    Sequence([# comma , 
              comma,
              sign, 
              value
             ], 
             minmax=lambda: (2, 2)
    ),
    # end of FUNCTION )
    endfunc
 ])
colorproductions = Choice([_funccolor,
                      Prod(name='HEX color', 
                           match=lambda t, v: t == types.HASH and 
                            len(v) == 4 or len(v) == 7,
                           toSeq=cssutils.css.CSSPrimitiveValue),
                      Prod(name='named color', match=lambda t, v: t == types.IDENT,
                           toSeq=cssutils.css.CSSPrimitiveValue),
                      ]
    )

# ----

# PRODUCTION FOR Rect
rectvalue = Prod(name='value in rect()', 
                 match=lambda t, v: t in (types.DIMENSION,) or\
                    str(v) in ('auto', '0'), 
                 toSeq=cssutils.css.CSSPrimitiveValue)
rectproductions = Sequence([Prod(name='FUNC rect(', 
                                 match=lambda t, v: v == u'rect('),  #normalized!
                            rectvalue,
                            Sequence([comma, 
                                      rectvalue], minmax=lambda: (3,3)),
                            endfunc 
                            ])

# tokenize    

text = 'hsl(1,2,3)'#rgb(1%,   \n2% , -3.0%)'
name = u'CSSColor'
productions = colorproductions
tokens = cssutils.tokenize2.Tokenizer().tokenize(text)

# parse
# RESULT: colorType filled, in test all values
store = {'test': []
         #'colorType': '', # rgb, rgba, hsl, hsla, name, hash, ?
         }
seq = cssutils.util.Seq(readonly=False)
wellformed, token = ProdsParser().parse(name,
                                               tokens, 
                                               productions, 
                                               seq=seq, 
                                               store=store)

print
print '- STORE:', store
print '- WELLFORMED:', wellformed
print '- TOKENIZER: ', list(tokens)
pp(seq)
