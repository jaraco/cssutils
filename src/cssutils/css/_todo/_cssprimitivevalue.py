"""
CSSPrimitiveValue implements DOM Level 2 CSS PrimitiveValue.
"""
__all__ = ['CSSPrimitiveValue']
__docformat__ = 'restructuredtext'
__version__ = '0.9a1'

 TODO: conversion (mm->cm etc.)
 TODO: cssText: fset
 TODO: getXXXValue methods
 TODO: readonly

import re
import xml.dom

import cssbuilder
import cssvalue


class CSSPrimitiveValue (cssvalue.Value):
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
    """
    Unit Types
    An integer indicating which type of unit applies to the value.
    """
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
        
    "string representations for most unit types"
    _unitstrings = {
        0: u'', # UNKNOWN
        1: u'',
        2: u'%',
        3: u'em',
        4: u'ex',
        5: u'px',
        6: u'cm',
        7: u'mn',
        8: u'in',
        9: u'pt',
        10: u'pc',
        11: u'deg',
        12: u'rad',
        13: u'grad',
        14: u'ms',
        15: u's',
        16: u'hz',
        17: u'khz',
        18: u'', # DIMENSION
        19: u'', # STRING
        20: u'', # URI
        21: u'', # IDENT
        22: u'', # ATTR
        23: u'', # COUNTER
        24: u'', # RECT
        25: u'', # RBG
        }

    _floattypes = [CSS_NUMBER, CSS_PERCENTAGE, CSS_EMS, CSS_EXS,
                   CSS_PX, CSS_CM, CSS_MM, CSS_IN, CSS_PT, CSS_PC,
                   CSS_DEG, CSS_RAD, CSS_GRAD, CSS_MS, CSS_S,
                   CSS_HZ, CSS_KHZ, CSS_DIMENSION
                   ]
    _stringtypes = [CSS_ATTR, CSS_IDENT, CSS_STRING, CSS_URI]
    _countertypes = [CSS_COUNTER]
    _recttypes = [CSS_RECT]
    _rbgtypes = [CSS_RGBCOLOR]

    def __init__(self, text=u'', readonly=False):
        """
        The type of the value as defined by the constants
        specified above.
        """
        self._readonly = False
        self._valuetype = self.CSS_PRIMITIVE_VALUE
        self.cssText = text
        self._readonly = readonly

    def getFormatted(self):
        "returns a string representation of the current value"
        # TODO: URI representation and other!
        if self._primitivetype == self.CSS_RGBCOLOR:
            return self._value.cssText
        else:
            return u'%s%s' % (
                self._value, self._unitstrings[self.primitiveType])
    def _setCssText(self, text):
        """
        raises DOMException
        SYNTAX_ERR: Raised if the specified CSS string value has a
            syntax error (according to the attached property) or is
            unparsable.
        INVALID_MODIFICATION_ERR: Raised if the specified CSS string
            value represents a different type of values than the values
            allowed by the CSS property.
        - NO_MODIFICATION_ALLOWED_ERR: Raised if this value is readonly.
        """
        self._checkReadonly()
        if not text or not text.strip():
            raise xml.dom.SyntaxErr(u'no value given.')
        # parse
        v = text = text.strip()
        
        # a valid rgb value?
        RE_rgb = re.compile(u"""
            rgb \s* \( 
                ( \s* \d*\.?\d+ \s*%?\s* ,){2} 
                \s* \d*\.?\d+ \s*%?\s* 
            \)
            """, re.VERBOSE | re.UNICODE | re.IGNORECASE)    
        # a single r, g or b value (2, 2.0 or 2% or 2.0%)
        RE_rgb2 = re.compile(u"""\d*\.?\d+ \s*%?""",
             re.VERBOSE | re.UNICODE | re.IGNORECASE)     


        if text == u'inherit':
            # TODO: return normal Value!
            pass
        elif RE_rgb.match(text): #text.startswith(u'rgb('):           
            r, g, b = RE_rgb2.findall(text)
            v = cssbuilder.RGBColor(r, g, b)
            self._primitivetype = self.CSS_RGBCOLOR
        else:
            self._primitivetype = self.CSS_UNKNOWN
        self._value = v

    cssText = property(getFormatted, _setCssText,
                    doc="A string representation of the current value.")

    def _getType(self):
        return self._primitivetype
        
    primitiveType = property(_getType, doc="The type of the value as\
            defined by the constants specified above.")

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
        return self._value

    def getFloatValue(self, unitType):
        """
        (DOM method) This method is used to get a float value in a
        specified unit. If this CSS value doesn't contain a float value
        or can't be converted into the specified unit, a DOMException
        is raised.
        
        unitType
            to get the float value. The unit code can only be a float unit type
            (i.e. CSS_NUMBER, CSS_PERCENTAGE, CSS_EMS, CSS_EXS, CSS_PX, CSS_CM,
            CSS_MM, CSS_IN, CSS_PT, CSS_PC, CSS_DEG, CSS_RAD, CSS_GRAD, CSS_MS,
            CSS_S, CSS_HZ, CSS_KHZ, CSS_DIMENSION).
        """
        if unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(
                u'unitType Parameter is not a float type')
        return self._value
    
    def getRGBColorValue(self):
        """
        (DOM method) This method is used to get the RGB color. If this
        CSS value doesn't contain a RGB color value, a DOMException
        is raised. Modification to the corresponding style property
        can be achieved using the RGBColor interface.
        """
        # TODO: what about coercing #000 to RGBColor?
        if self.primitiveType not in self._rbgtypes:
            raise xml.dom.InvalidAccessErr(u'Value is not a RGB value')
        # TODO: use RGBColor class
        return self._value
        
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
        return self._value

    def getStringValue(self):
        """
        (DOM method) This method is used to get the string value. If the
        CSS value doesn't contain a string value, a DOMException is raised.

        Some properties (like 'font-family' or 'voice-family')
        convert a whitespace separated list of idents to a string.
        """
        if self.primitiveType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(u'value is not a string type')
        return self._value
        
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
            the new float value

        raises DOMException
            - INVALID_ACCESS_ERR: Raised if the attached property doesn't 
                support the float value or the unit type.
            - NO_MODIFICATION_ALLOWED_ERR: Raised if this property is readonly.
        """
        self._checkReadonly()
        if unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(u'value is not a float type')
        self._primitiveType = unitType
        self._value = floatValue

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
            
        raises
            DOMException
            - INVALID_ACCESS_ERR: Raised if the CSS value doesn't contain a
                string value or if the string value can't be converted into
                the specified unit.
            - NO_MODIFICATION_ALLOWED_ERR: Raised if this property is readonly.
        """
        self._checkReadonly()
        if stringType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(u'value is not a string type')
        self._primitiveType = stringType
        self._value = stringValue

  
