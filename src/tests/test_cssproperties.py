"""Testcases for cssutils.css.cssproperties."""

import xml.dom
import basetest
import cssutils.css
import cssutils.profiles

class CSSPropertiesTestCase(basetest.BaseTestCase):

#    def test_cssvalues(self):
#        "cssproperties cssvalues"
#        # does actually return match object, so a very simplified test...
#        match = cssutils.css.cssproperties.cssvalues
#
#        self.assertEquals(True, bool(match['color']('red')))
#        self.assertEquals(False, bool(match['top']('red')))
#
#        self.assertEquals(True, bool(match['left']('0')))
#        self.assertEquals(True, bool(match['left']('1px')))
#        self.assertEquals(True, bool(match['left']('.1px')))
#        self.assertEquals(True, bool(match['left']('-1px')))
#        self.assertEquals(True, bool(match['left']('-.1px')))
#        self.assertEquals(True, bool(match['left']('-0.1px')))

    def test_toDOMname(self):
        "cssproperties _toDOMname(CSSname)"
        _toDOMname = cssutils.css.cssproperties._toDOMname

        self.assertEquals('color', _toDOMname('color'))
        self.assertEquals('fontStyle', _toDOMname('font-style'))
        self.assertEquals('MozOpacity', _toDOMname('-moz-opacity'))
        self.assertEquals('UNKNOWN', _toDOMname('UNKNOWN'))
        self.assertEquals('AnUNKNOWN', _toDOMname('-anUNKNOWN'))

    def test_toCSSname(self):
        "cssproperties _toCSSname(DOMname)"
        _toCSSname = cssutils.css.cssproperties._toCSSname

        self.assertEquals('color', _toCSSname('color'))
        self.assertEquals('font-style', _toCSSname('fontStyle'))
        self.assertEquals('-moz-opacity', _toCSSname('MozOpacity'))
        self.assertEquals('UNKNOWN', _toCSSname('UNKNOWN'))
        self.assertEquals('-anUNKNOWN', _toCSSname('AnUNKNOWN'))

    def test_CSS2Properties(self):
        "CSS2Properties"
        CSS2Properties = cssutils.css.cssproperties.CSS2Properties
        self.assertEquals(type(property()), type(CSS2Properties.color))
        self.assertEquals(sum([len(x) for x in cssutils.profiles.properties.values()]),
                          len(CSS2Properties._properties))

        c2 = CSS2Properties()
        # CSS2Properties has simplified implementation return always None
        self.assertEquals(None, c2.color)
        self.assertEquals(None, c2.__setattr__('color', 1))
        self.assertEquals(None, c2.__delattr__('color'))
        # only defined properties
        self.assertRaises(AttributeError, c2.__getattribute__, 'UNKNOWN')


if __name__ == '__main__':
    import unittest
    unittest.main()
