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
    """Choice between different tokens
    
    Attributes:
    
    items
        Choice, Group or Token objects
    """
    def __init__(self, items=None):
        self.items = items


class Sequence(object):
    """Sequence of Choice, Group or Token objects"""
    def __init__(self, sequence, repeat='1'):
        """
        repeat = '1' or *, +, ?, or range()
            number of times this group may come
        """
        self.sequence = sequence
        self._count = len(self.sequence)
        
        if type(repeat) == tuple:
            # (min, max)
            self._min, self._max = repeat
        else:
            # 1, ?, +, *
            if str(repeat) in '1+':
                self._min = 1
            else:
                self._min = 0
            if str(repeat) in '1?':
                self._max  = 1
            else:
                self._max = None
        
        self._round = 1 # 1 based!    
        self._pos = 0

    def nextItem(self, expected, token):
        "Return next matching item or raise ParseException."
        while self._pos < self._count:
            x = self.sequence[self._pos]

            print self._round, self._pos

            self._pos += 1
            if self._pos == self._count and self._round < self._max:
                self._pos = 0
                self._round += 1
                
            if isinstance(x, Item):
                if x.matches(expected, token):
                    # may raise if not match and not optional
                    return x
            
            else:
                # nested Sequence or Choice
                return x

        else:
            if self._min < self._round < self._max: 
                raise ParseException(msg)
   
class Item(ParseBase):
    """Single Item in ParseSequence or Group
    
    Attributes (all strings or functions):
    
    expect
        value of expected must be ``expect``
    match
        function getting tokentype and tokenvalue
    next = expect
        next value for expect 
        or in case of "STOP" raise StopIteration
    storeAs?
        save val in new[store]
    toSeqAs
        if given calling toSeqAs(val) will be appended to seq
        else simple val
    """
    def __init__(self, expected, match, next,
                 storeAs=None, toSeqAs=None,
                 optional=False):
        if not callable(expected):
            self.expected = lambda x: x == expected
        else:
            self.expected = expected
        # match is a function with parameters tokentype and tokenvalue
        self.match = match
        self.next = next
        self.storeAs = storeAs # to store dict
        self.toSeqAs = toSeqAs # call seq.append(toSeqAs(value))
        self.optional=optional
        
    def matches(self, expected, token):
        """Return True, False or raise ParseException."""
        type_, val, line, col = token
        msg = None 
        if not self.expected(expected):
            # check expected
            msg = u'Expected %r' % expected

        elif not self.match(type_, val):
            # check type and value
            msg = u'Wrong token %r' % type_

        if msg and self.optional:
            # try next
            return False
        
        elif msg:
            raise ParseException(msg)
        
        else:
            return True

       
class ProductionsParser(object):
    """Productions parser"""
    def parse(self, tokenizer, productions, expected=None, 
              store=None, seq=None):
        """
        expected
            first expected item (not token type!)
        store: UPDATED
            if item.store store val in here. Key ``raw`` is always added
            and holds all unprocessed values found
        seq: UPDATED
            append items' val here
          
        returns
            :wellformed: True or False
            :expected: last value of expected
            :token: Last token if not used
        """
        # contains raw values always?
        #store['raw'] = []
        wellformed = True
        token = None # last token may be used again
        prods = [productions]
        for token in tokenizer:
            type_, val, line, col = token
            #store['raw'].append(val)
            
            try:
                while True:
                    item = prods[-1].nextItem(expected, token)
                    if isinstance(item, Item):
                        break
                    elif not item and len(prods) > 1:
                        # nested exhausted
                        prods.pop()
                    else:
                        # nexted Sequence, Choice
                        prods.append(item)
                
            except ParseException, e:
                wellformed = False
                print u'ERROR: %s: %r' % (e, token)
                #self._log.error(u'Unexpected token (%s, %s, %s, %s)' % token)
            else:
                if item.storeAs:
                    store[item.storeAs] = val
                if item.toSeqAs:
                    seq.append(item.toSeqAs(val), type_, line, col)
                else:
                    seq.append(val, type_, line, col)
                
                expected = item.next
                if 'STOP' == expected:
                    # stop here and ignore following tokens
                    token = None
                    break

            print
        
        return wellformed, expected, token    


# PRODUCTION FOR CSSColor
types = cssutils.cssproductions.CSSProductions

# sign + or -
sign = Item(expected=lambda e: e.startswith('value'),
            match=lambda t, v: v in u'+-',
            optional=True,
            next='value')
# value NUMBER or PERCENTAGE
value = Item(expected=lambda e: e.startswith('value'),
             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
             toSeqAs=cssutils.css.CSSPrimitiveValue,
             next='comma-or-end')

productions = Sequence([
    Item(expected='colorType',
         match=lambda t, v: v in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION, 
         storeAs='colorType',
         next='value-or-sign'
         ),
    sign,
    value,
    # more values starting with Comma
    Sequence([# comma , 
              Item(expected='comma-or-end',
                   match=lambda t, v: v == u',',
                   next='value-or-sign'),
                   sign, 
                   value
             ], 
             repeat=(2, 2)
    ),
    # end of FUNCTION )
    Item(expected='comma-or-end',
         match=lambda t, v: v == u')',
         next='STOP')
 ])


# tokenize    
text = 'rgb(-1,-2,3)'
tokens = cssutils.tokenize2.Tokenizer().tokenize(text)

# parse
store = {'colorType': '', # rgb, rgba, hsl, hsla, name, hash, ?
         }
seq = cssutils.util.Seq(readonly=False)
wellformed, expected, token =  ProductionsParser().parse(tokens, 
                                                  productions, 
                                                  expected='colorType', 
                                                  seq=seq, 
                                                  store=store)

print
print '- STORE:', store
print '- WELLFORMED:', wellformed
print '- EXPECTED:', expected
print '- TOKENIZER: ', list(tokens)
pp(seq)
