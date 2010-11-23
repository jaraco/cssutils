"""Value related classes. 

DOM Level 2 CSS CSSValue, CSSPrimitiveValue and CSSValueList are **no longer**
supported and are replaced by these new classes.
"""
__all__ = ['PropertyValue',
           'Value',
           'DimensionValue',
           'CSSFunction', 
           'CSSVariable',
           'MSValue'
           ]
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from cssutils.prodparser import *
import cssutils
import cssutils.helper
import math
import re
import xml.dom

class PropertyValue(cssutils.util._NewBase):
    """
    - iterates over all contained Value objects (not the separators like ``,``,
    ``/`` or `` `` though
    - supports ``PropertyValue.item(index)`` and ``PropertyValue[index]`` access
    - supports ``PropertyValue.length`` or ``len(PropertyValue)``
    - property ``PropertyValue.cssText`` contains a string of this property 
    value
    - property ``PropertyValue.value`` contains a string of all values without
    comments etc
    """
    
    def __init__(self, cssText=None, parent=None, readonly=False):
        """
        :param cssText:
            the parsable cssText of the value
        :param readonly:
            defaults to False
        """
        super(PropertyValue, self).__init__()
        
        self.parent = parent
        self.wellformed = False
        
        if cssText is not None: # may be 0
            if type(cssText) in (int, float):
                cssText = unicode(cssText) # if it is a number
            self.cssText = cssText
        
        self._readonly = readonly

    def __len__(self):
        return len(list(self.__items()))
    
    def __getitem__(self, index):
        try:
            return list(self.__items())[index]
        except IndexError:
            return None
            
    def __iter__(self):
        "Generator which iterates over cssRules."
        for item in self.__items():
            yield item
            
    def __repr__(self):
        return u"cssutils.css.%s(%r)" % (self.__class__.__name__,
                                         self.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object cssText=%r at "\
               u"0x%x>" % (self.__class__.__name__, 
                           self.cssText, 
                           id(self))
        
    def __items(self, seq=None):
        "a generator of Value obects only, no , / or ' '"
        if seq is None:
            seq = self.seq
        return (x.value for x in seq if isinstance(x.value, Value))
    
    def _setCssText(self, cssText):
        if type(cssText) in (int, float):
                cssText = unicode(cssText) # if it is a number
        """
        Format::

            unary_operator
              : '-' | '+'
              ;
            operator
              : '/' S* | ',' S* | /* empty */
              ;
            expr
              : term [ operator term ]*
              ;
            term
              : unary_operator?
                [ NUMBER S* | PERCENTAGE S* | LENGTH S* | EMS S* | EXS S* | 
                  ANGLE S* | TIME S* | FREQ S* ]
              | STRING S* | IDENT S* | URI S* | hexcolor | function
              | UNICODE-RANGE S*
              ;
            function
              : FUNCTION S* expr ')' S*
              ;
            /*
             * There is a constraint on the color that it must
             * have either 3 or 6 hex-digits (i.e., [0-9a-fA-F])
             * after the "#"; e.g., "#000" is OK, but "#abcd" is not.
             */
            hexcolor
              : HASH S*
              ;

        :exceptions:
            - :exc:`~xml.dom.SyntaxErr`:
              Raised if the specified CSS string value has a syntax error
              (according to the attached property) or is unparsable.
            - :exc:`~xml.dom.InvalidModificationErr`:
              TODO: Raised if the specified CSS string value represents a 
              different type of values than the values allowed by the CSS 
              property.
            - :exc:`~xml.dom.NoModificationAllowedErr`:
              Raised if this value is readonly.
        """
        self._checkReadonly()
        
        # used as operator is , / or S
        nextSor = u',/'
        term = Choice(_DimensionProd(self, nextSor),
                      _ValueProd(self, nextSor),
#                      _CalcValueProd(self, nextSor),
#                      _RGBColord(self, nextSor),
#                      _Rect(self, nextSor),
                      # all other functions
                      _CSSVariableProd(self, nextSor),
                      _MSValueProd(self, nextSor),
                      _CSSFunctionProd(self, nextSor)                      
                      )
        operator = Choice(PreDef.S(toSeq=False),
                          PreDef.char('comma', ',',
                                      toSeq=lambda t, tokens: ('operator', t[1])),
                          PreDef.char('slash', '/',
                                      toSeq=lambda t, tokens: ('operator', t[1])),
                          optional=True)
        prods = Sequence(term,
                         Sequence(# mayEnd this Sequence if whitespace
                                  operator, 
                                  # TODO: only when setting via other class
                                  # used by variabledeclaration currently
                                  PreDef.char('END', ';',
                                              stopAndKeep=True,
                                              optional=True),
                                  # TODO: } and !important ends too!
                                  term,
                                  minmax=lambda: (0, None))) 
        # parse
        ok, seq, store, unused = ProdParser().parse(cssText,
                                                    u'PropertyValue',
                                                    prods)
        # must be at least one value!
        ok = ok and len(list(self.__items(seq))) > 0
        if ok:
            self._setSeq(seq)
            self.wellformed = True
        else:
            self._log.error(u'PropertyValue: Unknown syntax or no value: %r.' % 
                            self._valuestr(cssText))
    
    cssText = property(lambda self: cssutils.ser.do_css_PropertyValue(self),
                       _setCssText,
                       doc="A string representation of the current value.")

    def item(self, index):
        return self[index]

    length = property(lambda self: len(self),
                      doc=u'Number of values set.')

    value = property(lambda self: cssutils.ser.do_css_PropertyValue(self, 
                                                                    valuesOnly=True),
                       doc=u"A string representation of the current value "
                           u"without any comments used for validation.")


class Value(cssutils.util._NewBase):
    """
    HASH, IDENT, STRING, UNICODE-RANGE or URI values
    """    
    HASH = u'HASH'
    IDENT = u'IDENT'
    STRING = u'STRING'
    UNICODE_RANGE = u'UNICODE-RANGE'
    URI = u'URI'
    
    DIMENSION = u'DIMENSION'
    NUMBER = u'NUMBER'
    PERCENTAGE = u'PERCENTAGE' 
    
    def __init__(self, cssText=None, parent=None, readonly=False):
        super(Value, self).__init__()
        
        self._type = None
        self._value = u''
        self.parent = parent
        
        if cssText:
            self.cssText = cssText

    def __repr__(self):
        return u"cssutils.css.%s(%r)" % (self.__class__.__name__,
                                         self.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object value=%r type=%s cssText=%r at 0x%x>"\
               % (self.__class__.__name__, 
                  self.value, self.type, self.cssText,
                  id(self))

    def _setCssText(self, cssText):
        self._checkReadonly()

        prods = Choice(PreDef.hexcolor(stop=True),
                       PreDef.ident(stop=True),
                       PreDef.string(stop=True),
                       PreDef.uri(stop=True),
                       PreDef.unicode_range(stop=True),
                       )
        ok, seq, store, unused = ProdParser().parse(cssText, u'Value', prods)
        if ok:
            self._type = seq[0].type
            self._value = seq[0].value
                        
            self._setSeq(seq)
            self.wellformed = ok
                                        
    cssText = property(lambda self: cssutils.ser.do_css_Value(self), 
                       _setCssText, u'String value of this value.')

    type = property(lambda self: self._type, #_setType, 
                     u'Type of this value.')

    def _setValue(self, value):
        # TODO: check!
        self._value = value

    value = property(lambda self: self._value, _setValue, 
                     u'Typed value, string, int or float.')


class DimensionValue(Value):
    """
    DIMENSION, PERCENTAGE or NUMBER values.
    """
    __reNumDim = re.compile(ur'^(\d*\.\d+|\d+)(.*)$', re.I | re.U | re.X)
    _dimension = None
    
    def __str__(self):
        return u"<cssutils.css.%s object value=%r dimension=%s type=%s cssText=%r at 0x%x>"\
               % (self.__class__.__name__, 
                  self.value, self.dimension, self.type, self.cssText,
                  id(self))

    def _setCssText(self, cssText):
        self._checkReadonly()

        prods = Sequence(PreDef.unary(),
                         Choice(PreDef.dimension(stop=True),
                                PreDef.number(stop=True),
                                PreDef.percentage(stop=True)
                                )
                         )     
        ok, seq, store, unused = ProdParser().parse(cssText, 
                                                    u'DimensionValue', 
                                                    prods)
        if ok:
            sign = val = u''
            dim = type_ = None
            
            # find 
            for item in seq:
                if item.value in u'+-':
                    sign = item.value
                else:
                    type_ = item.type
                    
                    # number + optional dim
                    v, d = self.__reNumDim.findall(
                                cssutils.helper.normalize(item.value))[0]
                    if u'.' in v:
                        val = float(sign + v)
                    else:
                        val = int(sign + v)
                    if d:
                        dim = d
                                                    
            self._dimension = dim
            self._type = type_            
            self._value = val
            
            self._setSeq(seq)
            self.wellformed = ok
    
    cssText = property(lambda self: cssutils.ser.do_css_Value(self), 
                       _setCssText, u'String value of this value.')
        
    dimension = property(lambda self: self._dimension, #_setValue, 
                     u'Dimension if a DIMENSION or PERCENTAGE value, else None')
        

class CSSFunction(Value):
    """A function value"""
    type = 'FUNCTION'
    _functionName = 'FUNCTION'
    
    def _productions(self):
        """Return definition used for parsing."""
        types = self._prods # rename!
        
        itemProd = Choice(_DimensionProd(self),
                          _ValueProd(self),
                          #_CalcValueProd(self),
                          _CSSVariableProd(self),
                          _CSSFunctionProd(self)
                          )
        funcProds = Sequence(Prod(name='FUNCTION',
                                  match=lambda t, v: t == types.FUNCTION,
                                  toSeq=lambda t, tokens: (t[0], 
                                                           cssutils.helper.normalize(t[1]))),
                             Choice(Sequence(itemProd,
                                             Sequence(PreDef.comma(),
                                                      itemProd,
                                                      minmax=lambda: (0, None)),
                                             PreDef.funcEnd(stop=True)),
                                    PreDef.funcEnd(stop=True))
         )
        return funcProds
    
    def _setCssText(self, cssText):
        self._checkReadonly()
        ok, seq, store, unused = ProdParser().parse(cssText, 
                                                    self.type,
                                                    self._productions())
        if ok:
            self._setSeq(seq)
            self.wellformed = ok
                            
    cssText = property(lambda self: cssutils.ser.do_css_CSSFunction(self), 
                       _setCssText, u'String value of this value.')


class MSValue(CSSFunction):
    "An IE specific Microsoft only function value."
    type = _functionName = 'MSValue'
    
    def _productions(self):
        """Return definition used for parsing."""
        types = self._prods # rename!
        
        funcProds = Sequence(Prod(name='FUNCTION',
                                  match=lambda t, v: t == types.FUNCTION,
                                  toSeq=lambda t, tokens: (t[0], t[1])
                                  ),
                             Sequence(Choice(_DimensionProd(self),
                                             _ValueProd(self),
                                             _MSValueProd(self),
                                             #_CalcValueProd(self),
                                             _CSSVariableProd(self),
                                             _CSSFunctionProd(self),
                                             Prod(name='MSValuePart',
                                                  match=lambda t, v: v != u')',
                                                  toSeq=lambda t, tokens: (t[0], t[1])
                                                  )
                                             ),
                                      minmax=lambda: (0, None)
                                      ),
                             PreDef.funcEnd(stop=True)
                             )
        return funcProds


class CSSVariable(CSSFunction):
    """The CSSVariable represents a CSS variables like ``var(varname)``.
    
    A variable has a (nonnormalized!) `name` and a `value` which is
    tried to be resolved from any available CSSVariablesRule definition.
    """
    _functionName = 'CSSVariable'
    _name = None

    def __str__(self):
        return u"<cssutils.css.%s object name=%r value=%r at 0x%x>" % (
                self.__class__.__name__, self.name, self.value, id(self)) 
    
    def _setCssText(self, cssText):
        self._checkReadonly()

        types = self._prods # rename!
        prods = Sequence(Prod(name='var',
                                  match=lambda t, v: t == types.FUNCTION and
                                        cssutils.helper.normalize(v) == u'var(' 
                             ),
                             PreDef.ident(toStore='ident'),
                             PreDef.funcEnd(stop=True))
        
        # store: name of variable
        store = {'ident': None}
        ok, seq, store, unused = ProdParser().parse(cssText, 
                                                    u'CSSVariable',
                                                    prods)
        if ok:
            self._name = store['ident'].value
            self._setSeq(seq)
            self.wellformed = ok
            
    cssText = property(lambda self: cssutils.ser.do_css_CSSVariable(self),
                       _setCssText, doc=u"String representation of variable.")

    # TODO: writable? check if var (value) available?
    name = property(lambda self: self._name)

    def _getValue(self):
        "Find contained sheet and @variables there"
        rel = self
        while True:
            # find node which has parentRule to get to StyleSheet
            if hasattr(rel, 'parent'):
                rel = rel.parent
            else:
                break 
        try:
            variables = rel.parentRule.parentStyleSheet.variables
        except AttributeError:
            return None
        else:
            try:
                return variables[self.name]
            except KeyError:
                return None
        
    value = property(_getValue, doc=u'Resolved value or None.')


# helper for productions
def _ValueProd(parent, nextSor=False):
    return Prod(name='Value',
                match=lambda t, v: t in ('HASH', 'IDENT', 'STRING', 
                                         'UNICODE-RANGE', 'URI'),
                nextSor = nextSor,
                toSeq=lambda t, tokens: ('Value', Value(
                                            cssutils.helper.pushtoken(t, 
                                                                      tokens),
                                         parent=parent)
                                         )
                )
    
def _DimensionProd(parent, nextSor=False):
    return Prod(name='Dimension',
                match=lambda t, v: t in (u'DIMENSION', 
                                         u'NUMBER', 
                                         u'PERCENTAGE') or v in u'+-',
                nextSor = nextSor,
                toSeq=lambda t, tokens: ('Dimension', DimensionValue(
                                            cssutils.helper.pushtoken(t, 
                                                                      tokens),
                                         parent=parent)
                                         )
                )

def _CSSFunctionProd(parent, nextSor=False):
    return PreDef.function(nextSor=nextSor,
                           toSeq=lambda t, tokens: (CSSFunction._functionName, 
                                                    CSSFunction(
                                cssutils.helper.pushtoken(t, tokens),
                                parent=parent)
                                )
                           )

def _CSSVariableProd(parent, nextSor=False):
    return PreDef.variable(nextSor=nextSor,
                           toSeq=lambda t, tokens: (CSSVariable._functionName, 
                                                    CSSVariable(
                                cssutils.helper.pushtoken(t, tokens), 
                                parent=parent)
                                                    )
                           )  
    
def _MSValueProd(parent, nextSor=False):
    return Prod(name=MSValue._functionName,
                match=lambda t, v: (#t == self._prods.FUNCTION and (
                    cssutils.helper.normalize(v) in (u'expression(',
                                                 u'alpha(',
                                                 u'blur(',
                                                 u'chroma(',
                                                 u'dropshadow(',
                                                 u'fliph(',
                                                 u'flipv(',
                                                 u'glow(',
                                                 u'gray(',
                                                 u'invert(',
                                                 u'mask(',
                                                 u'shadow(',                                                               
                                                 u'wave(',
                                                 u'xray(') or
                    v.startswith(u'progid:DXImageTransform.Microsoft.')                               
                    ),
                nextSor=nextSor,
                toSeq=lambda t, tokens: (MSValue._functionName, 
                                         MSValue(cssutils.helper.pushtoken(t, 
                                                                           tokens
                                                                           ),
                                                 parent=parent
                                                 )
                                         )
                )