"""CSSValue implements DOM Level 2 CSS CSSValue.

TODO
    parsing and exception raising
    setting of correct CSSValueType

    pprint of value/unit e.g.   3 px  5px ->  3px 5px
    simplify colors if possible e.g. #ffaa55 ->  #fa5
    simplify values:    0px; ->  0;
"""
__all__ = ['CSSValue']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1b4'

__all__ = ['CSSStyleDeclaration']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'

import xml.dom 

import cssutils


class CSSValue(cssutils.util.Base):
    """
    The CSSValue interface represents a simple or a complex value.
    A CSSValue object only occurs in a context of a CSS property

    Properties
    ==========
    cssText
        A string representation of the current value.
    cssValueType
        A (readonly) code defining the type of the value.
    """
    CSS_INHERIT = 0         
    """ 
    The value is inherited and the cssText contains "inherit".
    """
    CSS_PRIMITIVE_VALUE = 1 
    """
    The value is a primitive value and an instance of the
    CSSPrimitiveValue interface can be obtained by using binding-specific
    casting methods on this instance of the CSSValue interface.
    """
    CSS_VALUE_LIST = 2
    """
    The value is a CSSValue list and an instance of the CSSValueList
    interface can be obtained by using binding-specific casting
    methods on this instance of the CSSValue interface.
    """
    CSS_CUSTOM = 3          
    """
    The value is a custom value.
    """
                            
    def __init__(self, cssText=u'inherit', readonly=False):
        """
        (cssutils)
        inits a new CSS Value

        cssText
            the parsable cssText of the value
        readonly
            defaults to False        
        """
        super(CSSValue, self).__init__()
        
        self.cssText = cssText
        self._readonly = readonly


    def _getCssText(self):
        return self._value

    def _setCssText(self, cssText):
        """
        DOMException on setting
        
        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error
          (according to the attached property) or is unparsable.
        - INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of values than the values allowed by the CSS property.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this value is readonly.
        """
        self._checkReadonly()
        
        # TODO: parse value, exceptions
        self._value = u' '.join(cssText.split())

        if cssText == u'inherit':
            self._cssValueType = self.CSS_INHERIT
        else:
            # TODO: set correct valuetype
            self._cssValueType = self.CSS_CUSTOM

    cssText = property(_getCssText, _setCssText,
        doc="A string representation of the current value.")


    def _getCssValueType(self):
        "readonly"
        return self._cssValueType

    cssValueType = property(_getCssValueType,
        doc="A code defining the type of the value as defined above.")
