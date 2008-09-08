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

    def nextItem(self, token=None):
        """Return next matching item or sequence or raise ParseException.
        Any one in item may match."""
        if not token:
            # called when probably done
            return None
        for x in self.items:
            if isinstance(x, Item):
                test = x
            else:
                # nested Sequence matches if 1st item matches
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
        for item in self.sequence:
            if not item.optional:
                return item

    def currentName(self):
        """Return current element of Sequence, used by name"""
        # TODO: current impl first only if 1st if an Item!
        for item in self.sequence[self._pos:]:
            if not item.optional:
                return item.name
        else:
            return 'Unknown'

    name = property(currentName, doc='Used for Error reporting')

    def nextItem(self, token=None):
        """Return next matching item or raise ParseException."""
        while self._pos < self._number:
            x = self.sequence[self._pos]
            self._pos += 1

            if self._pos == self._number and self._round < self._max:
                # new round
                self._pos = 0
                self._round += 1
                
            if isinstance(x, Item):
                if not token or x.matches(token):
                    # not token is probably done
                    return x
            else:
                # nested Sequence or Choice
                return x
        else:
            if not self._min <= self._round <= self._max: 
                raise ParseException(msg)
   
   
class Item(ParseBase):
    """Single Item in Sequence or Choice"""
    def __init__(self, name, match=None, storeAs=None, toSeq=None,
                 optional=False):
        """
        name
            name used for error reporting
        match callback
            function called with parameters tokentype and tokenvalue
            returning True, False or raising ParseException
        storeAs (optional)
            save val in store[storeAs]
        toSeq callback (optional)
            if given calling toSeq(val) will be appended to seq
            else simply seq
        optional = False
            wether Item is optional or not
        """
        # match is a function with parameters tokentype and tokenvalue
        self.name = name
        self.match = match
        self.storeAs = storeAs # to store dict
        if toSeq:
            self.toSeq = toSeq # call seq.append(toSeq(value))
        else:
            self.toSeq = lambda val: val
        self.optional=optional
        
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

class ProductionsParser(object):
    """Productions parser"""
    def __init__(self):
        self.types = cssutils.cssproductions.CSSProductions
        self._log = cssutils.log
    
    def parse(self, tokenizer, productions, store=None, seq=None):
        """
        tokenizer
            generating tokens
        productions
            used to parse tokens
        store  UPDATED
            item.store should be a dict. 
            
            TODO: NEEDED? 
            Key ``raw`` is always added and holds all unprocessed 
            values found
            
        seq (optional) UPDATED
            append items' value here
          
        returns
            :wellformed: True or False
            :token: Last token if not used to be used for new tokenizer
        """
        # contains always raw values?
        store['raw'] = []
        prods = [productions] # a stack

        wellformed = True
        next, token = None, None # if no tokens at all
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
                next = 'EOF'
            else:
                # check prods
                try:
                    while True:
                        # find next matching production
                        item = prods[-1].nextItem(token)
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
                    if item.toSeq:
                        seq.append(item.toSeq(val), type_, line, col)
                    else:
                        seq.append(val, type_, line, col)
                        
                    if 'STOP' == next:
                        # stop here and ignore following tokens
                        token = None
                        break
        while True:
            # not all needed productions done?
            item = prods[-1].nextItem()
            if hasattr(item, 'optional') and item.optional:
                # ignore optional ones
                continue
            
            if item:
                self._log.error(u'ERROR: Missing token for production %r' 
                                % item.name ) 
            elif not item:
                if len(prods) > 1:
                    # nested exhausted, next in parent
                    prods.pop()
                else:
                    break
    
        return wellformed, token    




types = cssutils.cssproductions.CSSProductions

# PRODUCTION FOR CSSColor
# sign + or -
sign = Item(name='sign +-', match=lambda t, v: v in u'+-',
            optional=True)
# value NUMBER or PERCENTAGE
value = Item(name='value', 
             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
             toSeq=cssutils.css.CSSPrimitiveValue)
comma = Item(name='comma', match=lambda t, v: v == u',')
endfunc = Item(name='end FUNC ")"', match=lambda t, v: v == u')')

# COLOR PRODUCTION
_funccolor = Sequence([
    Item(name='FUNC', match=lambda t, v: v in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION, 
         storeAs='colorType'),
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
                      Item(name='HEX color', 
                           match=lambda t, v: t == types.HASH and 
                            len(v) == 4 or len(v) == 7,
                           toSeq=cssutils.css.CSSPrimitiveValue),
                      Item(name='named color', match=lambda t, v: t == types.IDENT,
                           toSeq=cssutils.css.CSSPrimitiveValue),
                      ]
    )

# ----

# PRODUCTION FOR Rect
rectvalue = Item(name='value in rect()', 
                 match=lambda t, v: t in (types.DIMENSION,) or\
                    str(v) in ('auto', '0'), 
                 toSeq=cssutils.css.CSSPrimitiveValue)
rectproductions = Sequence([Item(name='FUNC rect(', 
                                 match=lambda t, v: v == u'rect('),  #normalized!
                            rectvalue,
                            Sequence([comma, 
                                      rectvalue], minmax=lambda: (3,3)),
                            endfunc 
                            ])

# tokenize    

text = 'rgb(1,2,3'#rgb(1%,   \n2% , -3.0%)'
productions = colorproductions
tokens = cssutils.tokenize2.Tokenizer().tokenize(text)

# parse
store = {'colorType': '', # rgb, rgba, hsl, hsla, name, hash, ?
         }
seq = cssutils.util.Seq(readonly=False)
wellformed, token =  ProductionsParser().parse(tokens, 
                                               productions, 
                                               seq=seq, 
                                               store=store)

print
print '- STORE:', store
print '- WELLFORMED:', wellformed
print '- TOKENIZER: ', list(tokens)
pp(seq)
