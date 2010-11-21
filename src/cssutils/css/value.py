"""CSSValue related classes

- CSSValue implements DOM Level 2 CSS CSSValue
- CSSPrimitiveValue implements DOM Level 2 CSS CSSPrimitiveValue
- CSSValueList implements DOM Level 2 CSS CSSValueList

"""
__all__ = ['PropertyValue',
           'Value', 
#           'CSSValue', 
#           'RGBColor',
#           'CSSVariable'
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
            self.cssText = cssText

        self._readonly = readonly
    
    
    def __iter__(self):
        "Generator which iterates over cssRules."
        for item in self.seq:
            if item.type == 'Value':
                yield item.value
            
    def __repr__(self):
        return u"cssutils.css.%s(%r)" % (self.__class__.__name__,
                                         self.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object cssText=%r at "\
               u"0x%x>" % (self.__class__.__name__, 
                           self.cssText, 
                           id(self))
        
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
        term = Choice(Prod(name='Value',
                           match=lambda t, v: t in Value._supported or
                                              v in u'+-',
                           nextSor = nextSor,
                           toSeq=lambda t, tokens: ('Value',
                                    Value(cssutils.helper.pushtoken(t, 
                                                                    tokens),
                                          parent=self))
                      ),
                      
                      # special case IE only expression
                      Prod(name='expression',
                           match=lambda t, v: t == self._prods.FUNCTION and (
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
                           toSeq=lambda t, tokens: (ExpressionValue._functionName,
                                                    ExpressionValue(
                                            cssutils.helper.pushtoken(t, tokens),
                                            parent=self)
                                                    )
                      ),
                      # calc(
                      PreDef.calc(nextSor=nextSor,
                                  toSeq=lambda t, tokens: (CalcValue._functionName,
                                                           CalcValue(
                                        cssutils.helper.pushtoken(t, tokens), 
                                        parent=self)
                                                           )
                      ),
                      # CSS Variable var(
                      PreDef.variable(nextSor=nextSor,
                                      toSeq=lambda t, tokens: ('CSSVariable',
                                                               CSSVariable(
                                        cssutils.helper.pushtoken(t, tokens), 
                                        parent=self)
                                                               )
                      ),
# TODO:
#                      # rgb/rgba(
#                      Prod(name='RGBColor',
#                           match=lambda t, v: t == self._prods.FUNCTION and (
#                              cssutils.helper.normalize(v) in (u'rgb(',
#                                                               u'rgba('
#                                                               )                               
#                           ),
#                           nextSor=nextSor,
#                                  toSeq=lambda t, tokens: (RGBColor._functionName,
#                                                           RGBColor(
#                                        cssutils.helper.pushtoken(t, tokens), 
#                                        parent=self)
#                                                           )
#                      ),
                      # other functions like rgb( etc
                      PreDef.function(nextSor=nextSor,
                                      toSeq=lambda t, tokens: ('FUNCTION',
                                                               CSSFunction(
                                        cssutils.helper.pushtoken(t, tokens),
                                        parent=self)
                                                               )
                      )
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
        if ok:
            self._setSeq(seq)
            self.wellformed = ok
    
    cssText = property(lambda self: cssutils.ser.do_css_PropertyValue(self),
                       _setCssText,
                       doc="A string representation of the current value.")

    value = property(lambda self: cssutils.ser.do_css_PropertyValue(self, 
                                                                    valuesOnly=True),
                       doc=u"A string representation of the current value "
                           u"without any comments used for validation.")


class Value(cssutils.util._NewBase):
    """
    Any simple value like ``1px``, ``red`` or ``url(some.png)``
    
    Supported types are listed in Value._supported
    """
    __reNumDim = re.compile(ur'^(\d*\.\d+|\d+)(.*)$', re.I | re.U | re.X)
    
    _supported = ('DIMENSION', 'HASH', 'IDENT', 'NUMBER', 'PERCENTAGE', 
                  'STRING', 'UNICODE-RANGE', 'URI')
    
    def __init__(self, cssText=None, parent=None, readonly=False):
        """See CSSPrimitiveValue.__init__()"""
        super(Value, self).__init__()

        self._type = None
        self._dimension = None
        self._value = u''
        
        if cssText:
            self.cssText = cssText

    def __repr__(self):
        return u"cssutils.css.%s(%r)" % (self.__class__.__name__,
                                         self.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object value=%r dimension=%s type=%s cssText=%r at 0x%x>"\
               % (self.__class__.__name__, 
                  self.value, self.dimension, self.type, self.cssText,
                  id(self))

    def _setCssText(self, cssText):
        self._checkReadonly()

        prods = Sequence(PreDef.unary(),
                         Choice(PreDef.dimension(stop=True),
                                PreDef.hexcolor(stop=True),
                                PreDef.ident(stop=True),
                                PreDef.number(stop=True),
                                PreDef.percentage(stop=True),
                                PreDef.string(stop=True),
                                PreDef.uri(stop=True),
                                PreDef.unicode_range(stop=True),
                                )
                         )     
        # store: colorType, parts
        ok, seq, store, unused = ProdParser().parse(cssText, u'Value', prods)
        if ok:
            sign = val = u''
            dim = type_ = None
            
            # find 
            for item in seq:
                if item.value in u'+-':
                    sign = item.value
                else:
                    type_ = item.type
                    
                    if type_ in ('DIMENSION', 'NUMBER', 'PERCENTAGE'):
                        # number + optional dim
                        v, d = self.__reNumDim.findall(
                                    cssutils.helper.normalize(item.value))[0]
                        if u'.' in v:
                            val = float(sign + v)
                        else:
                            val = int(sign + v)
                        if d:
                            dim = d

                    else:
                        val = item.value
                        
            self._setSeq(seq)
            self.wellformed = ok
                            
            self._type = type_
            
            self._value = val
            self._dimension = dim
            
    cssText = property(lambda self: cssutils.ser.do_css_Value(self), 
                       _setCssText, 
                       u'String value of this value')
    
    type = property(lambda self: self._type, #_setType, 
                     u'Type of this value')

#    def _setValue(self, value):
#        self._value = value
        
    value = property(lambda self: self._value, #_setValue, 
                     u'Typed value, string, int or float.')

    dimension = property(lambda self: self._dimension, #_setValue, 
                     u'Dimension if a DIMENSION or PERCENTAGE value')
