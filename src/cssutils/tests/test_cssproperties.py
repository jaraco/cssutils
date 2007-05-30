"""Testcases for cssutils.css.cssproperties.*."""
__version__ = '0.9a5'

import xml.dom

import basetest

import cssutils


class CSSPropertiesTestCase(basetest.BaseTestCase):

    def test_cssvalues(self):
        "cssvalues"
        # does actually return match object, so a very simplified test...
        val = cssutils.css.cssproperties.cssvalues
        
        self.assertEquals(True, bool(val['color']('red')))
        self.assertEquals(True, bool(val['top']('1px')))
        self.assertEquals(True, bool(val['top']('0')))
                          
        self.assertEquals(False, bool(val['top']('red')))

if __name__ == '__main__':
    import unittest
    unittest.main() 