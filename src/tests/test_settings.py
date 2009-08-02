"""Testcases for cssutils.settings"""
__version__ = '$Id: test_csscharsetrule.py 1356 2008-07-13 17:29:09Z cthedot $'

import re
import xml.dom
import test_cssrule
import cssutils.css

class Settings(test_cssrule.CSSRuleTestCase):

    def test_set(self):
        "settings.set()"
        cssutils.ser.prefs.useMinified()
        text = 'a {filter: progid:DXImageTransform.Microsoft.BasicImage( rotation = 90 )}'
        
        self.assertEqual(cssutils.parseString(text).cssText, '')
        
        from cssutils import settings
        settings.set('DXImageTransform.Microsoft', True)
        self.assertEqual(cssutils.parseString(text).cssText,
                         'a{filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=90)}')
        
        cssutils.ser.prefs.useDefaults()

if __name__ == '__main__':
    import unittest
    unittest.main()
