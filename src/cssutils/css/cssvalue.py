"""CSSValue related classes

- CSSValue implements DOM Level 2 CSS CSSValue
- CSSPrimitiveValue implements DOM Level 2 CSS CSSPrimitiveValue
- CSSValueList implements DOM Level 2 CSS CSSValueList

"""
__all__ = ['CSSValue', 'CSSPrimitiveValue', 'CSSValueList', 'RGBColor']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import re
import xml.dom
import cssutils
from cssutils.profiles import profiles
from cssutils.prodparser import *


class CSSValue(cssutils.util.Base2):
    """
    The CSSValue interface represents a simple or a complex value.
    A CSSValue object only occurs in a context of a CSS property

    Properties
    ==========
    cssText
        A string representation of the current value.
    cssValueType
        A (readonly) code defining the type of the value.
    cssValueTypeString
        A (readonly) string describing ``cssValueType``.

    seq: a list (cssutils)
        All parts of this style declaration including CSSComments
    wellformed
        if this value is syntactically ok
    """

    # The value is inherited and the cssText contains "inherit".
    CSS_INHERIT = 0
    # The value is a CSSPrimitiveValue.
    CSS_PRIMITIVE_VALUE = 1
    # The value is a CSSValueList.
    CSS_VALUE_LIST = 2
    # The value is a custom value.
    CSS_CUSTOM = 3

    _typestrings = {0: 'CSS_INHERIT' , 
                    1: 'CSS_PRIMITIVE_VALUE',
                    2: 'CSS_VALUE_LIST',
                    3: 'CSS_CUSTOM'}
    
    def __init__(self, cssText=None, readonly=False):
        """
        inits a new CSS Value

        cssText
            the parsable cssText of the value
        readonly
            defaults to False
        """
        super(CSSValue, self).__init__()

        self._cssValueType = None
        self.wellformed = False

        if cssText is not None: # may be 0
            if type(cssText) in (int, float):
                cssText = unicode(cssText) # if it is a number
            self.cssText = cssText

        self._readonly = readonly

    def _setCssText(self, cssText):
        """
        Format
        ======
        ::

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
                [ NUMBER S* | PERCENTAGE S* | LENGTH S* | EMS S* | EXS S* | ANGLE S* |
                  TIME S* | FREQ S* ]
              | STRING S* | IDENT S* | URI S* | hexcolor | function
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

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          (according to the attached property) or is unparsable.
        - TODO: INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of values than the values allowed by the CSS property.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this value is readonly.
        """
        self._checkReadonly()
        
        operator = Choice(PreDef.CHAR('slash', '/', toSeq=lambda t, v: ('operator', v)),
                          PreDef.CHAR('comma', ',', toSeq=lambda t, v: ('operator', v)),
                          PreDef.S()                          
                          )
        term = Choice(Sequence(PreDef.unary(), 
                               Choice(PreDef.number(), 
                                      PreDef.percentage(),
                                      PreDef.dimension())),
                      PreDef.string(),
                      PreDef.ident(),
                      PreDef.uri(),
                      PreDef.hexcolor(),#toSeq=lambda t, v: (RGBColor, RGBColor(v))),
                      PreDef.function())
        # CSSValue PRODUCTION
        valueprod = Sequence(term, 
                             Sequence(operator, 
                                      term,
                                      minmax=lambda: (0, None))) 
        # parse
        wellformed, seq, store, unusedtokens = ProdParser().parse(cssText,
                                                                  u'CSSValue', 
                                                                  valueprod)
        if wellformed:
            # filter out double operators (S + "," etc)
            # if operator is , or / it is never followed by S
            count, firstvalue = 0, ()
            newseq = self._tempSeq()
            i, end = 0, len(seq)
            while i < end:
                item = seq[i]
                if item.type == self._prods.S:
                    pass
                elif item.value == u',':
                    # counts as a single one
                    newseq.appendItem(item)
                    if firstvalue:
                        firstvalue = firstvalue[0], 'STRING'
                    count -= 1
                elif item.value == u'/':
                    # counts as a single one
                    newseq.appendItem(item)
                
                elif item.value == u'+' or item.value == u'-':
                    # combine +- and following number or other
                    i += 1
                    try:
                        next = seq[i]
                    except IndexError:
                        firstvalue = () # raised later
                        break
                    newseq.append(item.value + next.value, next.type, 
                                  item.line, item.col)
                    if not firstvalue:
                        firstvalue = (item.value + next.value, next.type)
                    count += 1
                
                elif item.type != cssutils.css.CSSComment:
                    newseq.appendItem(item)
                    if not firstvalue:
                        firstvalue = (item.value, item.type)
                    count += 1
    
                else:
                    newseq.appendItem(item)
                    
                i += 1

            if not firstvalue:
                self._log.error(
                        u'CSSValue: Unknown syntax or no value: %r.' %
                        self._valuestr(cssText))
                
            else:
    
                self._setSeq(newseq)
                self.wellformed = wellformed
                            
                if hasattr(self, '_value'):
                    # only in case of CSSPrimitiveValue, else remove!
                    del self._value
                        
                if count == 1:
                    if u'inherit' == cssutils.helper.normalize(firstvalue[0]):
                        self.__class__ = CSSValue
                        self._cssValueType = CSSValue.CSS_INHERIT                 
                    else:
                        self.__class__ = CSSPrimitiveValue
                        self._value = firstvalue
                        
                elif count > 1:
                    self.__class__ = CSSValueList
                    self._items = count * ['TODO']
                        
                else:
                    # ? should not happen...
                    self.__class__ = CSSValue
                    self._cssValueType = CSSValue.CSS_CUSTOM

    cssText = property(lambda self: cssutils.ser.do_css_CSSValue(self), 
                       _setCssText,
                       doc="A string representation of the current value.")

    cssValueType = property(lambda self: self._cssValueType,
        doc="A (readonly) code defining the type of the value.")

    cssValueTypeString = property(
        lambda self: CSSValue._typestrings.get(self.cssValueType, None),
        doc="(readonly) Name of cssValueType.")

    def __repr__(self):
        return "cssutils.css.%s(%r)" % (
                self.__class__.__name__, self.cssText)

    def __str__(self):
        return "<cssutils.css.%s object cssValueTypeString=%r cssText=%r at 0x%x>" % (
                self.__class__.__name__, self.cssValueTypeString,
                self.cssText, id(self))


class CSSPrimitiveValue(CSSValue):
    """
    represents a single CSS Value.  May be used to determine the value of a
    specific style property currently set in a block or to set a specific
    style property explicitly within the block. Might be obtained from the
    getPropertyCSSValue method of CSSStyleDeclaration.

    Conversions are allowed between absolute values (from millimeters to
    centimeters, from degrees to radians, and so on) but not between
    relative values. (For example, a pixel value cannot be converted to a
    centimeter value.) Percentage values can't be converted since they are
    relative to the parent value (or another property value). There is one
    exception for color percentage values: since a color percentage value
    is relative to the range 0-255, a color percentage value can be
    converted to a number; (see also the RGBColor interface).
    """
    # constant: type of this CSSValue class
    cssValueType = CSSValue.CSS_PRIMITIVE_VALUE

    __types = cssutils.cssproductions.CSSProductions 

    # An integer indicating which type of unit applies to the value.
    CSS_UNKNOWN = 0 # only obtainable via cssText
    CSS_NUMBER = 1
    CSS_PERCENTAGE = 2
    CSS_EMS = 3
    CSS_EXS = 4
    CSS_PX = 5
    CSS_CM = 6
    CSS_MM = 7
    CSS_IN = 8
    CSS_PT = 9
    CSS_PC = 10
    CSS_DEG = 11
    CSS_RAD = 12
    CSS_GRAD = 13
    CSS_MS = 14
    CSS_S = 15
    CSS_HZ = 16
    CSS_KHZ = 17
    CSS_DIMENSION = 18
    CSS_STRING = 19
    CSS_URI = 20
    CSS_IDENT = 21
    CSS_ATTR = 22
    CSS_COUNTER = 23
    CSS_RECT = 24
    CSS_RGBCOLOR = 25
    # NOT OFFICIAL:
    CSS_RGBACOLOR = 26

    _floattypes = [CSS_NUMBER, CSS_PERCENTAGE, CSS_EMS, CSS_EXS,
                   CSS_PX, CSS_CM, CSS_MM, CSS_IN, CSS_PT, CSS_PC,
                   CSS_DEG, CSS_RAD, CSS_GRAD, CSS_MS, CSS_S,
                   CSS_HZ, CSS_KHZ, CSS_DIMENSION
                   ]
    _stringtypes = [CSS_ATTR, CSS_IDENT, CSS_STRING, CSS_URI]
    _countertypes = [CSS_COUNTER]
    _recttypes = [CSS_RECT]
    _rbgtypes = [CSS_RGBCOLOR, CSS_RGBACOLOR]

    # oldtype: newType: converterfunc
    _converter = {
        # cm <-> mm <-> in, 1 inch is equal to 2.54 centimeters.
        # pt <-> pc, the points used by CSS 2.1 are equal to 1/72nd of an inch.
        # pc: picas - 1 pica is equal to 12 points
        (CSS_CM, CSS_MM): lambda x: x * 10,
        (CSS_MM, CSS_CM): lambda x: x / 10,

        (CSS_PT, CSS_PC): lambda x: x * 12,
        (CSS_PC, CSS_PT): lambda x: x / 12,

        (CSS_CM, CSS_IN): lambda x: x / 2.54,
        (CSS_IN, CSS_CM): lambda x: x * 2.54,
        (CSS_MM, CSS_IN): lambda x: x / 25.4,
        (CSS_IN, CSS_MM): lambda x: x * 25.4,

        (CSS_IN, CSS_PT): lambda x: x / 72,
        (CSS_PT, CSS_IN): lambda x: x * 72,
        (CSS_CM, CSS_PT): lambda x: x / 2.54 / 72,
        (CSS_PT, CSS_CM): lambda x: x * 72 * 2.54,
        (CSS_MM, CSS_PT): lambda x: x / 25.4 / 72,
        (CSS_PT, CSS_MM): lambda x: x * 72 * 25.4,

        (CSS_IN, CSS_PC): lambda x: x / 72 / 12,
        (CSS_PC, CSS_IN): lambda x: x * 12 * 72,
        (CSS_CM, CSS_PC): lambda x: x / 2.54 / 72 / 12,
        (CSS_PC, CSS_CM): lambda x: x * 12 * 72 * 2.54,
        (CSS_MM, CSS_PC): lambda x: x / 25.4 / 72 / 12,
        (CSS_PC, CSS_MM): lambda x: x * 12 * 72 * 25.4,

        # hz <-> khz
        (CSS_KHZ, CSS_HZ): lambda x: x * 1000,
        (CSS_HZ, CSS_KHZ): lambda x: x / 1000,
        # s <-> ms
        (CSS_S, CSS_MS): lambda x: x * 1000,
        (CSS_MS, CSS_S): lambda x: x / 1000

        # TODO: convert deg <-> rad <-> grad
    }

    def __init__(self, cssText=None, readonly=False):
        """
        see CSSPrimitiveValue.__init__()
        """
        super(CSSPrimitiveValue, self).__init__(cssText=cssText,
                                                readonly=readonly)


    _unitnames = ['CSS_UNKNOWN',
                  'CSS_NUMBER', 'CSS_PERCENTAGE',
                  'CSS_EMS', 'CSS_EXS',
                  'CSS_PX',
                  'CSS_CM', 'CSS_MM',
                  'CSS_IN',
                  'CSS_PT', 'CSS_PC',
                  'CSS_DEG', 'CSS_RAD', 'CSS_GRAD',
                  'CSS_MS', 'CSS_S',
                  'CSS_HZ', 'CSS_KHZ',
                  'CSS_DIMENSION', 
                  'CSS_STRING', 'CSS_URI', 'CSS_IDENT', 
                  'CSS_ATTR', 'CSS_COUNTER', 'CSS_RECT',
                  'CSS_RGBCOLOR', 'CSS_RGBACOLOR',
                  ]
    
    def _unitDIMENSION(val):
        """Check val for dimension name."""
        units = {'em': 'CSS_EMS', 'ex': 'CSS_EXS',
                 'px': 'CSS_PX',
                 'cm': 'CSS_CM', 'mm': 'CSS_MM',
                 'in': 'CSS_IN',
                 'pt': 'CSS_PT', 'pc': 'CSS_PC',
                 'deg': 'CSS_DEG', 'rad': 'CSS_RAD', 'grad': 'CSS_GRAD',
                 'ms': 'CSS_MS', 's': 'CSS_S',
                 'hz': 'CSS_HZ', 'khz': 'CSS_KHZ'
                 }        
        val = cssutils.helper.normalize(val)
        return units.get(re.findall(ur'^.*?([a-z]+)$', val, re.U)[0],
                         'CSS_DIMENSION')

    def _unitFUNCTION(val):
        """Check val for function name."""
        units = {'attr(': 'CSS_ATTR',
                 'counter(': 'CSS_COUNTER',
                 'rect(': 'CSS_RECT',
                 'rgb(': 'CSS_RGBCOLOR',
                 'rgba(': 'CSS_RGBACOLOR',
                 }
        val = cssutils.helper.normalize(val)
        return units.get(re.findall(ur'^(.*?\()', val, re.U)[0],
                         'CSS_FUNCTION')
    
    __unitbytype = {
        __types.NUMBER: 'CSS_NUMBER',
        __types.PERCENTAGE: 'CSS_PERCENTAGE',
        __types.STRING: 'CSS_STRING',
        __types.URI: 'CSS_URI',
        __types.IDENT: 'CSS_IDENT',
        __types.HASH: 'CSS_RGBCOLOR',
        __types.DIMENSION: _unitDIMENSION,
        __types.FUNCTION: _unitFUNCTION
        }

    def __set_primitiveType(self):
        """
        primitiveType is readonly but is set lazy if accessed
        """
        # TODO: check unary and font-family STRING a, b, "c"
        
        val, type_ = self._value
        # try get by type_
        pt = self.__unitbytype.get(type_, 'CSS_UNKNOWN')
        if callable(pt):
            # multiple options, check value too
            pt = pt(val)
        self._primitiveType = getattr(self, pt)
        
    def _getPrimitiveType(self):
        if not hasattr(self, '_primitivetype'):
            self.__set_primitiveType()
        return self._primitiveType

    primitiveType = property(_getPrimitiveType,
        doc="(readonly) The type of the value as defined by the constants specified above.")

    def _getPrimitiveTypeString(self):
        return self._unitnames[self.primitiveType]

    primitiveTypeString = property(_getPrimitiveTypeString,
                                   doc="Name of primitive type of this value.")

    def _getCSSPrimitiveTypeString(self, type):
        "get TypeString by given type which may be unknown, used by setters"
        try:
            return self._unitnames[type]
        except (IndexError, TypeError):
            return u'%r (UNKNOWN TYPE)' % type

    # TODO: maybe too simple!
    _reNumDim = re.compile(ur'^(.*?)(%|[a-z]+)$', re.I| re.U|re.X)

    def __getNumDim(self):
        "splits self._value in numerical and dimension part"
        value = cssutils.helper.normalize(self._value[0])
        try:
            val, dim = self._reNumDim.findall(value)[0]
        except IndexError:
            val, dim = value, u''
        try:
            val = float(val)
        except ValueError:
            raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue: No float value %r' % self._value[0])

        return val, dim

    def getFloatValue(self, unitType=None):
        """
        (DOM method) This method is used to get a float value in a
        specified unit. If this CSS value doesn't contain a float value
        or can't be converted into the specified unit, a DOMException
        is raised.

        unitType
            to get the float value. The unit code can only be a float unit type
            (i.e. CSS_NUMBER, CSS_PERCENTAGE, CSS_EMS, CSS_EXS, CSS_PX, CSS_CM,
            CSS_MM, CSS_IN, CSS_PT, CSS_PC, CSS_DEG, CSS_RAD, CSS_GRAD, CSS_MS,
            CSS_S, CSS_HZ, CSS_KHZ, CSS_DIMENSION) or None in which case
            the current dimension is used.

        returns not necessarily a float but some cases just an integer
        e.g. if the value is ``1px`` it return ``1`` and **not** ``1.0``

        conversions might return strange values like 1.000000000001
        """
        if unitType is not None and unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(
                u'unitType Parameter is not a float type')

        val, dim = self.__getNumDim()
        
        if unitType is not None and self.primitiveType != unitType:
            # convert if needed
            try:
                val = self._converter[self.primitiveType, unitType](val)
            except KeyError:
                raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue: Cannot coerce primitiveType %r to %r'
                % (self.primitiveTypeString,
                   self._getCSSPrimitiveTypeString(unitType)))

        if val == int(val):
            val = int(val)

        return val

    def setFloatValue(self, unitType, floatValue):
        """
        (DOM method) A method to set the float value with a specified unit.
        If the property attached with this value can not accept the
        specified unit or the float value, the value will be unchanged and
        a DOMException will be raised.

        unitType
            a unit code as defined above. The unit code can only be a float
            unit type
        floatValue
            the new float value which does not have to be a float value but
            may simple be an int e.g. if setting::

                setFloatValue(CSS_PX, 1)

        raises DOMException
            - INVALID_ACCESS_ERR: Raised if the attached property doesn't
                support the float value or the unit type.
            - NO_MODIFICATION_ALLOWED_ERR: Raised if this property is readonly.
        """
        self._checkReadonly()
        if unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(
               u'CSSPrimitiveValue: unitType %r is not a float type' %
               self._getCSSPrimitiveTypeString(unitType))
        try:
            val = float(floatValue)
        except ValueError, e:
            raise xml.dom.InvalidAccessErr(
               u'CSSPrimitiveValue: floatValue %r is not a float' %
               floatValue)

        oldval, dim = self.__getNumDim()
        if self.primitiveType != unitType:
            # convert if possible
            try:
                val = self._converter[unitType, self.primitiveType](val)
            except KeyError:
                raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue: Cannot coerce primitiveType %r to %r'
                % (self.primitiveTypeString,
                   self._getCSSPrimitiveTypeString(unitType)))

        if val == int(val):
            val = int(val)

        self.cssText = '%s%s' % (val, dim)

    def getStringValue(self):
        """
        (DOM method) This method is used to get the string value. If the
        CSS value doesn't contain a string value, a DOMException is raised.

        Some properties (like 'font-family' or 'voice-family')
        convert a whitespace separated list of idents to a string.

        Only the actual value is returned so e.g. all the following return the
        actual value ``a``: url(a), attr(a), "a", 'a'
        """
        if self.primitiveType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue %r is not a string type'
                % self.primitiveTypeString)

        if CSSPrimitiveValue.CSS_ATTR == self.primitiveType:
            return self._value[0][5:-1]
        else:
            return self._value[0]

    def setStringValue(self, stringType, stringValue):
        """
        (DOM method) A method to set the string value with the specified
        unit. If the property attached to this value can't accept the
        specified unit or the string value, the value will be unchanged and
        a DOMException will be raised.

        stringType
            a string code as defined above. The string code can only be a
            string unit type (i.e. CSS_STRING, CSS_URI, CSS_IDENT, and
            CSS_ATTR).
        stringValue
            the new string value
            Only the actual value is expected so for (CSS_URI, "a") the
            new value will be ``url(a)``. For (CSS_STRING, "'a'")
            the new value will be ``"\\'a\\'"`` as the surrounding ``'`` are
            not part of the string value

        raises
            DOMException

            - INVALID_ACCESS_ERR: Raised if the CSS value doesn't contain a
              string value or if the string value can't be converted into
              the specified unit.

            - NO_MODIFICATION_ALLOWED_ERR: Raised if this property is readonly.
        """
        self._checkReadonly()
        # self not stringType
        if self.primitiveType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue %r is not a string type'
                % self.primitiveTypeString)
        # given stringType is no StringType
        if stringType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue: stringType %s is not a string type'
                % self._getCSSPrimitiveTypeString(stringType))

        if self._primitiveType != stringType:
            raise xml.dom.InvalidAccessErr(
                u'CSSPrimitiveValue: Cannot coerce primitiveType %r to %r'
                % (self.primitiveTypeString,
                   self._getCSSPrimitiveTypeString(stringType)))

        if CSSPrimitiveValue.CSS_STRING == self._primitiveType:
            self.cssText = u'"%s"' % stringValue.replace(u'"', ur'\\"')
        elif CSSPrimitiveValue.CSS_URI == self._primitiveType:
            # Some characters appearing in an unquoted URI, such as
            # parentheses, commas, whitespace characters, single quotes
            # (') and double quotes ("), must be escaped with a backslash
            # so that the resulting URI value is a URI token:
            # '\(', '\)', '\,'.
            #
            # Here the URI is set in quotes alltogether!
            if u'(' in stringValue or\
               u')' in stringValue or\
               u',' in stringValue or\
               u'"' in stringValue or\
               u'\'' in stringValue or\
               u'\n' in stringValue or\
               u'\t' in stringValue or\
               u'\r' in stringValue or\
               u'\f' in stringValue or\
               u' ' in stringValue:
                stringValue = '"%s"' % stringValue.replace(u'"', ur'\"')
            self.cssText = u'url(%s)' % stringValue
        elif CSSPrimitiveValue.CSS_ATTR == self._primitiveType:
            self.cssText = u'attr(%s)' % stringValue
        else:
            self.cssText = stringValue
        self._primitiveType = stringType

    def getCounterValue(self):
        """
        (DOM method) This method is used to get the Counter value. If
        this CSS value doesn't contain a counter value, a DOMException
        is raised. Modification to the corresponding style property
        can be achieved using the Counter interface.
        """
        if not self.CSS_COUNTER == self.primitiveType:
            raise xml.dom.InvalidAccessErr(u'Value is not a counter type')
        # TODO: use Counter class
        raise NotImplementedError()

    def getRGBColorValue(self):
        """
        (DOM method) This method is used to get the RGB color. If this
        CSS value doesn't contain a RGB color value, a DOMException
        is raised. Modification to the corresponding style property
        can be achieved using the RGBColor interface.
        """
        if self.primitiveType not in self._rbgtypes:
            raise xml.dom.InvalidAccessErr(u'Value is not a RGBColor value')
        return RGBColor(self._value[0])

    def getRectValue(self):
        """
        (DOM method) This method is used to get the Rect value. If this CSS
        value doesn't contain a rect value, a DOMException is raised.
        Modification to the corresponding style property can be achieved
        using the Rect interface.
        """
        if self.primitiveType not in self._recttypes:
            raise xml.dom.InvalidAccessErr(u'value is not a Rect value')
        # TODO: use Rect class
        raise NotImplementedError()

    def _getCssText(self):
        """overwritten from CSSValue"""
        return cssutils.ser.do_css_CSSPrimitiveValue(self)

    def _setCssText(self, cssText):
        """use CSSValue's implementation"""
        return super(CSSPrimitiveValue, self)._setCssText(cssText)
    
    cssText = property(_getCssText, _setCssText,
        doc="A string representation of the current value.")

    def __str__(self):
        return "<cssutils.css.%s object primitiveType=%s cssText=%r at 0x%x>" % (
                self.__class__.__name__, self.primitiveTypeString,
                self.cssText, id(self))


class CSSValueList(CSSValue):
    """
    The CSSValueList interface provides the abstraction of an ordered
    collection of CSS values.

    Some properties allow an empty list into their syntax. In that case,
    these properties take the none identifier. So, an empty list means
    that the property has the value none.

    The items in the CSSValueList are accessible via an integral index,
    starting from 0.
    """
    cssValueType = CSSValue.CSS_VALUE_LIST

    def __init__(self, cssText=None, readonly=False):
        """
        inits a new CSSValueList
        """
        super(CSSValueList, self).__init__(cssText=cssText, readonly=readonly)
        self._items = []

    length = property(lambda self: len(self._items),
                doc="(DOM attribute) The number of CSSValues in the list.")

    def item(self, index):
        """
        (DOM method) Used to retrieve a CSSValue by ordinal index. The
        order in this collection represents the order of the values in the
        CSS style property. If index is greater than or equal to the number
        of values in the list, this returns None.
        """
        try:
            return self._items[index]
        except IndexError:
            return None

    def __iter__(self):
        "CSSValueList is iterable"
        return CSSValueList.__items(self)

    def __items(self):
        "the iterator"
        for i in range (0, self.length):
            yield self.item(i)

    def __str__(self):
        return "<cssutils.css.%s object cssValueType=%r cssText=%r length=%r at 0x%x>" % (
                self.__class__.__name__, self.cssValueTypeString,
                self.cssText, self.length, id(self))


class CSSFunction(CSSPrimitiveValue):
    """A CSS function value like rect() etc."""
    
    def __init__(self, cssText=None, readonly=False):
        """
        Init a new CSSFunction

        cssText
            the parsable cssText of the value
        readonly
            defaults to False
        """
        super(RGBColor, self).__init__()
        self.valid = False
        self.wellformed = False
        if cssText is not None:
            self.cssText = cssText

        self._funcType = None

        self._readonly = readonly
    
    def _setCssText(self, cssText):
        self._checkReadonly()
        if False:
            pass
        else:            
            types = self._prods # rename!
            valueProd = Prod(name='value', 
                         match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
                         toSeq=CSSPrimitiveValue,
                         toStore='parts'
                         )
            # COLOR PRODUCTION
            funcProds = Sequence([
                                  Prod(name='FUNC', 
                                       match=lambda t, v: t == types.FUNCTION, 
                                       toStore='funcType' ),
                                       Prod(**PreDef.sign), 
                                       valueProd,
                                  # more values starting with Comma
                                  # should use store where colorType is saved to 
                                  # define min and may, closure?
                                  Sequence([Prod(**PreDef.comma), 
                                            Prod(**PreDef.sign), 
                                            valueProd], 
                                           minmax=lambda: (2, 2)), 
                                  Prod(**PreDef.funcEnd)
             ])
            # store: colorType, parts
            wellformed, seq, store, unusedtokens = ProdsParser().parse(cssText, 
                                                                u'CSSFunction', 
                                                                funcProds,
                                                                {'parts': []})
            
            if wellformed:
                self.wellformed = True
                self._setSeq(seq)
                self._funcType = self._normalize(store['colorType'].value[:-1])

    cssText = property(lambda self: cssutils.ser.do_css_RGBColor(self), 
                       _setCssText)
    
    funcType = property(lambda self: self._funcType)
    
    def __repr__(self):
        return "cssutils.css.%s(%r)" % (self.__class__.__name__, self.cssText)

    def __str__(self):
        return "<cssutils.css.%s object colorType=%r cssText=%r at 0x%x>" % (
                self.__class__.__name__, self.colorType, self.cssText,
                id(self))


class RGBColor(CSSPrimitiveValue):
    """A CSS color like RGB, RGBA or a simple value like `#000` or `red`."""
    
    def __init__(self, cssText=None, readonly=False):
        """
        Init a new RGBColor

        cssText
            the parsable cssText of the value
        readonly
            defaults to False
        """
        super(RGBColor, self).__init__()
        self._colorType = None
        self.valid = False
        self.wellformed = False
        if cssText is not None:
            self.cssText = cssText

        self._readonly = readonly
    
    def _setCssText(self, cssText):
        self._checkReadonly()
        types = self._prods # rename!
        valueProd = Prod(name='value', 
                     match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
                     toSeq=lambda t, v: (CSSPrimitiveValue, CSSPrimitiveValue(v)),
                     toStore='parts'
                     )
        # COLOR PRODUCTION
        funccolor = Sequence(Prod(name='FUNC', 
                                  match=lambda t, v: self._normalize(v) in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION,
                                  toSeq=lambda t, v: (t, self._normalize(v)), 
                                  toStore='colorType' ),
                                  PreDef.unary(), 
                                  valueProd,
                              # 2 or 3 more values starting with Comma
                             Sequence(PreDef.comma(), 
                                      PreDef.unary(), 
                                      valueProd, 
                                      minmax=lambda: (2, 3)), 
                             PreDef.funcEnd()
                            )
        colorprods = Choice(funccolor,
                            PreDef.hexcolor('colorType'),
                            Prod(name='named color', 
                                 match=lambda t, v: t == types.IDENT,
                                 toStore='colorType'
                                 )
                            )     
        # store: colorType, parts
        wellformed, seq, store, unusedtokens = ProdParser().parse(cssText, 
                                                            u'RGBColor', 
                                                            colorprods,
                                                            {'parts': []})
        
        if wellformed:
            self.wellformed = True
            if store['colorType'].type == self._prods.HASH:
                self._colorType = 'HEX'
            elif store['colorType'].type == self._prods.IDENT:
                self._colorType = 'Named Color'
            else:
                self._colorType = self._normalize(store['colorType'].value)[:-1]
                
            self._setSeq(seq)

    cssText = property(lambda self: cssutils.ser.do_css_RGBColor(self), 
                       _setCssText)
    
    colorType = property(lambda self: self._colorType)
    
    def __repr__(self):
        return "cssutils.css.%s(%r)" % (self.__class__.__name__, self.cssText)

    def __str__(self):
        return "<cssutils.css.%s object colorType=%r cssText=%r at 0x%x>" % (
                self.__class__.__name__, self.colorType, self.cssText,
                id(self))
