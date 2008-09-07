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
    def __init__(self, items=None):
        """
        items
            Item or Sequence objects
        """
        self.items = items

    def nextItem(self, expected, token):
        """Return next matching item or sequence or raise ParseException.
        Any one in item may match."""
        for x in self.items:
            if isinstance(x, Item):
                test = x
            else:
                # nested Sequence matches if 1st item matches
                test = x.first()
            try:
                if test.matches(expected, token):
                    return x
            except ParseException, e:
                # do not raise if other my match
                continue
        else:
            # None matched
            raise ParseException('No match in choice')

class Sequence(object):
    """Sequence of Choice or Item objects"""
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
        # TODO: current impl first only if 1st if an Item!
        return self.sequence[0]

    def nextItem(self, expected, token):
        """Return next matching item or raise ParseException."""
        while self._pos < self._number:
            x = self.sequence[self._pos]
            self._pos += 1

            if self._pos == self._number and self._round < self._max:
                # new round
                self._pos = 0
                self._round += 1
                
            if isinstance(x, Item):
                if x.matches(expected, token):
                    return x
            else:
                # nested Sequence or Choice
                return x
        else:
            if not self._min <= self._round <= self._max: 
                raise ParseException(msg)
   
class Item(ParseBase):
    """Single Item in Sequence or Choice"""
    def __init__(self, expected=None, match=None, next='EOF',
                 storeAs=None, toSeqAs=None,
                 optional=False):
        """
        expected (optional, default to "match anything")
            callable or string matching current expected
        match
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseException
        next = expect
            next value for expected or in case of "STOP" raise StopIteration
        storeAs (optional)
            save val in store[storeAs]
        toSeqAs (optional)
            if given calling toSeqAs(val) will be appended to seq
            else simply val will be appended
        optional = False
            wether Item is optional or not
        """
        if expected is None:
            self.expected = lambda x: True
        elif callable(expected): 
            self.expected = expected
        else: # a simple value
            self.expected = lambda x: x == expected
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
        if not self.expected(expected): # check expected
            msg = u'Expected %r' % expected
        elif not self.match(type_, val): # check type and value
            msg = u'Wrong type or value'

        if msg and self.optional:
            return False # try next in Sequence
        elif msg:
            raise ParseException(msg)
        else:
            return True

class ProductionsParser(object):
    """Productions parser"""
    def __init__(self):
        self.types = cssutils.cssproductions.CSSProductions
        self._log = cssutils.log
    
    def parse(self, tokenizer, productions, expected=None, 
              store=None, seq=None):
        """
        tokenizer
            generating tokens
        productions
            used to parse tokens
        expected (optional)
            first expected item (not token type!)
        store  UPDATED
            item.store should be a dict. 
            
            TODO: NEEDED? 
            Key ``raw`` is always added and holds all unprocessed 
            values found
            
        seq (optional) UPDATED
            append items' value here
          
        returns
            :wellformed: True or False
            :expected: Last value of expected for validation checks
            :token: Last token if not used to be used for new tokenizer
        """
        # contains always raw values?
        store['raw'] = []
        prods = [productions] # a stack

        wellformed = True
        token = None # if no tokens at all
        for token in tokenizer:
            type_, val, line, col = token
            store['raw'].append(val)
            
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
                expected = 'EOF'
            else:
                # check prods
                try:
                    while True:
                        # find next matching production
                        item = prods[-1].nextItem(expected, token)
                        if isinstance(item, Item):
                            break
                        elif not item:
                            if len(prods) > 1:
                                # nested exhausted, next in parent
                                prods.pop()
                            else:
                                raise ParseException('No match found')
                        else:
                            # nested Sequence, Choice
                            prods.append(item)                    
                
                except ParseException, e:
                    wellformed = False
                    self._log.error(u'ERROR: %s: %r' % (e, token))
                
                else:
                    # process item
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
    
        return wellformed, expected, token    




types = cssutils.cssproductions.CSSProductions

# PRODUCTION FOR CSSColor
# sign + or -
sign = Item(expected=lambda e: e == 'value-or-sign',
            match=lambda t, v: v in u'+-',
            optional=True,
            next='value')
# value NUMBER or PERCENTAGE
value = Item(expected=lambda e: e.startswith('value'),
             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
             toSeqAs=cssutils.css.CSSPrimitiveValue,
             next='comma-or-end')

# COLOR PRODUCTION
_funccolor = Sequence([
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
             minmax=lambda: (2, 2)
    ),
    # end of FUNCTION )
    Item(expected='comma-or-end',
         match=lambda t, v: v == u')',
         next='STOP')
 ])

productions = Choice([_funccolor,
                      Item(match=lambda t, v: t == types.HASH and 
                            len(v) == 4 or len(v) == 7,
                           toSeqAs=cssutils.css.CSSPrimitiveValue),
                      Item(match=lambda t, v: t == types.IDENT,
                           toSeqAs=cssutils.css.CSSPrimitiveValue),
                      ]
    )

# tokenize    

text = 'rgb(1%,   \n2% , -3.0%)'
expected = 'colorType'#, 'colorType'
tokens = cssutils.tokenize2.Tokenizer().tokenize(text)

# parse
store = {'colorType': '', # rgb, rgba, hsl, hsla, name, hash, ?
         }
seq = cssutils.util.Seq(readonly=False)
wellformed, expected, token =  ProductionsParser().parse(tokens, 
                                                  productions, 
                                                  expected=expected, 
                                                  seq=seq, 
                                                  store=store)

print
print '- STORE:', store
print '- WELLFORMED:', wellformed
print '- EXPECTED:', expected
print '- TOKENIZER: ', list(tokens)
pp(seq)
