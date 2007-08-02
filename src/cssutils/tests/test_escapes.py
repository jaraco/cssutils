"""
tests for escaping
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-06-17 16:04:45 +0200 (So, 17 Jun 2007) $'
__version__ = '0.9.2a2, $LastChangedRevision: 63 $'

import xml.dom

import basetest


import cssutils.css


class CSSStyleSheetTestCase(basetest.BaseTestCase):

    pass

##    def test_escapes(self):
##        "ESCAPES"
##        tests = {
##            #u'\\@a "x";': u'\\@a "x";',
##            u'a\\{ {}': u'a\\{ {}',
##            u'a { x\\::1;y:2 }': u'a {\n    x\\:: 1;\n    y: 2\n    }'
##            }
##        for css, exp in tests.items():
##            s = cssutils.parseString(css)
##            self.assertEqual(exp, s.cssText)


if __name__ == '__main__':
    import unittest
    unittest.main()
