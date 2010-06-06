"""Testcases for cssutils.settings"""
__version__ = '$Id: test_csscharsetrule.py 1356 2008-07-13 17:29:09Z cthedot $'

import re
import xml.dom
import test_cssrule
import cssutils
import cssutils.settings

class Settings(test_cssrule.CSSRuleTestCase):

    def test_set(self):
        "settings.set()"
        cssutils.ser.prefs.useMinified()
        text = 'a {filter: progid:DXImageTransform.Microsoft.BasicImage( rotation = 90 )}'
        
        self.assertEqual(cssutils.parseString(text).cssText, '')
        
        cssutils.settings.set('DXImageTransform.Microsoft', True)
        self.assertEqual(cssutils.parseString(text).cssText,
                         'a{filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=90)}')
        
        cssutils.ser.prefs.useDefaults()

#    def test_parseComments(self):
#        "settings.parseComments()"
#        text = '/*1*/ /*2'        
#        self.assertEqual(cssutils.parseString(text).cssText, '/*1*/\n/*2*/')
#
#        cssutils.settings.parseComments(False)
#        text = '/*1*/ /*2'        
#        self.assertEqual(cssutils.parseString(text).cssText, '')
#        
#        # reset
#        cssutils.settings.parseComments(True)

if __name__ == '__main__':
    import unittest
    unittest.main()
