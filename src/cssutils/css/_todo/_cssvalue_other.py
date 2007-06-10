"""
contains DOM Level 2 CSS ValueList implementation classes.

** NOT USED CURRENTLY
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2 $LastChangedRevision$'

import xml.dom

import cssutils.css


class RGBColor(cssutils.css.Value):
    """
    The RGBColor interface is used to represent any RGB color value.
    This interface reflects the values in the underlying style property.
    Hence, modifications made to the CSSPrimitiveValue objects modify
    the style property.

    A specified RGB color is not clipped (even if the number is outside
    the range 0-255 or 0%-100%). A computed RGB color is clipped depending
    on the device.

    Even if a style sheet can only contain an integer for a color value,
    the internal storage of this integer is a float, and this can be used
    as a float in the specified or the computed style.

    A color percentage value can always be converted to a number and
    vice versa.    
    """
    def __init__(self, red, green, blue):
        """
        inits the RGBColor with possible values for red, green and blue as
        an integer (0-255) or float value (0.0% - 100.0%).
        cssutils only looks if a "%" is present, the type of the values is not
        used!
        """
        self.red = self.__parse(red)
        self.green = self.__parse(green)
        self.blue = self.__parse(blue)
    
    def __parse(self, v):
        "returns (value, percent[u'%' or ''])"
        # TODO: exceptions! - logging?
        v = unicode(v).strip()
        if u'%' == v[-1]:
            try:
                v = float(v[:-1])
                p = u'%'
            except ValueError:
                raise xml.dom.SyntaxErr(
                    '"%s" is not valid for a RGB Color value' % v)
        else:
            try:
                v = int(v)
                p = u''
            except ValueError:
                try:
                    v = float(v)
                    p = u'%'
                except ValueError:
                    raise xml.dom.SyntaxErr(
                        '"%s" is not valid for a RGB Color value' % v)
        return v, p
    
    def __getFormatted(self):
        """
        (cssutils only) returns a string representation 
        like rgb(1%, 20%, 100%)
        """
        return u'rgb(%s%s, %s%s, %s%s)' % (
            self.red[0], self.red[1], 
            self.green[0], self.green[1], 
            self.blue[0], self.blue[1])
        
    cssText = property(__getFormatted, doc=
            '(cssutils only) readonly string representation')


class Rect(cssbuilder.Value):
    """
    The Rect interface is used to represent any rect value. This interface
    reflects the values in the underlying style property. Hence,
    modifications made to the CSSPrimitiveValue objects modify the style
    property.

    // Introduced in DOM Level 2:
        interface Rect {
          readonly attribute CSSPrimitiveValue  top;
          readonly attribute CSSPrimitiveValue  right;
          readonly attribute CSSPrimitiveValue  bottom;
          readonly attribute CSSPrimitiveValue  left;
        };    
    """


class Counter(cssbuilder.Value):
    """
    The Counter interface is used to represent any counter or counters
    function value. This interface reflects the values in the underlying
    style property.

    // Introduced in DOM Level 2:
        interface Counter {
          readonly attribute DOMString        identifier;
          readonly attribute DOMString        listStyle;
          readonly attribute DOMString        separator;
        };        
    """
    
    